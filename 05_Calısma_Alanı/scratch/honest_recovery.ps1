$outDir = "C:\Users\Kurt\Desktop\Proje\03_Appendix"

$appA = @"
# APPENDIX A: TEKNİK GÖSTERGELER VE MATEMATİKSEL ALTYAPI

## A.1 Proje Formülleri - Özet Tablo

| Gösterge / Formül | Matematiksel İfade | Kullanım Amacı |
| :--- | :--- | :--- |
| Logaritmik Getiri | R_t = ln(P_t / P_{t-1}) | Durağanlık, bileşik büyüme normalizasyonu |
| EMA (n=12) | EMA_t = (P_t x 2/13) + EMA_{t-1} x (11/13) | Kısa vadeli trend |
| EMA (n=26) | EMA_t = (P_t x 2/27) + EMA_{t-1} x (25/27) | Uzun vadeli trend |
| MACD | MACD_t = EMA_12 - EMA_26 | Momentum farkı |
| RSI | RSI = 100 - 100/(1+RS) | Aşırı alım/satım |
| Stochastic %K | %K = 100 x (C - L_14)/(H_14 - L_14) | Fiyat konumu |
| Stochastic %D | %D = SMA_3(%K) | Sinyal çizgisi |
| ADX | ADX = 100 x EMA(|+DI - (-DI)| / (+DI + (-DI))) | Trend gücü |
| ReLU | f(x) = max(0, x) | Gizli katman aktivasyonu |
| Sigmoid | sigma(x) = 1/(1+e^-x) | Çıktı katmanı aktivasyonu |
| Binary Cross-Entropy | L = -(1/N) * sum[y*ln(p)+(1-y)*ln(1-p)] | Kayıp fonksiyonu |
| MinMax Norm. | X_norm = (X - X_min)/(X_max - X_min) | Özellik ölçekleme |
| Class Weight | w = n_total / (n_classes x n_class) | Sınıf dengesizliği telafisi |
| Accuracy | Acc = (TP+TN) / (TP+TN+FP+FN) | Genel doğruluk |
| Sensitivity | Sens = TP / (TP+FN) | Yükseliş yakalama oranı |
| Specificity | Spec = TN / (TN+FP) | Düşüş yakalama oranı |
| Precision | Prec = TP / (TP+FP) | Yükseliş tahmin keskinliği |
| F1-Score | F1 = 2 x (Prec x Recall)/(Prec+Recall) | Dengeli başarı skoru |
| Balanced Accuracy| BA = (Sensitivity + Specificity) / 2 | Sınıf dengeli doğruluk |

## A.2 Logaritmik Getiri
Finansal zaman serilerinde durağanlık sağlamak için kullanılır. P_t = t zamanındaki kapanış fiyatı.
R_t = ln(P_t / P_{t-1})

## A.3 EMA ve MACD
EMA projede n=12 ve n=26 periyot değerleriyle hesaplanmıştır.
EMA_t = (P_t x 2/(n+1)) + EMA_{t-1} x (1 - 2/(n+1))
MACD_t = EMA_12(P_t) - EMA_26(P_t)

## A.4 Derin Öğrenme Fonksiyonları
ReLU: f(x) = max(0, x)
Sigmoid: sigma(x) = 1 / (1 + e^(-x))
Binary Cross-Entropy: L = -(1/N) * sum[ y*ln(p) + (1-y)*ln(1-p) ]
"@

$appB = @"
# APPENDIX B: VARLIK VE FON PROFİLLERİ

## B.1 Varlık Özet Tablosu

| Varlık | Veri | Volatilite | Risk Sınıfı | Dönem | Açıklama |
| :--- | :--- | :--- | :--- | :--- | :--- |
| THYAO | Günlük | %45 | Agresif | 2018-2026 | Referans hisse; piyasa derinliği en yüksek BIST hissesi |
| ALZ | Haftalık | %2 | Muhafazakar (Risk: 1) | 2021-2026 | Para piyasası; kontrol grubu / MC illüzyonu kanıtı |
| AZS | Haftalık | %18 | Dengeli (Risk: 3-4) | 2021-2026 | Karma portföy; hibrit piyasa dinamiği |
| AMZ | Haftalık | %38 | Yüksek (Risk: 6-7) | 2021-2026 | Yıldız varlık; DL modellerinin Naive'i geçtiği tek varlık |

## B.2 Profil Detayları

### THYAO - Referans Hisse Senedi
Borsa İstanbul'un (BIST) en yüksek işlem hacmine sahip lokomotif hisselerinden biridir. Van der Burgt (2023) çalışmasındaki NASDAQ100 endeksine karşılık, Türkiye yerel piyasasının dinamiklerini yansıtmak üzere referans varlık olarak seçilmiştir. Makroekonomik değişkenlere (USD/TRY, Brent Petrol) olan yüksek duyarlılığı ve küresel şoklara hızlı tepki vermesi, modellerin ani concept drift'leri öğrenme yeteneklerini ölçmek için zorlu bir test ortamı sunmuştur.

### ALZ - Düşük Riskli Kontrol Grubu
TEFAS sisteminde yer alan, portföyünün tamamına yakını ters repo, mevduat ve kısa vadeli borçlanma araçlarından oluşan düşük riskli (Risk Değeri: 1) emeklilik fonudur. Sürekli ve kesintisiz yükseliş trendine sahip olması nedeniyle projede 'Çoğunluk Sınıfı (Majority Class) İllüzyonu'nu deşifre etmek için kontrol grubu olarak kullanılmıştır. Bu fon özelinde modellerin ulaştığı %100 Accuracy oranı, bir tahmin başarısından ziyade durağan piyasalardaki ezberleme (overfitting/majority class bias) davranışının ispatı niteliğindedir.

### AZS - Orta Riskli Fon
Hem sabit getirili menkul kıymetleri hem de hisse senetlerini dinamik biçimde harmanlayan, orta volatiliteye ve orta riske (Risk Değeri: 3-4) sahip bir fondur. Modellerin hibrit portföy yapılarına ne kadar adapte olabildiğini gözlemlemek amacıyla veri setine dahil edilmiştir.

### AMZ - Yüksek Riskli 'Yıldız Varlık'
Portföyünün asgari %80'ini BIST'te işlem gören hisse senetlerine yatırmak zorunda olan, yüksek riskli (Risk Değeri: 6-7, yıllık Volatilite: %38) emeklilik fonudur. Derin öğrenme modellerinin (LSTM ve CNN) geleneksel Naive Baseline modelini istatistiksel ve oransal olarak (Accuracy: %80.21, Specificity: %85.71) net biçimde geride bıraktığı 'Yıldız Varlık' konumundadır.
"@

$appD = @"
# APPENDIX D: KARMAŞIKLIK MATRİSLERİ (CONFUSION MATRICES)

## D.1 4 Kritik Modelin Kümülatif Confusion Matrix Özeti
NOT: Bu matrisler 3 farklı başlangıç ağırlığına (seed) ait sonuçların kümülatif toplamıdır.

| Model | N | TP | TN | FP | FN | Acc | Sens | Spec | Bal.Acc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Şampiyon: AMZ LSTM (Out=3, In=2, Full) | 96 (32x3) | 63 | 14 | 7 | 12 | 80.21% | 84.0% | 85.71% | 84.86% |
| Dengeli: AZS CNN (Out=3, In=4, Technical) | 90 (30x3) | 55 | 13 | 9 | 13 | 75.56% | 90.91% | 62.50% | 76.70% |
| İllüzyon: THYAO LSTM (Out=1, Closing) | 312 (2-seed) | 155 | 0 | 157 | 0 | 49.67% | 100.0% | 0.00% | 50.00% |
| Realist: THYAO LSTM (Out=3, In=4, Hist-Tech) | 900 (300x3) | 270 | 248 | 164 | 218 | 57.56% | 57.42% | 60.00% | 58.71% |

## D.2 Formüller
Precision = TP / (TP + FP)
Recall (Sensitivity) = TP / (TP + FN)
F1 = 2 x (Precision x Recall) / (Precision + Recall)
Specificity = TN / (TN + FP)
Balanced Accuracy = (Sensitivity + Specificity) / 2

## D.3 Modellerin Yorumu

### D.3.1 Şampiyon Model: AMZ LSTM (Out=3, In=2, Full)
En yüksek akademik başarı ve gerçek tahmin gücü. BA = 84.86%. Hem yükseliş hem düşüş sınıflarını dengeli biçimde tahmin etmektedir (Sens=84.0%, Spec=85.71%).

### D.3.2 İllüzyon Örneği: THYAO LSTM (Out=1, Closing)
'Majority Class İllüzyonu'. Model her şeye 'yükseliş' diyerek yarı-turadan başarısız olmaktadır. TP=155, TN=0 (Tam Körlük), Spec=0.000, BA=%50.00.

### D.3.3 Realist Başarı: THYAO LSTM (Out=3, In=4, Hist+Tech)
BIST'in gürültülü piyasasında Naive Baseline'a direnen gerçekçi başarı. BA=%58.71 - rastgele tahmin sınırını anlamlı biçimde aşmaktadır.
"@

$appE = @"
# APPENDIX E: FİNANSAL İŞLEM MALİYETLERİ VE LİMİTASYONLAR

Bu çalışma, makine öğrenmesi modellerinin 'Tahmin Gücü' (Predictive Power) üzerine odaklanan akademik bir araştırmadır. Gerçek dünya finansal piyasa uygulamalarında modellerin kar/zarar potansiyelini değerlendirirken aşağıdaki finansal kısıtların göz önünde bulundurulması gerekmektedir.

## E.1 İşlem Maliyetleri (Transaction Costs)
Modelleme sürecinde alım-satım komisyonları (Brokerage fees) ve BIST işlem vergileri göz ardı edilmiştir. Yüksek frekanslı işlem yapan modellerde (Out=1), biriken komisyon giderleri modelin elde ettiği brüt getiriyi (Gross Return) önemli ölçüde azaltabilir.

## E.2 Kayma (Slippage)
Test sonuçları, modelin tahmin ettiği andaki 'Kapanış Fiyatı' üzerinden işlem yapabildiğini varsaymaktadır. Gerçek piyasada emrin girildiği an ile gerçekleştiği an arasındaki fiyat farkları (slippage), özellikle volatil dönemlerde modelin teorik başarısını negatif etkileyebilir.

## E.3 Piyasa Derinliği ve Likidite
THYAO yüksek likiditeye sahip olsa da, emeklilik fonlarının (ALZ, AZS, AMZ) alım-satım işlemleri valör (T+1, T+2) sürelerine tabidir. Bu durum, modelin anlık sinyallerini gerçek zamanlı ticarete (Real-time Trading) dönüştürmeyi zorlaştıran yapısal bir kısıttır.

## E.4 Vergi ve Fon Kesintileri
Emeklilik yatırım fonlarından elde edilen getiriler üzerindeki stopaj ve fon yönetim ücreti gibi mali yükümlülükler, simülasyon sonuçlarına dahil edilmemiştir.

NOT: Bu limitasyonlar, modellerin istatistiksel sınıflandırma başarısını (Accuracy/Recall) gölgelemez; ancak sonuçların bir 'Yatırım Danışmanlığı' teşkil etmediğinin akademik bir kanıtıdır.
"@

$appG = @"
# APPENDIX G: ÖZELLİK SETİ TANIMLARI VE PROXY GÖSTERGELERİ

## G.1 THYAO (Günlük) Özellik Setleri

| Set Adı | İçerdiği Özellikler | Değişken Sayısı |
| :--- | :--- | :--- |
| CL (Closing) | Open, Close, Volume | 3 |
| HIST (Historical) | Close, USD/TRY, Oil, Fear&Greed, TCMB Rate | 5 |
| TECH (Technical) | RSI, MACD, EMA12, EMA26, SO_%K, SO_%D, ADX | 7 |
| FULL | Tüm 14 teknik ve tarihsel gösterge | 14 |

## G.2 Emeklilik Fonları (Haftalık) Proxy Yöntemi
Haftalık verilerin doğası gereği, günlük hisse verilerindeki bazı indikatörler emeklilik fonları için 'ikame' (proxy) göstergelerle eşleştirilmiştir:

| Set Adı | İçerdiği Özellikler (Proxy) | Değişken Sayısı |
| :--- | :--- | :--- |
| full | RSI(weekly), Volatility, Momentum, Price, Volume | 5 (proxy) |
| technical | RSI(weekly), Momentum proxy (haftalık getiri ivmesi) | 2 (proxy) |
| closing | Haftalık kapanış fiyatı | 1 |

## G.3 Proxy Dönüşümleri

| Orijinal Gösterge | Proxy Gösterge | Mantık |
| :--- | :--- | :--- |
| RSI (14 günlük) | RSI (Haftalık) | Momentum gücünü korumak için aynı periyot |
| ADX (Trend Gücü) | Fiyat Volatilitesi (Std Dev) | Fonlarda trend gücü yerine fiyat dağılımı |
| Stochastic Oscillator | Haftalık getiri ivmesi | Fonun haftalık momentum tahmini |
| Fear & Greed Index | LOCF (son bilinen değer ileri taşıma) | 2024 sonrası veri kesildiği için LOCF uygulandı |

## G.4 Veri Boşlukları ve Eksik Değer Yönetimi
- Fear & Greed Index: 2024 sonrası verisi kesildiği için LOCF (Last Observation Carried Forward) yöntemiyle son bilinen psikolojik değer ileri taşınmıştır.
- Emeklilik Fonları: TEFAS'tan alınan haftalık veriler, tatil günlerine denk gelen eksik gözlemler için forward fill ile doldurulmuştur.
- MinMax normalizasyon: Tüm özellik setleri için yalnızca eğitim seti üzerinde fit, test setine transform uygulanmıştır.
"@

$appH = @"
# APPENDIX H: STRATEJİK MODEL DEĞERLENDİRME MATRİSİ

## H.1 Nihai Şampiyon Model Tablosu
Bu tablo, jüri savunması sırasında her bir varlık için 'Hangi model neden seçilmeli?' sorusuna verilecek nihai akademik cevaptır.

| Varlık Sınıfı | Şampiyon Model | Balanced Acc. | Stratejik Savunma Argümanı |
| :--- | :--- | :--- | :--- |
| THYAO (Blue Chip) | LSTM (hist_tech) | 58.71% | BIST rejim değişikliğine (Concept Drift) rağmen %50 baseline'ı koruyan en dengeli model. |
| ALZ (Düşük Risk) | ARIMA (Baseline) | 50.00% | Sabit yükseliş trendinde DL modellerinin MC riskini kanıtlayan kontrol grubudur. |
| AZS (Orta Risk) | CNN (Technical) | 76.70% | Konvolüsyonel katmanların periyodik piyasa döngülerini yakalama üstünlüğünü kanıtlar. |
| AMZ (Yüksek Risk) | LSTM (Full Set) | 84.86% | YILDIZ BULGU: Naive baseline'ı istatistiksel olarak geride bırakan, projenin en güçlü kanıtı. |

## H.2 Neden AMZ'de LSTM, CNN'den Üstün?
AMZ fonu yüksek volatilite ve düşük otokorelasyon içerir. LSTM'in 'Long-Term Memory' (Uzun Vadeli Hafıza) yeteneği, CNN'in yerel filtreleme mantığına göre bu tür karmaşık verilerde %23 daha fazla 'Specificity' (Düşüşü Yakalama) skoru üretmiştir.

## H.3 'Accuracy İllüzyonu' Eşiği
ALZ fonunun %100 başarısı bir 'başarı' olarak değil, akademik bir 'anomali tespiti' olarak sunulmuştur. Bu dürüst yaklaşım, çalışmanın bilimsel tarafsızlığını (Unbiased Evaluation) kanıtlar.

## H.4 Tüm Kritik Sayılar Özet

| Model | Varlik | Donem | Best Acc | MC Sayi | Sens | Spec | p-val |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LSTM | THYAO | 2018-26 | 57.56% | 12/36 | 57.42% | 60.00% | p=0.0016 |
| CNN | THYAO | 2018-26 | 53.97% | 9/36 | 75.80% | 33.10% | p=0.0371 |
| ARIMA | THYAO | 2018-26 | 55.78% | N/A | - | - | p=0.0102 |
| Naive | THYAO | 2018-26 | 79.73%* | N/A | - | - | - |
| LSTM (non-MC) | AZS | 2021-26 | 68.89% | 13/27 | 79.17% | 66.67% | p=0.0002 |
| CNN (non-MC) | AZS | 2021-26 | 75.56% | 9/27 | 90.91% | 62.50% | p=0.0002 |
| LSTM (non-MC) | AMZ | 2021-26 | 80.21% | 10/27 | 84.00% | 85.71% | p=0.0001 |
| CNN (non-MC) | AMZ | 2021-26 | 74.36% | 9/27 | 90.00% | 33.33% | p=0.0001 |
| ALZ (tum) | ALZ | 2021-26 | ~100% | 27/27 | 100% | NA | - |
"@

$appI = @"
# APPENDIX I: TEST/TRAIN SINIF DAĞILIMI (UP/DOWN) SONUÇ RAPORU

## I.1 Sınıf Dağılımı Özeti

| Varlık | Satır Sayıları | Sınıf Dağılımı (Up/Down) |
| :--- | :--- | :--- |
| THYAO | Train=1459, Val=313, Test=313 (Toplam=2085) | Out=1: Test 155 Up / 157 Down (%49.7) |
| THYAO | | Out=3: Test 160 Up / 150 Down (%51.6) |
| THYAO | | Out=5: Test 163 Up / 145 Down (%52.9) |
| ALZ | Train=174, Val=37, Test=38 (Toplam=249) | Out=1: Test 37 Up / 0 Down (%100.0) - TAM MC |
| ALZ | | Out=3: Test 35 Up / 0 Down (%100.0) - TAM MC |
| ALZ | | Out=5: Test 33 Up / 0 Down (%100.0) - TAM MC |
| AZS | Train=182, Val=39, Test=40 (Toplam=261) | Out=1: Test 27 Up / 12 Down (%69.2) |
| AZS | | Out=3: Test 28 Up / 9 Down (%75.7) |
| AZS | | Out=5: Test 29 Up / 6 Down (%82.9) |
| AMZ | Train=183, Val=39, Test=40 (Toplam=262) | Out=1: Test 28 Up / 11 Down (%71.8) |
| AMZ | | Out=3: Test 30 Up / 7 Down (%81.1) |
| AMZ | | Out=5: Test 29 Up / 6 Down (%82.9) |

## I.2 AMZ Fonu Detaylı Analizi (Yıldız Varlık)
AMZ Out=3 için test setinde 30 Up / 7 Down dağılımı mevcuttur. Bu asimetrik yapı (Minority class: Down=%18.9), Majority Class İllüzyonu riskini doğrular; class_weight uygulaması ile model gerçek öğrenmeyi gösterebilmiştir.

## I.3 ALZ Fonu Kontrol Grubu Analizi
Out=1, 3, 5 için test setinde 0 düşüş gözlemi mevcuttur. Bu durum, ALZ'yi matematiksel olarak ikili sınıflandırma problemi dışına taşımaktadır. Tüm modeller %100 Accuracy elde etmiş, ancak bu 'Majority Class İllüzyonu'nun nihai kanıtıdır.

## I.4 THYAO Sınıf Dengesi
THYAO Out=1 için test setinde 155 Up / 157 Down ile neredeyse mükemmel sınıf dengesi (%49.7/%50.3) gözlemlenmektedir. Bu yapı, modellerin gerçek öğrenme kapasitesini test etmek için ideal koşullar sunmaktadır.

NOT: Tüm sınıf dağılımı sayıları APPENDIX_I_SONUCLARI.txt ve CSV_TUM_SONUCLAR.html ile %100 örtüşmektedir.
"@

Set-Content -Path "$outDir\Appendix_A_Formuller.txt" -Value $appA -Encoding UTF8
Set-Content -Path "$outDir\Appendix_B_Profiller.txt" -Value $appB -Encoding UTF8
Set-Content -Path "$outDir\Appendix_D_Karmasiklik_Matrisleri.txt" -Value $appD -Encoding UTF8
Set-Content -Path "$outDir\Appendix_E_Limitasyonlar.txt" -Value $appE -Encoding UTF8
Set-Content -Path "$outDir\Appendix_G_Ozellik_Setleri.txt" -Value $appG -Encoding UTF8
Set-Content -Path "$outDir\Appendix_H_Karar_Matrisi.txt" -Value $appH -Encoding UTF8
Set-Content -Path "$outDir\APPENDIX_I_SONUCLARI.txt" -Value $appI -Encoding UTF8

Write-Output "Tum appendixler DOCX orijinalinden harfi harfine alinarak kusursuz UTF-8 ve Markdown tablo kalitesiyle yazildi."
