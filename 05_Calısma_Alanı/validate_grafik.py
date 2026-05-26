# -*- coding: utf-8 -*-
"""Grafik <-> CSV <-> PROJECT_REPORT capraz dogrulama"""
import pandas as pd
import numpy as np
import glob
import os

base = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26  = [os.path.join(base,s) for s in os.listdir(base) if '2026' in s][0]
D22  = [os.path.join(base,s) for s in os.listdir(base) if '2022' in s][0]

def L(f, b=None):
    return pd.read_csv(os.path.join(b or D26, f))

lstm  = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn   = L('EMEKLILIK_CNN_sonuclar.csv')
naive = L('EMEKLILIK_NAIVE_baseline.csv')
arima = L('EMEKLILIK_ARIMA_sonuclar.csv')
lt    = L('LSTM_sonuclar_FINAL.csv')
ct    = L('CNN_sonuclar_FINAL.csv')
nt    = L('NAIVE_baseline.csv')
at_   = L('ARIMA_sonuclar.csv')
lt22  = L('LSTM_sonuclar_FINAL_eski.csv', D22)
ct22  = L('CNN_sonuclar_FINAL_eski.csv', D22)
at22  = L('ARIMA_sonuclar_eski.csv', D22)

def is_mc(r):
    s  = r.get('Spec', 1)
    se = r.get('Sens', 1)
    return pd.isna(s) or s == 0 or pd.isna(se) or se == 0

ERRORS  = []
OKAYS   = []

def chk(label, csv_val, report_val, tol=0.002):
    ok = abs(float(csv_val) - float(report_val)) <= tol
    tag = "OK" if ok else "HATA"
    line = f"[{tag}] {label}: CSV={float(csv_val):.4f}  Rapor={float(report_val):.4f}"
    if ok:
        OKAYS.append(line)
    else:
        ERRORS.append(line)
    print(line)

def chk_int(label, csv_val, report_val):
    ok = int(csv_val) == int(report_val)
    tag = "OK" if ok else "HATA"
    line = f"[{tag}] {label}: CSV={csv_val}  Rapor={report_val}"
    if ok:
        OKAYS.append(line)
    else:
        ERRORS.append(line)
    print(line)

# ─── 1. MC SAYILARI ───────────────────────────────────────────────────────────
print("\n=== 1. MC SAYILARI (Bolum 6.2 + G2) ===")
# Rapor: ALZ LSTM=27 CNN=27 | AZS LSTM=13 CNN=9 | AMZ LSTM=10 CNN=9
for fon, el, ec in [('ALZ', 27, 27), ('AZS', 13, 9), ('AMZ', 10, 9)]:
    lmc = lstm[lstm['Fon'] == fon].apply(is_mc, axis=1).sum()
    cmc = cnn[cnn['Fon']   == fon].apply(is_mc, axis=1).sum()
    chk_int(f"MC {fon} LSTM (/27)", lmc, el)
    chk_int(f"MC {fon} CNN  (/27)", cmc, ec)

# ─── 2. CLOSING SET MC (Bolum 9 + G3) ─────────────────────────────────────────
print("\n=== 2. CLOSING SET MC (Bolum 9) ===")
# AZS LSTM closing 9/9, AZS CNN closing 5/9, AMZ LSTM closing 9/9, AMZ CNN closing 7/9
for fon, model, df, exp in [
    ('AZS', 'LSTM', lstm, 9),
    ('AZS', 'CNN',  cnn,  5),
    ('AMZ', 'LSTM', lstm, 9),
    ('AMZ', 'CNN',  cnn,  7),
]:
    sub = df[(df['Fon'] == fon) & (df['Feature_Set'] == 'closing')]
    mc_cnt = sub.apply(is_mc, axis=1).sum()
    chk_int(f"Closing MC {fon} {model} (/9)", mc_cnt, exp)

# ─── 3. G3 MC ORANLARI (% hesabi) ─────────────────────────────────────────────
print("\n=== 3. G3 MC ORANLARI % (Bolum 9 + G3) ===")
# Grafik: closing LSTM=100% CNN=77.8% | technical LSTM=48.1% CNN=48.1% | full LSTM=37% CNN=40.7%
# Toplam = 27 konfig (3 fon x 9)
total_27 = 27
for fs, el_pct, ec_pct in [
    ('closing',   100.0, 77.8),
    ('technical',  48.1, 48.1),
    ('full',       37.0, 40.7),
]:
    lmc = lstm[lstm['Feature_Set'] == fs].apply(is_mc, axis=1).sum()
    cmc = cnn[cnn['Feature_Set']   == fs].apply(is_mc, axis=1).sum()
    chk(f"G3 {fs} LSTM MC%", lmc / total_27 * 100, el_pct, tol=0.5)
    chk(f"G3 {fs} CNN  MC%", cmc / total_27 * 100, ec_pct, tol=0.5)

# ─── 4. AMZ LSTM SAMPIYON (K-3, Bolum 10, G5) ────────────────────────────────
print("\n=== 4. AMZ LSTM SAMPIYON (Bolum 10 + G5) ===")
r = lstm[(lstm['Fon'] == 'AMZ') & (lstm['Feature_Set'] == 'full') &
         (lstm['Input'] == 2) & (lstm['Output'] == 3)].iloc[0]
ba_ = (r['Sens'] + r['Spec']) / 2
chk("AMZ LSTM Mean_Acc", r['Mean_Acc'], 0.8021)
chk("AMZ LSTM Sens",     r['Sens'],     0.84,  tol=0.005)
chk("AMZ LSTM Spec",     r['Spec'],     0.857, tol=0.005)
chk("AMZ LSTM F1",       r['F1'],       0.894, tol=0.005)
chk("AMZ LSTM BA",       ba_,           0.849, tol=0.003)
chk("AMZ LSTM P_Value",  r['P_Value'],  0.0001, tol=0.00005)
chk("AMZ LSTM Seed_23",  r['Seed_23'],  0.8438, tol=0.001)
chk("AMZ LSTM Seed_27",  r['Seed_27'],  0.7188, tol=0.001)
chk("AMZ LSTM Seed_98",  r['Seed_98'],  0.8438, tol=0.001)

# ─── 5. AZS CNN SAMPIYON (K-4, Bolum 10, G8) ────────────────────────────────
print("\n=== 5. AZS CNN SAMPIYON (Bolum 10 + G8) ===")
# technical / In=4 / Out=3 : Acc=0.756 Sens=0.910 Spec=0.625 F1=0.889 p=0.0002
r2 = cnn[(cnn['Fon'] == 'AZS') & (cnn['Feature_Set'] == 'technical') &
          (cnn['Input'] == 4) & (cnn['Output'] == 3)].iloc[0]
chk("AZS CNN Mean_Acc", r2['Mean_Acc'], 0.756,  tol=0.003)
chk("AZS CNN Sens",     r2['Sens'],     0.910,  tol=0.005)
chk("AZS CNN Spec",     r2['Spec'],     0.625,  tol=0.005)
chk("AZS CNN F1",       r2['F1'],       0.889,  tol=0.005)
chk("AZS CNN P_Value",  r2['P_Value'],  0.0002, tol=0.0001)

# ─── 6. AZS LSTM SAMPIYON DENGELI (Bolum 10) ─────────────────────────────────
print("\n=== 6. AZS LSTM SAMPIYON DENGELI (Bolum 10) ===")
# full / In=2 / Out=5 : Acc=0.6889 Sens=0.7917 Spec=0.6667 F1=0.8444
r3 = lstm[(lstm['Fon'] == 'AZS') & (lstm['Feature_Set'] == 'full') &
           (lstm['Input'] == 2) & (lstm['Output'] == 5)].iloc[0]
chk("AZS LSTM [dengeli] Acc",  r3['Mean_Acc'], 0.6889, tol=0.002)
chk("AZS LSTM [dengeli] Sens", r3['Sens'],     0.7917, tol=0.003)
chk("AZS LSTM [dengeli] Spec", r3['Spec'],     0.6667, tol=0.003)
chk("AZS LSTM [dengeli] F1",   r3['F1'],       0.8444, tol=0.003)
chk("AZS LSTM [dengeli] SD",   r3['SD'],       0.0839, tol=0.003)

# ─── 7. AMZ CNN SAMPIYON (Bolum 10 - en yuksek Acc non-MC) ──────────────────
print("\n=== 7. AMZ CNN SAMPIYON (Bolum 10) ===")
# closing / In=6 / Out=5 : Acc=0.7436 Sens=0.900 Spec=0.333 p=0.0047
r4 = cnn[(cnn['Fon'] == 'AMZ') & (cnn['Feature_Set'] == 'closing') &
          (cnn['Input'] == 6) & (cnn['Output'] == 5)].iloc[0]
chk("AMZ CNN [closing] Acc",     r4['Mean_Acc'], 0.7436, tol=0.002)
chk("AMZ CNN [closing] Sens",    r4['Sens'],     0.900,  tol=0.005)
chk("AMZ CNN [closing] Spec",    r4['Spec'],     0.333,  tol=0.005)
chk("AMZ CNN [closing] P_Value", r4['P_Value'],  0.0047, tol=0.0003)
# Alternatif: full/In=4/Out=1 : Acc=0.6042 Spec=0.6667
r4b = cnn[(cnn['Fon'] == 'AMZ') & (cnn['Feature_Set'] == 'full') &
           (cnn['Input'] == 4) & (cnn['Output'] == 1)].iloc[0]
chk("AMZ CNN [full/4/1] Acc",  r4b['Mean_Acc'], 0.6042, tol=0.002)
chk("AMZ CNN [full/4/1] Spec", r4b['Spec'],     0.6667, tol=0.003)

# ─── 8. NAIVE BASELINE (Bolum 7.2 + G6) ──────────────────────────────────────
print("\n=== 8. NAIVE BASELINE (Bolum 7.2 + G6) ===")
# AZS: Out1=60.00 Out3=84.85 Out5=90.32 | AMZ: Out1=60.00 Out3=78.79 Out5=83.87
expected_naive = {
    ('AZS', 1): 0.6000,
    ('AZS', 3): 0.8485,
    ('AZS', 5): 0.9032,
    ('AMZ', 1): 0.6000,
    ('AMZ', 3): 0.7879,
    ('AMZ', 5): 0.8387,
}
for (fon, out), exp in expected_naive.items():
    row = naive[(naive['Fon'] == fon) & (naive['Output'] == out)]
    if len(row):
        chk(f"Naive {fon} Out={out}", row.iloc[0]['Naive_Acc'], exp, tol=0.0005)
    else:
        ERRORS.append(f"[HATA] Naive {fon} Out={out}: CSV'de satir bulunamadi")
        print(f"[HATA] Naive {fon} Out={out}: CSV'de satir bulunamadi")

# ─── 9. THYAO NAIVE (Bolum 7.1 + G11) ────────────────────────────────────────
print("\n=== 9. THYAO NAIVE (Bolum 7.1 + G11) ===")
# Out1=53.11 Out3=73.93 Out5=79.73
for out, exp in [(1, 0.5311), (3, 0.7393), (5, 0.7973)]:
    row = nt[nt['Output'] == out]
    if len(row):
        chk(f"THYAO Naive Out={out}", row.iloc[0]['Naive_Acc'], exp, tol=0.0005)

# ─── 10. THYAO LSTM SAMPIYON (Bolum 7.1 + G11) ────────────────────────────────
print("\n=== 10. THYAO LSTM SAMPIYON (Bolum 7.1) ===")
# hist_tech / In=4 / Out=3 : Acc=0.5756 Sens=0.5742 Spec=0.6000
r5 = lt[(lt['Feature_Set'] == 'hist_tech') & (lt['Input'] == 4) & (lt['Output'] == 3)]
if len(r5):
    r5 = r5.iloc[0]
    chk("THYAO LSTM [hist_tech/4/3] Acc",  r5['Mean_Acc'], 0.5756, tol=0.002)
    chk("THYAO LSTM [hist_tech/4/3] Sens", r5['Sens'],     0.5742, tol=0.003)
    chk("THYAO LSTM [hist_tech/4/3] Spec", r5['Spec'],     0.6000, tol=0.003)
else:
    ERRORS.append("[HATA] THYAO LSTM hist_tech/4/3 bulunamadi")

# ─── 11. THYAO CNN SAMPIYON (Bolum 7.1 + G11) ─────────────────────────────────
print("\n=== 11. THYAO CNN SAMPIYON (Bolum 7.1) ===")
# hist_tech / In=2 / Out=3 : Acc=0.5397 Sens=0.758 Spec=0.331
r6 = ct[(ct['Feature_Set'] == 'hist_tech') & (ct['Input'] == 2) & (ct['Output'] == 3)]
if len(r6):
    r6 = r6.iloc[0]
    chk("THYAO CNN [hist_tech/2/3] Acc",  r6['Mean_Acc'], 0.5397, tol=0.002)
    chk("THYAO CNN [hist_tech/2/3] Sens", r6['Sens'],     0.758,  tol=0.005)
    chk("THYAO CNN [hist_tech/2/3] Spec", r6['Spec'],     0.331,  tol=0.005)
else:
    ERRORS.append("[HATA] THYAO CNN hist_tech/2/3 bulunamadi")

# ─── 12. ARIMA (Bolum 7.1 + 7.2) ─────────────────────────────────────────────
print("\n=== 12. ARIMA (Bolum 7.1 + 7.2) ===")
# THYAO best: In=6 Out=3 => 55.78%
r7 = at_[(at_['Input'] == 6) & (at_['Output'] == 3)]
if len(r7):
    chk("THYAO ARIMA best (In=6,Out=3)", r7.iloc[0]['Test_Acc'], 0.5578, tol=0.003)
# AMZ ARIMA: Out1=71.43 Out3=78.79 Out5=80.65
for out, exp in [(1, 0.7143), (3, 0.7879), (5, 0.8065)]:
    row = arima[(arima['Fon'] == 'AMZ') & (arima['Output'] == out)]
    if len(row):
        chk(f"AMZ ARIMA Out={out}", row.iloc[0]['Test_Acc'], exp, tol=0.0005)
# AZS ARIMA best: Out5=80.65
row_azs5 = arima[(arima['Fon'] == 'AZS') & (arima['Output'] == 5)]
if len(row_azs5):
    chk("AZS ARIMA Out=5 best", row_azs5['Test_Acc'].max(), 0.8065, tol=0.0005)

# ─── 13. G1 THYAO LSTM (Bolum 7.1) — grafik kodu hardcoded degerleri ─────────
print("\n=== 13. G1 GRAFIK HARDCODED DEGERLER (grafik_v3_p1.py) ===")
# Grafik: MC kateg: Acc=52.67 Spec=0 | REAL kateg: Acc=57.56 Spec=60
# MC: closing In=2 Out=5
mc_row = lt[(lt['Feature_Set'] == 'closing') & (lt['Input'] == 2) & (lt['Output'] == 5)]
if len(mc_row):
    chk("G1 MC Acc (closing/2/5)", mc_row.iloc[0]['Mean_Acc'], 0.5267, tol=0.002)
    mc_spec = mc_row.iloc[0]['Spec']
    ok_spec = pd.isna(mc_spec) or mc_spec == 0
    tag = "OK" if ok_spec else "HATA"
    line = f"[{tag}] G1 MC Spec sifir/NaN: CSV={mc_spec}"
    print(line)
    if ok_spec: OKAYS.append(line)
    else: ERRORS.append(line)
# REAL: hist_tech/4/3 Acc=57.56 Spec=60%
if len(r5):
    chk("G1 REAL Acc (hist_tech/4/3)", r5['Mean_Acc'], 0.5756, tol=0.002)

# ─── 14. G7 CONCEPT DRIFT DEGERLER (grafik_v3_p1.py) ─────────────────────────
print("\n=== 14. G7 CONCEPT DRIFT (Bolum 1.5.B M-1 + G7) ===")
# 2022: LSTM tech=55.83 CNN tech=56.79 ARIMA=49.83
# 2026: LSTM tech=50.52 CNN tech=49.55 ARIMA=51.34

def best_tech_acc(df):
    sub = df[df['Feature_Set'] == 'technical']
    return sub['Mean_Acc'].max() if len(sub) else np.nan

def arima_avg(df):
    return df['Test_Acc'].mean() if len(df) else np.nan

chk("G7 LSTM 2022 tech best",  best_tech_acc(lt22), 0.5583, tol=0.003)
chk("G7 CNN  2022 tech best",  best_tech_acc(ct22), 0.5679, tol=0.003)
chk("G7 ARIMA 2022 avg",       arima_avg(at22),     0.4983, tol=0.005)

chk("G7 LSTM 2026 tech best",  best_tech_acc(lt),  0.5052, tol=0.003)
chk("G7 CNN  2026 tech best",  best_tech_acc(ct),  0.4955, tol=0.003)
chk("G7 ARIMA 2026 avg",       arima_avg(at_),     0.5134, tol=0.005)

# ─── 15. G9 ISI HARITASI hardcoded (grafik_v3_p2.py) ─────────────────────────
print("\n=== 15. G9 ISI HARITASI HARDCODED (grafik_v3_p2.py) ===")
# matrix = [[50.0,68.89,80.21],[50.0,75.56,74.36],[100.0,80.65,80.65]]
# [LSTM][AZS]=68.89, [LSTM][AMZ]=80.21, [CNN][AZS]=75.56, [CNN][AMZ]=74.36
# ARIMA ALZ=100(MC), AZS=80.65, AMZ=80.65
lstm_azs_best = lstm[(lstm['Fon']=='AZS') & ~lstm.apply(is_mc,axis=1)]['Mean_Acc'].max()
lstm_amz_best = lstm[(lstm['Fon']=='AMZ') & ~lstm.apply(is_mc,axis=1)]['Mean_Acc'].max()
cnn_azs_best  = cnn[(cnn['Fon']=='AZS') & ~cnn.apply(is_mc,axis=1)]['Mean_Acc'].max()
cnn_amz_best  = cnn[(cnn['Fon']=='AMZ') & ~cnn.apply(is_mc,axis=1)]['Mean_Acc'].max()
arima_azs_best = arima[arima['Fon']=='AZS']['Test_Acc'].max()
arima_amz_best = arima[arima['Fon']=='AMZ']['Test_Acc'].max()

chk("G9 LSTM AZS best Acc", lstm_azs_best, 0.6889, tol=0.002)
chk("G9 LSTM AMZ best Acc", lstm_amz_best, 0.8021, tol=0.002)
chk("G9 CNN  AZS best Acc", cnn_azs_best,  0.7556, tol=0.002)
chk("G9 CNN  AMZ best Acc", cnn_amz_best,  0.7436, tol=0.002)
chk("G9 ARIMA AZS best",    arima_azs_best, 0.8065, tol=0.002)
chk("G9 ARIMA AMZ best",    arima_amz_best, 0.8065, tol=0.002)

# ─── 16. G10 CM KONTROLU (TP=64 FN=12 FP=3 TN=17 N=96) ──────────────────────
print("\n=== 16. G10 POOLED CM MATEMATIGI (Bolum K-9 + G10) ===")
# N=96=3*32, AMZ Out=3 naive=78.79% -> pozitif=round(0.7879*96)=76, negatif=20
# Sens=0.84 -> TP=round(0.84*76)=64, FN=12; Spec=0.8571 -> TN=round(0.8571*20)=17, FP=3
N = 96
pos_cls = round(0.7879 * N)  # 76
neg_cls = N - pos_cls         # 20
TP_exp = round(0.84 * pos_cls)   # 64
FN_exp = pos_cls - TP_exp        # 12
TN_exp = round(0.8571 * neg_cls) # 17
FP_exp = neg_cls - TN_exp        # 3
pool_acc = (TP_exp + TN_exp) / N

print(f"  N=96, Pozitif={pos_cls}, Negatif={neg_cls}")
print(f"  TP={TP_exp} FN={FN_exp} FP={FP_exp} TN={TN_exp}")
print(f"  Havuz Acc = {pool_acc:.4f} ({pool_acc*100:.2f}%)")

# Grafik kodu: TP=64 FN=12 FP=3 TN=17 -> ayni
for nm, gv, ev in [('TP',64,TP_exp),('FN',12,FN_exp),('FP',3,FP_exp),('TN',17,TN_exp)]:
    ok = gv == ev
    tag = "OK" if ok else "HATA"
    line = f"[{tag}] G10 {nm}: Grafik={gv}  Hesaplanan={ev}"
    print(line)
    if ok: OKAYS.append(line)
    else:  ERRORS.append(line)

# ─── 17. G6 NAIVE DOMINANCE GRAFIK HARDCODED ─────────────────────────────────
print("\n=== 17. G6 NAIVE DOMINANCE HARDCODED DEGERLERI ===")
# nd AZS=[60.00,84.85,90.32] AMZ=[60.00,78.79,83.87]
# ld AZS=[61.11,59.52,68.89] AMZ=[69.61,80.21,77.38]
# LSTM best acc per fon/output (non-MC)
for fon, outputs, lstm_exp in [
    ('AZS', [1,3,5], [61.11, 59.52, 68.89]),
    ('AMZ', [1,3,5], [69.61, 80.21, 77.38]),
]:
    for out, exp in zip(outputs, lstm_exp):
        sub = lstm[(lstm['Fon']==fon) & (lstm['Output']==out) & ~lstm.apply(is_mc,axis=1)]
        csv_v = sub['Mean_Acc'].max()*100 if len(sub) else 0.0
        chk(f"G6 LSTM {fon} Out={out} best", csv_v/100, exp/100, tol=0.003)

# ─── 18. MC DAGILIMI FEATURE_SET x FON (Bolum 6.2) ───────────────────────────
print("\n=== 18. MC DAGILIMI FEATURE_SET x FON (Bolum 6.2) ===")
# AZS LSTM: full=1/9 technical=3/9 closing=9/9
# AZS CNN:  full=1/9 technical=3/9 closing=5/9
# AMZ LSTM: full=0/9 technical=1/9 closing=9/9
# AMZ CNN:  full=1/9 technical=1/9 closing=7/9
expected_fs_mc = [
    ('AZS','LSTM','full',1), ('AZS','LSTM','technical',3), ('AZS','LSTM','closing',9),
    ('AZS','CNN', 'full',1), ('AZS','CNN', 'technical',3), ('AZS','CNN', 'closing',5),
    ('AMZ','LSTM','full',0), ('AMZ','LSTM','technical',1), ('AMZ','LSTM','closing',9),
    ('AMZ','CNN', 'full',1), ('AMZ','CNN', 'technical',1), ('AMZ','CNN', 'closing',7),
]
for fon, model, fs, exp in expected_fs_mc:
    df = lstm if model == 'LSTM' else cnn
    sub = df[(df['Fon']==fon) & (df['Feature_Set']==fs)]
    mc_cnt = sub.apply(is_mc, axis=1).sum()
    chk_int(f"MC {fon} {model} {fs} (/9)", mc_cnt, exp)

# ─── OZET ─────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"TOPLAM OK:   {len(OKAYS)}")
print(f"TOPLAM HATA: {len(ERRORS)}")
print("="*60)
if ERRORS:
    print("\n!!! HATALI KONTROLLER !!!")
    for e in ERRORS:
        print(" ", e)
else:
    print("\nTUM KONTROLLER BASARILI - Grafik ve Rapor CSV ile tutarli.")
