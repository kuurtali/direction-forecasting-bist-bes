# -*- coding: utf-8 -*-
"""
02_Akademik_Kanıtlar klasörü — tam denetim scripti
CSV ground-truth ile karşılaştırma + iç tutarlılık kontrolü
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import glob
import os
import re
import zipfile

ERRORS = []
WARNS  = []
OKAYS  = []

def ok(msg):
    OKAYS.append(msg)
    print(f"  [OK]   {msg}")

def err(msg):
    ERRORS.append(msg)
    print(f"  [HATA] {msg}")

def warn(msg):
    WARNS.append(msg)
    print(f"  [UYAR] {msg}")

# ── Dizinler ──────────────────────────────────────────────────────────────────
base = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26  = [os.path.join(base,s) for s in os.listdir(base) if '2026' in s][0]
D22  = [os.path.join(base,s) for s in os.listdir(base) if '2022' in s][0]

def L(f, b=None):
    return pd.read_csv(os.path.join(b or D26, f))

# ── CSV'leri yükle ────────────────────────────────────────────────────────────
lstm  = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn   = L('EMEKLILIK_CNN_sonuclar.csv')
naive = L('EMEKLILIK_NAIVE_baseline.csv')
arima = L('EMEKLILIK_ARIMA_sonuclar.csv')
lt    = L('LSTM_sonuclar_FINAL.csv')
ct    = L('CNN_sonuclar_FINAL.csv')
at_   = L('ARIMA_sonuclar.csv')
nt    = L('NAIVE_baseline.csv')
lt22  = L('LSTM_sonuclar_FINAL_eski.csv', D22)
ct22  = L('CNN_sonuclar_FINAL_eski.csv', D22)
at22  = L('ARIMA_sonuclar_eski.csv', D22)

def is_mc(r):
    s, se = r.get('Spec', 1), r.get('Sens', 1)
    return pd.isna(s) or s == 0 or pd.isna(se) or se == 0

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 1: CSV DOSYASI İÇ TUTARLILIK")
print("="*70)

# 1a. Satır sayıları
expected_rows = {
    'EMEKLILIK_LSTM_sonuclar.csv': 81,  # 3 fon * 27
    'EMEKLILIK_CNN_sonuclar.csv':  81,
    'EMEKLILIK_NAIVE_baseline.csv': 9,  # 3 fon * 3 output
    'EMEKLILIK_ARIMA_sonuclar.csv': 27, # 3 fon * 9
    'LSTM_sonuclar_FINAL.csv': 36,       # 4 fset * 9
    'CNN_sonuclar_FINAL.csv':  36,
    'ARIMA_sonuclar.csv':       9,
    'NAIVE_baseline.csv':       9,
}
for fname, exp in expected_rows.items():
    b = D22 if 'eski' in fname else D26
    df = pd.read_csv(os.path.join(b, fname))
    if len(df) == exp:
        ok(f"{fname}: {len(df)} satır ✓")
    else:
        err(f"{fname}: Beklenen={exp}, Gerçek={len(df)}")

# 1b. Mean_Acc = mean(Seed_23, Seed_27, Seed_98) kontrolü
print("\n--- Mean_Acc = (Seed_23+Seed_27+Seed_98)/3 doğrulaması ---")
for name, df in [('LSTM(BES)', lstm), ('CNN(BES)', cnn), ('LSTM(THYAO)', lt), ('CNN(THYAO)', ct)]:
    if all(c in df.columns for c in ['Seed_23','Seed_27','Seed_98','Mean_Acc']):
        calc = (df['Seed_23'] + df['Seed_27'] + df['Seed_98']) / 3
        diff = (calc - df['Mean_Acc']).abs()
        bad = diff[diff > 0.001]
        if len(bad) == 0:
            ok(f"{name}: Tüm {len(df)} satırda Mean_Acc = seed ortalaması ✓")
        else:
            for idx in bad.index:
                err(f"{name} satır {idx}: Mean_Acc={df.loc[idx,'Mean_Acc']:.4f}, calc={calc[idx]:.4f}, fark={diff[idx]:.4f}")

# 1c. Değer aralığı kontrolü
print("\n--- Değer aralığı [0,1] kontrolü ---")
for name, df in [('LSTM(BES)', lstm), ('CNN(BES)', cnn), ('LSTM(THYAO)', lt), ('CNN(THYAO)', ct)]:
    for col in ['Mean_Acc','F1','Sens','Spec']:
        if col in df.columns:
            sub = df[col].dropna()
            bad = sub[(sub < 0) | (sub > 1)]
            if len(bad) > 0:
                err(f"{name}.{col}: Aralık dışı değer: {list(bad)[:3]}")
            else:
                ok(f"{name}.{col}: Tüm değerler [0,1] ✓")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 2: GROUND-TRUTH SAYILAR — KRİTİK DEĞERLERİ DOĞRULA")
print("="*70)

# Şampiyon değerleri
champions = [
    # (label, fon/fset, df, filters, metric, expected, tol)
    ("AMZ LSTM [full/2/3] Mean_Acc", lstm,
     {'Fon':'AMZ','Feature_Set':'full','Input':2,'Output':3}, 'Mean_Acc', 0.8021, 0.001),
    ("AMZ LSTM [full/2/3] Sens",     lstm,
     {'Fon':'AMZ','Feature_Set':'full','Input':2,'Output':3}, 'Sens', 0.84, 0.005),
    ("AMZ LSTM [full/2/3] Spec",     lstm,
     {'Fon':'AMZ','Feature_Set':'full','Input':2,'Output':3}, 'Spec', 0.8571, 0.005),
    ("AMZ LSTM [full/2/3] F1",       lstm,
     {'Fon':'AMZ','Feature_Set':'full','Input':2,'Output':3}, 'F1', 0.8936, 0.005),
    ("AZS CNN [tech/4/3] Mean_Acc",  cnn,
     {'Fon':'AZS','Feature_Set':'technical','Input':4,'Output':3}, 'Mean_Acc', 0.7556, 0.002),
    ("AZS CNN [tech/4/3] Sens",      cnn,
     {'Fon':'AZS','Feature_Set':'technical','Input':4,'Output':3}, 'Sens', 0.9091, 0.005),
    ("AZS CNN [tech/4/3] Spec",      cnn,
     {'Fon':'AZS','Feature_Set':'technical','Input':4,'Output':3}, 'Spec', 0.625, 0.005),
    ("AZS LSTM [full/2/5] Mean_Acc", lstm,
     {'Fon':'AZS','Feature_Set':'full','Input':2,'Output':5}, 'Mean_Acc', 0.6889, 0.002),
    ("THYAO LSTM [hist_tech/4/3] Acc", lt,
     {'Feature_Set':'hist_tech','Input':4,'Output':3}, 'Mean_Acc', 0.5756, 0.002),
    ("THYAO CNN [hist_tech/2/3] Acc",  ct,
     {'Feature_Set':'hist_tech','Input':2,'Output':3}, 'Mean_Acc', 0.5397, 0.002),
    ("THYAO ARIMA [In6/Out3] Acc",     at_,
     {'Input':6,'Output':3}, 'Test_Acc', 0.5578, 0.002),
    ("AMZ Naive Out=3",               naive,
     {'Fon':'AMZ','Output':3}, 'Naive_Acc', 0.7879, 0.001),
    ("AZS Naive Out=5",               naive,
     {'Fon':'AZS','Output':5}, 'Naive_Acc', 0.9032, 0.001),
    ("THYAO Naive Out=5",             nt,
     {'Output':5}, 'Naive_Acc', 0.7973, 0.001),
]

for label, df, filters, col, exp, tol in champions:
    sub = df.copy()
    for k, v in filters.items():
        sub = sub[sub[k] == v]
    if len(sub) == 0:
        err(f"{label}: CSV'de satır bulunamadı!")
    else:
        val = sub.iloc[0][col]
        if abs(val - exp) <= tol:
            ok(f"{label}: {val:.4f} ≈ {exp} ✓")
        else:
            err(f"{label}: CSV={val:.4f}, Beklenen={exp}, fark={abs(val-exp):.4f}")

# MC sayıları
print("\n--- MC Sayı Kontrolü ---")
mc_expected = [
    ('ALZ','LSTM',lstm,27), ('ALZ','CNN',cnn,27),
    ('AZS','LSTM',lstm,13), ('AZS','CNN',cnn,9),
    ('AMZ','LSTM',lstm,10), ('AMZ','CNN',cnn,9),
]
for fon, model, df, exp in mc_expected:
    cnt = df[df['Fon']==fon].apply(is_mc, axis=1).sum()
    if cnt == exp:
        ok(f"MC {fon} {model}: {cnt}/27 ✓")
    else:
        err(f"MC {fon} {model}: CSV={cnt}/27, Beklenen={exp}/27")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 3: FINAL_KANIT_RAPORU.txt vs CSV")
print("="*70)

kanit_path = os.path.join(base, 'FINAL_KANIT_RAPORU.txt')
with open(kanit_path, encoding='utf-8', errors='replace') as f:
    kanit = f.read()

# Anahtar sayıları metinde ara
checks_kanit = [
    ("THYAO LSTM best %57.56", "57.56"),
    ("THYAO CNN best %53.97",  "53.97"),
    ("THYAO ARIMA best %55.78","55.78"),
    ("AMZ LSTM best %80.21",   "80.21"),
    ("AZS CNN best %75.56",    "75.56"),
    ("AMZ Naive Out=3 %78.79", "78.79"),
    ("AMZ Naive Out=5 %83.87", "83.87"),
    ("THYAO Naive Out=5 %79.73","79.73"),
    ("AZS Naive Out=5 %90.32", "90.32"),
    ("MC THYAO LSTM 12/36",    "12/36"),
    ("MC AZS LSTM 13/27",      "13/27"),
    ("MC AZS CNN 9/27",        "9/27"),
    ("MC AMZ LSTM 10/27",      "10/27"),
    ("MC AMZ CNN 9/27",        "9/27"),
]
for label, token in checks_kanit:
    if token in kanit:
        ok(f"FINAL_KANIT_RAPORU: '{token}' mevcut ✓")
    else:
        err(f"FINAL_KANIT_RAPORU: '{token}' bulunamadı!")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 4: MC_KANIT_RAPORU.txt vs CSV")
print("="*70)

mc_path = os.path.join(base, 'MC_KANIT_RAPORU.txt')
with open(mc_path, encoding='utf-8', errors='replace') as f:
    mc_txt = f.read()

mc_tokens = [
    ("THYAO LSTM eski 16/36",  "TOPLAM MC: 16 / 36"),
    ("THYAO CNN eski 8/36",    "TOPLAM MC: 8 / 36"),
    ("THYAO LSTM 2026 12/36",  "TOPLAM MC: 12 / 36"),
    ("THYAO CNN 2026 9/36",    "TOPLAM MC: 9 / 36"),
    ("ALZ LSTM 27/27",         "TOPLAM MC: 27 / 27"),
    ("AZS LSTM eski 19/27",    "TOPLAM MC: 19 / 27"),
    ("AZS CNN guncel 9/27",    "TOPLAM MC: 9 / 27"),
    ("AMZ LSTM eski 12/27",    "TOPLAM MC: 12 / 27"),
    ("AMZ LSTM guncel 10/27",  "TOPLAM MC: 10 / 27"),
    ("AMZ CNN eski 15/27",     "TOPLAM MC: 15 / 27"),
]
for label, token in mc_tokens:
    if token in mc_txt:
        ok(f"MC_KANIT: '{label}' doğru ✓")
    else:
        err(f"MC_KANIT: '{label}' ({token}) bulunamadı!")

# Ayrıca MC sayılarını 2022 CSV ile doğrula
print("\n--- 2022 eski CSV MC doğrulaması ---")
mc_22_expected = [
    ('THYAO','LSTM',lt22,16), ('THYAO','CNN',ct22,8),
]
for varlık, model, df, exp in mc_22_expected:
    cnt = df.apply(is_mc, axis=1).sum()
    if cnt == exp:
        ok(f"MC {varlık} {model} 2022: {cnt}/36 ✓")
    else:
        err(f"MC {varlık} {model} 2022: CSV={cnt}/36, Beklenen={exp}/36")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 5: CSV_TUM_SONUCLAR.html — Anahtar Sayı Kontrolü")
print("="*70)

html_path = os.path.join(base, 'CSV_TUM_SONUCLAR.html')
if os.path.exists(html_path):
    with open(html_path, encoding='utf-8', errors='replace') as f:
        html_txt = f.read()
    html_checks = [
        ("AMZ LSTM 80.21",   "0.8021"),
        ("AZS CNN 75.56",    "0.7556"),
        ("AMZ Naive 78.79",  "0.7879"),
        ("THYAO LSTM 57.56", "0.5756"),
    ]
    for label, token in html_checks:
        if token in html_txt:
            ok(f"CSV_TUM_SONUCLAR.html: {label} ({token}) mevcut ✓")
        else:
            warn(f"CSV_TUM_SONUCLAR.html: {label} ({token}) bulunamadı — yeniden üretilmeli olabilir")
else:
    warn("CSV_TUM_SONUCLAR.html bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 6: APPENDIX_TABLOLARI_OTOMATIK.html — Anahtar Sayı Kontrolü")
print("="*70)

app_html = os.path.join(base, 'APPENDIX_TABLOLARI_OTOMATIK.html')
if os.path.exists(app_html):
    with open(app_html, encoding='utf-8', errors='replace') as f:
        app_txt = f.read()
    app_checks = [
        ("AMZ LSTM Acc 0.8021", "0.8021"),
        ("AMZ LSTM Sens 0.84",  "0.8400"),
        ("AMZ LSTM Spec 0.8571","0.8571"),
        ("AZS CNN 0.7556",      "0.7556"),
        ("AMZ Naive 0.7879",    "0.7879"),
    ]
    for label, token in app_checks:
        if token in app_txt:
            ok(f"APPENDIX_OTOMATIK.html: {label} ✓")
        else:
            warn(f"APPENDIX_OTOMATIK.html: {label} ({token}) bulunamadı")
else:
    warn("APPENDIX_TABLOLARI_OTOMATIK.html bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 7: DOC3 (Model Karşılaştırma Tabloları) — DOCX İçerik Kontrolü")
print("="*70)

doc3_path = os.path.join(base, 'DOC3 Model Karsilastirma Tablolari.docx')
if os.path.exists(doc3_path):
    try:
        with zipfile.ZipFile(doc3_path) as z:
            xml = z.read('word/document.xml').decode('utf-8', errors='replace')
        doc3_txt = re.sub(r'<[^>]+>', ' ', xml)
        doc3_txt = re.sub(r'\s+', ' ', doc3_txt)
        doc3_checks = [
            ("AMZ LSTM 80.21", "80.21"),
            ("AZS CNN 75.56",  "75.56"),
            ("THYAO LSTM 57.56","57.56"),
        ]
        for label, token in doc3_checks:
            if token in doc3_txt:
                ok(f"DOC3: {label} ({token}) mevcut ✓")
            else:
                warn(f"DOC3: {label} ({token}) bulunamadı")
    except Exception as e:
        warn(f"DOC3 okunamadı: {e}")
else:
    warn("DOC3 bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 8: ALZ_AZS_AMZ_Haftalik.xlsx — Ham Veri Satır Sayısı")
print("="*70)

xlsx_path = os.path.join(base, 'ALZ_AZS_AMZ_Haftalik.xlsx')
if os.path.exists(xlsx_path):
    try:
        xls = pd.ExcelFile(xlsx_path)
        for sh in xls.sheet_names:
            df_sh = pd.read_excel(xlsx_path, sheet_name=sh)
            print(f"  Sheet '{sh}': {len(df_sh)} satır, {len(df_sh.columns)} sütun")
        # PROJECT_REPORT beklentisi: ALZ=249, AZS=261, AMZ=262
        expected_hafta = {'ALZ': 249, 'AZS': 261, 'AMZ': 262}
        for sh in xls.sheet_names:
            df_sh = pd.read_excel(xlsx_path, sheet_name=sh).dropna(subset=[df_sh.columns[0]])
            fon = sh.upper() if sh.upper() in expected_hafta else None
            if fon and fon in expected_hafta:
                if len(df_sh) == expected_hafta[fon]:
                    ok(f"ALZ_AZS_AMZ {fon}: {len(df_sh)} hafta ✓")
                else:
                    warn(f"ALZ_AZS_AMZ {fon}: {len(df_sh)} satır, beklenen {expected_hafta[fon]}")
    except Exception as e:
        warn(f"ALZ_AZS_AMZ_Haftalik.xlsx okunamadı: {e}")
else:
    warn("ALZ_AZS_AMZ_Haftalik.xlsx bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 9: 2018-2022 CSV'leri — İÇ TUTARLILIK")
print("="*70)

eski_files = {
    'LSTM_sonuclar_FINAL_eski.csv': (lt22, 36),
    'CNN_sonuclar_FINAL_eski.csv':  (ct22, 36),
    'ARIMA_sonuclar_eski.csv':      (at22, 9),
}
for fname, (df, exp_rows) in eski_files.items():
    if len(df) == exp_rows:
        ok(f"{fname}: {len(df)} satır ✓")
    else:
        err(f"{fname}: {len(df)} satır, beklenen {exp_rows}")

# Mean_Acc tutarlılığı eski THYAO CSV
for name, df in [('LSTM_eski', lt22), ('CNN_eski', ct22)]:
    if all(c in df.columns for c in ['Seed_23','Seed_27','Seed_98','Mean_Acc']):
        calc = (df['Seed_23'] + df['Seed_27'] + df['Seed_98']) / 3
        diff = (calc - df['Mean_Acc']).abs()
        bad  = diff[diff > 0.001]
        if len(bad) == 0:
            ok(f"{name}: Mean_Acc = seed ortalaması ✓")
        else:
            for idx in bad.index:
                err(f"{name} satır {idx}: Mean_Acc={df.loc[idx,'Mean_Acc']:.4f}, hesap={calc[idx]:.4f}")

# eski CSV'den bazı bilinen değerler
eski_checks = [
    ("THYAO LSTM eski best (hist2_Out5)", lt22,
     {'Feature_Set':'historical','Input':2,'Output':5}, 'Mean_Acc', 0.7416, 0.002),
    ("THYAO CNN eski best (closing6_Out5)", ct22,
     {'Feature_Set':'closing','Input':6,'Output':5}, 'Mean_Acc', 0.7356, 0.002),
]
print("\n--- 2022 eski CSV spot doğrulama ---")
for label, df, filters, col, exp, tol in eski_checks:
    sub = df.copy()
    for k, v in filters.items():
        sub = sub[sub[k] == v]
    if len(sub) == 0:
        warn(f"{label}: Satır bulunamadı")
    else:
        val = sub.iloc[0][col]
        if abs(val - exp) <= tol:
            ok(f"{label}: {val:.4f} ✓")
        else:
            err(f"{label}: CSV={val:.4f}, Beklenen={exp}")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("BÖLÜM 10: EMEKLILIK CSV çapraz — eski vs yeni MC karşılaştırması")
print("="*70)

emk_eski_files = {
    'EMEKLILIK_LSTM_sonuclar_eski.csv': 81,
    'EMEKLILIK_CNN_sonuclar_eski.csv':  81,
    'EMEKLILIK_NAIVE_baseline_eski.csv': 9,
    'EMEKLILIK_ARIMA_sonuclar_eski.csv': 27,
}
for fname, exp_rows in emk_eski_files.items():
    fpath = os.path.join(D22, fname)
    if os.path.exists(fpath):
        df_e = pd.read_csv(fpath)
        if len(df_e) == exp_rows:
            ok(f"{fname}: {len(df_e)} satır ✓")
        else:
            err(f"{fname}: {len(df_e)} satır, beklenen {exp_rows}")
    else:
        warn(f"{fname}: Dosya yok (D22 klasöründe aranıyor)")

# eski emeklilik MC'leri
lstm_eski = pd.read_csv(os.path.join(D22, 'EMEKLILIK_LSTM_sonuclar_eski.csv'))
cnn_eski  = pd.read_csv(os.path.join(D22, 'EMEKLILIK_CNN_sonuclar_eski.csv'))

eski_mc_exp = [
    ('AZS','LSTM',lstm_eski,19), ('AZS','CNN',cnn_eski,19),
    ('AMZ','LSTM',lstm_eski,12), ('AMZ','CNN',cnn_eski,15),
]
print("\n--- Eski emeklilik MC doğrulaması ---")
for fon, model, df_e, exp in eski_mc_exp:
    cnt = df_e[df_e.iloc[:,0]==fon].apply(is_mc, axis=1).sum()
    if cnt == exp:
        ok(f"MC {fon} {model} ESKİ: {cnt}/27 ✓")
    else:
        err(f"MC {fon} {model} ESKİ: CSV={cnt}/27, Beklenen={exp}/27")

# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ÖZET")
print("="*70)
print(f"\n  OK:    {len(OKAYS)}")
print(f"  UYARI: {len(WARNS)}")
print(f"  HATA:  {len(ERRORS)}")

if ERRORS:
    print("\n--- HATALAR ---")
    for e in ERRORS:
        print(f"  {e}")
if WARNS:
    print("\n--- UYARILAR ---")
    for w in WARNS:
        print(f"  {w}")

if not ERRORS:
    print("\n✅ BÜTÜN KRİTİK KONTROLLER BAŞARILI")
    print("   02_Akademik_Kanıtlar klasörü CSV ground-truth ile %100 uyumlu.")
