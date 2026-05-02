# data/

Bu klasör, scriptlerin beklediği yerel veri dosyaları içindir. **Telifli/dış kaynaklı veriler bu repoya commit edilmez** (bkz. `.gitignore`).

## Beklenen dosyalar

### `ALZ_AZS_AMZ_Haftalik.xlsx`

TEFAS sisteminden manuel olarak indirilen haftalık emeklilik fonu fiyat verisi.

**Beklenen kolonlar (sırasıyla):**

| # | Kolon | Açıklama |
|---|---|---|
| 1 | `Date` | Hafta tarihi |
| 2 | `Price_ALZ` | ALZ fonu kapanış fiyatı |
| 3 | `LogReturn_ALZ` | ALZ logaritmik getiri |
| 4 | `Price_AZS` | AZS fonu kapanış fiyatı |
| 5 | `LogReturn_AZS` | AZS logaritmik getiri |
| 6 | `Price_AMZ` | AMZ fonu kapanış fiyatı |
| 7 | `LogReturn_AMZ` | AMZ logaritmik getiri |

**Tarih aralığı:** 2021-04 → 2026-04 (haftalık)

**Fonlar:**

| Fon | Açıklama | Risk profili |
|---|---|---|
| ALZ | Allianz Yaşam Para Piyasası Emeklilik Yatırım Fonu | Düşük |
| AZS | Allianz Yaşam Karma Emeklilik Yatırım Fonu | Orta |
| AMZ | Allianz Yaşam Hisse Senedi Ağırlıklı Emeklilik Yatırım Fonu | Yüksek |

### Nasıl indirilir?

1. https://www.tefas.gov.tr/FonAnaliz.aspx adresine gidin
2. Sırasıyla ALZ, AZS, AMZ fonlarını sorgulayın
3. Tarih aralığını 2021-04 / 2026-04 olarak ayarlayın
4. CSV/Excel olarak indirin
5. Üç fonu yukarıdaki kolon yapısına göre tek bir Excel dosyasında birleştirin
6. Bu klasöre `ALZ_AZS_AMZ_Haftalik.xlsx` adıyla kaydedin

## İnternet üzerinden çekilen veriler

Aşağıdaki veri kaynakları script çalışırken otomatik indirilir, dosya olarak saklamanız gerekmez:

| Veri | R kaynağı |
|---|---|
| THYAO günlük fiyat | `quantmod::getSymbols("THYAO.IS")` |
| USD/TRY günlük | `quantmod::getSymbols("USDTRY=X")` |
| WTI petrol günlük | `quantmod::getSymbols("CL=F")` |
| TCMB politika faizi | `quantmod::getSymbols("INTDSRTRM193N", src = "FRED")` |
| Fear & Greed indeks | `gman4774/Fear_and_Greed_Index` GitHub mirror |

İnternet erişimi yoksa script ilgili veriyi atlar (uyarı verir) ve devam eder.
