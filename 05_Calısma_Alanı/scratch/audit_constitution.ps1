$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$csvFiles = Get-ChildItem $baseDir -Recurse -Filter "*.csv" | Sort-Object Name

# Tracking metrics
$totalChecked = 0
$errors = @()

foreach ($csv in $csvFiles) {
    if ($csv.Name -match "CSV_TUM_SONUCLAR") { continue }
    
    # Process only Deep Learning files that have Seeds
    if ($csv.Name -match "CNN" -or $csv.Name -match "LSTM") {
        $data = Import-Csv $csv.FullName -Encoding Default
        if (-not $data) { continue }
        
        $rowNum = 1
        foreach ($row in $data) {
            $rowNum++
            
            # Extract relevant columns
            $s23 = $row.Seed_23
            $s27 = $row.Seed_27
            $s98 = $row.Seed_98
            $meanStr = $row.Mean_Acc
            $sdStr = $row.SD
            $minStr = $row.Min_Acc
            $maxStr = $row.Max_Acc
            
            if ([string]::IsNullOrWhiteSpace($s23) -or $s23 -eq "NA") { continue }
            
            $v23 = [double]$s23
            $v27 = [double]$s27
            $v98 = [double]$s98
            $vMean = [double]$meanStr
            $vSD = [double]$sdStr
            $vMin = [double]$minStr
            $vMax = [double]$maxStr
            
            $totalChecked++
            
            # Check Min
            $actualMin = [Math]::Min($v23, [Math]::Min($v27, $v98))
            if ([Math]::Abs($actualMin - $vMin) -gt 0.0001) {
                $errors += "[$($csv.Name) Satir $rowNum] Min Hatasi: Dosya=$vMin, Gercek=$actualMin"
            }
            
            # Check Max
            $actualMax = [Math]::Max($v23, [Math]::Max($v27, $v98))
            if ([Math]::Abs($actualMax - $vMax) -gt 0.0001) {
                $errors += "[$($csv.Name) Satir $rowNum] Max Hatasi: Dosya=$vMax, Gercek=$actualMax"
            }
            
            # Check Mean
            $actualMean = ($v23 + $v27 + $v98) / 3.0
            if ([Math]::Abs($actualMean - $vMean) -gt 0.0002) {
                $errors += "[$($csv.Name) Satir $rowNum] Mean Hatasi: Dosya=$vMean, Gercek=$actualMean (Tohumlar: $v23, $v27, $v98)"
            }
            
            # Check SD
            $sqDiff = [Math]::Pow($v23 - $actualMean, 2) + [Math]::Pow($v27 - $actualMean, 2) + [Math]::Pow($v98 - $actualMean, 2)
            $actualSD = [Math]::Sqrt($sqDiff / 2.0)
            if ([Math]::Abs($actualSD - $vSD) -gt 0.0002 -and $vSD -ne 0) {
                $errors += "[$($csv.Name) Satir $rowNum] SD Hatasi: Dosya=$vSD, Gercek=$actualSD (Tohumlar: $v23, $v27, $v98)"
            }
        }
    }
}

Write-Output "Toplam kontrol edilen Seed barindiran satir: $totalChecked"
if ($errors.Count -eq 0) {
    Write-Output "Hicbir matematiksel uyusmazlik bulunamadi. Tum Seed / Mean / SD / Min / Max bagintilari KUSURSUZ."
} else {
    Write-Output "Bulunan Hatalar ($($errors.Count) adet):"
    $errors | Select-Object -First 30 | ForEach-Object { Write-Output $_ }
    if ($errors.Count -gt 30) { Write-Output "... ve $($errors.Count - 30) daha." }
}
