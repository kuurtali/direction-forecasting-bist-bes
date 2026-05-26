$base = "c:\Users\Kurt\Desktop\PROJE_ALL"

# Wide Definition: Sens=0 OR Spec=0 OR Spec=NA
function Is-MC($row) {
    if ($null -eq $row) { return $false }
    
    # Check for NA or null in Spec
    if ($row.Spec -eq "NA" -or [string]::IsNullOrWhiteSpace($row.Spec)) {
        return $true
    }
    
    # Try parsing metrics
    $sensVal = 0.0
    $specVal = 0.0
    
    if ([double]::TryParse($row.Sens, [ref]$sensVal) -and [double]::TryParse($row.Spec, [ref]$specVal)) {
        if ($sensVal -eq 0 -or $specVal -eq 0) {
            return $true
        }
    }
    elseif ([double]::TryParse($row.Sens, [ref]$sensVal)) {
         if ($sensVal -eq 0) { return $true }
    }

    return $false
}

function Get-MC-Stats($path) {
    $files = Get-ChildItem $path -ErrorAction SilentlyContinue
    if ($null -eq $files -or $files.Count -eq 0) { return "FILE NOT FOUND" }
    $target = $files[0].FullName
    $csv = Import-Csv $target
    $mc_count = 0
    foreach ($row in $csv) {
        if (Is-MC $row) { $mc_count++ }
    }
    return "$mc_count/$($csv.Count)"
}

function Load-Csv($path) {
    $files = Get-ChildItem $path -ErrorAction SilentlyContinue
    if ($null -eq $files -or $files.Count -eq 0) { return $null }
    return Import-Csv $files[0].FullName
}

# Directories with wildcards
$dir22 = "c:\Users\Kurt\Desktop\PROJE_ALL\2018-2022*"
$dir26 = "c:\Users\Kurt\Desktop\PROJE_ALL\2018-2026*"

$em_lstm_e = Load-Csv "$dir22\EMEKLILIK_LSTM_sonuclar_eski.csv"
$em_cnn_e = Load-Csv "$dir22\EMEKLILIK_CNN_sonuclar_eski.csv"
$em_lstm_g = Load-Csv "$dir26\EMEKLILIK_LSTM_sonuclar.csv"
$em_cnn_g = Load-Csv "$dir26\EMEKLILIK_CNN_sonuclar.csv"

function Count-Filtered($csv, $fon) {
    if ($null -eq $csv) { return "N/A" }
    $mc = 0; $total = 0
    foreach($r in $csv) { if($r.Fon -eq $fon) { $total++; if(Is-MC $r){$mc++} } }
    if ($total -eq 0) { return "0/0" }
    return "$mc/$total"
}

$final_table = @()
$final_table += [PSCustomObject]@{Varlik="THYAO"; Model="LSTM"; Eski=(Get-MC-Stats "$dir22\LSTM_sonuclar_FINAL_eski.csv"); Guncel=(Get-MC-Stats "$dir26\LSTM_sonuclar_FINAL.csv")}
$final_table += [PSCustomObject]@{Varlik="THYAO"; Model="CNN"; Eski=(Get-MC-Stats "$dir22\CNN_sonuclar_FINAL_eski.csv"); Guncel=(Get-MC-Stats "$dir26\CNN_sonuclar_FINAL.csv")}

foreach($fon in @("ALZ","AZS","AMZ")) {
    $final_table += [PSCustomObject]@{Varlik=$fon; Model="LSTM"; Eski=(Count-Filtered $em_lstm_e $fon); Guncel=(Count-Filtered $em_lstm_g $fon)}
    $final_table += [PSCustomObject]@{Varlik=$fon; Model="CNN"; Eski=(Count-Filtered $em_cnn_e $fon); Guncel=(Count-Filtered $em_cnn_g $fon)}
}

$final_table | Format-Table -AutoSize
