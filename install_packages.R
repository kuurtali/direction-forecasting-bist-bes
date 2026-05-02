# =================================================================
# install_packages.R
# R bağımlılıklarını kuran yardımcı script.
# Repo kökünden bir kez çalıştırın: source("install_packages.R")
# =================================================================

required_packages <- c(
  "quantmod",     # Yahoo Finance + FRED veri çekimi
  "tidyverse",    # data wrangling
  "TTR",          # Technical Trading Rules: RSI, MACD, EMA, ADX, vs.
  "caret",        # preProcess + class_weight altyapısı
  "zoo",          # zaman serisi köprü
  "abind",        # tensör birleştirme
  "forecast",     # ARIMA + Box-Jenkins
  "readxl",       # Excel okuma (TEFAS verisi)
  "reshape2"      # melt / cast — bazı eski R bağımlılıklarında lazım
)

# Eksik paketleri tespit et ve kur
to_install <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if (length(to_install) > 0) {
  cat("Şu paketler eksik, kurulacak:", paste(to_install, collapse = ", "), "\n")
  install.packages(to_install)
} else {
  cat("Tüm temel paketler yüklü.\n")
}

# Keras / TensorFlow — özel kurulum
if (!("keras3" %in% installed.packages()[,"Package"])) {
  cat("\nkeras3 paketi kuruluyor...\n")
  install.packages("keras3")
}

if (!("tensorflow" %in% installed.packages()[,"Package"])) {
  cat("tensorflow paketi kuruluyor...\n")
  install.packages("tensorflow")
}

cat("\n=================================================================\n")
cat("R paketleri tamam. Şimdi Python tarafında TensorFlow kurun:\n")
cat("    pip install tensorflow==2.16.1\n")
cat("=================================================================\n")

# reshape2 için source kurulum (Windows'ta bazen gerekir)
# install.packages("reshape2", type = "source")
