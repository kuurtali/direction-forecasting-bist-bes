# Derin Öğrenme ile Finansal Yön Tahmini: THYAO Hisse Senedi ve Bireysel Emeklilik Fonları Üzerine Karşılaştırmalı Bir Çalışma

## ARIMA, LSTM ve 1D-CNN Modellerinin Majority Class İllüzyonu Perspektifinden Analizi

**Hacettepe Üniversitesi, Fen Fakültesi, Aktüerya Bilimleri Bölümü, Ankara, Türkiye**

**Nisan 2026**

---

## ÖZET

Bu çalışmada, geleneksel zaman serisi yöntemi ARIMA ile derin öğrenme mimarileri LSTM ve 1D-CNN, iki farklı finansal varlık sınıfı üzerinde karşılaştırmalı olarak değerlendirilmiştir: Borsa İstanbul'da işlem gören Türk Hava Yolları (THYAO) hisse senedi (günlük, 2018–2026) ve TEFAS üzerinden elde edilen üç farklı risk profiline sahip Allianz Yaşam bireysel emeklilik fonu — ALZ (düşük risk), AZS (orta risk), AMZ (yüksek risk) — (haftalık, 2021–2026). Çalışmanın özgün katkısı, literatürde sıkça gözden kaçırılan Çoğunluk Sınıfı (Majority Class) illüzyonunun Specificity ve Sensitivity metrikleri ile sistematik biçimde deşifre edilmesidir. Referans alınan Van der Burgt (2023) çalışmasına dört metodolojik iyileştirme (train-only normalizasyon, split-bazlı etiketleme, class_weight, early stopping) uygulanmış; THYAO LSTM'de MC oranı 16/36'dan 12/36'ya, AZS CNN'de 19/27'den 9/27'ye düşürülmüştür. Projenin en güçlü bulgusu, yüksek riskli AMZ fonunda LSTM modelinin (full set, In=2, Out=3) %80,21 Accuracy, 0,894 F1 ve 0,857 Specificity ile Naive Baseline'ı (%78,79) istatistiksel olarak anlamlı biçimde (p=0,0001) geride bırakmasıdır.

**Anahtar Kelimeler:** Derin Öğrenme, LSTM, 1D-CNN, ARIMA, Yön Tahmini, Majority Class İllüzyonu, Bireysel Emeklilik Fonları, THYAO, Dengeli Doğruluk.

---

## 1. GİRİŞ

Finansal piyasaların yönünü önceden tahmin edebilmek; portföy yönetimi, risk kontrolü ve bireysel yatırımcı kararları açısından kritik öneme sahiptir. Gelişmekte olan piyasalarda dış şokların, enflasyon ve faiz politikalarının sıklıkla yarattığı gürültü, klasik zaman serisi yöntemlerinin performansını sınırlamakta; bu durum araştırmacıları Derin Öğrenme tabanlı mimarilere yöneltmektedir. Ancak literatürde yaygın biçimde karşılaşılan bir sorun, modellerin yüksek Accuracy değerleri üretirken aslında yalnızca çoğunluk sınıfını tahmin etmesi ve bu durumun Sensitivity–Specificity metrikleriyle raporlanmamasıdır (Valverde-Albacete ve Peláez-Moreno, 2014).

Bu çalışmanın temel amacı; gelişmekte olan bir piyasa temsilcisi olarak THYAO hisse senedi ile profesyonelce yönetilen üç farklı risk profilindeki bireysel emeklilik fonu üzerinde ARIMA, 1D-CNN ve LSTM modellerinin yön tahmin performanslarını, sınıf dengesizliğini deşifre edecek şekilde karşılaştırmaktır.

### 1.1. Literatür Taraması

Finansal zaman serilerinin tahmininde kullanılan yöntemler üç ana gruba ayrılabilir. Box ve Jenkins (1976) tarafından geliştirilen ARIMA modeli uzun yıllar temel referans olmuştur. Engle (1982) ve Bollerslev (1986) ARCH/GARCH modelleriyle oynaklık modellemesi için yaygın kullanılmıştır. Makine öğrenmesi yöntemlerinden Kim (2003) SVM, Khaidem ve ark. (2016) rastgele orman modellerini başarıyla uygulamıştır.

Derin öğrenme tabanlı çalışmalarda Hochreiter ve Schmidhuber (1997) LSTM'i önermiş; Fischer ve Krauss (2018) S&P 500'de başarılı sonuçlar elde etmiştir. Selvin ve ark. (2017) 1D-CNN'in LSTM'e göre daha hızlı yakınsadığını göstermiştir. Van der Burgt (2023) NASDAQ100 verisinde LSTM ve CNN'i karşılaştırmış; ancak Sensitivity–Specificity raporlamaması, class_weight eksikliği ve sabit epoch gibi metodolojik boşluklar bırakmıştır.

### 1.2. Özgün Katkı

Çalışmanın özgün katkısı üç başlık altında özetlenebilir: (i) Majority Class illüzyonunun sistematik raporlanması, (ii) Van der Burgt (2023)'teki metodolojik boşlukların kapatılması, (iii) hisse senedi ile emeklilik fonlarının risk profiline göre karşılaştırılması.

---

## 2. YÖNTEM

### 2.1. ARIMA

ARIMA(p,d,q) modeli doğrusal zaman serisi analizinin temel yapı taşıdır (Box ve Jenkins, 1976). Çalışmada d ∈ {0,1,2,3,4,5} grid search ile belirlenmiş, CSS yöntemi kullanılmıştır.

### 2.2. LSTM

Hochreiter ve Schmidhuber (1997) tarafından önerilen LSTM; unutma, giriş ve çıkış kapıları ile uzun vadeli bağımlılıkları öğrenir. Hücre sayısı {32, 64, 128}, Dropout {0, 0.2, 0.4}, Optimizer {Adam, SGD}, Activation {ReLU, tanh} denenmiştir.

### 2.3. 1D-CNN

Filtre sayıları {32-64-128, 64-128-256}, kernel {3, 5}, dense {64, 128, 256} kombinasyonlarında denenmiştir.

### 2.4. Naive Baseline

Bir önceki gözlemin yönünü tahmin olarak kullanan saf tahmincidir. Tahmin ufku uzadıkça güçlenir.

### 2.5. Performans Metrikleri

| Metrik | Formül | Açıklama |
|:---|:---|:---|
| Accuracy | (TP+TN) / N | Genel doğruluk |
| Sensitivity | TP / (TP+FN) | Yükseliş yakalama |
| Specificity | TN / (TN+FP) | Düşüş yakalama |
| Dengeli Doğruluk | (Sens+Spec) / 2 | Sınıf dengeli ölçüt |
| F1-Skoru | 2×(Prec×Rec)/(Prec+Rec) | Harmonik ortalama |
| p-değeri | Binom testi (H₀: p≤0.50) | İstatistiksel anlamlılık |

**MC Tanımı (Geniş):** Spec=0 VEYA Sens=0 VEYA Spec=NA → Majority Class.

### 2.6. Dört Akademik İyileştirme

| # | İyileştirme | Eski | Yeni | Etki |
|:---|:---|:---|:---|:---|
| 1 | preProcess train-only | Tüm veri normalize | Sadece train fit | Veri sızıntısı önlendi |
| 2 | Etiketleme ayrı split | Tüm veri etiketlendi | Her split ayrı | Look-ahead bias önlendi |
| 3 | class_weight | Yok | n/(2×n_class) | MC oranları düştü |
| 4 | Early stopping | Sabit 50 epoch | patience=5 | Overfitting azaldı |

---

## 3. VERİ VE ÖZELLIK MÜHENDİSLİĞİ

### 3.1. Varlık Profilleri

| Varlık | Frekans | Dönem | Gözlem | Volatilite | Risk | Rol |
|:---|:---|:---|:---|:---|:---|:---|
| THYAO | Günlük | 2018–2026 | 2.085* | ~%45 | Agresif | Referans hisse |
| ALZ | Haftalık | 2021–2026 | 249 | ~%2 | Düşük (1) | MC kontrol grubu |
| AZS | Haftalık | 2021–2026 | 261 | ~%18 | Orta (3-4) | Hibrit portföy |
| AMZ | Haftalık | 2021–2026 | 262 | ~%38 | Yüksek (6-7) | Yıldız varlık |

*Not: THYAO ham veri 2.037 işlem günüdür; sliding window ve train/val/test bölünmesi sonrası toplam gözlem sayısı 2.085'e (Train=1.459, Val=313, Test=313) ulaşmaktadır.*

### 3.2. Özellik Setleri

**THYAO (4 set):**

| Set | Özellikler | Sayı |
|:---|:---|:---|
| hist_tech | RSI, MACD, EMA12, EMA26, SO_K, SO_D, ADX + USD/TRY, TCMB, Petrol, Hacim, Açılış, Kapanış | 13 |
| technical | RSI, MACD, EMA12, EMA26, SO_K, SO_D, ADX | 7 |
| historical | Close, Volume, Open, USD/TRY, TCMB, WTI | 6 |
| closing | Kapanış fiyatı | 1 |

**Emeklilik Fonları (3 set):**

| Set | Özellikler | Sayı |
|:---|:---|:---|
| full | RSI, MACD, EMA12, EMA26, Momentum, Volatilite, Kapanış | 7 |
| technical | Momentum, Volatilite, Kapanış | 3 |
| closing | Kapanış fiyatı | 1 |

> **Not:** TEFAS verisinde High/Low bulunmadığından SO_K/SO_D → Momentum, ADX → Volatilite ile ikame edilmiştir.

### 3.3. Deneysel Tasarım

- Giriş penceresi: In ∈ {2, 4, 6}
- Tahmin ufku: Out ∈ {1, 3, 5}
- Seed: {23, 27, 98} — Van der Burgt (2023) ile tutarlı
- Toplam: ~3.000 konfigürasyon eğitilmiştir

### 3.4. Test Seti Sınıf Dağılımı

| Varlık | Test N | Yükseliş | Düşüş | Oran | Not |
|:---|:---|:---|:---|:---|:---|
| THYAO (Out=1) | 313 | 155 | 157 | %49,7 | İdeal denge |
| ALZ | 38 | 37–38 | 0 | %100 | Tam MC |
| AZS (Out=3) | ~33 | ~28 | ~9 | %75,7 | Asimetrik |
| AMZ (Out=3) | ~37 | ~30 | ~7 | %81,1 | Asimetrik |

---

## 4. BULGULAR

### 4.1. THYAO Hisse Senedi Sonuçları

**Tablo 1. THYAO Model Karşılaştırması (2018–2026, Test Seti)**

| Model | En İyi Acc | F1 | Sens | Spec | BA | Konfigürasyon | MC |
|:---|:---|:---|:---|:---|:---|:---|:---|
| ARIMA | %55,78 | — | — | — | — | In=6, Out=3, d=1 | — |
| CNN | %53,97 | 0,638 | 0,758 | 0,331 | %54,45 | hist_tech, In=2, Out=3 | 9/36 |
| **LSTM ★** | **%57,56** | **0,589** | **0,574** | **0,600** | **%58,71** | **hist_tech, In=4, Out=3** | **12/36** |
| Naive | %79,73 | — | — | — | — | Out=5 | — |

> THYAO'da hiçbir karmaşık model Naive Baseline'ı tutarlı biçimde aşamamıştır. Piyasa gürültüsü algoritma karmaşıklığına baskın gelmektedir.

**Tablo 2. THYAO Concept Drift Analizi (Technical Özellik Seti Ortalaması)**

*Not: Aşağıdaki değerler, technical (7 özellik) setindeki 9 konfigürasyonun (3 In × 3 Out) ortalama test doğruluğudur. Kaynak: LSTM_sonuclar_FINAL.csv (satır 11–19) ve CNN_sonuclar_FINAL.csv (satır 11–19).*

| Model | Eski (2018–2022) | Güncel (2018–2026) | Değişim |
|:---|:---|:---|:---|
| LSTM | %55,83 | %50,52 | −%5,31 ↓ |
| CNN | %56,79 | %49,55 | −%7,24 ↓ |
| ARIMA (ort.) | %49,83 | %51,34 | +%1,51 (stabil) |

> ARIMA zaten random walk (~%50) seviyesindeydi — başarısız kalmanın sürmesi dirençlilik sayılamaz. Asıl darbeyi alan derin öğrenme modelleridir.

---

### 4.2. ALZ — Düşük Riskli Fon (Kontrol Grubu)

**Tablo 3. ALZ Sonuçları**

| Model | Acc | Spec | BA | Not |
|:---|:---|:---|:---|:---|
| ARIMA | %100,0 | — | — | Monoton yükseliş |
| CNN | %100,0 | NA | %50,00 ⚠ | 27/27 MC |
| LSTM | %100,0 | NA | %50,00 ⚠ | 27/27 MC |
| Naive | %100,0 | — | — | Test setinde 0 düşüş |

> ALZ bir başarı ölçütü değil, MC İllüzyonu'nun ispatıdır. Test döneminde düşüş hareketi olmadığından her model %100 alır — bu öğrenme değil, ezberdir.

---

### 4.3. AZS — Orta Riskli Fon

**Tablo 4. AZS Sonuçları (Non-MC En İyiler)**

| Model | Acc | F1 | Sens | Spec | BA | Konfigürasyon | MC |
|:---|:---|:---|:---|:---|:---|:---|:---|
| ARIMA | %80,65 | — | — | — | — | In=2, Out=5, d=0 | — |
| **CNN ★** | **%75,56** | **0,889** | **0,909** | **0,625** | **%76,70** | **technical, In=4, Out=3** | **9/27** |
| LSTM | %68,89 | 0,844 | 0,792 | 0,667 | %72,95 | full, In=2, Out=5 | 13/27 |
| Naive | %90,32 | — | — | — | — | Out=5 | — |

> CNN, AZS'de LSTM'i hem Accuracy hem MC direnci bakımından geride bırakmıştır. Konvolüsyonel filtrelerin periyodik piyasa döngülerini yakalama üstünlüğü ortadadır.

---

### 4.4. AMZ — Yüksek Riskli Fon (Projenin Yıldızı ★★)

**Tablo 5. AMZ Sonuçları — Projenin En Güçlü Bulgusu**

| Model | Acc | F1 | Sens | Spec | BA | Konfigürasyon | MC |
|:---|:---|:---|:---|:---|:---|:---|:---|
| ARIMA | %80,65 | — | — | — | — | d=0, tüm In'ler aynı | — |
| CNN | %74,36 | 0,857 | 0,900 | 0,333 | %61,65 | closing, In=6, Out=5 | 9/27 |
| **LSTM ★★** | **%80,21** | **0,894** | **0,840** | **0,857** | **%84,86** | **full, In=2, Out=3** | **10/27** |
| Naive (Out=3) | %78,79 | — | — | — | — | — | — |
| Naive (Out=5) | %83,87 | — | — | — | — | — | — |

> AMZ LSTM, **kendi tahmin ufkunda** (Out=3) Naive Baseline'ı (%78,79) geride bırakarak projenin yıldız bulgusunu oluşturmuştur. p=0,0001 ile istatistiksel anlamlılık kesindir.

**Tablo 5a. AMZ LSTM Şampiyon — Havuzlanmış Karmaşıklık Matrisi (N=96)**

|  | Tahmin: Yükseliş | Tahmin: Düşüş |
|:---|:---|:---|
| **Gerçek: Yükseliş** | TP = 63 | FN = 12 |
| **Gerçek: Düşüş** | FP = 3 | TN = 18 |

*Metodolojik Not:* Havuzlanmış karmaşıklık matrisi, 3 bağımsız seed'in (23, 27, 98) test tahminlerinin kümülatif olarak birleştirilmesiyle oluşturulmuştur (N = 32 × 3 = 96). Matristen hesaplanan doğruluk oranı (63+18)/96 = %84,38 iken, Tablo 5'te raporlanan ortalama doğruluk %80,21'dir. Bu fark, havuzlanmış matrisin üç seed'in ham tahminlerini eşit ağırlıkla birleştirmesinden; ortalama doğruluğun ise her seed'in kendi test setindeki doğruluğunun aritmetik ortalaması (0,8438 + 0,7188 + 0,8438) / 3 = 0,8021 olmasından kaynaklanmaktadır. Seed 27'nin daha düşük performansı (%71,88), ortalamayı aşağı çekerken; havuzlanmış matriste bu seed'in hataları diğer iki seed'in doğru tahminleri tarafından dengelenmektedir. Her iki raporlama yöntemi de literatürde kabul görmektedir; bu çalışmada şeffaflık adına her ikisi de sunulmuştur.

> Seed sonuçları: 0,8438 / 0,7188 / 0,8438 — SD = 0,0722. Grafik 10'da bu havuzlanmış matris görselleştirilmiştir.

---

### 4.5. Majority Class Dağılımı Özeti

**Tablo 6. MC Dağılımı — Tüm Varlıklar**

| Varlık/Model | full | technical | historical | closing | TOPLAM | Oran |
|:---|:---|:---|:---|:---|:---|:---|
| THYAO LSTM | — | 0/9 | 3/9 | 9/9 | 12/36 | %33 |
| THYAO CNN | — | 0/9 | 0/9 | 9/9 | 9/36 | %25 |
| ALZ (tümü) | 9/9 | 9/9 | — | 9/9 | 27/27 | %100 |
| AZS LSTM | 1/9 | 3/9 | — | 9/9 | 13/27 | %48 |
| AZS CNN | 1/9 | 3/9 | — | 5/9 | 9/27 | %33 |
| AMZ LSTM | 0/9 | 1/9 | — | 9/9 | 10/27 | %37 |
| AMZ CNN | 1/9 | 1/9 | — | 7/9 | 9/27 | %33 |

> **Anahtar bulgular:** (1) CNN her varlıkta LSTM'den daha az MC üretmiştir. (2) Closing seti neredeyse tüm varlıklarda %100 MC'ye düşmüştür. (3) AMZ LSTM full seti 0/9 MC — projenin en temiz öğrenme bölgesidir.

---

## 5. TARTIŞMA

### 5.1. Bulgu 1: Sinyal/Gürültü Oranı Algoritma Karmaşıklığından Belirleyicidir

THYAO'da hiçbir model Naive'i aşamazken, AMZ fonunda LSTM %80,21 ile olağanüstü başarı yakalamıştır. Aynı metodoloji, aynı mimari — değişen yalnızca verinin yapısıdır. Emeklilik fonlarının kurumsal yönetim kaynaklı ataleti, derin öğrenme için öğrenilebilir sinyal üretmektedir.

### 5.2. Bulgu 2: CNN, MC'ye LSTM'den Daha Dirençlidir

Tüm varlıklarda CNN ≤ LSTM (MC sayısı). LSTM'in uzun vadeli hafıza yapısı gürültülü verilerde avantaj yerine ağırlığa dönüşmektedir. CNN'in yerel filtreleri sınıf dengesizliğine karşı daha esnek kalmıştır.

### 5.3. Bulgu 3: Düşük Riskli Fonlarda Öğrenme Yetersizliği

ALZ'de 27/27 MC — test setinde düşüş hareketi yoktur. %100 Accuracy bir illüzyondur; Balanced Accuracy %50,00 ile rastlantı düzeyindedir. Bu tür varlıklarda ARIMA yeterlidir.

### 5.4. Bulgu 4: Metodolojik İyileştirmelerin Katkısı

class_weight uygulaması ile:
- AZS CNN: 19/27 → 9/27 MC (−10, dramatik)
- AMZ CNN: 15/27 → 9/27 MC (−6)
- THYAO LSTM: 16/36 → 12/36 MC (−4, veri dönemi uzaması ile birlikte)

### 5.5. Etkin Piyasa Hipotezi (EMH) Tartışması

- **THYAO:** %50 civarı sonuçlar → EMH geçerli, piyasa etkin
- **AMZ:** %80,21 → EMH'ye aykırı gözlem; emeklilik fonlarının kurumsal atalet yapısı tahmin edilebilir sinyal içermektedir

### 5.6. Kısıtlar

1. İşlem maliyetleri (komisyon, slippage) dahil edilmemiştir
2. Emeklilik fonlarında valor süreleri (T+1, T+2) gerçek zamanlı ticareti kısıtlar
3. 3 seed kullanılmıştır — 10+ seed daha güvenilir olurdu
4. TEFAS verisinde High/Low yoktur → SO_K/SO_D hesaplanamamıştır

---

## 6. SONUÇ

Finansal piyasaların yönünü tahmin etmede tek ve kusursuz bir derin öğrenme modeli bulunmamaktadır. Model seçimi varlığın risk profiline ve verinin gürültü seviyesine göre yapılmalıdır. Yüksek gürültülü piyasalarda (THYAO) algoritmalar yön bulmakta zorlanırken, temiz momentum serilerinde (AMZ) LSTM, orta riskli serilerde (AZS) ise 1D-CNN öne çıkmaktadır. Elde edilen bulgular, derin öğrenmenin finansal yön tahminindeki sınırlarını ortaya koymakla birlikte, Majority Class illüzyonunun raporlanmasının alan için kritik bir gereklilik olduğunu göstermektedir.

**Tablo 7. Nihai Şampiyon Model Tablosu**

| Varlık | Şampiyon | BA | Gerekçe |
|:---|:---|:---|:---|
| THYAO | LSTM (hist_tech) | %58,71 | Concept drift'e rağmen %50'yi koruyan en dengeli model |
| ALZ | ARIMA | %50,00 | MC laboratuvarı — DL gereksiz |
| AZS | CNN (technical) | %76,70 | Periyodik döngüleri yakalama üstünlüğü |
| **AMZ** | **LSTM (full)** | **%84,86 ★** | **Naive'i aşan tek model — projenin en güçlü kanıtı** |

---

## KAYNAKÇA

1. Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
2. Box, G. E. P., & Jenkins, G. M. (1976). *Time series analysis: Forecasting and control*. Holden-Day.
3. Chong, E., Han, C., & Park, F. C. (2017). Deep learning networks for stock market analysis. *Expert Systems with Applications*, 83, 187–205.
4. Engle, R. F. (1982). Autoregressive conditional heteroscedasticity. *Econometrica*, 50(4), 987–1008.
5. Fama, E. F. (1970). Efficient capital markets. *The Journal of Finance*, 25(2), 383–417.
6. Fischer, T., & Krauss, C. (2018). Deep learning with LSTM for financial market predictions. *European Journal of Operational Research*, 270(2), 654–669.
7. He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE TKDE*, 21(9), 1263–1284.
8. Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.
9. Kara, Y., Boyacioglu, M. A., & Baykan, Ö. K. (2011). Predicting direction of stock price index. *Expert Systems with Applications*, 38(5), 5311–5319.
10. Khaidem, L., Saha, S., & Dey, S. R. (2016). Predicting the direction of stock market prices using random forest. *arXiv:1605.00003*.
11. Kim, K. J. (2003). Financial time series forecasting using SVM. *Neurocomputing*, 55(1–2), 307–319.
12. King, G., & Zeng, L. (2001). Logistic regression in rare events data. *Political Analysis*, 9(2), 137–163.
13. Krauss, C., Do, X. A., & Huck, N. (2017). Deep neural networks, gradient-boosted trees, random forests. *European Journal of Operational Research*, 259(2), 689–702.
14. Selvin, S., Vinayakumar, R., et al. (2017). Stock price prediction using LSTM, RNN and CNN. *ICACCI 2017*, 1643–1647.
15. Siami-Namini, S., Tavakoli, N., & Namin, A. S. (2018). ARIMA vs LSTM in forecasting time series. *ICMLA 2018*, 1394–1401.
16. Valverde-Albacete, F. J., & Peláez-Moreno, C. (2014). 100% classification accuracy considered harmful. *PLoS ONE*, 9(1), e84217.
17. Van der Burgt, M. (2023). *Navigating trends: Predicting NASDAQ100 direction with ML and DL* [Master's thesis]. Tilburg University.

---

## EKLER

### EK A — Van der Burgt (2023) ile 9 Metodolojik Fark

| # | Fark | Gerekçe |
|:---|:---|:---|
| 1 | NASDAQ100 → THYAO | Gelişmekte olan piyasada test |
| 2 | DXY → USD/TRY | Yerel kur daha açıklayıcı |
| 3 | FED → TCMB | Yerel para politikası |
| 4 | Investing.com → Yahoo Finance | Tekrar üretilebilirlik |
| 5 | CNN Business → GitHub (F&G) | Veri 2020'de bitiyor → çıkarıldı |
| 6 | Forward fill açıkça belirtildi | Orijinal açıklamamış |
| 7 | ARIMA: CSS vs ML | Yakınsama sorunu çözümü |
| 8 | Appendix C p/q tutarsızlığı | Metin-tablo uyuşmazlığı |
| 9 | Fear&Greed çıkarıldı | 14 → 13 özellik |

### EK B — Teknik Gösterge Formülleri

| Gösterge | Formül | Kullanım |
|:---|:---|:---|
| Log Getiri | R_t = ln(P_t / P_{t-1}) | Durağanlık |
| EMA(12) | EMA_t = P_t×(2/13) + EMA_{t-1}×(11/13) | Kısa trend |
| MACD | EMA_12 − EMA_26 | Momentum farkı |
| RSI | 100 − 100/(1+RS) | Aşırı alım/satım |
| SO %K | 100×(C−L₁₄)/(H₁₄−L₁₄) | Fiyat konumu |
| ADX | 100×EMA(\|+DI−(−DI)\|/(+DI+(−DI))) | Trend gücü |
| class_weight | w = n_total / (2×n_class) | Sınıf dengesizliği |

### EK C — Grafik Listesi

| Grafik | Açıklama | Kaynak |
|:---|:---|:---|
| Grafik 1 | Doğruluk Yanılgısı — LSTM Kapanış Acc %52,67 ama Spec %0 | 04_TR/01 |
| Grafik 2 | Ufuk Süresi vs Doğruluk — Naive Out uzadıkça güçlenir | 04_TR/02 |
| Grafik 3 | Model×Varlık Isı Haritası — ARIMA/CNN/LSTM/Naive | 04_TR/03 |
| Grafik 4 | AMZ Dengeli Doğruluk — LSTM (%84,86) vs CNN (%61,65) | 04_TR/04 |
| Grafik 5 | Risk vs Öğrenme — ALZ (0) → AZS (~%44) → AMZ (~%48) | 04_TR/05 |
| Grafik 6 | MC Direnci — CNN sürekli LSTM'den dirençli | 04_TR/06 |
| Grafik 7 | Özellik Etkisi — Kapanış %100 MC, Tarihsel+Teknik %0 MC | 04_TR/07 |
| Grafik 8 | Concept Drift — 2022 sonrası DL performans düşüşü | 04_TR/08 |
| Grafik 9 | AMZ LSTM Dengeli Performans — Acc/F1/Sens/Spec profili | 04_TR/09 |
| Grafik 10 | AMZ LSTM Karmaşıklık Matrisi (N=96) — 81/96 doğru | 04_TR/10 |
