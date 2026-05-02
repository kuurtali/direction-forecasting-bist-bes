# ============================================================
# THYAO Hisse Senedi Fiyat Yonu Tahmini — GÜNCEL VERSİYON
# Referans: Van der Burgt (2023) "Navigating Trends"
# Tarih: 2018-01-01 / 2026-03-31
# Fear&Greed çıkarıldı (veri 2020'de bitiyor — FARK 9)
#
# Makaleye sadık mimari:
#   - Tek katman LSTM (64 units) — makaleyle birebir
#   - 3 katman CNN (makaleyle birebir)
#   - 50 epoch, batch_size=32
#
# Akademik iyileştirmeler (makale yapmamış, biz yaptık):
#   - preProcess sadece train üzerinde fit (data leakage yok)
#   - Label her split için ayrı oluşturulur
#   - class_weight ile sınıf dengesizliği düzeltilir
#   - Early stopping (patience=5, restore_best_weights)
#   - Sınıf dengesi raporlanır
# ============================================================

# TensorFlow Kurulum (sadece ilk seferde):
# 1. R/RStudio TF kurulumu için install_packages.R çalıştırın
# 2. pip install tensorflow==2.16.1

# install.packages("reshape2", type = "source")  # Bkz. install_packages.R
library(quantmod)
library(tidyverse)
library(TTR)
library(caret)
library(zoo)
library(keras3)
library(tensorflow)
library(abind)
library(forecast)

# Çıktı klasörünü hazırla
if (!dir.exists("output")) dir.create("output", showWarnings = FALSE, recursive = TRUE)


# ============================================================
# BÖLÜM 1: VERİ ÇEKME VE ÖN İŞLEME
# ============================================================

getSymbols("THYAO.IS")
THYAO <- THYAO.IS["2018-01-01/2026-03-31"]

THYAO_df <- data.frame(
  Date   = as.character(index(THYAO)),
  Open   = as.numeric(Op(THYAO)),
  High   = as.numeric(Hi(THYAO)),
  Low    = as.numeric(Lo(THYAO)),
  Close  = as.numeric(Cl(THYAO)),
  Volume = as.numeric(Vo(THYAO))
)

THYAO_df <- THYAO_df[THYAO_df$Volume > 0, ]
THYAO_df <- THYAO_df[complete.cases(THYAO_df[, c("Open","High","Low","Close")]), ]

# Teknik göstergeler
THYAO_df$RSI   <- RSI(THYAO_df$Close, n = 14)
macd_vals      <- MACD(THYAO_df$Close)
THYAO_df$MACD  <- macd_vals[, "macd"]
THYAO_df$EMA12 <- EMA(THYAO_df$Close, n = 12)
THYAO_df$EMA26 <- EMA(THYAO_df$Close, n = 26)
stoch_vals     <- stoch(THYAO_df[, c("High", "Low", "Close")])
THYAO_df$SO_K  <- stoch_vals[, "fastK"]
THYAO_df$SO_D  <- stoch_vals[, "fastD"]
adx_vals       <- ADX(THYAO_df[, c("High", "Low", "Close")])
THYAO_df$ADX   <- adx_vals[, "ADX"]

# İlk 27 satır çıkar (gösterge ısınma süresi)
THYAO_df <- THYAO_df[28:nrow(THYAO_df), ]

# Dış değişkenler
getSymbols("USDTRY=X", from = "2018-01-01", to = "2026-03-31")
USDTRY_df <- data.frame(
  Date   = as.character(index(`USDTRY=X`)),
  USDTRY = as.numeric(Cl(`USDTRY=X`))
)

getSymbols("CL=F", from = "2018-01-01", to = "2026-03-31")
OIL_df <- data.frame(
  Date = as.character(index(`CL=F`)),
  Oil  = as.numeric(Cl(`CL=F`))
)

getSymbols("INTDSRTRM193N", src = "FRED", from = "2018-01-01", to = "2026-03-31")
TCMB_df <- data.frame(
  Date      = as.Date(index(INTDSRTRM193N)),
  TCMB_Rate = as.numeric(INTDSRTRM193N)
)
TCMB_daily <- data.frame(Date = as.Date(THYAO_df$Date)) %>%
  mutate(YearMonth = format(Date, "%Y-%m")) %>%
  left_join(TCMB_df %>% mutate(YearMonth = format(Date, "%Y-%m")), by = "YearMonth") %>%
  select(Date = Date.x, TCMB_Rate)

# Birleştir (Fear&Greed YOK — FARK 9)
THYAO_final <- THYAO_df %>%
  left_join(USDTRY_df, by = "Date") %>%
  left_join(OIL_df, by = "Date") %>%
  left_join(TCMB_daily %>% mutate(Date = as.character(Date)), by = "Date")

THYAO_final$USDTRY    <- na.locf(THYAO_final$USDTRY, na.rm = FALSE)
THYAO_final$Oil       <- na.locf(THYAO_final$Oil, na.rm = FALSE)
THYAO_final$TCMB_Rate <- na.locf(THYAO_final$TCMB_Rate, na.rm = FALSE)

cat("Asama 1 tamam:", nrow(THYAO_final), "satir\n")

# ============================================================
# BÖLÜM 2: KRONOLOJİK BÖLME + ÖLÇEKLEME (data leakage yok)
# preProcess sadece train üzerinde fit edilir
# ============================================================

n <- nrow(THYAO_final)
train_end <- floor(n * 0.70)
val_end   <- floor(n * 0.85)

train_raw <- THYAO_final[1:train_end, ]
val_raw   <- THYAO_final[(train_end + 1):val_end, ]
test_raw  <- THYAO_final[(val_end + 1):n, ]

cat(sprintf("Bolunme: Train=%d  Val=%d  Test=%d\n",
            nrow(train_raw), nrow(val_raw), nrow(test_raw)))

olcek_sutunlar <- c("Open", "Close", "Volume", "USDTRY", "Oil", "TCMB_Rate")

# MinMax sadece train'den hesaplanır, val/test'e uygulanır
preproc    <- preProcess(train_raw[, olcek_sutunlar], method = "range")
train_data <- predict(preproc, train_raw)
val_data   <- predict(preproc, val_raw)
test_data  <- predict(preproc, test_raw)

# ============================================================
# BÖLÜM 3: LABEL OLUŞTURMA (her split için ayrı)
# ============================================================

create_label <- function(close_prices, output_len) {
  n <- length(close_prices)
  label <- rep(NA, n)
  for(i in 1:(n - output_len)) {
    label[i] <- ifelse(close_prices[i + output_len] > close_prices[i], 1, 0)
  }
  return(label)
}

for(out_len in c(1, 3, 5)) {
  col <- paste0("label_", out_len)
  train_data[[col]] <- create_label(train_data$Close, out_len)
  val_data[[col]]   <- create_label(val_data$Close, out_len)
  test_data[[col]]  <- create_label(test_data$Close, out_len)
}

cat("Asama 2 tamam: Train=", nrow(train_data),
    "Val=", nrow(val_data), "Test=", nrow(test_data), "\n")

# ============================================================
# BÖLÜM 4: SINIF DENGESİ VE CLASS_WEIGHT
# ============================================================

cat("\n--- Sinif Dengesi (train) ---\n")
sinif_agirlik <- list()
for(out_len in c(1, 3, 5)) {
  col     <- paste0("label_", out_len)
  gecerli <- train_data[[col]][!is.na(train_data[[col]])]
  tablo   <- table(gecerli)
  n0 <- as.numeric(tablo["0"]); if(is.na(n0)) n0 <- 0
  n1 <- as.numeric(tablo["1"]); if(is.na(n1)) n1 <- 0
  toplm <- n0 + n1
  cat(sprintf("  label_%d -> Dusus: %d (%.1f%%) | Yukselis: %d (%.1f%%)\n",
              out_len, n0, 100*n0/toplm, n1, 100*n1/toplm))
  w0 <- toplm / (2 * max(n0, 1))
  w1 <- toplm / (2 * max(n1, 1))
  sinif_agirlik[[col]] <- list("0" = w0, "1" = w1)
}

# ============================================================
# BÖLÜM 5: ORTAK PARAMETRELER
# ============================================================

feature_sets <- list(
  "hist_tech"  = c("Open","Close","Volume","RSI","MACD","EMA12","EMA26",
                   "SO_K","SO_D","ADX","USDTRY","Oil","TCMB_Rate"),
  "technical"  = c("RSI","MACD","EMA12","EMA26","SO_K","SO_D","ADX"),
  "historical" = c("Open","Close","Volume","USDTRY","Oil","TCMB_Rate"),
  "closing"    = c("Close")
)

kombinasyonlar <- list(
  list(input=2, output=1, label="label_1"),
  list(input=2, output=3, label="label_3"),
  list(input=2, output=5, label="label_5"),
  list(input=4, output=1, label="label_1"),
  list(input=4, output=3, label="label_3"),
  list(input=4, output=5, label="label_5"),
  list(input=6, output=1, label="label_1"),
  list(input=6, output=3, label="label_3"),
  list(input=6, output=5, label="label_5")
)

seeds  <- c(23, 27, 98)
toplam <- length(feature_sets) * length(kombinasyonlar)

# ============================================================
# BÖLÜM 6: YARDIMCI FONKSİYONLAR
# ============================================================

create_seq <- function(data, input_len, label_col, feat_cols) {
  X <- list(); y <- c()
  for(i in input_len:nrow(data)) {
    pencere <- as.matrix(data[(i - input_len + 1):i, feat_cols, drop=FALSE])
    X[[length(X)+1]] <- pencere
    y <- c(y, data[[label_col]][i])
  }
  X_array <- array(unlist(X), dim=c(length(X), input_len, length(feat_cols)))
  return(list(X=X_array, y=y))
}

hesapla_metrikler <- function(seed_accs, all_preds, y_test) {
  gecerli <- !is.na(seed_accs)
  if(sum(gecerli) == 0) {
    return(list(mean_acc=NA, sd_acc=NA, min_acc=NA, max_acc=NA,
                p_val=NA, f1=NA, sens=NA, spec=NA))
  }
  mean_acc <- mean(seed_accs, na.rm=TRUE)
  sd_acc   <- ifelse(sum(gecerli)>1, sd(seed_accs, na.rm=TRUE), 0)
  min_acc  <- min(seed_accs, na.rm=TRUE)
  max_acc  <- max(seed_accs, na.rm=TRUE)
  best_idx <- which.max(seed_accs)
  best_pred <- all_preds[[best_idx]]
  p_val <- NA; f1 <- NA; sens <- NA; spec <- NA
  if(!is.null(best_pred) && length(best_pred)==length(y_test)) {
    p_val <- binom.test(sum(best_pred==y_test), length(y_test), p=0.5, alternative="greater")$p.value
    tryCatch({
      cm <- confusionMatrix(factor(best_pred, levels=c(0,1)), factor(y_test, levels=c(0,1)), positive="1")
      f1   <- cm$byClass["F1"]
      sens <- cm$byClass["Sensitivity"]
      spec <- cm$byClass["Specificity"]
    }, error=function(e) NULL)
  }
  return(list(mean_acc=mean_acc, sd_acc=sd_acc, min_acc=min_acc, max_acc=max_acc, p_val=p_val, f1=f1, sens=sens, spec=spec))
}

yeni_early_stop <- function() {
  callback_early_stopping(
    monitor              = "val_loss",
    patience             = 5,
    restore_best_weights = TRUE
  )
}

# ============================================================
# BÖLÜM 7: ARIMA
# ============================================================

cat("\n=== MODEL 1: ARIMA ===\n")
arima_sonuclar <- data.frame()

for(k in kombinasyonlar) {
  input_len <- k$input; label_col <- k$label
  best_acc <- 0; best_d <- 0
  for(d in 0:5) {
    model <- withCallingHandlers(
      tryCatch({arima(train_data$Close, order=c(input_len,d,input_len), method="CSS")}, error=function(e) NULL),
      warning=function(w) invokeRestart("muffleWarning"))
    if(!is.null(model)) {
      preds <- tryCatch(forecast(model, h=nrow(val_data))$mean, error=function(e) NULL)
      if(is.null(preds)) next
      pred_labels <- ifelse(diff(c(tail(train_data$Close,1), preds))>0, 1, 0)
      gercek <- val_data[[label_col]]; gercek <- gercek[!is.na(gercek)]
      pred_labels <- pred_labels[1:length(gercek)]
      acc <- mean(pred_labels == gercek)
      if(acc > best_acc) {best_acc <- acc; best_d <- d}
    }
  }
  model_final <- withCallingHandlers(
    tryCatch({arima(c(train_data$Close, val_data$Close), order=c(input_len, best_d, input_len), method="CSS")}, error=function(e) NULL),
    warning=function(w) invokeRestart("muffleWarning"))
  if(!is.null(model_final)) {
    preds_test <- tryCatch(forecast(model_final, h=nrow(test_data))$mean, error=function(e) NULL)
    if(!is.null(preds_test)) {
      pred_labels_test <- ifelse(diff(c(tail(val_data$Close,1), preds_test))>0, 1, 0)
      gercek_test <- test_data[[label_col]]; gercek_test <- gercek_test[!is.na(gercek_test)]
      pred_labels_test <- pred_labels_test[1:length(gercek_test)]
      test_acc <- mean(pred_labels_test == gercek_test)
      arima_sonuclar <- rbind(arima_sonuclar, data.frame(Input=input_len, Output=k$output, Best_d=best_d, Test_Acc=round(test_acc,4)))
      cat(sprintf("  Input=%d Output=%d d=%d -> Acc=%.4f\n", input_len, k$output, best_d, test_acc))
    }
  }
}

write.csv(arima_sonuclar, "output/ARIMA_sonuclar.csv", row.names=FALSE)
cat("ARIMA tamam. Ortalama:", round(mean(arima_sonuclar$Test_Acc),4), "\n")

# ============================================================
# BÖLÜM 8: LSTM — Tek katman 64 units (makaleyle birebir)
# ============================================================

cat("\n=== MODEL 2: LSTM ===\n")

build_lstm <- function(input_len, n_features, activation, dropout_rate, optimizer_name) {
  model <- keras_model_sequential() %>%
    layer_lstm(units=64, activation=activation, input_shape=c(input_len, n_features)) %>%
    layer_dropout(rate=dropout_rate) %>%
    layer_dense(units=1, activation="sigmoid")
  model %>% compile(optimizer=optimizer_name, loss="binary_crossentropy", metrics=list("accuracy"))
  return(model)
}

lstm_grid <- expand.grid(optimizer=c("adam","sgd"), activation=c("relu","tanh"), dropout=c(0.0, 0.2, 0.4), stringsAsFactors=FALSE)

lstm_sonuclar <- data.frame()
sayac <- 0

for(set_name in names(feature_sets)) {
  feat_cols <- feature_sets[[set_name]]; n_feat <- length(feat_cols)
  cat(sprintf("\n-- LSTM: %s (%d ozellik) --\n", set_name, n_feat))
  for(k in kombinasyonlar) {
    sayac <- sayac + 1
    input_len <- k$input; label_col <- k$label
    cw <- sinif_agirlik[[label_col]]
    cat(sprintf("[%d/%d] Input=%d Output=%d ", sayac, toplam, input_len, k$output))
    train_s <- create_seq(train_data, input_len, label_col, feat_cols)
    val_s   <- create_seq(val_data, input_len, label_col, feat_cols)
    tok <- !is.na(train_s$y); vok <- !is.na(val_s$y)
    X_tr <- train_s$X[tok,,,drop=F]; y_tr <- train_s$y[tok]
    X_vl <- val_s$X[vok,,,drop=F]; y_vl <- val_s$y[vok]
    best_val <- -1; best_p <- list(optimizer="adam",activation="relu",dropout=0.0)
    for(g in 1:nrow(lstm_grid)) {
      set.seed(23); tensorflow::tf$random$set_seed(23L)
      m <- tryCatch(build_lstm(input_len,n_feat,lstm_grid$activation[g],lstm_grid$dropout[g],lstm_grid$optimizer[g]), error=function(e) NULL)
      if(is.null(m)) next
      tryCatch({
        m %>% fit(X_tr,y_tr,epochs=50,batch_size=32,
                  validation_data=list(X_vl,y_vl),
                  class_weight=cw,
                  callbacks=list(yeni_early_stop()),
                  verbose=0)
        va <- mean(as.numeric(predict(m,X_vl,verbose=0)>0.5)==y_vl)
        if(va>best_val){best_val<-va; best_p<-list(optimizer=lstm_grid$optimizer[g],activation=lstm_grid$activation[g],dropout=lstm_grid$dropout[g])}
      }, error=function(e) NULL)
    }
    comb <- rbind(train_data, val_data)
    cs <- create_seq(comb, input_len, label_col, feat_cols)
    ts <- create_seq(test_data, input_len, label_col, feat_cols)
    cok <- !is.na(cs$y); teok <- !is.na(ts$y)
    X_c <- cs$X[cok,,,drop=F]; y_c <- cs$y[cok]
    X_te <- ts$X[teok,,,drop=F]; y_te <- ts$y[teok]
    sa <- c(); ap <- list()
    for(s in seeds) {
      set.seed(s); tensorflow::tf$random$set_seed(as.integer(s))
      fm <- tryCatch(build_lstm(input_len,n_feat,best_p$activation,best_p$dropout,best_p$optimizer), error=function(e) NULL)
      if(is.null(fm)){sa<-c(sa,NA); next}
      tryCatch({
        fm %>% fit(X_c,y_c,epochs=50,batch_size=32,
                   class_weight=cw,
                   verbose=0)
        pr <- as.numeric(predict(fm,X_te,verbose=0)>0.5)
        sa <- c(sa, mean(pr==y_te)); ap[[as.character(s)]] <- pr
      }, error=function(e){sa<<-c(sa,NA)})
    }
    met <- hesapla_metrikler(sa, ap, y_te)
    lstm_sonuclar <- rbind(lstm_sonuclar, data.frame(Feature_Set=set_name, Input=input_len, Output=k$output, Optimizer=best_p$optimizer, Activation=best_p$activation, Dropout=best_p$dropout, Seed_23=round(sa[1],4), Seed_27=round(sa[2],4), Seed_98=round(sa[3],4), Mean_Acc=round(met$mean_acc,4), SD=round(met$sd_acc,4), Min_Acc=round(met$min_acc,4), Max_Acc=round(met$max_acc,4), P_Value=round(met$p_val,4), F1=round(as.numeric(met$f1),4), Sens=round(as.numeric(met$sens),4), Spec=round(as.numeric(met$spec),4), stringsAsFactors=FALSE))
    cat(sprintf("-> %.4f (SD=%.4f)\n", met$mean_acc, met$sd_acc))
    if(sayac%%9==0) {write.csv(lstm_sonuclar,"output/LSTM_sonuclar_ARAKAYIT.csv",row.names=F)}
  }
}

write.csv(lstm_sonuclar, "output/LSTM_sonuclar_FINAL.csv", row.names=FALSE)
cat("LSTM tamam\n")

# ============================================================
# BÖLÜM 9: 1D-CNN — 3 katman Conv1D (makaleyle birebir)
# ============================================================

cat("\n=== MODEL 3: 1D-CNN ===\n")

build_cnn <- function(input_len, n_features, filters, kernel_size, dense_units, dropout_rate) {
  model <- keras_model_sequential() %>%
    layer_conv_1d(filters=filters[1], kernel_size=kernel_size, activation="relu", input_shape=c(input_len, n_features), padding="same") %>%
    layer_conv_1d(filters=filters[2], kernel_size=kernel_size, activation="relu", padding="same") %>%
    layer_conv_1d(filters=filters[3], kernel_size=kernel_size, activation="relu", padding="same") %>%
    layer_flatten() %>%
    layer_dense(units=dense_units, activation="relu") %>%
    layer_dropout(rate=dropout_rate) %>%
    layer_dense(units=1, activation="sigmoid")
  model %>% compile(optimizer="adam", loss="binary_crossentropy", metrics=list("accuracy"))
  return(model)
}

filter_configs <- list(c(32,64,128), c(64,128,256))
cnn_grid <- expand.grid(dropout=c(0.2,0.3,0.4), filter_idx=c(1,2), kernel_size=c(3), dense_units=c(64,128,256), stringsAsFactors=FALSE)
cnn_grid_k5 <- expand.grid(dropout=c(0.2,0.4), filter_idx=c(1), kernel_size=c(5), dense_units=c(128), stringsAsFactors=FALSE)
cnn_grid <- rbind(cnn_grid, cnn_grid_k5)

cnn_sonuclar <- data.frame()
sayac <- 0

for(set_name in names(feature_sets)) {
  feat_cols <- feature_sets[[set_name]]; n_feat <- length(feat_cols)
  cat(sprintf("\n-- CNN: %s (%d ozellik) --\n", set_name, n_feat))
  for(k in kombinasyonlar) {
    sayac <- sayac + 1
    input_len <- k$input; label_col <- k$label
    cw <- sinif_agirlik[[label_col]]
    cat(sprintf("[%d/%d] Input=%d Output=%d ", sayac, toplam, input_len, k$output))
    train_s <- create_seq(train_data, input_len, label_col, feat_cols)
    val_s   <- create_seq(val_data, input_len, label_col, feat_cols)
    tok <- !is.na(train_s$y); vok <- !is.na(val_s$y)
    X_tr <- train_s$X[tok,,,drop=F]; y_tr <- train_s$y[tok]
    X_vl <- val_s$X[vok,,,drop=F]; y_vl <- val_s$y[vok]
    best_val <- -1
    best_p <- list(dropout=0.2, filters=c(32,64,128), kernel_size=3, dense_units=64)
    for(g in 1:nrow(cnn_grid)) {
      filt <- filter_configs[[cnn_grid$filter_idx[g]]]
      set.seed(23); tensorflow::tf$random$set_seed(23L)
      m <- tryCatch(build_cnn(input_len,n_feat,filt,cnn_grid$kernel_size[g],cnn_grid$dense_units[g],cnn_grid$dropout[g]), error=function(e) NULL)
      if(is.null(m)) next
      tryCatch({
        m %>% fit(X_tr,y_tr,epochs=50,batch_size=32,
                  validation_data=list(X_vl,y_vl),
                  class_weight=cw,
                  callbacks=list(yeni_early_stop()),
                  verbose=0)
        va <- mean(as.numeric(predict(m,X_vl,verbose=0)>0.5)==y_vl)
        if(va>best_val){best_val<-va; best_p<-list(dropout=cnn_grid$dropout[g],filters=filt,kernel_size=cnn_grid$kernel_size[g],dense_units=cnn_grid$dense_units[g])}
      }, error=function(e) NULL)
    }
    comb <- rbind(train_data, val_data)
    cs <- create_seq(comb, input_len, label_col, feat_cols)
    ts <- create_seq(test_data, input_len, label_col, feat_cols)
    cok <- !is.na(cs$y); teok <- !is.na(ts$y)
    X_c <- cs$X[cok,,,drop=F]; y_c <- cs$y[cok]
    X_te <- ts$X[teok,,,drop=F]; y_te <- ts$y[teok]
    sa <- c(); ap <- list()
    for(s in seeds) {
      set.seed(s); tensorflow::tf$random$set_seed(as.integer(s))
      fm <- tryCatch(build_cnn(input_len,n_feat,best_p$filters,best_p$kernel_size,best_p$dense_units,best_p$dropout), error=function(e) NULL)
      if(is.null(fm)){sa<-c(sa,NA); next}
      tryCatch({
        fm %>% fit(X_c,y_c,epochs=50,batch_size=32,
                   class_weight=cw,
                   verbose=0)
        pr <- as.numeric(predict(fm,X_te,verbose=0)>0.5)
        sa <- c(sa, mean(pr==y_te)); ap[[as.character(s)]] <- pr
      }, error=function(e){sa<<-c(sa,NA)})
    }
    met <- hesapla_metrikler(sa, ap, y_te)
    cnn_sonuclar <- rbind(cnn_sonuclar, data.frame(Feature_Set=set_name, Input=input_len, Output=k$output, Dropout=best_p$dropout, Filters=paste(best_p$filters,collapse="-"), Kernel=best_p$kernel_size, Dense=best_p$dense_units, Seed_23=round(sa[1],4), Seed_27=round(sa[2],4), Seed_98=round(sa[3],4), Mean_Acc=round(met$mean_acc,4), SD=round(met$sd_acc,4), Min_Acc=round(met$min_acc,4), Max_Acc=round(met$max_acc,4), P_Value=round(met$p_val,4), F1=round(as.numeric(met$f1),4), Sens=round(as.numeric(met$sens),4), Spec=round(as.numeric(met$spec),4), stringsAsFactors=FALSE))
    cat(sprintf("-> %.4f (SD=%.4f)\n", met$mean_acc, met$sd_acc))
    if(sayac%%9==0) {write.csv(cnn_sonuclar,"output/CNN_sonuclar_ARAKAYIT.csv",row.names=F)}
  }
}

write.csv(cnn_sonuclar, "output/CNN_sonuclar_FINAL.csv", row.names=FALSE)
cat("CNN tamam\n")

# ============================================================
# BÖLÜM 10: NAIVE BASELINE
# ============================================================

cat("\n=== NAIVE BASELINE ===\n")
naive_sonuclar <- data.frame()
for(k in kombinasyonlar) {
  gercek <- test_data[[k$label]]; gercek <- gercek[!is.na(gercek)]
  son_val <- tail(val_data[[k$label]][!is.na(val_data[[k$label]])], 1)
  naive_pred <- c(son_val, head(gercek, -1))
  naive_acc  <- mean(naive_pred == gercek)
  naive_sonuclar <- rbind(naive_sonuclar, data.frame(Input=k$input, Output=k$output, Naive_Acc=round(naive_acc,4)))
  cat(sprintf("  Output=%d -> %.4f\n", k$output, naive_acc))
}
write.csv(naive_sonuclar, "output/NAIVE_baseline.csv", row.names=FALSE)

# ============================================================
# BÖLÜM 11: ÖZET
# ============================================================

cat("\n=== TUM MODELLER TAMAMLANDI ===\n")
cat("ARIMA Ortalama:", round(mean(arima_sonuclar$Test_Acc),4), "\n")
cat("Naive Ortalama:", round(mean(naive_sonuclar$Naive_Acc),4), "\n")
for(sn in names(feature_sets)) {
  ls <- lstm_sonuclar[lstm_sonuclar$Feature_Set==sn,]
  cs <- cnn_sonuclar[cnn_sonuclar$Feature_Set==sn,]
  cat(sprintf("LSTM %-12s: %.4f | CNN %-12s: %.4f\n", sn, mean(ls$Mean_Acc,na.rm=T), sn, mean(cs$Mean_Acc,na.rm=T)))
}
cat("\nDosyalar: ARIMA_sonuclar.csv, LSTM_sonuclar_FINAL.csv, CNN_sonuclar_FINAL.csv, NAIVE_baseline.csv\n")

cat("\n--- Akademik Iyilestirmeler (makaleye ek) ---\n")
cat("1. preProcess sadece train uzerinde fit (data leakage onlendi)\n")
cat("2. Label her split icin ayri olusturuldu\n")
cat("3. class_weight ile sinif dengesizligi duzeltildi\n")
cat("4. Early stopping (patience=5) grid search asamasinda kullanildi\n")
cat("5. Fear&Greed cikarildi (veri 2020'de bitiyor — FARK 9)\n")