# 📈 BIST & BES Direction Forecasting (Deep Learning)

<p align="center">
  <img src="https://img.shields.io/badge/R-276DC3?style=for-the-badge&logo=r&logoColor=white" />
  <img src="https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=Keras&logoColor=white" />
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Machine%20Learning-Actuarial-brightgreen?style=for-the-badge" />
</p>

> 🚨 **DİKKAT:** Bu akademik çalışma, "Majority Class" tuzağını ve "Anti-Predictive" model davranışlarını keşfettiğimiz öncü araştırmamızdır. Daha gelişmiş Multi-Defense mimarisi içeren **TÜBİTAK 2209-A (MC-AWARE)** projemizin temelini oluşturur. [TÜBİTAK Projesi (Canlı Demo) İçin Tıklayın](https://github.com/kuurtali/Tubitak-2209A-MCAware)

Bu repository, derin öğrenme modellerinin Borsa İstanbul (BIST) ve Bireysel Emeklilik Fonları (BES) üzerindeki finansal yön tahmin yeteneklerini inceleyen aşağıdaki akademik çalışmanın **%100 yeniden üretilebilir (reproducible) kod tabanıdır**:

> 📄 **Kurt, M. A., Demir, Ş., Karadağ Erdemir, Ö. (2026).** *Türkiye piyasasında yön tahmini: derin öğrenme ve majority class illüzyonu.* Hacettepe Üniversitesi, Aktüerya Bilimleri Bölümü.

## 📌 Proje Özeti (Executive Summary)

Finansal zaman serilerinde yön tahmini (Yükseliş/Düşüş) yaparken, Derin Öğrenme modelleri (LSTM/CNN) genellikle veri setindeki dominant sınıfa (örneğin pazarın sürekli yükselişte olduğu dönemlere) aşırı uyum sağlar. Bu durum literatürde **"Majority Class Illusion" (Çoğunluk Sınıfı İllüzyonu)** olarak bilinir.

Bu projede; ARIMA, LSTM ve 1D-CNN mimarilerinin THYAO hissesi ve Allianz Yaşam emeklilik fonları (ALZ, AZS, AMZ) üzerindeki performansları kıyaslanmıştır. Model, **Van der Burgt (2023)** metodolojisi baz alınarak 4 farklı teknikle (train-only preProcess, per-split labeling, class weighting, early stopping) Türkiye piyasasına özel olarak güçlendirilmiştir.

## 📊 Model Karşılaştırması ve Temel Sonuçlar

BIST (THYAO) ve Emeklilik Fonları (BES) üzerinde yapılan testlerde, Derin Öğrenme modelleri (LSTM/CNN) ile geleneksel ekonometrik modeller (ARIMA) karşılaştırılmıştır:

| Model Türü | THYAO Başarısı (Accuracy) | BES (AMZ) Başarısı | Öne Çıkan Özellik / Zayıflık |
|------------|---------------------------|--------------------|------------------------------|
| **ARIMA** (Baseline) | %52.3 | %51.1 | Çoğunluk sınıfına (Majority Class) daha az eğilimli, stabil ancak düşük doğruluk. |
| **1D-CNN** | %51.8 | %53.4 | Gürültülü finansal veride yerel örüntüleri (local patterns) yakalamada başarılı. |
| **LSTM** | **%54.1** | **%55.8** | Uzun vadeli zaman serisi bağımlılıklarında (özellikle BES fonlarında) **şampiyon model**. |

*Not: "Majority Class" düzeltmeleri yapılmadığı takdirde DL modellerinin (LSTM/CNN) %60+ gibi sahte doğruluk oranları verdiği, ancak bunun tüm günleri "Yükseliş" (1) olarak tahmin etme illüzyonundan kaynaklandığı makalede ispatlanmıştır.*

## Klasör yapısı

```
GITHUB_HAZIR/
├── R/                                # Bilimsel pipeline kodları
│   ├── THYAO_2018-2026.R             # Güncel dönem THYAO modeli (ana)
│   ├── THYAO_2018-2022.R             # Eski dönem THYAO (kavramsal sürüklenme analizi için)
│   ├── EMEKLILIK_2021-2026.R         # ALZ/AZS/AMZ emeklilik fonu modelleri
│   └── APPENDIX_I_class_distribution.R   # Sınıf dağılımı raporu üretici
├── data/
│   └── README.md                     # Veri dosyası beklentileri
├── output/                           # Script çıktıları (.gitignore'lu)
├── install_packages.R                # R paket kurulum yardımcısı
├── README.md                         # bu dosya
├── LICENSE                           # MIT
├── CITATION.cff                      # Atıf bilgileri
└── .gitignore
```

## Hızlı kurulum

### 1. R + RStudio kurulumu
R 4.3 veya üzeri gerekir. RStudio önerilir.

### 2. R paketlerinin kurulumu
```r
source("install_packages.R")
```

### 3. TensorFlow + Keras (LSTM ve 1D-CNN için)
TensorFlow Python tarafında çalışır; R'den `tensorflow` paketi köprü kurar.

```bash
# CMD veya Terminal'de
pip install tensorflow==2.16.1
```

R tarafında:
```r
library(tensorflow)
library(keras3)
# İlk çalıştırmada Keras kendisi gerekirse Python ortamı kurar
```

NVIDIA GPU sorunu olanlar (RTX 5050 / CUDA uyumsuzluğu vb.) için scriptlerin başında bulunan satır:
```r
Sys.setenv(CUDA_VISIBLE_DEVICES = "-1")
```
GPU'yu bypass eder; CPU modunda koşar (yavaş ama stabil).

## Veri

| Dosya | Kaynak | Bu repoda mı? |
|---|---|---|
| THYAO günlük fiyat | `quantmod::getSymbols("THYAO.IS")` (Yahoo Finance) | İnternet üzerinden çekilir |
| USD/TRY, WTI petrol | `quantmod::getSymbols("USDTRY=X", "CL=F")` | İnternet üzerinden çekilir |
| TCMB politika faizi | `getSymbols("INTDSRTRM193N", src="FRED")` | İnternet üzerinden çekilir |
| Fear & Greed indeks | gman4774 GitHub mirror | İnternet üzerinden çekilir |
| ALZ/AZS/AMZ haftalık | TEFAS sistemi (manuel indirilir) | **Hayır** — `data/` klasörüne sen indir |

**Önemli:** TEFAS verisi telif sebebiyle bu repoya dahil değildir. `data/ALZ_AZS_AMZ_Haftalik.xlsx` dosyasını TEFAS sisteminden manuel olarak indirip `data/` klasörüne yerleştirmeniz gerekir. Beklenen kolon yapısı:

```
Date | Price_ALZ | LogReturn_ALZ | Price_AZS | LogReturn_AZS | Price_AMZ | LogReturn_AMZ
```

(Eski kolonlu sürüm verildiğinde script ilk koddaki `colnames(df_e) <- ...` adımıyla yeniden adlandırır.)

## Koşum sırası

Kodları repo kökünden (yani `GITHUB_HAZIR/` içinden) çalıştırın. Çıktılar `output/` klasörüne yazılır.

```r
# 1. Sınıf dağılımı raporu (Appendix I tablosu)
source("R/APPENDIX_I_class_distribution.R")

# 2. THYAO 2018-2022 dönemi (kavramsal sürüklenme karşılaştırması)
source("R/THYAO_2018-2022.R")

# 3. THYAO 2018-2026 dönemi (ana sonuçlar)
source("R/THYAO_2018-2026.R")

# 4. Emeklilik fonları (ana sonuçlar — AMZ LSTM şampiyonu burada)
source("R/EMEKLILIK_2021-2026.R")
```

Her script şu CSV çıktılarını üretir (`output/` altına):

| Script | Çıktı |
|---|---|
| THYAO_2018-2026.R | `ARIMA_sonuclar.csv`, `LSTM_sonuclar_FINAL.csv`, `CNN_sonuclar_FINAL.csv`, `NAIVE_baseline.csv` |
| THYAO_2018-2022.R | Aynılarının `_eski` ekli sürümü |
| EMEKLILIK_2021-2026.R | `EMEKLILIK_ARIMA_sonuclar.csv`, `EMEKLILIK_LSTM_sonuclar.csv`, `EMEKLILIK_CNN_sonuclar.csv`, `EMEKLILIK_NAIVE_baseline.csv` |
| APPENDIX_I_class_distribution.R | `APPENDIX_I_SONUCLARI.txt` |

## Reproducibility

| Bileşen | Sürüm (test edilmiş) |
|---|---|
| R | 4.3.2 |
| Python | 3.11 |
| TensorFlow | 2.16.1 |
| Keras | 3.0.5 |
| Seed'ler | 23, 27, 98 |
| THYAO test seti | 313 gözlem |
| BES test seti | ~32 hafta (pooled N = 96) |

Üç farklı tohum (Seed = 23, 27, 98) ile her konfigürasyon koşulur, sonuçlar pooled (havuzlanmış) karmaşıklık matrisi ile birleştirilir. Detaylı metodoloji makalede §2.6'da.

## Toplam koşum süresi

CPU modunda (GPU bypass):
- THYAO 2018-2026: ~3-4 saat (108 LSTM + 108 CNN + 9 ARIMA = 225 trained model)
- THYAO 2018-2022: ~3-4 saat (aynı sayım, daha kısa veri)
- Emeklilik: ~5-6 saat (243 LSTM + 243 CNN + 27 ARIMA = 513 trained model)

GPU ile süreler 4-5x kısalır.

## Atıf

Bu kodu kullanırsanız lütfen makaleye atıfta bulunun:

```bibtex
@misc{kurt2026directionforecasting,
  author       = {Kurt, Mehmet Ali and Demir, Şevval and Karadağ Erdemir, Övgücan},
  title        = {Türkiye piyasasında yön tahmini: derin öğrenme ve majority class illüzyonu},
  year         = {2026},
  institution  = {Hacettepe Üniversitesi, Aktüerya Bilimleri Bölümü}
}
```

## 🔗 İlgili Projeler / Related Projects

| Proje / Project | Açıklama / Description |
|-----------------|------------------------|
| [Tubitak-2209A-MCAware](https://github.com/kuurtali/Tubitak-2209A-MCAware) | TÜBİTAK 2209-A: BIST'te derin öğrenme ile anti-prediktif davranış keşfi |
| [ADAS Pricing Paradox](https://github.com/kuurtali/ADAS-Pricing-Paradox) | Aktüeryal ADAS fiyatlama: 100K poliçe, Poisson + Gamma GLM |
| [VOL2 — ADAS Advanced](https://github.com/kuurtali/VOL2-ADAS-Pricing-Paradox) | ADAS fiyatlama VOL2: 200K poliçe, Gini Index, Lift Charts |
| [Actuarial Shiny Dashboard](https://github.com/kuurtali/actuarial-analysis-w-shiny-and-glm) | İnteraktif R Shiny risk skorlama: Logistic GLM (AUC 0.828) |

## Lisans

MIT License — bkz. [LICENSE](LICENSE).

## İletişim

- Mehmet Ali Kurt — m.alikuurt0@gmail.com (ORCID: 0009-0008-3371-7952)
- Şevval Demir — dsevval5@gmail.com (ORCID: 0009-0005-3077-3666)
- Övgücan Karadağ Erdemir (danışman) — ovgucan@hacettepe.edu.tr (ORCID: 0000-0002-4725-3588)
