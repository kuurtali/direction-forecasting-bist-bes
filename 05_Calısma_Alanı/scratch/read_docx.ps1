param(
    [string]$DocxPath
)

if (-not (Test-Path $DocxPath)) {
    Write-Error "File not found: $DocxPath"
    exit
}

$TempDir = Join-Path $env:TEMP ([Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TempDir | Out-Null

try {
    $ZipPath = Join-Path $TempDir "doc.zip"
    Copy-Item $DocxPath $ZipPath
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force
    $XmlPath = Join-Path $TempDir "word/document.xml"
    if (Test-Path $XmlPath) {
        # Force UTF-8 reading
        $xmlContent = [System.IO.File]::ReadAllText($XmlPath, [System.Text.Encoding]::UTF8)
        [xml]$xml = $xmlContent
        $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace("w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
        $nodes = $xml.SelectNodes("//w:t", $ns)
        $text = ""
        foreach ($node in $nodes) {
            $text += $node.InnerText + "`n"
        }
        Write-Output $text
    }
} finally {
    Remove-Item -Path $TempDir -Recurse -Force
}
