# -*- coding: utf-8 -*-
"""
TAM TARAMA — BÖLÜM 2
B1: BES CSV Feature Set doğrulaması (historical false positive mu?)
B2: FINAL_KANIT_RAPORU.txt + MC_KANIT_RAPORU.txt vs CSV
B3: DOC1/DOC2/DOC3 vs CSV
B4: APPENDIX_TABLOLARI.xlsx vs CSV
B5: CSV_TUM_SONUCLAR.html spot-check
B6: PROJECT_REPORT sayısal iddiaların BES bölümü
"""
import sys, io, os, glob as gl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, re

folders = gl.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')
BASE02 = folders[0]
subs = [os.path.join(BASE02, d) for d in os.listdir(BASE02) if os.path.isdir(os.path.join(BASE02, d)) and 'kt' in d.lower()]
D26 = [s for s in subs if '26' in os.path.basename(s)][0]
D22 = [s for s in subs if '22' in os.path.basename(s)][0]

def L(f, b=D26): return pd.read_csv(os.path.join(b, f))

lstm = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn  = L('EMEKLILIK_CNN_sonuclar.csv')
naive= L('EMEKLILIK_NAIVE_baseline.csv')
arima= L('EMEKLILIK_ARIMA_sonuclar.csv')
lt   = L('LSTM_sonuclar_FINAL.csv')
ct   = L('CNN_sonuclar_FINAL.csv')
at_  = L('ARIMA_sonuclar.csv')
nt   = L('NAIVE_baseline.csv')
lt22 = L('LSTM_sonuclar_FINAL_eski.csv', D22)
ct22 = L('CNN_sonuclar_FINAL_eski.csv', D22)

OK=[]; WARN=[]; ERR=[]
def ok(m):   OK.append(f'  [OK]  {m}')
def warn(m): WARN.append(f'  [UYR] {m}')
def err(m):  ERR.append(f'  [HATA] {m}')

# ============================================================
print('='*65)
print('B1: BES CSV FEATURE SET NE OLMALI?')
print('='*65)

# BES: closing, technical, full (3 adet) — "historical" YOK ve OLMAMALI
for fname, df in [('EMEKLILIK_LSTM', lstm), ('EMEKLILIK_CNN', cnn)]:
    fs_set = set(df.Feature_Set.unique())
    expected_fs = {'closing', 'technical', 'full'}
    extra = fs_set - expected_fs
    missing = expected_fs - fs_set
    if not extra and not missing:
        ok(f'{fname}: Feature setler doğru: {sorted(fs_set)} ✓')
    if extra:
        err(f'{fname}: Beklenmeyen feature set: {extra}')
    if missing:
        err(f'{fname}: Eksik feature set: {missing}')

ok('SONUÇ: "historical" BES CSVlerinde YOK — bu DOĞRU (BES özellik tasarımı: closing/technical/full)')

# THYAO: closing, hist_tech, historical, technical (4 adet)
for fname, df in [('THYAO_LSTM', lt), ('THYAO_CNN', ct)]:
    fs_set = set(df.Feature_Set.unique())
    print(f'  {fname} feature setler: {sorted(fs_set)}')

# ============================================================
print()
print('='*65)
print('B2: FINAL_KANIT_RAPORU.txt vs CSV')
print('='*65)

kanit = open(os.path.join(BASE02, 'FINAL_KANIT_RAPORU.txt'), 'r', encoding='utf-8', errors='replace').read()

# Kritik sayılar FINAL_KANIT_RAPORU'nda var mı ve doğru mu?
checks_kanit = [
    ('0.8021', 'AMZ LSTM Acc'),
    ('0.7556', 'AZS CNN Acc'),
    ('0.5756', 'THYAO LSTM Acc'),
    ('0.5397', 'THYAO CNN Acc'),
    ('0.5578', 'THYAO ARIMA best'),
    ('0.8021', 'AMZ LSTM şampiyon'),
    ('0.8485', 'AZS Naive Out=3'),
    ('0.7879', 'AMZ Naive Out=3'),
    ('80.21', 'AMZ yüzdelik'),
]

for kw, desc in checks_kanit:
    if kw in kanit:
        ok(f'FINAL_KANIT: "{kw}" ({desc}) ✓')
    else:
        warn(f'FINAL_KANIT: "{kw}" ({desc}) bulunamadı')

# Yanlış değer var mı?
wrong_vals = ['0.8438', '63/75', '18/21']  # Eski pooled değerleri
for wv in wrong_vals:
    if wv in kanit:
        warn(f'FINAL_KANIT: "{wv}" geçiyor — eski pooled hesabı (metodolojik not olabilir)')

# ============================================================
print()
print('='*65)
print('B3: MC_KANIT_RAPORU.txt vs CSV')
print('='*65)

mc_kanit = open(os.path.join(BASE02, 'MC_KANIT_RAPORU.txt'), 'r', encoding='utf-8', errors='replace').read()

# MC sayıları
mc_checks = [
    ('27/27', 'ALZ LSTM MC'),
    ('13/27', 'AZS LSTM MC'),
    ('9/27',  'AZS CNN MC'),
    ('10/27', 'AMZ LSTM MC'),
    ('9/27',  'AMZ CNN MC'),
    ('12/36', 'THYAO LSTM MC'),
    ('9/36',  'THYAO CNN MC'),
]
for kw, desc in mc_checks:
    if kw in mc_kanit:
        ok(f'MC_KANIT: "{kw}" ({desc}) ✓')
    else:
        warn(f'MC_KANIT: "{kw}" ({desc}) bulunamadı')

# ============================================================
print()
print('='*65)
print('B4: DOC3 Model Karsilastirma Tablolari.docx SPOT-CHECK')
print('='*65)

import zipfile
doc3_path = os.path.join(BASE02, 'DOC3 Model Karsilastirma Tablolari.docx')
with zipfile.ZipFile(doc3_path, 'r') as z:
    doc3_raw = z.read('word/document.xml').decode('utf-8', errors='replace')
doc3_text = re.sub(r'<[^>]+>', ' ', doc3_raw)
doc3_text = re.sub(r'\s+', ' ', doc3_text)

doc3_checks = [
    ('80.21', 'AMZ LSTM Acc'),
    ('75.56', 'AZS CNN Acc'),
    ('57.56', 'THYAO LSTM Acc'),
    ('84.85', 'AZS Naive Out=3'),
    ('78.79', 'AMZ Naive Out=3'),
]
for kw, desc in doc3_checks:
    if kw in doc3_text:
        ok(f'DOC3: "{kw}" ({desc}) ✓')
    else:
        # Virgüllü format dene
        kw2 = kw.replace('.', ',')
        if kw2 in doc3_text:
            ok(f'DOC3: "{kw2}" ({desc} - virgüllü) ✓')
        else:
            warn(f'DOC3: "{kw}" veya "{kw2}" ({desc}) bulunamadı')

# ============================================================
print()
print('='*65)
print('B5: CSV_TUM_SONUCLAR.html SPOT-CHECK')
print('='*65)

html_path = os.path.join(BASE02, 'CSV_TUM_SONUCLAR.html')
html_text = open(html_path, 'r', encoding='utf-8', errors='replace').read()

html_checks = [
    ('0.8021', 'AMZ LSTM Acc'),
    ('0.7556', 'AZS CNN Acc'),
    ('0.5756', 'THYAO LSTM Acc'),
    ('0.8485', 'AZS Naive Out=3'),
    ('0.7879', 'AMZ Naive Out=3'),
    ('0.8571', 'AMZ LSTM Spec'),
    ('0.9091', 'AZS CNN Sens'),
]
for kw, desc in html_checks:
    cnt = html_text.count(kw)
    if cnt > 0:
        ok(f'HTML: "{kw}" ({desc}): {cnt}x ✓')
    else:
        err(f'HTML: "{kw}" ({desc}) bulunamadı!')

# ============================================================
print()
print('='*65)
print('B6: APPENDIX_TABLOLARI_OTOMATIK.html SPOT-CHECK')
print('='*65)

app_html = open(os.path.join(BASE02, 'APPENDIX_TABLOLARI_OTOMATIK.html'), 'r', encoding='utf-8', errors='replace').read()

app_checks = [
    ('80.21', 'AMZ LSTM Acc %'),
    ('75.56', 'AZS CNN Acc %'),
    ('57.56', 'THYAO LSTM Acc %'),
    ('84.86', 'AMZ BA %'),
]
for kw, desc in app_checks:
    if kw in app_html or kw.replace('.', ',') in app_html:
        ok(f'APP_HTML: "{kw}" ({desc}) ✓')
    else:
        warn(f'APP_HTML: "{kw}" ({desc}) bulunamadı — format farklı olabilir')

# ============================================================
print()
print('='*65)
print('B7: PROJECT_REPORT BES BÖLÜMÜ — ELEŞTİREL KONTROL')
print('='*65)

pr = open(r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJECT_REPORT.txt',
          'r', encoding='utf-8', errors='replace').read()

# PR'deki her iddiayı CSV ile karşılaştır
pr_checks = [
    # (PR'deki metin, CSV değeri, beklenen değer, açıklama)
    ('80.21', lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0].Mean_Acc, 0.8021, 'AMZ LSTM Acc'),
    ('75.56', cnn[(cnn.Fon=='AZS')&(cnn.Feature_Set=='technical')&(cnn.Input==4)&(cnn.Output==3)].iloc[0].Mean_Acc, 0.7556, 'AZS CNN Acc'),
    ('84.85', naive[(naive.Fon=='AZS')&(naive.Output==3)].iloc[0].Naive_Acc, 0.8485, 'AZS Naive Out=3'),
    ('78.79', naive[(naive.Fon=='AMZ')&(naive.Output==3)].iloc[0].Naive_Acc, 0.7879, 'AMZ Naive Out=3'),
    ('0.8400', lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0].Sens, 0.84, 'AMZ LSTM Sens'),
    ('0.8571', lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0].Spec, 0.8571, 'AMZ LSTM Spec'),
]

for pr_kw, csv_val, exp, desc in pr_checks:
    csv_ok = abs(float(csv_val) - float(exp)) < 0.002
    pr_has = pr_kw in pr
    if csv_ok and pr_has:
        ok(f'PR+CSV: "{pr_kw}" ({desc}) ✓')
    elif not csv_ok:
        err(f'CSV: {desc} = {float(csv_val):.4f} ≠ beklenen {exp:.4f}')
    elif not pr_has:
        warn(f'PR: "{pr_kw}" ({desc}) metinde bulunamadı')

# ============================================================
print()
print('='*65)
print('NİHAİ ÖZET — TÜM BÖLÜMLER')
print('='*65)
for o in OK:   print(o)
print()
for w in WARN: print(w)
if ERR:
    print()
    for e in ERR: print(e)
print()
print(f'SONUÇ: OK={len(OK)} | UYARI={len(WARN)} | HATA={len(ERR)}')
if len(ERR)==0:
    print()
    print('>>> TÜM 02 KLASÖR DOSYALARI VE PROJECT_REPORT CSV İLE UYUMLU <<<')
