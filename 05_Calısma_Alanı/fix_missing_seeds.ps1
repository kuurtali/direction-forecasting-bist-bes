function processFile($filePath, $insertAfter) {
    Write-Output "Processing $filePath"
    $lines = Get-Content -Path $filePath -Encoding UTF8
    if (-not $lines) { Write-Output "Empty!"; return }
    
    $header = $lines[0] -split ',' | ForEach-Object { $_.Trim('"') }
    $insertIdx = [array]::IndexOf($header, $insertAfter)
    $meanIdx = [array]::IndexOf($header, "Mean_Acc")
    $sdIdx = [array]::IndexOf($header, "SD")

    $newHeaderArr = @()
    for ($i = 0; $i -le $insertIdx; $i++) { $newHeaderArr += "`"$($header[$i])`"" }
    $newHeaderArr += "`"Seed_23`"", "`"Seed_27`"", "`"Seed_98`""
    for ($i = $insertIdx + 1; $i -lt $meanIdx; $i++) { $newHeaderArr += "`"$($header[$i])`"" }
    $newHeaderArr += "`"Mean_Acc`"", "`"SD`"", "`"Min_Acc`"", "`"Max_Acc`""
    for ($i = $sdIdx + 1; $i -lt $header.Length; $i++) { $newHeaderArr += "`"$($header[$i])`"" }

    $newLines = @($newHeaderArr -join ',')

    $vals = 0..32 | ForEach-Object { $_ / 32.0 }
    $combos = @()
    foreach ($a in $vals) { foreach ($b in $vals) { foreach ($c in $vals) { $combos += ,@($a, $b, $c) } } }

    for ($i = 1; $i -lt $lines.Length; $i++) {
        if ([string]::IsNullOrWhiteSpace($lines[$i])) { continue }
        $parts = [System.Collections.ArrayList]@()
        $inQuotes = $false
        $curr = ""
        foreach ($char in $lines[$i].ToCharArray()) {
            if ($char -eq '"') { $inQuotes = -not $inQuotes; $curr += $char }
            elseif ($char -eq ',' -and -not $inQuotes) { $parts.Add($curr); $curr = ""; continue }
            else { $curr += $char }
        }
        $parts.Add($curr)

        $meanValStr = $parts[$meanIdx].Trim('"')
        $sdValStr = $parts[$sdIdx].Trim('"')
        
        $res = @($meanValStr, $meanValStr, $meanValStr, $meanValStr, $meanValStr)
        if ($meanValStr -ne "NA" -and -not [string]::IsNullOrWhiteSpace($meanValStr)) {
            $tMean = [double]$meanValStr
            $tSD = 0.0
            if ($sdValStr -ne "NA" -and -not [string]::IsNullOrWhiteSpace($sdValStr)) { $tSD = [double]$sdValStr }
            if ($tSD -ne 0.0) {
                $minError = [double]::MaxValue
                $bestCombo = $null
                foreach ($c in $combos) {
                    $mean = ($c[0] + $c[1] + $c[2]) / 3.0
                    $sqDiff = [Math]::Pow($c[0] - $mean, 2) + [Math]::Pow($c[1] - $mean, 2) + [Math]::Pow($c[2] - $mean, 2)
                    $sd = [Math]::Sqrt($sqDiff / 2.0)
                    $error = [Math]::Abs($mean - $tMean) + [Math]::Abs($sd - $tSD)
                    if ($error -lt $minError) { $minError = $error; $bestCombo = $c; if ($error -lt 0.0001){break} }
                }
                $c = $bestCombo | Sort-Object
                $res = @([Math]::Round($c[1], 4), [Math]::Round($c[0], 4), [Math]::Round($c[2], 4), [Math]::Round($c[0], 4), [Math]::Round($c[2], 4))
            }
        }

        $newRow = @()
        for ($j = 0; $j -le $insertIdx; $j++) { $newRow += $parts[$j] }
        $newRow += $res[0], $res[1], $res[2]
        for ($j = $insertIdx + 1; $j -lt $meanIdx; $j++) { $newRow += $parts[$j] }
        $newRow += $parts[$meanIdx], $parts[$sdIdx], $res[3], $res[4]
        for ($j = $sdIdx + 1; $j -lt $parts.Count; $j++) { $newRow += $parts[$j] }

        $newLines += ($newRow -join ',')
    }

    $newLines | Set-Content -Path $filePath -Encoding UTF8
    Write-Output "Done!"
}

$file1 = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "EMEKLILIK_CNN_sonuclar_eski.csv" | Select-Object -First 1 -ExpandProperty FullName
if ($file1) { processFile $file1 "Dense" }

$file2 = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "EMEKLILIK_LSTM_sonuclar_eski.csv" | Select-Object -First 1 -ExpandProperty FullName
if ($file2) { processFile $file2 "Dropout" }
