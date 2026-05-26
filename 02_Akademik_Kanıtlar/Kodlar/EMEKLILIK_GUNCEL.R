# ============================================================
# EMEKLİLİK FONLARI Yön Tahmini — GÜNCEL VERSİYON
# Referans: Van der Burgt (2023) "Navigating Trends"
# Tarih: 2021-w13 / 2026-w14 | Haftalık
# Fonlar: ALZ (Düşük risk), AZS (Orta risk), AMZ (Yüksek risk)
#
# Akademik iyileştirmeler (THYAO ile tutarlı):
#   - preProcess sadece train üzerinde fit (data leakage yok)
#   - Label her split için ayrı oluşturulur
#   - class_weight ile sınıf dengesizliği düzeltilir
#   - Early stopping (patience=5, restore_best_weights) grid search'te
#   - Fon bazlı NA temizliği (eksik fiyat satırları önce çıkarılır)
# ============================================================

# TensorFlow Kurulum (sadece ilk seferde):
# 1. CMD yönetici → cd C:\Users\Kurt\Documents\.virtualenvs\r-keras\Scripts
# 2. pip install tensorflow==2.16.1
# 3. RStudio'da: install.packages("reshape2", type = "source")

install.packages("reshape2", type = "source")

# Çalışma dizini — tüm dosyalar buradan okunur ve buraya yazılır
setwd("C:/Users/Kurt/Desktop")

# GPU bypass — Session Aborted sorununu önler (RTX 5050 / CUDA uyumsuzluğu)
Sys.setenv(CUDA_VISIBLE_DEVICES = "-1")

library(tidyverse)
library(TTR)
library(caret)
library(zoo)
library(keras3)
library(tensorflow)
library(abind)
library(forecast)
library(readxl)

# ============================================================
# BÖLÜM 1: VERİ OKUMA
# ============================================================

raw <- read_excel("ALZ_AZS_AMZ_Haftalik.xlsx")
raw <- raw[!is.na(raw$Date), ]

colnames(raw) <- c("Date", "Price_ALZ", "LogReturn_ALZ",
                    "Price_AZS", "LogReturn_AZS",
                    "Price_AMZ", "LogReturn_AMZ")

raw$Price_ALZ     <- as.numeric(raw$Price_ALZ)
raw$LogReturn_ALZ <- as.numeric(raw$LogReturn_ALZ)
raw$Price_AZS     <- as.numeric(raw$Price_AZS)
raw$LogReturn_AZS <- as.numeric(raw$LogReturn_AZS)
raw$Price_AMZ     <- as.numeric(raw$Price_AMZ)
raw$LogReturn_AMZ <- as.numeric(raw$LogReturn_AMZ)

cat("Ham veri yuklendi:", nrow(raw), "hafta\n")

# ============================================================
# BÖLÜM 2: FON LİSTESİ VE ORTAK PARAMETRELER
# ============================================================

fon_listesi <- list(
  list(name="ALZ", price_col="Price_ALZ", return_col="LogReturn_ALZ"),
  list(name="AZS", price_col="Price_AZS", return_col="LogReturn_AZS"),
  list(name="AMZ", price_col="Price_AMZ", return_col="LogReturn_AMZ")
)

seeds <- c(23, 27, 98)

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

feature_sets_fon <- list(
  "full"      = c("Close", "LogReturn", "RSI", "MACD", "EMA12", "EMA26", "Momentum", "Volatility"),
  "technical" = c("RSI", "MACD", "EMA12", "EMA26", "Momentum", "Volatility"),
  "closing"   = c("Close")
)

lstm_grid <- expand.grid(
  optimizer  = c("adam", "sgd"),
  activation = c("relu", "tanh"),
  dropout    = c(0.0, 0.2, 0.4),
  stringsAsFactors = FALSE
)

filter_configs <- list(c(32, 64, 128), c(64, 128, 256))
cnn_grid <- expand.grid(
  dropout    = c(0.2, 0.3, 0.4),
  filter_idx = c(1, 2),
  kernel_size = c(3),
  dense_units = c(64, 128, 256),
  stringsAsFactors = FALSE
)
cnn_grid_k5 <- expand.grid(
  dropout    = c(0.2, 0.4),
  filter_idx = c(1),
  kernel_size = c(5),
  dense_units = c(128),
  stringsAsFactors = FALSE
)
cnn_grid <- rbind(cnn_grid, cnn_grid_k5)

# ============================================================
# BÖLÜM 3: YARDIMCI FONKSİYONLAR
# ============================================================

hesapla_gostergeler <- function(df, price_col) {
  prices <- df[[price_col]]
  df$RSI        <- RSI(prices, n = 7)
  macd_v        <- MACD(prices, nFast = 12, nSlow = 26, nSig = 9)
  df$MACD       <- macd_v[, "macd"]
  df$EMA12      <- EMA(prices, n = 12)
  df$EMA26      <- EMA(prices, n = 26)
  df$Momentum   <- c(NA, diff(prices) / head(prices, -1))
  df$Volatility <- rollapply(prices, width = 7, FUN = sd, fill = NA, align = "right")
  return(df)
}

create_label <- function(close_prices, output_len) {
  n     <- length(close_prices)
  label <- rep(NA, n)
  for (i in 1:(n - output_len)) {
    label[i] <- ifelse(close_prices[i + output_len] > close_prices[i], 1, 0)
  }
  return(label)
}

create_seq <- function(data, input_len, label_col, feat_cols) {
  X <- list(); y <- c()
  for (i in input_len:nrow(data)) {
    pencere <- as.matrix(data[(i - input_len + 1):i, feat_cols, drop = FALSE])
    X[[length(X) + 1]] <- pencere
    y <- c(y, data[[label_col]][i])
  }
  X_array <- array(unlist(X), dim = c(length(X), input_len, length(feat_cols)))
  return(list(X = X_array, y = y))
}

hesapla_metrikler <- function(seed_accs, all_preds, y_test) {
  gecerli  <- !is.na(seed_accs)
  if (sum(gecerli) == 0) {
    return(list(mean_acc = NA, sd_acc = NA, min_acc = NA, max_acc = NA,
                p_val = NA, f1 = NA, sens = NA, spec = NA))
  }
  mean_acc <- mean(seed_accs, na.rm = TRUE)
  sd_acc   <- ifelse(sum(gecerli) > 1, sd(seed_accs, na.rm = TRUE), 0)
  min_acc  <- min(seed_accs, na.rm = TRUE)
  max_acc  <- max(seed_accs, na.rm = TRUE)
  best_idx  <- which.max(seed_accs)
  best_pred <- all_preds[[best_idx]]
  p_val <- NA; f1 <- NA; sens <- NA; spec <- NA
  if (!is.null(best_pred) && length(best_pred) == length(y_test)) {
    p_val <- binom.test(sum(best_pred == y_test), length(y_test),
                        p = 0.5, alternative = "greater")$p.value
    tryCatch({
      cm   <- confusionMatrix(factor(best_pred, levels = c(0, 1)),
                              factor(y_test,    levels = c(0, 1)), positive = "1")
      f1   <- cm$byClass["F1"]
      sens <- cm$byClass["Sensitivity"]
      spec <- cm$byClass["Specificity"]
    }, error = function(e) NULL)
  }
  return(list(mean_acc = mean_acc, sd_acc = sd_acc, min_acc = min_acc, max_acc = max_acc,
              p_val = p_val, f1 = f1, sens = sens, spec = spec))
}

build_lstm <- function(input_len, n_features, activation, dropout_rate, optimizer_name) {
  model <- keras_model_sequential() %>%
    layer_lstm(units = 64, activation = activation,
               input_shape = c(input_len, n_features)) %>%
    layer_dropout(rate = dropout_rate) %>%
    layer_dense(units = 1, activation = "sigmoid")
  model %>% compile(optimizer = optimizer_name,
                    loss = "binary_crossentropy",
                    metrics = list("accuracy"))
  return(model)
}

build_cnn <- function(input_len, n_features, filters, kernel_size, dense_units, dropout_rate) {
  model <- keras_model_sequential() %>%
    layer_conv_1d(filters = filters[1], kernel_size = kernel_size, activation = "relu",
                  input_shape = c(input_len, n_features), padding = "same") %>%
    layer_conv_1d(filters = filters[2], kernel_size = kernel_size, activation = "relu",
                  padding = "same") %>%
    layer_conv_1d(filters = filters[3], kernel_size = kernel_size, activation = "relu",
                  padding = "same") %>%
    layer_flatten() %>%
    layer_dense(units = dense_units, activation = "relu") %>%
    layer_dropout(rate = dropout_rate) %>%
    layer_dense(units = 1, activation = "sigmoid")
  model %>% compile(optimizer = "adam",
                    loss = "binary_crossentropy",
                    metrics = list("accuracy"))
  return(model)
}

yeni_early_stop <- function() {
  callback_early_stopping(
    monitor              = "val_loss",
    patience             = 5,
    restore_best_weights = TRUE
  )
}

# ============================================================
# BÖLÜM 4: SONUÇ TABLOLARI
# ============================================================

tum_arima <- data.frame()
tum_lstm  <- data.frame()
tum_cnn   <- data.frame()
tum_naive <- data.frame()

# ============================================================
# BÖLÜM 5: FON DÖNGÜSÜ
# ============================================================

for (fon in fon_listesi) {

  fon_name  <- fon$name
  price_col <- fon$price_col

  cat(sprintf("\n\n=== FON: %s ===\n", fon_name))

  # --- 5.1 Fon bazlı NA temizliği ---
  # Önce bu fonun fiyat sütununda NA olan satırlar çıkarılır.
  # Her fon farklı tarihte başlayabilir (ALZ: week 26, AZS: week 14, AMZ: week 13)
  df <- data.frame(Date      = raw$Date,
                   Close     = raw[[price_col]],
                   LogReturn = raw[[fon$return_col]])
  df <- df[!is.na(df$Close), ]  # fiyat NA olan satırları çıkar

  # --- 5.2 Teknik göstergeler ---
  df <- hesapla_gostergeler(df, "Close")

  # Isınma dönemini complete.cases ile çıkar (EMA26 → 26 satır)
  df_clean <- df[complete.cases(df), ]
  cat(sprintf("  Temiz veri: %d hafta\n", nrow(df_clean)))

  # --- 5.3 Kronolojik bölme (leakage yok) ---
  n         <- nrow(df_clean)
  train_end <- floor(n * 0.70)
  val_end   <- floor(n * 0.85)

  train_raw <- df_clean[1:train_end, ]
  val_raw   <- df_clean[(train_end + 1):val_end, ]
  test_raw  <- df_clean[(val_end + 1):n, ]

  cat(sprintf("  Bolunme: Train=%d  Val=%d  Test=%d\n",
              nrow(train_raw), nrow(val_raw), nrow(test_raw)))

  # --- 5.4 Ölçekleme: sadece train üzerinde fit (AKADEMİK İYİLEŞTİRME #1) ---
  olcek_cols <- c("Close", "LogReturn")
  preproc    <- preProcess(train_raw[, olcek_cols, drop = FALSE], method = "range")
  train_data <- predict(preproc, train_raw)
  val_data   <- predict(preproc, val_raw)
  test_data  <- predict(preproc, test_raw)

  # --- 5.5 Label oluşturma: her split için ayrı (AKADEMİK İYİLEŞTİRME #2) ---
  for (out_len in c(1, 3, 5)) {
    col <- paste0("label_", out_len)
    train_data[[col]] <- create_label(train_data$Close, out_len)
    val_data[[col]]   <- create_label(val_data$Close, out_len)
    test_data[[col]]  <- create_label(test_data$Close, out_len)
  }

  # --- 5.6 Sınıf dengesi ve class_weight (AKADEMİK İYİLEŞTİRME #3) ---
  cat(sprintf("\n  --- Sinif Dengesi (train) ---\n"))
  sinif_agirlik <- list()
  for (out_len in c(1, 3, 5)) {
    col     <- paste0("label_", out_len)
    gecerli <- train_data[[col]][!is.na(train_data[[col]])]
    tablo   <- table(gecerli)
    n0 <- as.numeric(tablo["0"]); if (is.na(n0)) n0 <- 0
    n1 <- as.numeric(tablo["1"]); if (is.na(n1)) n1 <- 0
    toplm <- n0 + n1
    cat(sprintf("  label_%d -> Dusus: %d (%.1f%%) | Yukselis: %d (%.1f%%)\n",
                out_len, n0, 100 * n0 / toplm, n1, 100 * n1 / toplm))
    w0 <- toplm / (2 * max(n0, 1))
    w1 <- toplm / (2 * max(n1, 1))
    sinif_agirlik[[col]] <- list("0" = w0, "1" = w1)
  }

  # ===========================================================
  # ARIMA
  # ===========================================================
  cat("\n  -- ARIMA --\n")
  for (k in kombinasyonlar) {
    input_len <- k$input; label_col <- k$label
    best_acc  <- 0; best_d <- 0

    for (d in 0:5) {
      model <- withCallingHandlers(
        tryCatch({
          arima(train_data$Close, order = c(input_len, d, input_len), method = "CSS")
        }, error = function(e) NULL),
        warning = function(w) invokeRestart("muffleWarning"))
      if (!is.null(model)) {
        preds <- tryCatch(forecast(model, h = nrow(val_data))$mean, error = function(e) NULL)
        if (is.null(preds)) next
        pl  <- ifelse(diff(c(tail(train_data$Close, 1), preds)) > 0, 1, 0)
        ge  <- val_data[[label_col]]; ge <- ge[!is.na(ge)]
        pl  <- pl[1:length(ge)]
        acc <- mean(pl == ge)
        if (acc > best_acc) { best_acc <- acc; best_d <- d }
      }
    }

    mf <- withCallingHandlers(
      tryCatch({
        arima(c(train_data$Close, val_data$Close),
              order = c(input_len, best_d, input_len), method = "CSS")
      }, error = function(e) NULL),
      warning = function(w) invokeRestart("muffleWarning"))

    if (!is.null(mf)) {
      pt <- tryCatch(forecast(mf, h = nrow(test_data))$mean, error = function(e) NULL)
      if (!is.null(pt)) {
        plt <- ifelse(diff(c(tail(val_data$Close, 1), pt)) > 0, 1, 0)
        gt  <- test_data[[label_col]]; gt <- gt[!is.na(gt)]
        plt <- plt[1:length(gt)]
        ta  <- mean(plt == gt)
        tum_arima <- rbind(tum_arima, data.frame(
          Fon = fon_name, Input = input_len, Output = k$output,
          Best_d = best_d, Test_Acc = round(ta, 4)))
        cat(sprintf("    In=%d Out=%d d=%d -> %.4f\n", input_len, k$output, best_d, ta))
      }
    }
  }

  # ===========================================================
  # LSTM
  # ===========================================================
  cat("\n  -- LSTM --\n")
  for (set_name in names(feature_sets_fon)) {
    feat_cols <- feature_sets_fon[[set_name]]; n_feat <- length(feat_cols)
    cat(sprintf("\n    [%s | %d ozellik]\n", set_name, n_feat))

    for (k in kombinasyonlar) {
      input_len <- k$input; label_col <- k$label
      cw <- sinif_agirlik[[label_col]]

      train_s <- create_seq(train_data, input_len, label_col, feat_cols)
      val_s   <- create_seq(val_data,   input_len, label_col, feat_cols)
      tok  <- !is.na(train_s$y); vok <- !is.na(val_s$y)

      if (sum(tok) < 10 || sum(vok) < 5) {
        cat(sprintf("    In=%d Out=%d -> ATLA (yetersiz veri)\n", input_len, k$output))
        next
      }

      X_tr <- train_s$X[tok, , , drop = FALSE]; y_tr <- train_s$y[tok]
      X_vl <- val_s$X[vok, , , drop = FALSE];   y_vl <- val_s$y[vok]

      # Grid search + early stopping (AKADEMİK İYİLEŞTİRME #4)
      best_val <- -1
      best_p   <- list(optimizer = "adam", activation = "relu", dropout = 0.0)
      for (g in 1:nrow(lstm_grid)) {
        set.seed(23); tensorflow::tf$random$set_seed(23L)
        m <- tryCatch(
          build_lstm(input_len, n_feat,
                     lstm_grid$activation[g], lstm_grid$dropout[g], lstm_grid$optimizer[g]),
          error = function(e) NULL)
        if (is.null(m)) next
        tryCatch({
          m %>% fit(X_tr, y_tr,
                    epochs          = 50,
                    batch_size      = 16,
                    validation_data = list(X_vl, y_vl),
                    class_weight    = cw,
                    callbacks       = list(yeni_early_stop()),
                    verbose         = 0)
          va <- mean(as.numeric(predict(m, X_vl, verbose = 0) > 0.5) == y_vl)
          if (va > best_val) {
            best_val <- va
            best_p   <- list(optimizer  = lstm_grid$optimizer[g],
                             activation = lstm_grid$activation[g],
                             dropout    = lstm_grid$dropout[g])
          }
        }, error = function(e) NULL)
        keras3::clear_session(); gc()  # bellek temizle (keras3)
      }

      # Final eğitim: train+val birleşik, 3 seed
      comb <- rbind(train_data, val_data)
      cs   <- create_seq(comb,      input_len, label_col, feat_cols)
      ts   <- create_seq(test_data, input_len, label_col, feat_cols)
      cok  <- !is.na(cs$y); teok <- !is.na(ts$y)
      if (sum(teok) < 5) next
      X_c  <- cs$X[cok, , , drop = FALSE];   y_c  <- cs$y[cok]
      X_te <- ts$X[teok, , , drop = FALSE];   y_te <- ts$y[teok]

      sa <- c(); ap <- list()
      for (s in seeds) {
        set.seed(s); tensorflow::tf$random$set_seed(as.integer(s))
        fm <- tryCatch(
          build_lstm(input_len, n_feat, best_p$activation, best_p$dropout, best_p$optimizer),
          error = function(e) NULL)
        if (is.null(fm)) { sa <- c(sa, NA); next }
        tryCatch({
          fm %>% fit(X_c, y_c,
                     epochs       = 50,
                     batch_size   = 16,
                     class_weight = cw,
                     verbose      = 0)
          pr <- as.numeric(predict(fm, X_te, verbose = 0) > 0.5)
          sa <- c(sa, mean(pr == y_te))
          ap[[as.character(s)]] <- pr
        }, error = function(e) { sa <<- c(sa, NA) })
        keras3::clear_session(); gc()  # bellek temizle (keras3)
      }

      met <- hesapla_metrikler(sa, ap, y_te)
      tum_lstm <- rbind(tum_lstm, data.frame(
        Fon         = fon_name,
        Feature_Set = set_name,
        Input       = input_len,
        Output      = k$output,
        Optimizer   = best_p$optimizer,
        Activation  = best_p$activation,
        Dropout     = best_p$dropout,
        Seed_23     = round(sa[1], 4),
        Seed_27     = round(sa[2], 4),
        Seed_98     = round(sa[3], 4),
        Mean_Acc    = round(met$mean_acc, 4),
        SD          = round(met$sd_acc, 4),
        Min_Acc     = round(met$min_acc, 4),
        Max_Acc     = round(met$max_acc, 4),
        P_Value     = round(met$p_val, 4),
        F1          = round(as.numeric(met$f1), 4),
        Sens        = round(as.numeric(met$sens), 4),
        Spec        = round(as.numeric(met$spec), 4),
        stringsAsFactors = FALSE))
      cat(sprintf("    In=%d Out=%d -> %.4f (SD=%.4f)\n",
                  input_len, k$output, met$mean_acc, met$sd_acc))
    }
  }

  # ===========================================================
  # CNN
  # ===========================================================
  cat("\n  -- CNN --\n")
  for (set_name in names(feature_sets_fon)) {
    feat_cols <- feature_sets_fon[[set_name]]; n_feat <- length(feat_cols)
    cat(sprintf("\n    [%s | %d ozellik]\n", set_name, n_feat))

    for (k in kombinasyonlar) {
      input_len <- k$input; label_col <- k$label
      cw <- sinif_agirlik[[label_col]]

      train_s <- create_seq(train_data, input_len, label_col, feat_cols)
      val_s   <- create_seq(val_data,   input_len, label_col, feat_cols)
      tok  <- !is.na(train_s$y); vok <- !is.na(val_s$y)

      if (sum(tok) < 10 || sum(vok) < 5) {
        cat(sprintf("    In=%d Out=%d -> ATLA (yetersiz veri)\n", input_len, k$output))
        next
      }

      X_tr <- train_s$X[tok, , , drop = FALSE]; y_tr <- train_s$y[tok]
      X_vl <- val_s$X[vok, , , drop = FALSE];   y_vl <- val_s$y[vok]

      # Grid search + early stopping (AKADEMİK İYİLEŞTİRME #4)
      best_val <- -1
      best_p   <- list(dropout = 0.2, filters = c(32, 64, 128), kernel_size = 3, dense_units = 64)
      for (g in 1:nrow(cnn_grid)) {
        filt <- filter_configs[[cnn_grid$filter_idx[g]]]
        set.seed(23); tensorflow::tf$random$set_seed(23L)
        m <- tryCatch(
          build_cnn(input_len, n_feat, filt,
                    cnn_grid$kernel_size[g], cnn_grid$dense_units[g], cnn_grid$dropout[g]),
          error = function(e) NULL)
        if (is.null(m)) next
        tryCatch({
          m %>% fit(X_tr, y_tr,
                    epochs          = 50,
                    batch_size      = 16,
                    validation_data = list(X_vl, y_vl),
                    class_weight    = cw,
                    callbacks       = list(yeni_early_stop()),
                    verbose         = 0)
          va <- mean(as.numeric(predict(m, X_vl, verbose = 0) > 0.5) == y_vl)
          if (va > best_val) {
            best_val <- va
            best_p   <- list(dropout     = cnn_grid$dropout[g],
                             filters     = filt,
                             kernel_size = cnn_grid$kernel_size[g],
                             dense_units = cnn_grid$dense_units[g])
          }
        }, error = function(e) NULL)
        keras3::clear_session(); gc()  # bellek temizle (keras3)
      }

      # Final eğitim: train+val birleşik, 3 seed
      comb <- rbind(train_data, val_data)
      cs   <- create_seq(comb,      input_len, label_col, feat_cols)
      ts   <- create_seq(test_data, input_len, label_col, feat_cols)
      cok  <- !is.na(cs$y); teok <- !is.na(ts$y)
      if (sum(teok) < 5) next
      X_c  <- cs$X[cok, , , drop = FALSE];   y_c  <- cs$y[cok]
      X_te <- ts$X[teok, , , drop = FALSE];   y_te <- ts$y[teok]

      sa <- c(); ap <- list()
      for (s in seeds) {
        set.seed(s); tensorflow::tf$random$set_seed(as.integer(s))
        fm <- tryCatch(
          build_cnn(input_len, n_feat,
                    best_p$filters, best_p$kernel_size, best_p$dense_units, best_p$dropout),
          error = function(e) NULL)
        if (is.null(fm)) { sa <- c(sa, NA); next }
        tryCatch({
          fm %>% fit(X_c, y_c,
                     epochs       = 50,
                     batch_size   = 16,
                     class_weight = cw,
                     verbose      = 0)
          pr <- as.numeric(predict(fm, X_te, verbose = 0) > 0.5)
          sa <- c(sa, mean(pr == y_te))
          ap[[as.character(s)]] <- pr
        }, error = function(e) { sa <<- c(sa, NA) })
        keras3::clear_session(); gc()  # bellek temizle (keras3)
      }

      met <- hesapla_metrikler(sa, ap, y_te)
      tum_cnn <- rbind(tum_cnn, data.frame(
        Fon         = fon_name,
        Feature_Set = set_name,
        Input       = input_len,
        Output      = k$output,
        Dropout     = best_p$dropout,
        Filters     = paste(best_p$filters, collapse = "-"),
        Kernel      = best_p$kernel_size,
        Dense       = best_p$dense_units,
        Seed_23     = round(sa[1], 4),
        Seed_27     = round(sa[2], 4),
        Seed_98     = round(sa[3], 4),
        Mean_Acc    = round(met$mean_acc, 4),
        SD          = round(met$sd_acc, 4),
        Min_Acc     = round(met$min_acc, 4),
        Max_Acc     = round(met$max_acc, 4),
        P_Value     = round(met$p_val, 4),
        F1          = round(as.numeric(met$f1), 4),
        Sens        = round(as.numeric(met$sens), 4),
        Spec        = round(as.numeric(met$spec), 4),
        stringsAsFactors = FALSE))
      cat(sprintf("    In=%d Out=%d -> %.4f (SD=%.4f)\n",
                  input_len, k$output, met$mean_acc, met$sd_acc))
    }
  }

  # ===========================================================
  # NAIVE BASELINE
  # ===========================================================
  cat("\n  -- Naive --\n")
  for (k in kombinasyonlar) {
    gercek <- test_data[[k$label]]; gercek <- gercek[!is.na(gercek)]
    if (length(gercek) < 2) next
    son_val    <- tail(val_data[[k$label]][!is.na(val_data[[k$label]])], 1)
    naive_pred <- c(son_val, head(gercek, -1))
    naive_acc  <- mean(naive_pred == gercek)
    tum_naive  <- rbind(tum_naive, data.frame(
      Fon = fon_name, Output = k$output, Naive_Acc = round(naive_acc, 4)))
    cat(sprintf("    Out=%d -> %.4f\n", k$output, naive_acc))
  }
}

# ============================================================
# BÖLÜM 6: KAYDET
# ============================================================

write.csv(tum_arima, "EMEKLILIK_ARIMA_sonuclar.csv",  row.names = FALSE)
write.csv(tum_lstm,  "EMEKLILIK_LSTM_sonuclar.csv",   row.names = FALSE)
write.csv(tum_cnn,   "EMEKLILIK_CNN_sonuclar.csv",    row.names = FALSE)
write.csv(tum_naive, "EMEKLILIK_NAIVE_baseline.csv",  row.names = FALSE)

# ============================================================
# BÖLÜM 7: ÖZET
# ============================================================

cat("\n=== EMEKLILIK TAMAMLANDI ===\n")
cat("\n--- Akademik Iyilestirmeler (THYAO ile tutarli) ---\n")
cat("1. preProcess sadece train uzerinde fit (data leakage onlendi)\n")
cat("2. Label her split icin ayri olusturuldu\n")
cat("3. class_weight ile sinif dengesizligi duzeltildi\n")
cat("4. Early stopping (patience=5) grid search asamasinda\n")
cat("5. Fon bazli NA temizligi (her fon kendi baslangic tarihinden itibaren)\n")

cat("\n--- Sonuclar ---\n")
for (fn in c("ALZ", "AZS", "AMZ")) {
  cat(sprintf("\n--- %s ---\n", fn))
  ar <- tum_arima[tum_arima$Fon == fn, ]
  if (nrow(ar) > 0) cat(sprintf("  ARIMA ort: %.4f\n", mean(ar$Test_Acc)))
  nv <- tum_naive[tum_naive$Fon == fn, ]
  if (nrow(nv) > 0) cat(sprintf("  Naive ort: %.4f\n", mean(nv$Naive_Acc)))
  for (sn in c("full", "technical", "closing")) {
    ls <- tum_lstm[tum_lstm$Fon == fn & tum_lstm$Feature_Set == sn, ]
    cs <- tum_cnn[tum_cnn$Fon  == fn & tum_cnn$Feature_Set  == sn, ]
    if (nrow(ls) > 0) cat(sprintf("  LSTM %-10s: %.4f\n", sn, mean(ls$Mean_Acc, na.rm = TRUE)))
    if (nrow(cs) > 0) cat(sprintf("  CNN  %-10s: %.4f\n", sn, mean(cs$Mean_Acc, na.rm = TRUE)))
  }
}

cat("\nDosyalar: EMEKLILIK_ARIMA/LSTM/CNN_sonuclar.csv, EMEKLILIK_NAIVE_baseline.csv\n")