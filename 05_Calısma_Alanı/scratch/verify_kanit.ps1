$kanitRapor = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar\MC_KANIT_RAPORU.txt"
$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"

$lines = Get-Content $kanitRapor -Encoding UTF8
$currentMimar = ""
$errorCount=0
$successCount=0

foreach ($line in $lines) {
    if ($line -match "# ESKI THYAO LSTM") { $currentMimar = "LSTM_sonuclar_FINAL_eski.csv" }
    elseif ($line -match "# ESKI THYAO CNN") { $currentMimar = "CNN_sonuclar_FINAL_eski.csv" }
    elseif ($line -match "# GUNCEL THYAO LSTM") { $currentMimar = "LSTM_sonuclar_FINAL.csv" }
    elseif ($line -match "# GUNCEL THYAO CNN") { $currentMimar = "CNN_sonuclar_FINAL.csv" }
    # other models similarly...
    
    if ($line -match "(hist_tech|technical|historical|closing|full)\s+In=(\d) Out=(\d)\s+Acc=([\d\.]+)") {
        $feat = $matches[1]
        $in = $matches[2]
        $out = $matches[3]
        $acc = $matches[4]
        
        # Sadece THYAO'da _FINAL.csv var, digerlerinde isim formatı degisik (ornek EMEKLILIK_LSTM_sonuclar.csv)
        # Ama THYAO final dosyalarinda direk aratabiliriz. Eger currentMimar atanmissa:
        if ($currentMimar -ne "") {
            $csvPath = (Get-ChildItem -Path $baseDir -Recurse -Filter $currentMimar | Select-Object -First 1).FullName
            if ($csvPath) {
                # hizli kontrol
                $content = [System.IO.File]::ReadAllText($csvPath)
                if ($content -match $acc) {
                    $successCount++
                } else {
                    Write-Output "HATA: $feat In=$in Out=$out Acc=$acc ($currentMimar icinde bulunamadi)"
                    $errorCount++
                }
            }
        }
    }
}
Write-Output "Dogrulama Tamamlandi. Basarili: $successCount, Hata: $errorCount"
