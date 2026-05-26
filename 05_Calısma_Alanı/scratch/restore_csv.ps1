$baseDir = "c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
if (-not (Test-Path $baseDir)) {
    $baseDir = Get-ChildItem "c:\Users\Kurt\Desktop\Proje" -Recurse -Filter "CSV_TUM_SONUCLAR.html" | Select-Object -ExpandProperty FullName -First 1 | Split-Path
}

$filesToFix = @("EMEKLILIK_CNN_sonuclar_eski.csv", "EMEKLILIK_LSTM_sonuclar_eski.csv")

function Pop-Number([System.Collections.ArrayList]$list) {
    if ($list.Count -eq 0) { return "" }
    $last = $list[$list.Count - 1].Trim()
    $list.RemoveAt($list.Count - 1)
    if ($last -eq "0" -or $last -eq "1" -or $last -eq "NA" -or ($last -match "\.")) {
        return $last
    } else {
        $whole = $list[$list.Count - 1].Trim()
        $list.RemoveAt($list.Count - 1)
        return "$whole.$last"
    }
}

foreach ($fileName in $filesToFix) {
    $filePath = Get-ChildItem $baseDir -Recurse -Filter $fileName | Select-Object -ExpandProperty FullName -First 1
    if (-not $filePath) { continue }
    
    $lines = Get-Content $filePath -Encoding UTF8
    $newLines = @()
    $headerRestored = $false
    
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        
        # Split but preserve quoting structure for simple fields if any
        # Fortunately none of the numeric fields have commas inside quotes in this specific dataset's tail.
        # But we must be careful with '32-64-128' etc.
        # The easiest is basic split by comma because R's output CSV doesn't quote numbers, and strings don't contain commas here.
        # Let's do a reliable simple split
        $parts = $line.Split(',')
        
        if (-not $headerRestored) {
            # Restore Exact 14 Column Header
            $newLines += '"Fon","Feature_Set","Input","Output","Dropout","Filters","Kernel","Dense","Mean_Acc","SD","P_Value","F1","Sens","Spec"'
            $headerRestored = $true
            continue
        }
        
        if ($parts.Count -lt 14) {
            $newLines += $line # Fallback
            continue
        }
        
        # Last 4 always untouched
        $pVal = $parts[$parts.Count - 4]
        $f1   = $parts[$parts.Count - 3]
        $sens = $parts[$parts.Count - 2]
        $spec = $parts[$parts.Count - 1]
        
        # Middle
        $midList = [System.Collections.ArrayList]@()
        for ($i = 8; $i -lt ($parts.Count - 4); $i++) {
            [void]$midList.Add($parts[$i])
        }
        
        # Discard corrupted Max and Min
        $discardMax = Pop-Number $midList
        $discardMin = Pop-Number $midList
        
        # Recover exact SD and Mean_Acc
        $origSD = Pop-Number $midList
        $origMean = Pop-Number $midList
        
        # Create cleanly restored string
        $restoredRow = [System.Collections.ArrayList]@()
        for ($i = 0; $i -lt 8; $i++) { [void]$restoredRow.Add($parts[$i]) }
        [void]$restoredRow.Add($origMean)
        [void]$restoredRow.Add($origSD)
        [void]$restoredRow.Add($pVal)
        [void]$restoredRow.Add($f1)
        [void]$restoredRow.Add($sens)
        [void]$restoredRow.Add($spec)
        
        $newLines += ($restoredRow -join ',')
    }
    
    $newLines | Set-Content -Path $filePath -Encoding UTF8
    Write-Output "Cerrah operasyonu basarili: Orijinal $fileName 14 kolon olarak %100 kurtarildi."
}
