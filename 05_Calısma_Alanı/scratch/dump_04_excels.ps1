$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$dir = "C:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo"
$files = Get-ChildItem -Path $dir -Filter "*.xlsx"
$outPath = "C:\Users\Kurt\Desktop\Proje\06_Kodlar\scratch\excel_dump.txt"
$report = @()

foreach ($file in $files) {
    Try {
        $report += "============================================================"
        $report += "FILE: $($file.Name)"
        $report += "============================================================"
        $wb = $excel.Workbooks.Open($file.FullName, $null, $true) # true for read-only
        $sheet = $wb.Sheets.Item(1)
        
        $maxRow = $sheet.UsedRange.Rows.Count
        $maxCol = $sheet.UsedRange.Columns.Count
        
        for ($r=1; $r -le $maxRow; $r++) {
            $line = ""
            for ($c=1; $c -le $maxCol; $c++) {
                $val = $sheet.Cells.Item($r, $c).Text
                $line += "$val | "
            }
            $report += $line
        }
        $wb.Close($false)
    } Catch {
        $report += "ERROR READING: $($file.Name) - $($_.Exception.Message)"
    }
}

$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
$report | Set-Content $outPath -Encoding UTF8
Write-Output "Dump completed to $outPath"
