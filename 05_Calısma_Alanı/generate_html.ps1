$htmlPath = Get-ChildItem -Path "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1
$baseDir = Split-Path $htmlPath

$htmlContent = @"
<!DOCTYPE html>
<html lang='tr'>
<head>
<meta charset='UTF-8'>
<title>Akademik Kanitlar - Tum CSV Sonuclari</title>
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f9fa; padding: 30px; color: #333; margin: 0; }
h1 { text-align: center; color: #1a202c; font-size: 2.2rem; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 1px; }
.folder { margin-bottom: 50px; background: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
h2 { color: #2d3748; border-bottom: 3px solid #3182ce; padding-bottom: 10px; font-size: 1.8rem; margin-top: 0; }
h3 { color: #c53030; margin-top: 30px; font-size: 1.4rem; border-left: 4px solid #c53030; padding-left: 10px; }
.table-responsive { overflow-x: auto; margin-top: 15px; border-radius: 8px; box-shadow: 0 0 0 1px rgba(0,0,0,0.05); }
table { width: 100%; border-collapse: collapse; font-size: 13px; white-space: nowrap; }
th, td { border: 1px solid #e2e8f0; padding: 10px 15px; text-align: center; }
th { background-color: #ebf8ff; color: #2b6cb0; font-weight: 600; position: sticky; top: 0; }
tr:nth-child(even) { background-color: #f7fafc; }
tr:hover { background-color: #edf2f7; transition: background-color 0.2s; }
.na-val { color: #a0aec0; font-style: italic; }
</style>
</head>
<body>
<h1>AKADEM&Icirc;K KANITLAR - K&Uuml;M&Uuml;LAT&Icirc;F (N=96) KONSOL&Icirc;DASYON RAPORU</h1>
"@

function ParseCsvToHtml($filePath) {
    # Import-Csv automatically assigns generic header names if needed, removing any encoding risk
    $data = Import-Csv -Path $filePath -Encoding Default
    if (-not $data -or $data.Count -eq 0) { return "<p>Tablo verisi bos.</p>" }
    
    $headers = $data[0].psobject.properties | Select-Object -ExpandProperty Name
    
    $html = "<div class='table-responsive'><table><thead><tr>"
    foreach ($h in $headers) { 
        $html += "<th>$h</th>" 
    }
    $html += "</tr></thead><tbody>"
    
    foreach ($row in $data) {
        $html += "<tr>"
        foreach ($h in $headers) {
            $val = $row.$h
            if ([string]::IsNullOrWhiteSpace($val) -or $val -eq "NA") {
                $html += "<td class='na-val'>NA</td>"
            } else {
                $html += "<td>$val</td>"
            }
        }
        $html += "</tr>"
    }
    
    $html += "</tbody></table></div>"
    return $html
}

# 2018-2022 klasöru
$htmlContent += "`n<div class='folder'><h2>Klas&ouml;r: 2018-2022</h2>"
$csvs_eski = Get-ChildItem $baseDir -Recurse -Filter "*_eski.csv" | Sort-Object Name
foreach ($csv in $csvs_eski) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    $htmlContent += "<h3>$($csv.Name)</h3>"
    $htmlContent += ParseCsvToHtml $csv.FullName
}
$htmlContent += "</div>"

# 2018-2026 klasöru
$htmlContent += "`n<div class='folder'><h2>Klas&ouml;r: 2018-2026</h2>"
$csvs_yeni = Get-ChildItem $baseDir -Recurse -Filter "*.csv" | Where-Object { $_.Name -notmatch "_eski.csv" } | Sort-Object Name
foreach ($csv in $csvs_yeni) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    $htmlContent += "<h3>$($csv.Name)</h3>"
    $htmlContent += ParseCsvToHtml $csv.FullName
}
$htmlContent += "</div></body></html>"

[System.IO.File]::WriteAllText($htmlPath, $htmlContent, [System.Text.Encoding]::UTF8)
Write-Output "HTML generated successfully without encoding errors."
