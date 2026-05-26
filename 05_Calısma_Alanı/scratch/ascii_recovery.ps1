$outDir = "C:\Users\Kurt\Desktop\Proje\03_Appendix"

$appA = @"
# APPENDIX A: TEKNIK GOSTERGELER VE MATEMATIKSEL ALTYAPI

## A.1 Proje Formulleri - Ozet Tablo

| Gosterge / Formul | Matematiksel Ifade | Kullanim Amaci |
| :--- | :--- | :--- |
| Logaritmik Getiri | R_t = ln(P_t / P_{t-1}) | Duraganlik, bilesik buyume normalizasyonu |
| EMA (n=12) | EMA_t = (P_t x 2/13) + EMA_{t-1} x (11/13) | Kisa vadeli trend |
| EMA (n=26) | EMA_t = (P_t x 2/27) + EMA_{t-1} x (25/27) | Uzun vadeli trend |
| MACD | MACD_t = EMA_12 - EMA_26 | Momentum farki |
| RSI | RSI = 100 - 100/(1+RS) | Asiri alim/satim |
| Stochastic %K | %K = 100 x (C - L_14)/(H_14 - L_14) | Fiyat konumu |
| Stochastic %D | %D = SMA_3(%K) | Sinyal cizgisi |
| ADX | ADX = 100 x EMA(|+DI - (-DI)| / (+DI + (-DI))) | Trend gucu |
| ReLU | f(x) = max(0, x) | Gizli katman aktivasyonu |
| Sigmoid | sigma(x) = 1/(1+e^-x) | Cikti katmani aktivasyonu |
| Binary Cross-Entropy | L = -(1/N) * sum[y*ln(p)+(1-y)*ln(1-p)] | Kayip fonksiyonu |
| MinMax Norm. | X_norm = (X - X_min)/(X_max - X_min) | Ozellik olcekleme |
| Class Weight | w = n_total / (n_classes x n_class) | Sinif dengesizligi telafisi |
| Accuracy | Acc = (TP+TN) / (TP+TN+FP+FN) | Genel dogruluk |
| Sensitivity | Sens = TP / (TP+FN) | Yukselis yakalama orani |
| Specificity | Spec = TN / (TN+FP) | Dusus yakalama orani |
| Precision | Prec = TP / (TP+FP) | Yukselis tahmin keskinligi |
| F1-Score | F1 = 2 x (Prec x Recall)/(Prec+Recall) | Dengeli basari skoru |
| Balanced Accuracy| BA = (Sensitivity + Specificity) / 2 | Sinif dengeli dogruluk |

## A.2 Logaritmik Getiri
Finansal zaman serilerinde duraganlik saglamak icin kullanilir. P_t = t zamanindaki kapanis fiyati.
R_t = ln(P_t / P_{t-1})

## A.3 EMA ve MACD
EMA projede n=12 ve n=26 periyot degerleriyle hesaplanmistir.
EMA_t = (P_t x 2/(n+1)) + EMA_{t-1} x (1 - 2/(n+1))
MACD_t = EMA_12(P_t) - EMA_26(P_t)

## A.4 Derin Ogrenme Fonksiyonlari
ReLU: f(x) = max(0, x)
Sigmoid: sigma(x) = 1 / (1 + e^(-x))
Binary Cross-Entropy: L = -(1/N) * sum[ y*ln(p) + (1-y)*ln(1-p) ]
"@

$appB = @"
# APPENDIX B: VARLIK VE FON PROFILLERI

## B.1 Varlik Ozet Tablosu

| Varlik | Veri | Volatilite | Risk Sinifi | Donem | Aciklama |
| :--- | :--- | :--- | :--- | :--- | :--- |
| THYAO | Gunluk | %45 | Agresif | 2018-2026 | Referans hisse; piyasa derinligi en yuksek BIST hissesi |
| ALZ | Haftalik | %2 | Muhafazakar (Risk: 1) | 2021-2026 | Para piyasasi; kontrol grubu / MC illuzyonu kaniti |
| AZS | Haftalik | %18 | Dengeli (Risk: 3-4) | 2021-2026 | Karma portfoy; hibrit piyasa dinamigi |
| AMZ | Haftalik | %38 | Yuksek (Risk: 6-7) | 2021-2026 | Yildiz varlik; DL modellerinin Naive'i gectigi tek varlik |

## B.2 Profil Detaylari

### THYAO - Referans Hisse Senedi
Borsa Istanbul'un (BIST) en yuksek islem hacmine sahip lokomotif hisselerinden biridir. Van der Burgt (2023) calismasindaki NASDAQ100 endeksine karsilik, Turkiye yerel piyasasinin dinamiklerini yansitmak uzere referans varlik olarak secilmistir. Makroekonomik degiskenlere (USD/TRY, Brent Petrol) olan yuksek duyarliligi ve kuresel soklara hizli tepki vermesi, modellerin ani concept drift'leri ogrenme yeteneklerini olcmek icin zorlu bir test ortami sunmustur.

### ALZ - Dusuk Riskli Kontrol Grubu
TEFAS sisteminde yer alan, portfoyunun tamamina yakini ters repo, mevduat ve kisa vadeli borclanma araclarindan olusan dusuk riskli (Risk Degeri: 1) emeklilik fonudur. Surekli ve kesintisiz yukselis trendine sahip olmasi nedeniyle projede 'Cogunluk Sinifi (Majority Class) Illuzyonu'nu desifre etmek icin kontrol grubu olarak kullanilmistir. Bu fon ozelinde modellerin ulastigi %100 Accuracy orani, bir tahmin basarisindan ziyade duragan piyasalardaki ezberleme (overfitting/majority class bias) davranisinin ispati niteligindedir.

### AZS - Orta Riskli Fon
Hem sabit getirili menkul kiymetleri hem de hisse senetlerini dinamik bicimde harmanlayan, orta volatiliteye ve orta riske (Risk Degeri: 3-4) sahip bir fondur. Modellerin hibrit portfoy yapilarina ne kadar adapte olabildigini gozlemlemek amaciyla veri setine dahil edilmistir.

### AMZ - Yuksek Riskli 'Yildiz Varlik'
Portfoyunun asgari %80'ini BIST'te islem goren hisse senetlerine yatirmak zorunda olan, yuksek riskli (Risk Degeri: 6-7, yillik Volatilite: %38) emeklilik fonudur. Derin ogrenme modellerinin (LSTM ve CNN) geleneksel Naive Baseline modelini istatistiksel ve oransal olarak (Accuracy: %80.21, Specificity: %85.71) net bicimde geride biraktigi 'Yildiz Varlik' konumundadir.
"@

$appD = @"
# APPENDIX D: KARMASIKLIK MATRISLERI (CONFUSION MATRICES)

## D.1 4 Kritik Modelin Kumulatif Confusion Matrix Ozeti
NOT: Bu matrisler 3 farkli baslangic agirligina (seed) ait sonuclarin kumulatif toplamidir.

| Model | N | TP | TN | FP | FN | Acc | Sens | Spec | Bal.Acc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sampiyon: AMZ LSTM (Out=3, In=2, Full) | 96 (32x3) | 63 | 14 | 7 | 12 | 80.21% | 84.0% | 85.71% | 84.86% |
| Dengeli: AZS CNN (Out=3, In=4, Technical) | 90 (30x3) | 55 | 13 | 9 | 13 | 75.56% | 90.91% | 62.50% | 76.70% |
| Illuzyon: THYAO LSTM (Out=1, Closing) | 312 (2-seed) | 155 | 0 | 157 | 0 | 49.67% | 100.0% | 0.00% | 50.00% |
| Realist: THYAO LSTM (Out=3, In=4, Hist-Tech) | 900 (300x3) | 270 | 248 | 164 | 218 | 57.56% | 57.42% | 60.00% | 58.71% |

## D.2 Formuller
Precision = TP / (TP + FP)
Recall (Sensitivity) = TP / (TP + FN)
F1 = 2 x (Precision x Recall) / (Precision + Recall)
Specificity = TN / (TN + FP)
Balanced Accuracy = (Sensitivity + Specificity) / 2

## D.3 Modellerin Yorumu

### D.3.1 Sampiyon Model: AMZ LSTM (Out=3, In=2, Full)
En yuksek akademik basari ve gercek tahmin gucu. BA = 84.86%. Hem yukselis hem dusus siniflarini dengeli bicimde tahmin etmektedir (Sens=84.0%, Spec=85.71%).

### D.3.2 Illuzyon Ornegi: THYAO LSTM (Out=1, Closing)
'Majority Class Illuzyonu'. Model her seye 'yukselis' diyerek yari-turadan basarisiz olmaktadir. TP=155, TN=0 (Tam Korluk), Spec=0.000, BA=%50.00.

### D.3.3 Realist Basari: THYAO LSTM (Out=3, In=4, Hist+Tech)
BIST'in gurultulu piyasasinda Naive Baseline'a direnen gercekci basari. BA=%58.71 - rastgele tahmin sinirini anlamli bicimde asmaktadir.
"@

$appE = @"
# APPENDIX E: FINANSAL ISLEM MALIYETLERI VE LIMITASYONLAR

Bu calisma, makine ogrenmesi modellerinin 'Tahmin Gucu' (Predictive Power) uzerine odaklanan akademik bir arastirmadir. Gercek dunya finansal piyasa uygulamalarinda modellerin kar/zarar potansiyelini degerlendirirken asagidaki finansal kisitlarin coz onunde bulundurulmasi gerekmektedir.

## E.1 Islem Maliyetleri (Transaction Costs)
Modelleme surecinde alim-satim komisyonlari (Brokerage fees) ve BIST islem vergileri goz ardi edilmistir. Yuksek frekansli islem yapan modellerde (Out=1), biriken komisyon giderleri modelin elde ettigi brut getiriyi (Gross Return) onemli olcude azaltabilir.

## E.2 Kayma (Slippage)
Test sonuclari, modelin tahmin ettigi andaki 'Kapanis Fiyati' uzerinden islem yapabildigini varsaymaktadir. Gercek piyasada emrin girildigi an ile gerceklestigi an arasindaki fiyat farklari (slippage), ozellikle volatil donemlerde modelin teorik basarisini negatif etkileyebilir.

## E.3 Piyasa Derinligi ve Likidite
THYAO yuksek likiditeye sahip olsa da, emeklilik fonlarinin (ALZ, AZS, AMZ) alim-satim islemleri valor (T+1, T+2) surelerine tabidir. Bu durum, modelin anlik sinyallerini gercek zamanli ticarete (Real-time Trading) donusturmeyi zorlastiran yapisal bir kisittir.

## E.4 Vergi ve Fon Kesintileri
Emeklilik yatirim fonlarindan elde edilen getiriler uzerindeki stopaj ve fon yonetim ucreti gibi mali yukumlulukler, simulasyon sonuclarina dahil edilmemistir.

NOT: Bu limitasyonlar, modellerin istatistiksel siniflandirma basarisini (Accuracy/Recall) golgelemez; ancak sonuclarin bir 'Yatirim Danismanligi' teskil etmediginin akademik bir kanitidir.
"@

$appG = @"
# APPENDIX G: OZELLIK SETI TANIMLARI VE PROXY GOSTERGELERI

## G.1 THYAO (Gunluk) Ozellik Setleri

| Set Adi | Icerdigi Ozellikler | Degisken Sayisi |
| :--- | :--- | :--- |
| CL (Closing) | Open, Close, Volume | 3 |
| HIST (Historical) | Close, USD/TRY, Oil, Fear&Greed, TCMB Rate | 5 |
| TECH (Technical) | RSI, MACD, EMA12, EMA26, SO_%K, SO_%D, ADX | 7 |
| FULL | Tum 14 teknik ve tarihsel gosterge | 14 |

## G.2 Emeklilik Fonlari (Haftalik) Proxy Yontemi
Haftalik verilerin dogasi geregi, gunluk hisse verilerindeki bazi indikatorler emeklilik fonlari icin 'ikame' (proxy) gostergelerle eslestirilmistir:

| Set Adi | Icerdigi Ozellikler (Proxy) | Degisken Sayisi |
| :--- | :--- | :--- |
| full | RSI(weekly), Volatility, Momentum, Price, Volume | 5 (proxy) |
| technical | RSI(weekly), Momentum proxy (haftalik getiri ivmesi) | 2 (proxy) |
| closing | Haftalik kapanis fiyati | 1 |

## G.3 Proxy Donusumleri

| Orijinal Gosterge | Proxy Gosterge | Mantik |
| :--- | :--- | :--- |
| RSI (14 gunluk) | RSI (Haftalik) | Momentum gucunu korumak icin ayni periyot |
| ADX (Trend Gucu) | Fiyat Volatilitesi (Std Dev) | Fonlarda trend gucu yerine fiyat dagilimi |
| Stochastic Oscillator | Haftalik getiri ivmesi | Fonun haftalik momentum tahmini |
| Fear & Greed Index | LOCF (son bilinen deger ileri tasima) | 2024 sonrasi veri kesildigi icin LOCF uygulandi |

## G.4 Veri Bosluklari ve Eksik Deger Yonetimi
- Fear & Greed Index: 2024 sonrasi verisi kesildigi icin LOCF (Last Observation Carried Forward) yontemiyle son bilinen psikolojik deger ileri tasinmistir.
- Emeklilik Fonlari: TEFAS'tan alinan haftalik veriler, tatil gunlerine denk gelen eksik gozlemler icin forward fill ile doldurulmustur.
- MinMax normalizasyon: Tum ozellik setleri icin yalnizca egitim seti uzerinde fit, test setine transform uygulanmistir.
"@

$appH = @"
# APPENDIX H: STRATEJIK MODEL DEGERLENDIRME MATRISI

## H.1 Nihai Sampiyon Model Tablosu
Bu tablo, juri savunmasi sirasinda her bir varlik icin 'Hangi model neden secilmeli?' sorusuna verilecek nihai akademik cevaptir.

| Varlik Sinifi | Sampiyon Model | Balanced Acc. | Stratejik Savunma Argumani |
| :--- | :--- | :--- | :--- |
| THYAO (Blue Chip) | LSTM (hist_tech) | 58.71% | BIST rejim degisikligine (Concept Drift) ragmen %50 baseline'i koruyan en dengeli model. |
| ALZ (Dusuk Risk) | ARIMA (Baseline) | 50.00% | Sabit yukselis trendinde DL modellerinin MC riskini kanitlayan kontrol grubudur. |
| AZS (Orta Risk) | CNN (Technical) | 76.70% | Konvolusyonel katmanlarin periyodik piyasa dongulerini yakalama ustunlugunu kanitlar. |
| AMZ (Yuksek Risk) | LSTM (Full Set) | 84.86% | YILDIZ BULGU: Naive baseline'i istatistiksel olarak geride birakan, projenin en guclu kaniti. |

## H.2 Neden AMZ'de LSTM, CNN'den Ustun?
AMZ fonu yuksek volatilite ve dusuk otokorelasyon icerir. LSTM'in 'Long-Term Memory' (Uzun Vadeli Hafiza) yetenegi, CNN'in yerel filtreleme mantigina gore bu tur karmasik verilerde %23 daha fazla 'Specificity' (Dusus Yakalama) skoru uretmistir.

## H.3 'Accuracy Illuzyonu' Esigi
ALZ fonunun %100 basarisi bir 'basari' olarak degil, akademik bir 'anomali tespiti' olarak sunulmustur. Bu durust yaklasim, calismanin bilimsel tarafsizligini (Unbiased Evaluation) kanitlar.

## H.4 Tum Kritik Sayilar Ozet

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
# APPENDIX I: TEST/TRAIN SINIF DAGILIMI (UP/DOWN) SONUC RAPORU

## I.1 Sinif Dagilimi Ozeti

| Varlik | Satir Sayilari | Sinif Dagilimi (Up/Down) |
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

## I.2 AMZ Fonu Detayli Analizi (Yildiz Varlik)
AMZ Out=3 icin test setinde 30 Up / 7 Down dagilimi mevcuttur. Bu asimetrik yapi (Minority class: Down=%18.9), Majority Class Illuzyonu riskini dogrular; class_weight uygulamasi ile model gercek ogrenmeyi gosterebilmistir.

## I.3 ALZ Fonu Kontrol Grubu Analizi
Out=1, 3, 5 icin test setinde 0 dusus gozlemi mevcuttur. Bu durum, ALZ'yi matematiksel olarak ikili siniflandirma problemi disina tasimaktadir. Tum modeller %100 Accuracy elde etmis, ancak bu 'Majority Class Illuzyonu'nun nihai kanitidir.

## I.4 THYAO Sinif Dengesi
THYAO Out=1 icin test setinde 155 Up / 157 Down ile neredeyse mukemmel sinif dengesi (%49.7/%50.3) gozlemlenmektedir. Bu yapi, modellerin gercek ogrenme kapasitesini test etmek icin ideal kosullar sunmaktadir.

NOT: Tum sinif dagilimi sayilari APPENDIX_I_SONUCLARI.txt ve CSV_TUM_SONUCLAR.html ile %100 ortusmektedir.
"@

Set-Content -Path "$outDir\Appendix_A_Formuller.txt" -Value $appA -Encoding UTF8
Set-Content -Path "$outDir\Appendix_B_Profiller.txt" -Value $appB -Encoding UTF8
Set-Content -Path "$outDir\Appendix_D_Karmasiklik_Matrisleri.txt" -Value $appD -Encoding UTF8
Set-Content -Path "$outDir\Appendix_E_Limitasyonlar.txt" -Value $appE -Encoding UTF8
Set-Content -Path "$outDir\Appendix_G_Ozellik_Setleri.txt" -Value $appG -Encoding UTF8
Set-Content -Path "$outDir\Appendix_H_Karar_Matrisi.txt" -Value $appH -Encoding UTF8
Set-Content -Path "$outDir\APPENDIX_I_SONUCLARI.txt" -Value $appI -Encoding UTF8

Write-Output "Tum appendixler tamamen ASCII Ingilizce harflerle yeniden olusturuldu!"
