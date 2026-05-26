$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$csvFiles = Get-ChildItem $baseDir -Recurse -Filter "*.csv"
$errors = 0
$totalRows = 0

foreach ($csv in $csvFiles) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    $data = Import-Csv $csv.FullName -Encoding Default
    if (-not $data) { continue }
    
    foreach ($row in $data) {
        $totalRows++
        # Common validities
        $cols = $row.psobject.properties | Select-Object -ExpandProperty Name
        if ("Sens" -in $cols -and $row.Sens -ne "NA") {
            $sens = [double]$row.Sens
            if ($sens -lt 0 -or $sens -gt 1) { Write-Output "Sens hatasi: $($csv.Name)"; $errors++ }
        }
        if ("Spec" -in $cols -and $row.Spec -ne "NA") {
            $spec = [double]$row.Spec
            if ($spec -lt 0 -or $spec -gt 1) { Write-Output "Spec hatasi: $($csv.Name)"; $errors++ }
        }
        if ("F1" -in $cols -and $row.F1 -ne "NA") {
            $f1 = [double]$row.F1
            if ($f1 -lt 0 -or $f1 -gt 1) { Write-Output "F1 hatasi: $($csv.Name)"; $errors++ }
        }
        if ("P_Value" -in $cols -and $row.P_Value -ne "NA") {
            $p = [double]$row.P_Value
            if ($p -lt 0 -or $p -gt 1) { Write-Output "P_Value hatasi: $($csv.Name)"; $errors++ }
        }
    }
}
Write-Output "Toplam satır kontrolü: $totalRows. Sınır dişi anomali sayısı (Fake metrik tespiti): $errors"
