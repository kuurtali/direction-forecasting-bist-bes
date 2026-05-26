$outDir = "C:\Users\Kurt\Desktop\Proje\03_Appendix"

$appA = @"
# APPENDIX A: TEKNİK GÖSTERGELER VE MATEMATİKSEL ALTYAPI (TECHNICAL INDICATORS)

Bu çalışmada, modellerin özellik setlerini oluşturmak amacıyla 14 farklı finansal ve teknik gösterge kullanılmıştır. Temel göstergeler şunlardır:
1. Logaritmik Getiri (Log-Return)
2. Basit Hareketli Ortalama (SMA) ve Üstel Hareketli Ortalama (EMA)
3. Göreceli Güç Endeksi (RSI)
4. MACD ve Sinyal Çizgisi
5. Stokastik Osilatör (SO_K, SO_D)
6. Ortalama Yönsel Endeks (ADX)
7. Bollinger Bantları
"@

$appB = @"
# APPENDIX B: VARLIK VE FON PROFİLLERİ (ASSET AND FUND PROFILES)

Bu çalışmada 4 farklı finansal varlık seçilmiştir:
1. Türk Hava Yolları A.O. (THYAO) - Referans Hisse Senedi
2. ALZ - Düşük Riskli Para Piyasası Fonu: Sürekli yükseliş trendi sergiler. Majority Class (Çoğunluk Sınıfı) zafiyetlerini test etmek için bir laboratuvar olarak kullanılmıştır.
3. AZS - Orta Riskli Fon: Kısmi varyanslı orta risk düzeyi.
4. AMZ - Yüksek Riskli Fon: Derin öğrenme modellerinin gerçek gücünün (Predictive Power) test edildiği, dengeli sınıf dağılımına sahip ana hedef fondur.
"@

$appD = @"
# APPENDIX D: KARMAŞIKLIK MATRİSLERİ (CONFUSION MATRICES)

Bu bölüm stratejik modellerin tahmin performansını özetler. Balanced Accuracy (Dengeli Doğruluk) metriği ile sınıf dengesizliklerinin önüne geçilmiştir.

AMZ LSTM Master Result (N=96 Havuzu Kümülatif):
- Doğruluk Oranı (Accuracy): %80.21
- Özgüllük (Specificity / Düşüşü Bilme Oranı): %85.71
- Toplam Havuz TP İsabet: 77 / 96 Doğru Tahmin.
"@

$appE = @"
# APPENDIX E: FİNANSAL İŞLEM MALİYETLERİ VE LİMİTASYONLAR (TRANSACTION COSTS)

Bu çalışma makine öğrenmesi modellerinin akademik "Tahmin Gücü" üzerine odaklanmıştır. Finansal kısıtlar şu şekildedir:
1. İşlem Maliyetleri (Transaction Costs): Komisyonlar göz ardı edilmiştir.
2. Kayma (Slippage): Gerçekleşme anı fiyat kaymaları teorik olarak dikkate alınmamıştır.
3. Piyasa Derinliği ve Likidite: Emeklilik fonlarının T+1 ve T+2 valör süreleri, anlık alım satımı kısıtlayan bir bariyerdir ve modeller simülasyon olarak tasarlanmıştır.
"@

$appG = @"
# APPENDIX G: ÖZELLİK SETLERİ VE GÖSTERGE KARŞILIKLARI

G.1. THYAO (Günlük Veri Setleri):
- CL (Closing): Sadece Fiyat (Open, Close, Volume)
- HIST (Historical): Makro Veriler (USD/TRY, Oil, Fear&Greed, TCMB Rate)
- TECH (Technical): Teknik Göstergeler (RSI, MACD, EMA, ADX vb.)
- FULL: Tüm teknik ve tarihsel göstergelerin bileşimi.

G.2. Emeklilik Fonları (Haftalık Veri Seti İkameleri):
- Günlük RSI (14) -> Haftalık RSI olarak adapte edilmiştir.
- ADX (Trend Gücü) -> Haftalık Volatiliteye (Standart Sapma) dönüştürülmüştür.
- Stokastik Osilatör -> Haftalık fiyatsal momentum ile ikame edilmiştir.
"@

$appH = @"
# APPENDIX H: STRATEJİK MODEL KARŞILAŞTIRMA VE KARAR MATRİSİ

| Varlık | Champion Model | Balanced Acc | Stratejik Savunma Argümanı |
|---|---|---|---|
| THYAO | LSTM (hist_tech) | %58.71 | BIST rejim değişimlerine (Concept Drift) karşı %50 baseline'ı koruyabilen en dengeli modeldir. |
| ALZ | ARIMA (Baseline) | %50.00 | Sürekli yükseliş trendinde DL modellerinin "aşırı öğrenme" (Majority Class) riskini kanıtlayan kontrol grubudur. |
| AZS | CNN (Technical) | %76.70 | Konvolüsyonel katmanların lokal periyodik piyasa döngülerini yakalama üstünlüğünü kanıtlamıştır. |
| AMZ | LSTM (Full Set) | %84.86 | Naive baseline'ı istatistiksel olarak geride bırakan, projenin en güçlü ve kırılmaz tahmin kanıtıdır. |
"@

$appI = @"
# APPENDIX I: TEST/TRAIN SINIF DAĞILIMI (UP/DOWN)

Modellerin çoğunluk sınıfı (Majority Class) eğilimlerini anlamak için referans 5 günlük (Out=5) test havuzu dağılımları:

- THYAO Test: 163 Yükseliş, 145 Düşüş (%52.9 Yükseliş Eğilimi - Oldukça Dengeli)
- ALZ Test: 33 Yükseliş, 0 Düşüş (%100.0 Yükseliş Eğilimi - Tamamen Çarpık, MC Tuzağı)
- AZS Test: 29 Yükseliş, 6 Düşüş (%82.9 Yükseliş Eğilimi)
- AMZ Test: 29 Yükseliş, 6 Düşüş (%82.9 Yükseliş Eğilimi)

Akademik Not: Yukarıdaki oranlar, ALZ fonunda Accuracy'nin neden %100'e kilitlendiğini (çünkü düşüş ihtimali sıfır) matematiksel olarak açıklamaktadır.
"@

Set-Content -Path "$outDir\Appendix_A_Formuller.txt" -Value $appA -Encoding UTF8
Set-Content -Path "$outDir\Appendix_B_Profiller.txt" -Value $appB -Encoding UTF8
Set-Content -Path "$outDir\Appendix_D_Karmasiklik_Matrisleri.txt" -Value $appD -Encoding UTF8
Set-Content -Path "$outDir\Appendix_E_Limitasyonlar.txt" -Value $appE -Encoding UTF8
Set-Content -Path "$outDir\Appendix_G_Ozellik_Setleri.txt" -Value $appG -Encoding UTF8
Set-Content -Path "$outDir\Appendix_H_Karar_Matrisi.txt" -Value $appH -Encoding UTF8
Set-Content -Path "$outDir\APPENDIX_I_SONUCLARI.txt" -Value $appI -Encoding UTF8

Write-Output "Tum 03 Appendix dosyalari bozuk karakterlerden arindirilarak temiz UTF-8 formunda baştan yaratildi!"
