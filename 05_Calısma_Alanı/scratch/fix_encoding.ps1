param([string]$TargetFile)

$bytes = [System.IO.File]::ReadAllBytes($TargetFile)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

function DoFix($old, $new) {
    $cnt = 0
    $idx = $content.IndexOf($old)
    while ($idx -ge 0) {
        $content = $content.Remove($idx, $old.Length).Insert($idx, $new)
        $cnt++
        $idx = $content.IndexOf($old, $idx + $new.Length)
    }
    $script:content = $content
    return $cnt
}

$total = 0

# BOM
$bom = [char]0xFEFF
$script:content = $content.Replace([string]$bom, "")

# Turkce kucuk harfler
$total += DoFix "Ã¼" "u"
$total += DoFix "ÃƒÂ¼" "u"
$total += DoFix "Ã¶" "o"
$total += DoFix "ÃƒÂ¶" "o"
$total += DoFix "Ã§" "c"
$total += DoFix "ÃƒÂ§" "c"
$total += DoFix "Ã±" "n"

# Turkce buyuk harfler
$total += DoFix "Ã–" "O"
$total += DoFix "ÃƒÂ–" "O"
$total += DoFix "Ãœ" "U"
$total += DoFix "Ã‡" "C"
$total += DoFix "ÃƒÂ‡" "C"

# i dotless ve I dotted
$total += DoFix "Ã„Â±" "i"
$total += DoFix "Ã„Â°" "I"

# g breve ve s cedilla (UTF-8 multi-byte kaliplar)
$total += DoFix "Ã„Å¸" "g"
$total += DoFix "Ã„Å¾" "G"
$total += DoFix "Ã…Å¸" "s"
$total += DoFix "Ã…Åž" "S"

# Unicode Turkce karakterleri dogrudan ASCII'ye
$script:content = $script:content.Replace([string][char]0x011F, "g")
$script:content = $script:content.Replace([string][char]0x011E, "G")
$script:content = $script:content.Replace([string][char]0x015F, "s")
$script:content = $script:content.Replace([string][char]0x015E, "S")
$script:content = $script:content.Replace([string][char]0x0131, "i")
$script:content = $script:content.Replace([string][char]0x0130, "I")
$script:content = $script:content.Replace([string][char]0x00FC, "u")
$script:content = $script:content.Replace([string][char]0x00DC, "U")
$script:content = $script:content.Replace([string][char]0x00F6, "o")
$script:content = $script:content.Replace([string][char]0x00D6, "O")
$script:content = $script:content.Replace([string][char]0x00E7, "c")
$script:content = $script:content.Replace([string][char]0x00C7, "C")
$script:content = $script:content.Replace([string][char]0x00FC, "u")

# Noktalama isaretleri
$script:content = $script:content.Replace([string][char]0x2014, "-")  # em dash
$script:content = $script:content.Replace([string][char]0x2013, "-")  # en dash
$script:content = $script:content.Replace([string][char]0x2019, "'")  # right single quote
$script:content = $script:content.Replace([string][char]0x2018, "'")  # left single quote
$script:content = $script:content.Replace([string][char]0x201C, '"')  # left double quote
$script:content = $script:content.Replace([string][char]0x201D, '"')  # right double quote
$script:content = $script:content.Replace([string][char]0x2022, "*")  # bullet
$script:content = $script:content.Replace([string][char]0x2192, "->") # right arrow
$script:content = $script:content.Replace([string][char]0x2190, "<-") # left arrow
$script:content = $script:content.Replace([string][char]0x00D7, "x")  # multiplication sign
$script:content = $script:content.Replace([string][char]0x2713, "(v)") # check mark

$outBytes = [System.Text.Encoding]::UTF8.GetBytes($script:content)
[System.IO.File]::WriteAllBytes($TargetFile, $outBytes)
Write-Output "Tamamlandi: $total double-encode kalip duzeltildi."
Write-Output "Dosya: $(Split-Path $TargetFile -Leaf)"
