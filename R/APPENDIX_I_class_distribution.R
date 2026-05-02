# ====================================================================
# APPENDIX I: TRAIN / TEST CLASS DISTRIBUTION (UP/DOWN) EXTRACTOR
# ====================================================================

library(quantmod)
library(readxl)

# Çıktı klasörünü hazırla
if (!dir.exists("output")) dir.create("output", showWarnings = FALSE, recursive = TRUE)


# 1. THYAO Verisini Çek
cat("THYAO (Yahoo Finance) verisi indiriliyor...\n")
options(download.file.method="libcurl")
thyao_close <- NULL
tryCatch({
  THYAO.IS <- suppressWarnings(getSymbols("THYAO.IS", src="yahoo", from="2018-01-01", to="2026-04-01", auto.assign=FALSE))
  df_t <- na.omit(THYAO.IS)
  thyao_close <- as.numeric(df_t[,4])
}, error = function(e) {
  cat("\n!!! UYARI: Yahoo sunucularina erisilemedi (DNS/Internet Engeli). THYAO hesaplamasi atlanacak !!!\n\n")
})

# 2. Emeklilik Fonlarını Oku
cat("Emeklilik fonları excelden okunuyor...\n")
df_e <- read_excel("data/ALZ_AZS_AMZ_Haftalik.xlsx")

# Excel içerisindeki orijinal kolonları makaledeki mantığa göre adlandırıp çekiyoruz:
colnames(df_e) <- c("Date", "Price_ALZ", "LogReturn_ALZ",
                    "Price_AZS", "LogReturn_AZS",
                    "Price_AMZ", "LogReturn_AMZ")

df_e$Price_ALZ <- as.numeric(df_e$Price_ALZ)
df_e$Price_AZS <- as.numeric(df_e$Price_AZS)
df_e$Price_AMZ <- as.numeric(df_e$Price_AMZ)

# 3. Hesaplama Fonksiyonu
calc_stats <- function(name, vec) {
  vec <- vec[!is.na(vec)]
  n <- length(vec)
  t_end <- floor(n * 0.70)
  v_end <- floor(n * 0.85)
  cat(sprintf("\n=================================="))
  cat(sprintf("\n=== %s (Appendix I İstatistikleri) ===\n", name))
  cat(sprintf("Satir Sayilari: Train=%d, Val=%d, Test=%d (Total=%d)\n", t_end, v_end-t_end, n-v_end, n))
  cat("----------------------------------\n")
  
  for(o in c(1,3,5)) {
    y <- ifelse(diff(vec, lag=o) > 0, 1, 0)
    
    up_tr <- sum(y[1:t_end]==1, na.rm=TRUE)
    n_tr <- length(na.omit(y[1:t_end]))
    down_tr <- n_tr - up_tr
    
    up_te <- sum(y[(v_end+1):n]==1, na.rm=TRUE)
    n_te <- length(na.omit(y[(v_end+1):n]))
    down_te <- n_te - up_te
    
    cat(sprintf("Out=%d:\n", o))
    cat(sprintf("  -> Train: %d Up, %d Down (%%%.1f Yükseliş)\n", up_tr, down_tr, (up_tr/n_tr)*100))
    cat(sprintf("  -> Test : %d Up, %d Down (%%%.1f Yükseliş)\n", up_te, down_te, (up_te/n_te)*100))
  }
}

# 4. Sonuçları Bastır ve Dosyaya Kaydet
cat("\nSonuclar hesaplaniyor ve metin dosyasina yazdiriliyor...\n")
sink("output/APPENDIX_I_SONUCLARI.txt")

cat("====================================================================\n")
cat("APPENDIX I: TEST/TRAIN SINIF DAĞILIMI (UP/DOWN) SONUÇ RAPORU\n")
cat("====================================================================\n")

if(!is.null(thyao_close)) {
  calc_stats("THYAO (Hisse Senedi)", thyao_close)
}
calc_stats("ALZ (Düşük Risk Fon)", df_e$Price_ALZ)
calc_stats("AZS (Orta Risk Fon)", df_e$Price_AZS)
calc_stats("AMZ (Yüksek Risk Fon)", df_e$Price_AMZ)

sink()
cat("\nTAMAMLANDI! Yenilenmiş analizler ve doğru sayılar 'APPENDIX_I_SONUCLARI.txt' dosyasına kaydedildi.\n")
