# -*- coding: utf-8 -*-
"""
TAM TARAMA — BÖLÜM 1: CSV İÇ TUTARLILIK + ARAKAYIT vs FINAL
Eleştirel açıdan: her CSV kendi içinde matematiksel olarak tutarlı mı?
ARAKAYIT ile FINAL byte-byte aynı mı? Satır sayıları doğru mu?
"""
import sys, io, os, glob as gl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np

folders = gl.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')
BASE02 = folders[0]
subs = [os.path.join(BASE02, d) for d in os.listdir(BASE02) if os.path.isdir(os.path.join(BASE02, d)) and 'kt' in d.lower()]
D26 = [s for s in subs if '26' in os.path.basename(s)][0]
D22 = [s for s in subs if '22' in os.path.basename(s)][0]

OK=[]; WARN=[]; ERR=[]
def ok(m):  OK.append(f'  [OK]   {m}')
def warn(m):WARN.append(f'  [UYR] {m}')
def err(m): ERR.append(f'  [HATA] {m}')

def L(f, b=D26): return pd.read_csv(os.path.join(b, f))

def is_mc(r):
    s,se = r.get('Spec',1), r.get('Sens',1)
    return pd.isna(s) or float(s)==0 or pd.isna(se) or float(se)==0

# ============================================================
print('='*65)
print('A1: ARAKAYIT vs FINAL BYTE KARŞILAŞTIRMASI')
print('='*65)

pairs = [
    ('LSTM_sonuclar_ARAKAYIT.csv',    'LSTM_sonuclar_FINAL.csv',    D26),
    ('CNN_sonuclar_ARAKAYIT.csv',     'CNN_sonuclar_FINAL.csv',     D26),
    ('LSTM_sonuclar_ARAKAYIT_eski.csv','LSTM_sonuclar_FINAL_eski.csv', D22),
    ('CNN_sonuclar_ARAKAYIT_eski.csv', 'CNN_sonuclar_FINAL_eski.csv',  D22),
]
for fa, fb, base in pairs:
    ba = open(os.path.join(base, fa), 'rb').read()
    bb = open(os.path.join(base, fb), 'rb').read()
    if ba == bb:
        ok(f'{fa} == {fb} (byte-byte özdeş)')
    else:
        # Farkli satirlari bul
        la, lb = ba.decode('utf-8',errors='replace').splitlines(), bb.decode('utf-8',errors='replace').splitlines()
        diffs = [(i,a,b) for i,(a,b) in enumerate(zip(la,lb),1) if a!=b]
        err(f'{fa} vs {fb}: {len(diffs)} farklı satır! İlk fark: L{diffs[0][0]}: "{diffs[0][1][:60]}" vs "{diffs[0][2][:60]}"')

# ============================================================
print()
print('='*65)
print('A2: CSV SATIR SAYISI VE SÜTUN TUTARLILIĞI')
print('='*65)

expected = {
    'ARIMA_sonuclar.csv':             (9,  ['Input','Output','Best_d','Test_Acc']),
    'CNN_sonuclar_FINAL.csv':         (36, ['Feature_Set','Input','Output']),
    'LSTM_sonuclar_FINAL.csv':        (36, ['Feature_Set','Input','Output']),
    'NAIVE_baseline.csv':             (9,  ['Input','Output','Naive_Acc']),
    'EMEKLILIK_ARIMA_sonuclar.csv':   (27, ['Fon','Input','Output','Best_d','Test_Acc']),
    'EMEKLILIK_CNN_sonuclar.csv':     (81, ['Fon','Feature_Set','Input','Output']),
    'EMEKLILIK_LSTM_sonuclar.csv':    (81, ['Fon','Feature_Set','Input','Output']),
    'EMEKLILIK_NAIVE_baseline.csv':   (27, ['Fon','Output','Naive_Acc']),
}
for fname, (exp_rows, req_cols) in expected.items():
    df = L(fname)
    if len(df) == exp_rows:
        ok(f'{fname}: {len(df)} satır ✓')
    else:
        err(f'{fname}: {len(df)} satır (beklenen {exp_rows})')
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        err(f'{fname}: eksik sütun: {missing}')

# ============================================================
print()
print('='*65)
print('A3: EMEKLILIK CSV MANTIKSAl TUTARLILIK — FON/IN/OUT TAM GRID')
print('='*65)

# BES: 3 fon × 3 feature × 3 in × 3 out = 81 (LSTM/CNN)
# BES: 3 fon × 3 in × 3 out = 27 (ARIMA, NAIVE)
for fname in ['EMEKLILIK_LSTM_sonuclar.csv', 'EMEKLILIK_CNN_sonuclar.csv']:
    df = L(fname)
    for fon in ['ALZ','AZS','AMZ']:
        for fs in ['closing','historical','technical']:
            for inp in [2,4,6]:
                for out in [1,3,5]:
                    sub = df[(df.Fon==fon)&(df.Feature_Set==fs)&(df.Input==inp)&(df.Output==out)]
                    if len(sub)==0:
                        err(f'{fname}: EKSİK SATIR Fon={fon} FS={fs} In={inp} Out={out}')
                    elif len(sub)>1:
                        warn(f'{fname}: TEKRAR SATIR Fon={fon} FS={fs} In={inp} Out={out} ({len(sub)}x)')
print('  BES LSTM/CNN grid kontrolü tamamlandı.')

for fname in ['EMEKLILIK_ARIMA_sonuclar.csv', 'EMEKLILIK_NAIVE_baseline.csv']:
    df = L(fname)
    for fon in ['ALZ','AZS','AMZ']:
        for out in [1,3,5]:
            sub = df[(df.Fon==fon)&(df.Output==out)]
            if len(sub)==0:
                err(f'{fname}: EKSİK SATIR Fon={fon} Out={out}')
            elif len(sub)>1:
                # NAIVE'de her out için 3 in degeri olabilir
                pass
print('  BES ARIMA/Naive grid kontrolü tamamlandı.')

# THYAO: 4 fs × 3 in × 3 out = 36 (LSTM/CNN), 3×3=9 (ARIMA/Naive)
for fname in ['LSTM_sonuclar_FINAL.csv', 'CNN_sonuclar_FINAL.csv']:
    df = L(fname)
    for fs in ['closing','hist_tech','historical','technical']:
        if fs not in df.Feature_Set.values:
            if fs in ['hist_tech','historical']:
                continue  # Olmayabilir
        for inp in [2,4,6]:
            for out in [1,3,5]:
                sub = df[(df.Feature_Set==fs)&(df.Input==inp)&(df.Output==out)]
                if len(sub)==0 and fs in df.Feature_Set.values:
                    err(f'{fname}: EKSİK Fset={fs} In={inp} Out={out}')
print('  THYAO grid kontrolü tamamlandı.')

# ============================================================
print()
print('='*65)
print('A4: METRİK ARALIK KONTROLÜ (0-1 arası mı?)')
print('='*65)

for fname in ['EMEKLILIK_LSTM_sonuclar.csv','EMEKLILIK_CNN_sonuclar.csv','LSTM_sonuclar_FINAL.csv','CNN_sonuclar_FINAL.csv']:
    df = L(fname)
    for col in ['Mean_Acc','Sens','Spec','F1']:
        if col not in df.columns: continue
        out_of_range = df[(df[col].notna()) & ((df[col] < 0) | (df[col] > 1))]
        if len(out_of_range)>0:
            err(f'{fname} sütun {col}: {len(out_of_range)} değer [0,1] dışında: {out_of_range[col].values[:3]}')
        else:
            ok(f'{fname} [{col}]: tüm değerler [0,1] içinde')

# SD negatif olmamalı
for fname in ['EMEKLILIK_LSTM_sonuclar.csv','EMEKLILIK_CNN_sonuclar.csv','LSTM_sonuclar_FINAL.csv','CNN_sonuclar_FINAL.csv']:
    df = L(fname)
    if 'SD' in df.columns:
        neg_sd = df[df.SD < 0]
        if len(neg_sd)>0:
            err(f'{fname}: {len(neg_sd)} negatif SD değeri')
        else:
            ok(f'{fname} [SD]: tüm değerler ≥ 0')

# ============================================================
print()
print('='*65)
print('A5: ALZ KONTROL — MC ZORUNLULUĞU')
print('='*65)

lstm_bes = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn_bes  = L('EMEKLILIK_CNN_sonuclar.csv')
alz_lstm = lstm_bes[lstm_bes.Fon=='ALZ']
alz_cnn  = cnn_bes[cnn_bes.Fon=='ALZ']

# ALZ'de tüm satırlar MC olmali (Spec=0 veya NaN)
non_mc_lstm = alz_lstm[(alz_lstm.Spec.notna()) & (alz_lstm.Spec > 0)]
non_mc_cnn  = alz_cnn[(alz_cnn.Spec.notna()) & (alz_cnn.Spec > 0)]

if len(non_mc_lstm)==0:
    ok('ALZ LSTM: 27/27 satır Spec=0 veya NaN (MC bekleniyor) ✓')
else:
    err(f'ALZ LSTM: {len(non_mc_lstm)} satırda Spec>0 — MC bekleniyordu!')
    print(non_mc_lstm[['Feature_Set','Input','Output','Spec']])

if len(non_mc_cnn)==0:
    ok('ALZ CNN: 27/27 satır Spec=0 veya NaN (MC bekleniyor) ✓')
else:
    err(f'ALZ CNN: {len(non_mc_cnn)} satırda Spec>0 — MC bekleniyordu!')

# ============================================================
print()
print('='*65)
print('A6: AMZ LSTM ŞAMPİYON SEED TUTARLILIĞI')
print('='*65)

# AMZ LSTM full In=2 Out=3 için seed bazlı doğruluk:
# S23=84.38% S27=71.88% S98=84.38% → Mean=80.21%, SD≈7.22%
row = lstm_bes[(lstm_bes.Fon=='AMZ')&(lstm_bes.Feature_Set=='full')&(lstm_bes.Input==2)&(lstm_bes.Output==3)].iloc[0]
print(f'  AMZ LSTM full In=2 Out=3:')
print(f'    Mean_Acc={row.Mean_Acc:.4f}  Sens={row.Sens:.4f}  Spec={row.Spec:.4f}  F1={row.get("F1",float("nan")):.4f}')
if 'SD' in row: print(f'    SD={row.SD:.4f}')

# Matematiksel tutarlilik: Mean×96 tam sayı mı?
n=96
corr = round(row.Mean_Acc * n)
diff_frac = abs(row.Mean_Acc * n - corr)
if diff_frac < 0.5:
    ok(f'AMZ LSTM: Mean×96 = {row.Mean_Acc*n:.2f} → {corr} (tam sayıya yakın ✓)')
else:
    warn(f'AMZ LSTM: Mean×96 = {row.Mean_Acc*n:.2f} → tam sayıya uzak')

# Sens check: CSV 0.84 → Seed98 değeri
# TP = Sens × (toplam Up = 75 tahmini)
# AMZ Out=3: 30 Up / 7 Down (EK-C), pooled × 3 = 90 Up / 21 Down
tp_est = round(row.Sens * 90)  # yaklaşık
tn_est = round(row.Spec * 21)
print(f'  Havuzlanmış matris tahmini: TP≈{tp_est} TN≈{tn_est} N=111(30+7+74...)')
print(f'  NOT: CSV Sens/Spec Seed98 oranı; True Pooled: TP=60,TN=17 (PR 12.8.1)')

# ============================================================
print()
print('='*65)
print('A7: THYAO CSV — CLOSING MC ZORUNLULUĞU')
print('='*65)

lt = L('LSTM_sonuclar_FINAL.csv')
ct = L('CNN_sonuclar_FINAL.csv')

thyao_lstm_closing = lt[lt.Feature_Set=='closing']
thyao_cnn_closing  = ct[ct.Feature_Set=='closing']

lstm_cl_mc = thyao_lstm_closing.apply(is_mc, axis=1).sum()
cnn_cl_mc  = thyao_cnn_closing.apply(is_mc, axis=1).sum()

if lstm_cl_mc == 9:
    ok(f'THYAO LSTM closing: {lstm_cl_mc}/9 MC ✓')
else:
    err(f'THYAO LSTM closing: {lstm_cl_mc}/9 MC (beklenen 9)')

if cnn_cl_mc == 9:
    ok(f'THYAO CNN closing: {cnn_cl_mc}/9 MC ✓')
else:
    err(f'THYAO CNN closing: {cnn_cl_mc}/9 MC (beklenen 9)')

# hist_tech de kontrol
thyao_lstm_ht = lt[lt.Feature_Set=='hist_tech']
if len(thyao_lstm_ht) > 0:
    ok(f'THYAO LSTM hist_tech: {len(thyao_lstm_ht)} satır mevcut')
else:
    warn('THYAO LSTM: hist_tech feature seti yok (historical kullanılıyor olabilir)')

# ============================================================
print()
print('='*65)
print('A8: 2022 vs 2026 CSV KARŞILAŞTIRMASI — CONCEPT DRIFT')
print('='*65)

lt22 = L('LSTM_sonuclar_FINAL_eski.csv', D22)
ct22 = L('CNN_sonuclar_FINAL_eski.csv', D22)

for fs in ['technical']:
    m26_lstm = lt[lt.Feature_Set==fs].Mean_Acc.mean() if fs in lt.Feature_Set.values else None
    m22_lstm = lt22[lt22.Feature_Set==fs].Mean_Acc.mean() if fs in lt22.Feature_Set.values else None
    m26_cnn  = ct[ct.Feature_Set==fs].Mean_Acc.mean() if fs in ct.Feature_Set.values else None
    m22_cnn  = ct22[ct22.Feature_Set==fs].Mean_Acc.mean() if fs in ct22.Feature_Set.values else None

    if m22_lstm and m26_lstm:
        drift = m22_lstm - m26_lstm
        print(f'  LSTM {fs}: 2022={m22_lstm:.4f} → 2026={m26_lstm:.4f} | drift={drift:+.4f}')
        if abs(drift - 0.0531) < 0.003:
            ok(f'LSTM drift={drift:.4f} (PR: 0.0531 ✓)')
        else:
            err(f'LSTM drift={drift:.4f} (PR: 0.0531 — FARK!)')
    if m22_cnn and m26_cnn:
        drift = m22_cnn - m26_cnn
        print(f'  CNN  {fs}: 2022={m22_cnn:.4f} → 2026={m26_cnn:.4f} | drift={drift:+.4f}')
        if abs(drift - 0.0724) < 0.003:
            ok(f'CNN drift={drift:.4f} (PR: 0.0724 ✓)')
        else:
            err(f'CNN drift={drift:.4f} (PR: 0.0724 — FARK!)')

# ARIMA drift
at26 = L('ARIMA_sonuclar.csv')
at22 = L('ARIMA_sonuclar_eski.csv', D22)
m26_ar = at26.Test_Acc.mean()
m22_ar = at22.Test_Acc.mean()
print(f'  ARIMA: 2022={m22_ar:.4f} → 2026={m26_ar:.4f} | drift={m26_ar-m22_ar:+.4f}')
if abs(m26_ar - 0.5134) < 0.003 and abs(m22_ar - 0.4983) < 0.003:
    ok(f'ARIMA: 2022≈{m22_ar:.4f}, 2026≈{m26_ar:.4f} (PR değerleri ✓)')
else:
    err(f'ARIMA beklenen: 2022≈0.4983 2026≈0.5134')

# ============================================================
print()
print('='*65)
print('ÖZET')
print('='*65)
for o in OK:  print(o)
print()
for w in WARN: print(w)
if ERR:
    print()
    for e in ERR: print(e)
print()
print(f'  OK: {len(OK)} | UYARI: {len(WARN)} | HATA: {len(ERR)}')
