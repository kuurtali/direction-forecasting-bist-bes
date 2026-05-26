$kanitPath = "C:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar\MC_KANIT_RAPORU.txt"

# Safe wildcard path resolution
$base = "C:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
$lstmCSVFile = Get-ChildItem -Path $base -Recurse -Filter "EMEKLILIK_LSTM_sonuclar.csv" | Select-Object -ExpandProperty FullName -First 1
$cnnCSVFile = Get-ChildItem -Path $base -Recurse -Filter "EMEKLILIK_CNN_sonuclar.csv" | Select-Object -ExpandProperty FullName -First 1

$kanitLines = Get-Content $kanitPath -Encoding UTF8
$lstm = Import-Csv $lstmCSVFile
$cnn = Import-Csv $cnnCSVFile

$out = "C:\Users\Kurt\Desktop\Proje\06_Kodlar\scratch\mc_mismatches.txt"
$report = @()

function Check-Mismatches($modelName, $csvData) {
    global $kanitLines, $report
    foreach ($row in $csvData) {
        $fon = $row.Fon
        $feat = $row.Feature_Set
        $in = $row.Input
        $out = $row.Output
        $fullModelName = "$fon GUNCEL $modelName"
        
        $isCSVMC = ($row.Sens -eq '0' -or $row.Sens -eq '1' -or $row.Spec -eq '0' -or $row.Spec -eq '1')
        
        # Owerwrite logic for regex escape
        $pattern = "$feat\s+In=$in\s+Out=$out"
        $lines = $kanitLines | Select-String -Pattern $pattern
        
        $foundLine = $null
        foreach ($l in $lines) {
            # Find the header before this line
            $lineIdx = $l.LineNumber - 1
            $header = $null
            for ($i = $lineIdx; $i -ge 0; $i--) {
                if ($kanitLines[$i] -match "# (.*) – \d+ SATIR" -or $kanitLines[$i] -match "# (.*) - \d+ SATIR") {
                    $header = $kanitLines[$i]
                    break
                }
            }
            if ($header -and $header -match $fullModelName) {
                $foundLine = $l.Line
                break
            }
        }
        
        if ($foundLine) {
            $isRaporMC = ($foundLine -match '<<<< MC')
            if ($isCSVMC -ne $isRaporMC) {
                $status = "RaporMC: $isRaporMC, CsvMC: $isCSVMC | Sens: $($row.Sens), Spec: $($row.Spec)"
                $report += "$fullModelName | $feat In=$in Out=$out | $status"
            }
        }
    }
}

Check-Mismatches "LSTM" $lstm
Check-Mismatches "CNN" $cnn

$report | Set-Content $out -Encoding UTF8
Write-Output "Mismatch extraction complete."
