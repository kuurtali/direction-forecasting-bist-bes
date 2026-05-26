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
# Add common mathematical constants or zero values that are always safe
$validNumbers.Add("0.0000") | Out-Null
$validNumbers.Add("1.0000") | Out-Null
$validNumbers.Add("100.00") | Out-Null
$validNumbers.Add("0.5000") | Out-Null
$validNumbers.Add("50.00") | Out-Null

Write-Host "Reading CSVs to build truth database..."
foreach ($dir in $csvDirs) {
    if (Test-Path $dir) {
        $csvs = Get-ChildItem -Path $dir -Filter "*.csv"
        foreach ($csv in $csvs) {
            $content = Import-Csv $csv.FullName
            foreach ($row in $content) {
                foreach ($prop in $row.psobject.properties) {
                    $val = $prop.Value
                    if ($val -match "^[0-9]+\.[0-9]+$") {
                        try {
                            $rounded = [math]::Round([double]$val, 4).ToString("0.0000")
                            $validNumbers.Add($rounded) | Out-Null
                            
                            $asPercent = ([math]::Round([double]$val * 100, 2)).ToString("0.00")
                            $validNumbers.Add($asPercent) | Out-Null
                            
                            # Also check for 1-decimal rounding if applicable
                            $asPercentFix = ([math]::Round([double]$val * 100, 1)).ToString("0.0")
                            $validNumbers.Add($asPercentFix) | Out-Null
                        } catch {}
                    }
                }
            }
        }
    }
}
Write-Host "Database built with $($validNumbers.Count) valid metrics."
Write-Host "Commencing Line-by-Line Sweep in Texts..."

$report = @()

foreach ($txt in $textFiles) {
    if (-not (Test-Path $txt)) { continue }
    
    $lines = Get-Content $txt
    Write-Host "`nScanning $($txt | Split-Path -Leaf)..."
    
    for ($i=0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        
        # Match percentages like %74.30 or 74.30%
        $matches = [regex]::Matches($line, "(?:%([0-9]{1,3}\.[0-9]{1,2}))|([0-9]{1,3}\.[0-9]{1,2})%")
        foreach ($m in $matches) {
            $val = if ($m.Groups[1].Value) { $m.Groups[1].Value } else { $m.Groups[2].Value }
            
            $foundMatch = $false
            if ($validNumbers.Contains($val)) { $foundMatch = $true }
            else {
                # Tolerance check
                $numVal = [double]$val
                foreach ($v in $validNumbers) {
                    if ([double]::TryParse($v, [ref]$null)) {
                        if ([math]::Abs([double]$v - $numVal) -le 0.015) { $foundMatch = $true; break }
                    }
                }
            }

            if (-not $foundMatch) {
                $report += [PSCustomObject]@{ File = ($txt | Split-Path -Leaf); Line = $i+1; Type = "Percentage"; Value = $val; Content = $line.Trim() }
            }
        }
        
        # Match raw floats like 0.7430
        $matches2 = [regex]::Matches($line, "(?:[^\d]|^)(0\.[0-9]{2,4})(?:[^\d]|$)")
        foreach ($m in $matches2) {
            $val = $m.Groups[1].Value
            $padded = ([double]$val).ToString("0.0000")
            
            $foundMatch = $false
            if ($validNumbers.Contains($padded)) { $foundMatch = $true }
            else {
                $numVal = [double]$val
                foreach ($v in $validNumbers) {
                    if ([double]::TryParse($v, [ref]$null)) {
                        if ([math]::Abs([double]$v - $numVal) -le 0.0002) { $foundMatch = $true; break }
                    }
                }
            }

            if (-not $foundMatch) {
                # Exclude common stuff like 0.01 or 0.2 if p-value thresholds or dropout
                if ($numVal -eq 0.01 -or $numVal -eq 0.2 -or $numVal -eq 0.4 -or $numVal -eq 0.3) { $foundMatch = $true }
            }

            if (-not $foundMatch) {
                $report += [PSCustomObject]@{ File = ($txt | Split-Path -Leaf); Line = $i+1; Type = "Float"; Value = $val; Content = $line.Trim() }
            }
        }
    }
}

$report | Export-Csv -Path "$baseDir\scratch\anomaly_report.csv" -NoTypeInformation -Encoding UTF8
Write-Host "`nSweep complete. Report saved to scratch\anomaly_report.csv"
Write-Host "Found $($report.Count) potential anomalies."
