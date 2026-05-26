Add-Type -Assembly System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead('c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\YAPILACAKLAR_RAPOR.docx')
$entry = $zip.GetEntry('word/document.xml')
$sr = New-Object System.IO.StreamReader($entry.Open())
$xml = [xml]$sr.ReadToEnd()
$sr.Close()
$zip.Dispose()
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('w','http://schemas.openxmlformats.org/wordprocessingml/2006/main')
$paragraphs = $xml.SelectNodes('//w:p', $ns)
$lines = @()
foreach($p in $paragraphs) {
    $texts = $p.SelectNodes('.//w:t', $ns)
    $line = ($texts | ForEach-Object { $_.InnerText }) -join ''
    $lines += $line
}
$lines -join "`n" | Out-File -FilePath 'c:\Users\Kurt\Desktop\Proje\YAPILACAKLAR_TEXT.txt' -Encoding UTF8
Write-Host "Done. Lines: $($lines.Count)"
