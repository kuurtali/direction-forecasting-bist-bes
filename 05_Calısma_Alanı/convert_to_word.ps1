# Word COM ile MD -> DOCX Donusturme
$word = New-Object -ComObject Word.Application
$word.Visible = $false

function New-WordDoc {
    param($srcMd, $outDocx)
    
    $doc = $word.Documents.Add()
    $sel = $word.Selection
    
    # Font ayari
    $sel.Font.Name = "Times New Roman"
    $sel.Font.Size = 12
    
    $lines = Get-Content $srcMd -Encoding UTF8
    $inTable = $false
    $tableRows = @()
    
    function Flush-Table {
        if ($script:tableRows.Count -eq 0) { return }
        $ncols = ($script:tableRows[0] -split '\|' | Where-Object { $_ -ne '' }).Count
        if ($ncols -lt 2) { $script:tableRows = @(); return }
        
        $dataRows = @()
        foreach ($r in $script:tableRows) {
            $cells = ($r -split '\|' | Where-Object { $_ -ne '' }) | ForEach-Object { $_.Trim() }
            if ($cells -and -not ($cells[0] -match '^[-:]+$')) {
                $dataRows += ,@($cells)
            }
        }
        
        if ($dataRows.Count -gt 0) {
            $nRows = $dataRows.Count
            $nCols = $dataRows[0].Count
            $range = $sel.Range
            $table = $doc.Tables.Add($range, $nRows, $nCols)
            $table.Borders.Enable = $true
            $table.Style = "Table Grid"
            
            for ($i = 0; $i -lt $nRows; $i++) {
                for ($j = 0; $j -lt [Math]::Min($nCols, $dataRows[$i].Count); $j++) {
                    $cellText = $dataRows[$i][$j] -replace '\*\*','' -replace [char]0x2605,'*' -replace [char]0x26A0,'(!)'
                    $table.Cell($i+1, $j+1).Range.Text = $cellText
                    $table.Cell($i+1, $j+1).Range.Font.Size = 10
                    $table.Cell($i+1, $j+1).Range.Font.Name = "Times New Roman"
                    if ($i -eq 0) { $table.Cell($i+1, $j+1).Range.Font.Bold = $true }
                }
            }
            $sel.EndOf(6) | Out-Null  # wdStory
            $sel.MoveRight() | Out-Null
            $sel.TypeParagraph()
        }
        $script:tableRows = @()
    }
    
    foreach ($line in $lines) {
        $line = $line.TrimEnd()
        
        # Tablo satiri mi?
        if ($line -match '^\|') {
            $tableRows += $line
            continue
        } else {
            if ($tableRows.Count -gt 0) { Flush-Table }
        }
        
        # Ayirici
        if ($line -eq '---') { continue }
        
        # H1
        if ($line -match '^# (.+)$' -and $line -notmatch '^## ') {
            $sel.Style = $doc.Styles["Heading 1"]
            $text = $line -replace '^# ',''
            $sel.TypeText($text)
            $sel.TypeParagraph()
            $sel.Style = $doc.Styles["Normal"]
            continue
        }
        
        # H2
        if ($line -match '^## (.+)$' -and $line -notmatch '^### ') {
            $sel.Style = $doc.Styles["Heading 2"]
            $text = $line -replace '^## ',''
            $sel.TypeText($text)
            $sel.TypeParagraph()
            $sel.Style = $doc.Styles["Normal"]
            continue
        }
        
        # H3
        if ($line -match '^### (.+)$') {
            $sel.Style = $doc.Styles["Heading 3"]
            $text = $line -replace '^### ',''
            $sel.TypeText($text)
            $sel.TypeParagraph()
            $sel.Style = $doc.Styles["Normal"]
            continue
        }
        
        # Bold paragraf
        if ($line -match '^\*\*(.+)\*\*$') {
            $sel.Font.Bold = $true
            $sel.TypeText($Matches[1])
            $sel.Font.Bold = $false
            $sel.TypeParagraph()
            continue
        }
        
        # Blockquote
        if ($line -match '^> (.+)$') {
            $text = $line -replace '^> ','' -replace '\*\*',''
            $sel.ParagraphFormat.LeftIndent = 36
            $sel.Font.Italic = $true
            $sel.TypeText($text)
            $sel.Font.Italic = $false
            $sel.ParagraphFormat.LeftIndent = 0
            $sel.TypeParagraph()
            continue
        }
        
        # Italic not
        if ($line -match '^\*[^*]' -and $line -match '\*$') {
            $text = $line.Trim('*').Trim()
            $sel.Font.Italic = $true
            $sel.Font.Size = 10
            $sel.TypeText($text)
            $sel.Font.Italic = $false
            $sel.Font.Size = 12
            $sel.TypeParagraph()
            continue
        }
        
        # Liste
        if ($line -match '^- (.+)$') {
            $sel.Range.ListFormat.ApplyBulletDefault()
            $text = $line -replace '^- ',''
            $sel.TypeText($text)
            $sel.TypeParagraph()
            $sel.Range.ListFormat.RemoveNumbers()
            continue
        }
        
        if ($line -match '^\d+\. (.+)$') {
            $text = $line -replace '^\d+\. ',''
            $sel.TypeText($text)
            $sel.TypeParagraph()
            continue
        }
        
        # Normal paragraf
        if ($line.Trim() -ne '') {
            $clean = $line -replace '\*\*','' -replace [char]0x2605,'*' -replace [char]0x26A0,'(!)'
            $sel.TypeText($clean)
            $sel.TypeParagraph()
        }
    }
    
    if ($tableRows.Count -gt 0) { Flush-Table }
    
    $doc.SaveAs([ref]$outDocx, [ref]16)  # wdFormatDocumentDefault
    $doc.Close()
    Write-Host "SAVED: $outDocx"
}

# 1. Makale
New-WordDoc -srcMd "C:\Users\Hp\Desktop\Proje\MAKALE_FORMAT_TR.md" -outDocx "C:\Users\Hp\Desktop\Proje\MAKALE_FORMAT_TR.docx"

# 2. Konusmaci Notlari
New-WordDoc -srcMd "C:\Users\Hp\Desktop\Proje\UYIK_2026_KONUSMACI_NOTLARI.md" -outDocx "C:\Users\Hp\Desktop\Proje\UYIK_2026_KONUSMACI_NOTLARI.docx"

$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "ALL DONE"
