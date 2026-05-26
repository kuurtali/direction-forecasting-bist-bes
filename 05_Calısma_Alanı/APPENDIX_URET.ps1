$base = "c:\Users\Kurt\Desktop\PROJE_ALL"
$out  = "$base\Literatür+Kodlar\APPENDIX_TABLOLARI_CSV.xlsx"

# CSV yollari
$thyao_lstm  = Import-Csv "$base\2018-2026 çıktılar\LSTM_sonuclar_FINAL.csv"
$thyao_cnn   = Import-Csv "$base\2018-2026 çıktılar\CNN_sonuclar_FINAL.csv"
$thyao_arima = Import-Csv "$base\2018-2026 çıktılar\ARIMA_sonuclar.csv"
$thyao_naive = Import-Csv "$base\2018-2026 çıktılar\NAIVE_baseline.csv"
$em_lstm     = Import-Csv "$base\2018-2026 çıktılar\EMEKLILIK_LSTM_sonuclar.csv"
$em_cnn      = Import-Csv "$base\2018-2026 çıktılar\EMEKLILIK_CNN_sonuclar.csv"
$em_arima    = Import-Csv "$base\2018-2026 çıktılar\EMEKLILIK_ARIMA_sonuclar.csv"
$em_naive    = Import-Csv "$base\2018-2026 çıktılar\EMEKLILIK_NAIVE_baseline.csv"

# Eski CSV'ler
$thyao_lstm_e  = Import-Csv "$base\2018-2022 çıktılar\LSTM_sonuclar_FINAL_eski.csv"
$thyao_cnn_e   = Import-Csv "$base\2018-2022 çıktılar\CNN_sonuclar_FINAL_eski.csv"
$em_lstm_e     = Import-Csv "$base\2018-2022 çıktılar\EMEKLILIK_LSTM_sonuclar_eski.csv"
$em_cnn_e      = Import-Csv "$base\2018-2022 çıktılar\EMEKLILIK_CNN_sonuclar_eski.csv"

# MC hesaplama fonksiyonu
function Is-MC($row) {
    ($row.Sens -eq "0" -and $row.Spec -eq "1") -or 
    ($row.Sens -eq "1" -and $row.Spec -eq "0") -or 
    $row.Spec -eq "NA"
}

function Count-MC($rows) {
    ($rows | Where-Object { Is-MC $_ }).Count
}

# ===================================================================
# HTML RAPOR URETIMI
# ===================================================================
$html = @"
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>APPENDIX TABLOLARI - CSV'DEN OTOMATIK URETILDI</title>
<style>
body { font-family: Calibri, Arial; font-size: 11px; margin: 20px; background: #f5f5f5; }
h1 { color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 5px; }
h2 { color: #283593; margin-top: 30px; border-bottom: 2px solid #ccc; padding-bottom: 3px; }
h3 { color: #3949ab; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 25px 0; background: white; }
th { background: #1a237e; color: white; padding: 6px 10px; text-align: left; font-size: 11px; }
td { border: 1px solid #ddd; padding: 5px 10px; font-size: 11px; }
tr:nth-child(even) { background: #f8f9fa; }
.mc { background: #ffcdd2 !important; font-weight: bold; }
.best { background: #c8e6c9 !important; font-weight: bold; }
.meta { color: #666; font-style: italic; font-size: 10px; margin-bottom: 20px; }
.nav { background: #1a237e; padding: 10px; margin-bottom: 20px; }
.nav a { color: white; margin-right: 15px; text-decoration: none; font-size: 12px; }
.nav a:hover { text-decoration: underline; }
</style>
</head><body>

<h1>APPENDIX TABLOLARI</h1>
<p class="meta">Bu dosya CSV sonuc dosyalarindan otomatik olarak uretilmistir. Hicbir sayisal veri elle girilmemistir.<br>
Uretim tarihi: $(Get-Date -Format 'yyyy-MM-dd HH:mm') | MC Tanimi: Sens=0,Spec=1 VEYA Sens=1,Spec=0 VEYA Spec=NA</p>

<div class="nav">
<a href="#d1">D1-THYAO LSTM</a>
<a href="#d2">D2-THYAO CNN</a>
<a href="#d3">D3-THYAO ARIMA</a>
<a href="#d4">D4-THYAO Naive</a>
<a href="#e1">E1-Emeklilik LSTM</a>
<a href="#e2">E2-Emeklilik CNN</a>
<a href="#e3">E3-Emeklilik ARIMA</a>
<a href="#e4">E4-Emeklilik Naive</a>
<a href="#g">G-MC Analizi</a>
<a href="#h">H-Eski vs Guncel</a>
<a href="#h2">H2-Model Karsilastirma</a>
</div>
"@

# --- D1: THYAO LSTM ---
$html += '<h2 id="d1">APPENDIX D1: THYAO LSTM Sonuclari (2018-2026) - 36 Konfigurasyon</h2>'
$html += '<table><tr><th>Feature_Set</th><th>Input</th><th>Output</th><th>Mean_Acc</th><th>SD</th><th>Sens</th><th>Spec</th><th>F1</th><th>Seed_23</th><th>Seed_27</th><th>Seed_98</th><th>MC?</th></tr>'
foreach ($r in $thyao_lstm) {
    $mc = if (Is-MC $r) { "YES" } else { "" }
    $cls = if ($mc -eq "YES") { ' class="mc"' } else { "" }
    $html += "<tr$cls><td>$($r.Feature_Set)</td><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Mean_Acc)</td><td>$($r.SD)</td><td>$($r.Sens)</td><td>$($r.Spec)</td><td>$($r.F1)</td><td>$($r.Seed_23)</td><td>$($r.Seed_27)</td><td>$($r.Seed_98)</td><td>$mc</td></tr>"
}
$html += '</table>'

# --- D2: THYAO CNN ---
$html += '<h2 id="d2">APPENDIX D2: THYAO CNN Sonuclari (2018-2026) - 36 Konfigurasyon</h2>'
$html += '<table><tr><th>Feature_Set</th><th>Input</th><th>Output</th><th>Mean_Acc</th><th>SD</th><th>Sens</th><th>Spec</th><th>F1</th><th>Seed_23</th><th>Seed_27</th><th>Seed_98</th><th>MC?</th></tr>'
foreach ($r in $thyao_cnn) {
    $mc = if (Is-MC $r) { "YES" } else { "" }
    $cls = if ($mc -eq "YES") { ' class="mc"' } else { "" }
    $html += "<tr$cls><td>$($r.Feature_Set)</td><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Mean_Acc)</td><td>$($r.SD)</td><td>$($r.Sens)</td><td>$($r.Spec)</td><td>$($r.F1)</td><td>$($r.Seed_23)</td><td>$($r.Seed_27)</td><td>$($r.Seed_98)</td><td>$mc</td></tr>"
}
$html += '</table>'

# --- D3: THYAO ARIMA ---
$html += '<h2 id="d3">APPENDIX D3: THYAO ARIMA Sonuclari (2018-2026)</h2>'
$html += '<table><tr><th>Input</th><th>Output</th><th>Best_d</th><th>Test_Acc</th></tr>'
foreach ($r in $thyao_arima) {
    $html += "<tr><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Best_d)</td><td>$($r.Test_Acc)</td></tr>"
}
$html += '</table>'

# --- D4: THYAO Naive ---
$html += '<h2 id="d4">APPENDIX D4: THYAO Naive Baseline</h2>'
$html += '<table><tr><th>Input</th><th>Output</th><th>Naive_Acc</th></tr>'
foreach ($r in $thyao_naive) {
    $html += "<tr><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Naive_Acc)</td></tr>"
}
$html += '</table>'

# --- E1: Emeklilik LSTM ---
$html += '<h2 id="e1">APPENDIX E1: Emeklilik LSTM Sonuclari (TEFAS 2021-2026) - 81 Konfigurasyon</h2>'
foreach ($fon in @("ALZ","AZS","AMZ")) {
    $html += "<h3>$fon</h3>"
    $html += '<table><tr><th>Feature_Set</th><th>Input</th><th>Output</th><th>Mean_Acc</th><th>SD</th><th>Sens</th><th>Spec</th><th>F1</th><th>Seed_23</th><th>Seed_27</th><th>Seed_98</th><th>MC?</th></tr>'
    $rows = $em_lstm | Where-Object { $_.Fon -eq $fon }
    foreach ($r in $rows) {
        $mc = if (Is-MC $r) { "YES" } else { "" }
        $cls = if ($mc -eq "YES") { ' class="mc"' } else { "" }
        $html += "<tr$cls><td>$($r.Feature_Set)</td><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Mean_Acc)</td><td>$($r.SD)</td><td>$($r.Sens)</td><td>$($r.Spec)</td><td>$($r.F1)</td><td>$($r.Seed_23)</td><td>$($r.Seed_27)</td><td>$($r.Seed_98)</td><td>$mc</td></tr>"
    }
    $html += '</table>'
}

# --- E2: Emeklilik CNN ---
$html += '<h2 id="e2">APPENDIX E2: Emeklilik CNN Sonuclari (TEFAS 2021-2026) - 81 Konfigurasyon</h2>'
foreach ($fon in @("ALZ","AZS","AMZ")) {
    $html += "<h3>$fon</h3>"
    $html += '<table><tr><th>Feature_Set</th><th>Input</th><th>Output</th><th>Mean_Acc</th><th>SD</th><th>Sens</th><th>Spec</th><th>F1</th><th>Seed_23</th><th>Seed_27</th><th>Seed_98</th><th>MC?</th></tr>'
    $rows = $em_cnn | Where-Object { $_.Fon -eq $fon }
    foreach ($r in $rows) {
        $mc = if (Is-MC $r) { "YES" } else { "" }
        $cls = if ($mc -eq "YES") { ' class="mc"' } else { "" }
        $html += "<tr$cls><td>$($r.Feature_Set)</td><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Mean_Acc)</td><td>$($r.SD)</td><td>$($r.Sens)</td><td>$($r.Spec)</td><td>$($r.F1)</td><td>$($r.Seed_23)</td><td>$($r.Seed_27)</td><td>$($r.Seed_98)</td><td>$mc</td></tr>"
    }
    $html += '</table>'
}

# --- E3: Emeklilik ARIMA ---
$html += '<h2 id="e3">APPENDIX E3: Emeklilik ARIMA Sonuclari</h2>'
$html += '<table><tr><th>Fon</th><th>Input</th><th>Output</th><th>Best_d</th><th>Test_Acc</th></tr>'
foreach ($r in $em_arima) {
    $html += "<tr><td>$($r.Fon)</td><td>$($r.Input)</td><td>$($r.Output)</td><td>$($r.Best_d)</td><td>$($r.Test_Acc)</td></tr>"
}
$html += '</table>'

# --- E4: Emeklilik Naive ---
$html += '<h2 id="e4">APPENDIX E4: Emeklilik Naive Baseline</h2>'
$html += '<table><tr><th>Fon</th><th>Output</th><th>Naive_Acc</th></tr>'
foreach ($r in $em_naive) {
    $html += "<tr><td>$($r.Fon)</td><td>$($r.Output)</td><td>$($r.Naive_Acc)</td></tr>"
}
$html += '</table>'

# --- G: MC Analizi ---
$html += '<h2 id="g">APPENDIX G: Majority Class (MC) Analiz Tablosu</h2>'
$html += '<p class="meta">MC Tanimi: Sens=0 ve Spec=1 (tum tahminler Down) VEYA Sens=1 ve Spec=0 (tum tahminler Up) VEYA Spec=NA (testte dusus yok)</p>'
$html += '<table><tr><th>Varlik/Fon</th><th>Model</th><th>Feature Set 1</th><th>Feature Set 2</th><th>Feature Set 3</th><th>Feature Set 4</th><th>TOPLAM MC</th><th>TOPLAM Konfig</th><th>MC Orani</th></tr>'

# THYAO LSTM
$sets = @("hist_tech","technical","historical","closing")
$counts = @()
foreach ($s in $sets) {
    $rows = $thyao_lstm | Where-Object { $_.Feature_Set -eq $s }
    $counts += "$(Count-MC $rows)/9"
}
$total = Count-MC $thyao_lstm
$html += "<tr><td>THYAO</td><td>LSTM</td><td>h_t: $($counts[0])</td><td>tech: $($counts[1])</td><td>hist: $($counts[2])</td><td>close: $($counts[3])</td><td>$total/36</td><td>36</td><td>$([math]::Round($total/36*100,1))%</td></tr>"

# THYAO CNN
$counts = @()
foreach ($s in $sets) {
    $rows = $thyao_cnn | Where-Object { $_.Feature_Set -eq $s }
    $counts += "$(Count-MC $rows)/9"
}
$total = Count-MC $thyao_cnn
$html += "<tr><td>THYAO</td><td>CNN</td><td>h_t: $($counts[0])</td><td>tech: $($counts[1])</td><td>hist: $($counts[2])</td><td>close: $($counts[3])</td><td>$total/36</td><td>36</td><td>$([math]::Round($total/36*100,1))%</td></tr>"

# Emeklilik
$esets = @("full","technical","closing")
foreach ($fon in @("ALZ","AZS","AMZ")) {
    foreach ($info in @(@{name="LSTM";data=$em_lstm},@{name="CNN";data=$em_cnn})) {
        $counts = @()
        foreach ($s in $esets) {
            $rows = $info.data | Where-Object { $_.Fon -eq $fon -and $_.Feature_Set -eq $s }
            $counts += "$(Count-MC $rows)/9"
        }
        $total = Count-MC ($info.data | Where-Object { $_.Fon -eq $fon })
        $html += "<tr><td>$fon</td><td>$($info.name)</td><td>full: $($counts[0])</td><td>tech: $($counts[1])</td><td>close: $($counts[2])</td><td>-</td><td>$total/27</td><td>27</td><td>$([math]::Round($total/27*100,1))%</td></tr>"
    }
}
$html += '</table>'

# --- H: Eski vs Guncel MC ---
$html += '<h2 id="h">APPENDIX H: Eski vs Guncel MC Karsilastirmasi</h2>'
$html += '<table><tr><th>Varlik</th><th>Model</th><th>Eski MC</th><th>Guncel MC</th><th>Degisim</th><th>Yorum</th></tr>'

$pairs = @(
    @{v="THYAO";m="LSTM";old=$thyao_lstm_e;new=$thyao_lstm;n=36},
    @{v="THYAO";m="CNN";old=$thyao_cnn_e;new=$thyao_cnn;n=36}
)
foreach ($p in $pairs) {
    $o = Count-MC $p.old; $g = Count-MC $p.new; $d = $g - $o
    $ds = if($d -gt 0){"+" + $d}elseif($d -lt 0){"$d"}else{"0"}
    $y = if($d -lt 0){"Iyilesme (class_weight)"}elseif($d -gt 0){"Artis (closing kaynakli)"}else{"Degisim yok"}
    $html += "<tr><td>$($p.v)</td><td>$($p.m)</td><td>$o/$($p.n)</td><td>$g/$($p.n)</td><td>$ds</td><td>$y</td></tr>"
}

foreach ($fon in @("AZS","AMZ")) {
    foreach ($info in @(@{m="LSTM";old=$em_lstm_e;new=$em_lstm},@{m="CNN";old=$em_cnn_e;new=$em_cnn})) {
        $o = Count-MC ($info.old | Where-Object { $_.Fon -eq $fon })
        $g = Count-MC ($info.new | Where-Object { $_.Fon -eq $fon })
        $d = $g - $o
        $ds = if($d -gt 0){"+" + $d}elseif($d -lt 0){"$d"}else{"0"}
        $y = if($d -lt 0){"Iyilesme (class_weight)"}elseif($d -gt 0){"Artis"}else{"Degisim yok"}
        $html += "<tr><td>$fon</td><td>$($info.m)</td><td>$o/27</td><td>$g/27</td><td>$ds</td><td>$y</td></tr>"
    }
}
$html += '</table>'

# --- H2: Model Karsilastirma ---
$html += '<h2 id="h2">APPENDIX H2: En Iyi Sonuclar Karsilastirmasi</h2>'
$html += '<table><tr><th>Varlik</th><th>Model</th><th>En Iyi Acc</th><th>Konfigurasyon</th><th>Spec</th><th>MC?</th><th>Naive (ayni Out)</th><th>Naive''i Geciyor?</th></tr>'

# THYAO
$bestLstm = $thyao_lstm | Where-Object { -not (Is-MC $_) } | Sort-Object { [double]$_.Mean_Acc } -Descending | Select-Object -First 1
$bestCnn = $thyao_cnn | Where-Object { -not (Is-MC $_) } | Sort-Object { [double]$_.Mean_Acc } -Descending | Select-Object -First 1
$bestArima = $thyao_arima | Sort-Object { [double]$_.Test_Acc } -Descending | Select-Object -First 1
$naiveMap = @{}; foreach ($n in $thyao_naive) { $naiveMap[$n.Output] = $n.Naive_Acc }

$html += "<tr class='best'><td>THYAO</td><td>LSTM</td><td>$($bestLstm.Mean_Acc)</td><td>$($bestLstm.Feature_Set) In=$($bestLstm.Input) Out=$($bestLstm.Output)</td><td>$($bestLstm.Spec)</td><td>NO</td><td>$($naiveMap[$bestLstm.Output])</td><td>$(if([double]$bestLstm.Mean_Acc -gt [double]$naiveMap[$bestLstm.Output]){'YES'}else{'NO'})</td></tr>"
$html += "<tr><td>THYAO</td><td>CNN</td><td>$($bestCnn.Mean_Acc)</td><td>$($bestCnn.Feature_Set) In=$($bestCnn.Input) Out=$($bestCnn.Output)</td><td>$($bestCnn.Spec)</td><td>NO</td><td>$($naiveMap[$bestCnn.Output])</td><td>$(if([double]$bestCnn.Mean_Acc -gt [double]$naiveMap[$bestCnn.Output]){'YES'}else{'NO'})</td></tr>"
$html += "<tr><td>THYAO</td><td>ARIMA</td><td>$($bestArima.Test_Acc)</td><td>In=$($bestArima.Input) Out=$($bestArima.Output) d=$($bestArima.Best_d)</td><td>-</td><td>-</td><td>$($naiveMap[$bestArima.Output])</td><td>$(if([double]$bestArima.Test_Acc -gt [double]$naiveMap[$bestArima.Output]){'YES'}else{'NO'})</td></tr>"

# Emeklilik
$naiveEMap = @{}; foreach ($n in $em_naive) { $naiveEMap["$($n.Fon)_$($n.Output)"] = $n.Naive_Acc }
foreach ($fon in @("AZS","AMZ")) {
    $fRows = $em_lstm | Where-Object { $_.Fon -eq $fon -and -not (Is-MC $_) }
    if ($fRows) {
        $best = $fRows | Sort-Object { [double]$_.Mean_Acc } -Descending | Select-Object -First 1
        $nk = "$($fon)_$($best.Output)"
        $nv = if($naiveEMap.ContainsKey($nk)){$naiveEMap[$nk]}else{"-"}
        $cls = if([double]$best.Mean_Acc -gt [double]$nv){' class="best"'}else{""}
        $html += "<tr$cls><td>$fon</td><td>LSTM</td><td>$($best.Mean_Acc)</td><td>$($best.Feature_Set) In=$($best.Input) Out=$($best.Output)</td><td>$($best.Spec)</td><td>NO</td><td>$nv</td><td>$(if([double]$best.Mean_Acc -gt [double]$nv){'YES - NAIVE''I GECIYOR!'}else{'NO'})</td></tr>"
    }
    $fRows = $em_cnn | Where-Object { $_.Fon -eq $fon -and -not (Is-MC $_) }
    if ($fRows) {
        $best = $fRows | Sort-Object { [double]$_.Mean_Acc } -Descending | Select-Object -First 1
        $nk = "$($fon)_$($best.Output)"
        $nv = if($naiveEMap.ContainsKey($nk)){$naiveEMap[$nk]}else{"-"}
        $html += "<tr><td>$fon</td><td>CNN</td><td>$($best.Mean_Acc)</td><td>$($best.Feature_Set) In=$($best.Input) Out=$($best.Output)</td><td>$($best.Spec)</td><td>NO</td><td>$nv</td><td>$(if([double]$best.Mean_Acc -gt [double]$nv){'YES'}else{'NO'})</td></tr>"
    }
}
$html += '</table>'

$html += '<hr><p class="meta">Rapor sonu. Tum veriler CSV dosyalarindan otomatik olarak cekilmistir. Hicbir elle veri girisi yapilmamistir.</p>'
$html += '</body></html>'

$outHtml = "$base\Literatür+Kodlar\APPENDIX_TABLOLARI_OTOMATIK.html"
$html | Out-File -FilePath $outHtml -Encoding UTF8
Write-Host "TAMAMLANDI: $outHtml"
Write-Host "Boyut: $((Get-Item $outHtml).Length) byte"
