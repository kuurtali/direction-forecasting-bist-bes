$ErrorActionPreference = "Stop"
$baseDir = "c:\Users\Kurt\Desktop\PROJE_ALL"
$csvDirs = @("$baseDir\2018-2022 çıktılar", "$baseDir\2018-2026 çıktılar")

$textFiles = @(
    "$baseDir\PROJE_RAPOR.txt",
    "$baseDir\PROJE_ADIMLAR.txt",
    "$baseDir\JURI_SAVUNMA_VE_BILINMESI_GEREKENLER.txt",
    "$baseDir\MAKALE_YAZIM_REHBERI.txt",
    "$baseDir\MAKALE_TASLAK_METODOLOJI.txt",
    "$baseDir\GRAFIK_VE_MATRIS_REHBERI.txt"
)

# 1. Gather all truth values from CSVs
$validNumbers = New-Object 'System.Collections.Generic.HashSet[string]'
# Common constants
@("0.0000", "1.0000", "100.00", "0.5000", "50.00", "0.00", "100", "0", "1", "2", "3", "4", "5", "6", "9", "10", "12", "13", "14", "15", "16", "23", "27", "98", "70", "15", "85", "36", "27", "262", "249", "261", "1425", "306", "13", "1225", "2037", "2026", "2018", "2022") | ForEach-Object { $validNumbers.Add($_) | Out-Null }

Write-Host "Scraping numbers from CSVs..."
foreach ($dir in $csvDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Filter "*.csv" | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            # Any sequence of digits with optional dot
            $matches = [regex]::Matches($content, "[0-9]+(\.[0-9]+)?")
            foreach ($m in $matches) {
                $val = $m.Value
                $validNumbers.Add($val) | Out-Null
                if ($val.Contains(".")) {
                    # Add variants
                    if ([double]::TryParse($val, [ref]$null)) {
                        $num = [double]$val
                        $validNumbers.Add($num.ToString("0.0000")) | Out-Null
                        $validNumbers.Add($num.ToString("0.00")) | Out-Null
                        $validNumbers.Add($num.ToString("0.0")) | Out-Null
                        $validNumbers.Add($num.ToString("0")) | Out-Null
                        
                        $p = $num * 100
                        $validNumbers.Add($p.ToString("0.00")) | Out-Null
                        $validNumbers.Add($p.ToString("0.0")) | Out-Null
                        $validNumbers.Add($p.ToString("0")) | Out-Null
                    }
                } else {
                     if ([double]::TryParse($val, [ref]$null)) {
                        $num = [double]$val
                        $p = $num / 100
                        $validNumbers.Add($p.ToString("0.0000")) | Out-Null
                        $validNumbers.Add($p.ToString("0.00")) | Out-Null
                         $validNumbers.Add($p.ToString("0.0")) | Out-Null
                     }
                }
            }
        }
    }
}

# Add known MC counts
@("9/36", "12/36", "8/36", "16/36", "14/36", "7/36", "27/27", "13/27", "9/27", "10/27", "15/27", "19/27", "12/27", "0/9", "1/9", "3/9", "5/9", "7/9", "9/9", "10/27") | ForEach-Object { $validNumbers.Add($_) | Out-Null }
# Add class balance (hardcoded since it's from R console output/Appendix)
@("49.9", "50.1", "45.5", "54.5", "44.4", "55.6", "0.857", "0.8571") | ForEach-Object { $validNumbers.Add($_) | Out-Null }

Write-Host "Database built with $($validNumbers.Count) valid metrics."
Write-Host "Commencing Line-by-Line Sweep..."

$report = @()

foreach ($txt in $textFiles) {
    if (-not (Test-Path $txt)) { continue }
    $lines = Get-Content $txt -Encoding UTF8
    for ($idx=0; $idx -lt $lines.Count; $idx++) {
        $line = $lines[$idx]
        
        # Match percentages like %74.30
        $matches = [regex]::Matches($line, "(?:%([0-9]{1,3}(?:\.[0-9]{1,2})?))|([0-9]{1,3}(?:\.[0-9]{1,2})?)%")
        foreach ($m in $matches) {
            $val = if ($m.Groups[1].Value) { $m.Groups[1].Value } else { $m.Groups[2].Value }
            $foundMatch = $false
            if ($validNumbers.Contains($val)) { $foundMatch = $true }
            else {
                $numVal = 0.0
                if ([double]::TryParse($val, [ref]$numVal)) {
                    foreach ($v in $validNumbers) {
                        $vNum = 0.0
                        if ([double]::TryParse($v, [ref]$vNum)) {
                            if ([math]::Abs($vNum - $numVal) -le 0.051) { $foundMatch = $true; break }
                        }
                    }
                }
            }
            if (-not $foundMatch -and $numVal -lt 2030 -and $numVal -gt 2010) { $foundMatch = $true }
            if (-not $foundMatch) {
                $report += [PSCustomObject]@{ File = ($txt | Split-Path -Leaf); Line = $idx+1; Type = "Percentage"; Value = "%$val"; Content = $line.Trim() }
            }
        }
        
        # Match raw floats
        $matches2 = [regex]::Matches($line, "(?:[^\d]|^)(0\.[0-9]{2,4})(?:[^\d]|$)")
        foreach ($m in $matches2) {
            $val = $m.Groups[1].Value
            $numVal = [double]$val
            $foundMatch = $false
            if ($validNumbers.Contains($numVal.ToString("0.0000")) -or $validNumbers.Contains($numVal.ToString("0.00"))) { $foundMatch = $true }
            else {
                foreach ($v in $validNumbers) {
                    if ([double]::TryParse($v, [ref]$vNum)) {
                        if ([math]::Abs($vNum - $numVal) -le 0.0011) { $foundMatch = $true; break }
                    }
                }
            }
            if (-not $foundMatch) {
                $report += [PSCustomObject]@{ File = ($txt | Split-Path -Leaf); Line = $idx+1; Type = "Float"; Value = $val; Content = $line.Trim() }
            }
        }
        
        # Match MC counts
        $matches3 = [regex]::Matches($line, "([0-9]{1,2}/[0-9]{2})")
        foreach ($m in $matches3) {
            $val = $m.Groups[1].Value
            if (-not $validNumbers.Contains($val)) {
                $report += [PSCustomObject]@{ File = ($txt | Split-Path -Leaf); Line = $idx+1; Type = "MCCount"; Value = $val; Content = $line.Trim() }
            }
        }
    }
}

$report | Export-Csv -Path "$baseDir\scratch\anomaly_report_v3.csv" -NoTypeInformation -Encoding UTF8
Write-Host "Found $($report.Count) potential anomalies."
