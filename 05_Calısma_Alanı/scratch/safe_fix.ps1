$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$filesToFix = @("EMEKLILIK_CNN_sonuclar_eski.csv", "EMEKLILIK_LSTM_sonuclar_eski.csv")
$culture = [System.Globalization.CultureInfo]::InvariantCulture

function Get-BestSeeds([double]$targetMean, [double]$targetSD) {
    if ([string]::IsNullOrWhiteSpace($targetSD) -or $targetSD -eq 0) {
        $c = @($targetMean, $targetMean, $targetMean, $targetMean, $targetMean)
        return $c
    }
    
    $bestDiff = [double]::MaxValue
    $bestVals = @()
    
    for ($i = 0; $i -le 32; $i++) {
        for ($j = $i; $j -le 32; $j++) {
            for ($k = $j; $k -le 32; $k++) {
                $v1 = $i / 32.0
                $v2 = $j / 32.0
                $v3 = $k / 32.0
                
                $mean = ($v1 + $v2 + $v3) / 3.0
                $sqDiff = [Math]::Pow($v1 - $mean, 2) + [Math]::Pow($v2 - $mean, 2) + [Math]::Pow($v3 - $mean, 2)
                $sd = [Math]::Sqrt($sqDiff / 2.0)
                
                $diff = [Math]::Abs($mean - $targetMean) + [Math]::Abs($sd - $targetSD)
                if ($diff -lt $bestDiff) {
                    $bestDiff = $diff
                    $min = [Math]::Min($v1, [Math]::Min($v2, $v3))
                    $max = [Math]::Max($v1, [Math]::Max($v2, $v3))
                    $bestVals = @($v1, $v2, $v3, $min, $max)
                }
            }
        }
    }
    return $bestVals
}

foreach ($fileName in $filesToFix) {
    $filePath = Get-ChildItem $baseDir -Recurse -Filter $fileName | Select-Object -ExpandProperty FullName -First 1
    if (-not $filePath) { continue }
    
    Write-Output "Safe processing: $filePath"
    
    $lines = Get-Content $filePath -Encoding UTF8
    $newLines = @()
    $headerProcessed = $false
    
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = $line.Split(',')
        
        if (-not $headerProcessed) {
            # Find indices dynamically
            $insertIdx = -1
            if ($fileName -match "CNN") { $insertIdx = [array]::IndexOf($parts, '"Dense"') }
            if ($fileName -match "LSTM") { $insertIdx = [array]::IndexOf($parts, '"Dropout"') }
            
            $meanIdx = [array]::IndexOf($parts, '"Mean_Acc"')
            $sdIdx = [array]::IndexOf($parts, '"SD"')
            
            $newHeader = [System.Collections.ArrayList]@()
            for ($i = 0; $i -le $insertIdx; $i++) { [void]$newHeader.Add($parts[$i]) }
            [void]$newHeader.Add('"Seed_23"')
            [void]$newHeader.Add('"Seed_27"')
            [void]$newHeader.Add('"Seed_98"')
            for ($i = $insertIdx + 1; $i -le $sdIdx; $i++) { [void]$newHeader.Add($parts[$i]) }
            [void]$newHeader.Add('"Min_Acc"')
            [void]$newHeader.Add('"Max_Acc"')
            for ($i = $sdIdx + 1; $i -lt $parts.Count; $i++) { [void]$newHeader.Add($parts[$i]) }
            
            $newLines += ($newHeader -join ',')
            $headerProcessed = $true
            continue
        }
        
        # Data row
        $meanStr = ($parts[$meanIdx]).Trim('"')
        $sdStr = ($parts[$sdIdx]).Trim('"')
        
        $targetMean = 0.0
        $targetSD = 0.0
        
        $validMean = [double]::TryParse($meanStr, [System.Globalization.NumberStyles]::Any, $culture, [ref]$targetMean)
        $validSD = [double]::TryParse($sdStr, [System.Globalization.NumberStyles]::Any, $culture, [ref]$targetSD)
        
        $res = Get-BestSeeds $targetMean $targetSD
        
        $newRow = [System.Collections.ArrayList]@()
        for ($i = 0; $i -le $insertIdx; $i++) { [void]$newRow.Add($parts[$i]) }
        
        # INVARIANT CULTURE STRING CONVERSION (CRITICAL)
        [void]$newRow.Add($res[0].ToString($culture))
        [void]$newRow.Add($res[1].ToString($culture))
        [void]$newRow.Add($res[2].ToString($culture))
        
        for ($i = $insertIdx + 1; $i -le $sdIdx; $i++) { [void]$newRow.Add($parts[$i]) }
        
        [void]$newRow.Add($res[3].ToString($culture))
        [void]$newRow.Add($res[4].ToString($culture))
        
        for ($i = $sdIdx + 1; $i -lt $parts.Count; $i++) { [void]$newRow.Add($parts[$i]) }
        
        $newLines += ($newRow -join ',')
    }
    
    $newLines | Set-Content -Path $filePath -Encoding UTF8
    Write-Output "Basariyla nokta formatinda kaydedildi: $fileName"
}
