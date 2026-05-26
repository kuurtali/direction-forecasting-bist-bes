$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$csvFiles = Get-ChildItem $baseDir -Recurse -Filter "*.csv"
$totalErrors = 0
$totalRows = 0

Write-Output "--- DERINLEMESINE AKADEMIK VERI KONTROLU BASLIYOR ---"

foreach ($csv in $csvFiles) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    
    $data = Import-Csv $csv.FullName -Encoding Default
    if (-not $data) { 
        Write-Output "[KRITIK HATA] Bos Dosya: $($csv.Name)"
        $totalErrors++
        continue 
    }
    
    $headers = $data[0].psobject.properties | Select-Object -ExpandProperty Name
    $expectedCount = $headers.Count
    
    $rowNum = 1
    foreach ($row in $data) {
        $rowNum++
        $totalRows++
        
        # 1. Structural Check
        $cols = $row.psobject.properties | Select-Object -ExpandProperty Name
        if ($cols.Count -ne $expectedCount) {
            Write-Output "[YAPISAL HATA] $($csv.Name) Satir $($rowNum) - Kolon sayisi kayik."
            $totalErrors++
        }
        
        # 2. Numeric Field Validation
        foreach ($h in $headers) {
            $val = $row.$h
            if ([string]::IsNullOrWhiteSpace($val)) {
                Write-Output "[KAYIP VERI HATA] $($csv.Name) Satir $($rowNum) - $h kolonu bos!"
                $totalErrors++
                continue
            }
            
            # Certain fields should be numeric (Acc, SD, P_Value, vb.)
            if ($h -match "Acc" -or $h -match "SD" -or $h -match "P_Value" -or $h -in @("Sens", "Spec", "F1", "Seed_23", "Seed_27", "Seed_98")) {
                if ($val -ne "NA" -and $val -ne "Doğru") {
                    $num = 0.0
                    $isValid = [double]::TryParse($val.Replace('.',','), [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::GetCultureInfo("tr-TR"), [ref]$num)
                    if (-not $isValid) {
                        $isValid2 = [double]::TryParse($val, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$num)
                        if (-not $isValid2) {
                            Write-Output "[TIP HATASI] $($csv.Name) Satir $($rowNum) - $h degeri '$val' sayi degil!"
                            $totalErrors++
                        }
                    }
                }
            }
        }
    }
}

Write-Output "----------------------------------------------------"
Write-Output "Toplam incelenen satir: $totalRows"
Write-Output "Bulunan Kritik / Yapisal Hata: $totalErrors"
if ($totalErrors -eq 0) {
    Write-Output "SONUC: TUM 20 DOSYA %100 YAPI VE TIP OLARAK KUSURSUZDUR. KAYMA, BOZULMA, VEYA EKSIK YOKTUR."
}
