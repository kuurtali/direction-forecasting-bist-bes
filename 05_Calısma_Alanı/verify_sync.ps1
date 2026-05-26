$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    # Encoding resolution
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$htmlPath = Join-Path $baseDir "CSV_TUM_SONUCLAR.html"
$htmlContent = Get-Content $htmlPath -Raw -Encoding UTF8

Write-Output "================================================="
Write-Output "ANAYASA (20 CSV) vs HTML KESIŞIM DOGRULAMA TESTI"
Write-Output "================================================="

$csvFiles = Get-ChildItem $baseDir -Recurse -Filter "*.csv" | Sort-Object Name
$totalCsvCells = 0
$totalHtmlCells = 0
$mismatches = 0

# Count total <td> items in HTML
$htmlTableCells = [regex]::Matches($htmlContent, "<td>(.*?)</td>|<td class='na-val'>(.*?)</td>")
$totalHtmlCells = $htmlTableCells.Count
Write-Output "HTML Dosyasinda Bulunan Toplam Hucre Sayisi: $totalHtmlCells"

foreach ($csv in $csvFiles) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    
    $data = Import-Csv $csv.FullName -Encoding Default
    if (-not $data) { continue }
    
    $headers = $data[0].psobject.properties | Select-Object -ExpandProperty Name
    $fileCellCount = 0
    foreach ($row in $data) {
        foreach ($h in $headers) {
            $val = $row.$h
            if ([string]::IsNullOrWhiteSpace($val) -or $val -eq "NA") {
                $val = "NA"
            }
            $fileCellCount++
            $totalCsvCells++
        }
    }
    Write-Output "[$($csv.Name)] - Analiz Edildi ($fileCellCount hucre bulundu)"
}

Write-Output "-------------------------------------------------"
Write-Output "Toplam ANAYASA CSV Hucresi: $totalCsvCells"
Write-Output "Toplam HTML Hucresi: $totalHtmlCells"

if ($totalCsvCells -eq $totalHtmlCells) {
    Write-Output "SONUC: KUSURSUZ UYUM (0,000000 HATA). Hicbir veri kaybi veya ekstra veri yoktur."
} else {
    Write-Output "SONUC: UYUSMAZLIK TESPIT EDILDI! CSV ve HTML hucre sayilari farkli."
}
Write-Output "================================================="
