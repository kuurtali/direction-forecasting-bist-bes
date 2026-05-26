# UYIK-2026 KONUŞMACI NOTLARI
## VII. International Applied Statistics Congress — 11-13 Mayıs 2026, İstanbul
### Sunum Süresi: 12 dakika + 3 dakika Soru-Cevap
### BES Emeklilik Fonları Üzerine Derin Öğrenme ile Yön Tahmini

---

## SLAYT AKIŞI VE SÜRE PLANI

| Bölüm | Slaytlar | Süre | Konuşmacı |
|:---|:---|:---|:---|
| Açılış + Motivasyon | S1–S4 | 2 dk | Konuşmacı 1 |
| Literatür + Metodoloji | S5–S12 | 3 dk | Konuşmacı 1 |
| Veri ve Deneysel Tasarım | S13–S16 | 2 dk | Konuşmacı 2 |
| Sonuçlar + MC Analizi | S17–S26 | 3.5 dk | Konuşmacı 2 |
| Sonuç + Tartışma | S27–S31 | 1.5 dk | Konuşmacı 1 |
| Teşekkür + Soru-Cevap | S32 | 3 dk | İkisi birlikte |

---

## KONUŞMACI 1 — AÇILIŞ (S1–S4, ~2 dk)

### S1 — Kapak Slaytı
"Sayın başkan, değerli jüri üyeleri, meslektaşlarım; sunumumuza hoş geldiniz. Bugün sizlerle, bireysel emeklilik yatırım fonlarının fiyat yönünü tahmin etmede derin öğrenme modellerinin gerçek performansını paylaşacağız."

### S2 — Outline
"Sunumumuz şu akışla ilerleyecek: Önce motivasyonumuzu ve araştırma sorularımızı paylaşacağız. Ardından metodolojimizi, veri yapımızı ve sonuçlarımızı sunacak; en sonunda bulgularımızı tartışacağız."

### S3 — Motivasyon / Problem Tanımı
"Finansal tahminleme literatüründe yüksek Accuracy değerleri sıklıkla başarı olarak raporlanmaktadır. Ancak bir model %100 doğruluk elde ettiğinde bu gerçekten öğrenme midir? Çalışmamızda bu soruya yanıt arıyoruz. Özellikle sınıf dengesizliğinin yarattığı Majority Class illüzyonunu, Türkiye bireysel emeklilik fonları üzerinde test ediyoruz."

### S4 — Araştırma Soruları
"Üç temel soru sorduk: Birincisi, derin öğrenme modelleri geleneksel ARIMA'yı emeklilik fonlarında geçebilir mi? İkincisi, düşük riskli fonlardaki yüksek accuracy değerleri gerçek öğrenmeyi mi yansıtıyor? Üçüncüsü, hangi risk seviyesinde hangi model daha başarılı?"

---

## KONUŞMACI 1 — LİTERATÜR + METODOLOJİ (S5–S12, ~3 dk)

### S5-S6 — Literatür Taraması
"Referans çalışmamız Van der Burgt 2023'tür; NASDAQ100 üzerinde LSTM ve CNN modellerini karşılaştırmıştır. Ancak bu çalışmada Sensitivity ve Specificity raporlanmamış, sınıf ağırlıklandırması yapılmamıştır. Biz bu boşlukları kapatarak gelişmekte olan bir piyasada, emeklilik fonları üzerinde test yapıyoruz."

### S7 — Referans Çalışmadan 4 İyileştirme
"Van der Burgt'tan dört kritik iyileştirme yaptık. Birincisi, normalizasyonu sadece eğitim verisi üzerinden yaparak veri sızıntısını önledik. İkincisi, etiketlemeyi her bölüm için ayrı yaptık. Üçüncüsü, class weight ekleyerek sınıf dengesizliğini telafi ettik. Dördüncüsü, early stopping ile aşırı öğrenmeyi kontrol altına aldık."

### S8-S9 — ARIMA ve Derin Öğrenme Mimarileri
"Geleneksel baseline olarak ARIMA, derin öğrenme mimarileri olarak LSTM ve 1D-CNN kullandık. LSTM'in kapı mekanizmaları uzun vadeli bağımlılıkları öğrenirken, CNN'in konvolüsyon filtreleri yerel paternleri yakalar."

### S10-S11 — Metrikler ve MC Tanımı
"Sınıflandırma problemi olduğu için MSE veya RMSE değil, Accuracy, Sensitivity, Specificity ve F1 kullanıyoruz. Majority Class tanımımız geniştir: Specificity sıfır, Sensitivity sıfır veya Specificity tanımsız olan her konfigürasyon MC olarak işaretlenmiştir."

### S12 — Naive Baseline Açıklaması
"Naive Baseline, önceki gözlemin yönünü doğrudan tahmin olarak kullanır. Tahmin ufku uzadıkça güçlenir. Bir modelin Naive'i geçememesi, gerçek tahmin gücü olmadığını gösterir."

---

## KONUŞMACI 2 — VERİ VE DENEYSEL TASARIM (S13–S16, ~2 dk)

### S13 — Veri Seti Tanıtımı
"Üç Allianz Yaşam emeklilik fonu kullandık. ALZ düşük riskli para piyasası fonudur — kontrol grubumuz. AZS orta riskli karma fondur. AMZ ise yüksek riskli hisse ağırlıklı fondur. Veriler TEFAS'tan haftalık periyotlarla 2021-2026 arası alınmıştır. Gözlem sayıları sırasıyla 249, 261 ve 262'dir."

### S14 — Özellik Setleri
"TEFAS verisinde High ve Low fiyatları bulunmadığından, Stochastic Oscillator yerine Momentum, ADX yerine rolling standart sapma tabanlı Volatilite kullanılmıştır. Üç özellik seti tanımladık: full yedi özellik, technical üç, closing sadece kapanış fiyatı."

### S15 — Deneysel Tasarım
"Input penceresi 2, 4 ve 6 hafta; tahmin ufku 1, 3 ve 5 hafta olarak 9 kombinasyon denenmiştir. Her model 3 farklı seed ile eğitilmiştir. Toplamda 3 fon çarpı 2 model çarpı 3 özellik seti çarpı 9 kombinasyon çarpı 3 seed, yaklaşık 500 model eğitimi gerçekleştirilmiştir."

### S16 — Sınıf Dağılımı
"Burada kritik bir nokta var: ALZ test setinde sıfır düşüş gözlemi mevcuttur. Bu, binary sınıflandırmayı matematiksel olarak anlamsız kılmaktadır ve kontrol grubu olarak kullanılmasının nedeni budur."

---

## KONUŞMACI 2 — SONUÇLAR (S17–S26, ~3.5 dk)

### S17-S18 — ALZ Sonuçları (Kontrol Grubu)
"ALZ fonunda tüm modeller yüzde yüz Accuracy elde etmiştir. Ancak Specificity tanımsızdır çünkü test setinde düşüş yoktur. Dengeli Doğruluk yüzde elli, yani rastlantı düzeyindedir. Bu, Accuracy illüzyonunun en net kanıtıdır. Yüzde yüz Accuracy, sıfır gerçek öğrenme anlamına gelmektedir."

### S19-S20 — AZS Sonuçları
"Orta riskli AZS fonunda CNN, yüzde 75,56 Accuracy ve yüzde 76,70 Dengeli Doğruluk ile LSTM'i geçmiştir. CNN'in MC sayısı 9/27 iken LSTM'in 13/27'dir. Konvolüsyon filtrelerinin periyodik piyasa döngülerini yakalamada üstün olduğu görülmektedir."

### S21-S23 — AMZ Sonuçları (Yıldız Bulgu)
"Ve şimdi projenin yıldız bulgusuna geliyoruz. Yüksek riskli AMZ fonunda LSTM modeli, full özellik seti, 2 haftalık giriş penceresi ve 3 haftalık tahmin ufku ile yüzde 80,21 Accuracy, 0,894 F1 ve yüzde 85,7 Specificity elde etmiştir. Daha da önemlisi, bu model 3 haftalık Naive Baseline'ı — yüzde 78,79'u — istatistiksel olarak anlamlı biçimde geçmiştir. Binom testinde p değeri 0,0001'dir. Bu, tüm çalışmanın en güçlü bulgusudur."

### S24 — Karmaşıklık Matrisi
"Havuzlanmış karmaşıklık matrisinde — 96 gözlem üzerinden — 63 doğru yükseliş, 18 doğru düşüş tahmini görülmektedir. Model hem yükselişleri hem düşüşleri dengeli biçimde ayırt edebilmektedir."

### S25-S26 — MC Direnci Karşılaştırması
"Class weight uygulaması ile MC oranları dramatik biçimde düşmüştür. AZS CNN'de 19/27'den 9/27'ye, AMZ CNN'de 15/27'den 9/27'ye inmiştir. Tüm varlıklarda CNN, LSTM'den daha az MC üretmiştir."

---

## KONUŞMACI 1 — SONUÇ VE TARTIŞMA (S27–S31, ~1.5 dk)

### S27 — Dört Ana Bulgu
"Dört temel bulguyu özetliyoruz: Birincisi, modelin başarısı algoritmadan çok verinin yapısına bağlıdır. İkincisi, CNN sınıf dengesizliğine LSTM'den daha dirençlidir. Üçüncüsü, düşük riskli fonlarda derin öğrenme anlamsızdır. Dördüncüsü, metodolojik iyileştirmeler — özellikle class weight — gerçek öğrenmeyi ortaya çıkarmıştır."

### S28 — Kısıtlar
"Çalışmamızın kısıtlarını da dürüstçe belirtiyoruz: İşlem maliyetleri dahil edilmemiştir, TEFAS verisinde High/Low eksiktir ve 3 seed kullanılmıştır."

### S29-S30 — Gelecek Çalışmalar
"Gelecekte Transformer ve Attention mekanizmaları, online learning yaklaşımları ve daha geniş fon evreninde testler planlanmaktadır."

### S31 — Kapanış
"Sonuç olarak: Emeklilik fonlarının kurumsal atalet yapısı, derin öğrenme için öğrenilebilir sinyal içermektedir. Ancak bu sinyali gerçek öğrenmeden ayırt edebilmek için Specificity ve Sensitivity raporlaması vazgeçilmezdir. Teşekkür ederiz."

---

## S32 — SORU-CEVAP HAZIRLIĞI (3 dk)

**Olası Soru 1:** "ALZ'de yüzde yüz başarı neden raporlanmadı?"
**Cevap:** "ALZ kontrol grubumuzdu. Test setinde düşüş olmadığından her model ve Naive yüzde yüz alır. Bu öğrenme değil, verinin yapısal özelliğidir."

**Olası Soru 2:** "3 seed yeterli mi?"
**Cevap:** "Referans çalışmamız Van der Burgt da 3 seed kullanmıştır. Tutarlılık için aynı sayıyı tercih ettik. Her konfigürasyonda standart sapma raporlanmıştır."

**Olası Soru 3:** "AMZ'nin Naive'i geçmesi şans eseri olabilir mi?"
**Cevap:** "P değerimiz 0,0001'dir. Bu, şans olasılığının on binde bir olduğunu gösterir. İstatistiksel olarak kesindir."

**Olası Soru 4:** "İşlem maliyetleri hesaba katıldı mı?"
**Cevap:** "Hayır, bu bir tahmin gücü çalışmasıdır, portföy optimizasyonu değil. Kısıtlar bölümünde açıkça belirttik."

**Olası Soru 5:** "Neden emeklilik fonları için farklı göstergeler kullandınız?"
**Cevap:** "TEFAS verisi sadece kapanış fiyatı içerir, High/Low yoktur. Stochastic Oscillator ve ADX hesaplanamadığından Momentum ve Volatilite ile ikame ettik."
