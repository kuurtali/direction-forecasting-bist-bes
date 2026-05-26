# -*- coding: utf-8 -*-
"""TÜM FONLAR — Seed-level veri toplama ve pooled hesaplama"""
import sys, io, csv, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

base = r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"

# Champion configs to extract
champions = {
    "AMZ_LSTM": {"Fon": "AMZ", "Model": "LSTM", "Feature_Set": "full", "Input": "2", "Output": "3"},
    "AZS_CNN":  {"Fon": "AZS", "Model": "CNN",  "Feature_Set": "technical", "Input": "4", "Output": "3"},
    "AZS_LSTM": {"Fon": "AZS", "Model": "LSTM", "Feature_Set": "full", "Input": "2", "Output": "5"},
    "THYAO_LSTM": {"Fon": "THYAO", "Model": "LSTM", "Feature_Set": "hist_tech", "Input": "4", "Output": "3"},
    "THYAO_CNN":  {"Fon": "THYAO", "Model": "CNN", "Feature_Set": "hist_tech", "Input": "2", "Output": "3"},
}

print("=" * 80)
print("TÜM FON SEED VERİLERİ — CSV GROUND-TRUTH")
print("=" * 80)

# Scan ALL CSVs
all_rows = []
for f in sorted(glob.glob(base + "/**/EMEKLILIK_*.csv", recursive=True)):
    if '2018-2026' not in f:
        continue
    model_type = "LSTM" if "LSTM" in f else ("CNN" if "CNN" in f else ("ARIMA" if "ARIMA" in f else "NAIVE"))
    with open(f, 'r', encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row['_model_type'] = model_type
            row['_file'] = f
            all_rows.append(row)

# Group by fund
funds = {}
for row in all_rows:
    fon = row.get('Fon', '')
    if fon not in funds:
        funds[fon] = []
    funds[fon].append(row)

# Print ALL configurations with seed data
for fon in sorted(funds.keys()):
    print(f"\n{'='*60}")
    print(f"FON: {fon}")
    print(f"{'='*60}")
    
    for row in funds[fon]:
        fs = row.get('Feature_Set', row.get('feature_set', ''))
        inp = row.get('Input', row.get('input', ''))
        out = row.get('Output', row.get('output', ''))
        model = row['_model_type']
        mean = row.get('Mean_Acc', '')
        s23 = row.get('Seed_23', '')
        s27 = row.get('Seed_27', '')
        s98 = row.get('Seed_98', '')
        sens = row.get('Sens', '')
        spec = row.get('Spec', '')
        sd = row.get('SD', '')
        p = row.get('P_Value', '')
        
        # Highlight champions
        is_champ = False
        for cname, cspec in champions.items():
            if (cspec['Fon'] in fon and cspec['Model'] == model and 
                cspec['Feature_Set'] in fs and cspec['Input'] == inp and cspec['Output'] == out):
                is_champ = True
                break
        
        marker = " ★★ CHAMPION" if is_champ else ""
        
        if s23 and s23 != s27:  # Only show rows with varying seeds (interesting)
            print(f"  {model} {fs} In={inp} Out={out}: Mean={mean} | S23={s23} S27={s27} S98={s98} | Sens={sens} Spec={spec} SD={sd}{marker}")
        elif is_champ:
            print(f"  {model} {fs} In={inp} Out={out}: Mean={mean} | S23={s23} S27={s27} S98={s98} | Sens={sens} Spec={spec} SD={sd}{marker}")

# Now compute actual pooled CMs for champions
print("\n\n" + "=" * 80)
print("CHAMPION POOLED vs MEAN HESAPLAMASI")
print("=" * 80)

# AMZ LSTM champion: full In=2 Out=3
# Test set: 32 per seed (Out=3)
# Class distribution: ~25 UP / 7 DOWN per seed
print("\n--- AMZ LSTM full In=2 Out=3 ---")
print("Per-seed CMs (from BES B3 fixed):")
print("  Seed 23: TP=21 FN=4 TN=6 FP=1 → N=32, Acc=27/32=84.38%")
print("  Seed 27: TP=18 FN=7 TN=5 FP=2 → N=32, Acc=23/32=71.88%")
print("  Seed 98: TP=21 FN=4 TN=6 FP=1 → N=32, Acc=27/32=84.38%")
print("True Pooled: TP=60 FN=15 TN=17 FP=4 → 77/96=80.21%")
print("3-seed Mean: (84.38+71.88+84.38)/3 = 80.21%")
print("CSV-Rate Pooled: Sens=0.84×75=63, Spec=0.857×21=18 → 81/96=84.38%")

# AZS CNN champion: tech In=4 Out=3
# S23=0.70, S27=0.7333, S98=0.8333
# Per seed N=30 (Out=3)
print("\n--- AZS CNN technical In=4 Out=3 ---")
print(f"Seeds: S23=70.00% S27=73.33% S98=83.33%")
print(f"3-seed Mean: (70+73.33+83.33)/3 = {(70+73.33+83.33)/3:.2f}%")
s23_c = round(0.70 * 30)
s27_c = round(0.7333 * 30)
s98_c = round(0.8333 * 30)
total_c = s23_c + s27_c + s98_c
print(f"Per-seed correct: {s23_c}+{s27_c}+{s98_c} = {total_c}")
print(f"True Pooled: {total_c}/90 = {total_c/90*100:.2f}%")
# CSV rates
print(f"CSV-Rate Pooled (Sens=0.9091 Spec=0.625):")
# AZS class dist Out=3: ~22 UP / 8 DOWN per seed? Check
# N=30, Sens=0.9091 → TP/(TP+FN)=20/22, Spec=0.625 → TN/(TN+FP)=5/8
print(f"  If ~22UP/8DOWN per seed → Pooled 66UP/24DOWN")
print(f"  TP=0.9091×66≈60, TN=0.625×24=15 → 75/90=83.33%")

# THYAO LSTM champion: hist_tech In=4 Out=3
# Need to check test set size
print("\n--- THYAO LSTM hist_tech In=4 Out=3 ---")
for row in all_rows:
    if 'THYAO' in row.get('Fon','') and 'LSTM' in row['_model_type']:
        fs = row.get('Feature_Set','')
        if 'hist_tech' in fs and row.get('Input','')=='4' and row.get('Output','')=='3':
            print(f"  Mean={row['Mean_Acc']} S23={row['Seed_23']} S27={row['Seed_27']} S98={row['Seed_98']}")
            print(f"  Sens={row['Sens']} Spec={row['Spec']} SD={row['SD']}")

# ALZ - all MC
print("\n--- ALZ (tüm modeller MC — Seed varyansı yok) ---")
for row in all_rows:
    if 'ALZ' in row.get('Fon',''):
        fs = row.get('Feature_Set','')
        model = row['_model_type']
        inp = row.get('Input','')
        out = row.get('Output','')
        s23 = row.get('Seed_23','')
        s27 = row.get('Seed_27','')
        s98 = row.get('Seed_98','')
        mean = row.get('Mean_Acc','')
        if s23 and s23 == s27 == s98:
            print(f"  {model} {fs} In={inp} Out={out}: All seeds = {s23} (MC)")
        elif s23:
            print(f"  {model} {fs} In={inp} Out={out}: S23={s23} S27={s27} S98={s98} Mean={mean}")

# NAIVE baselines
print("\n--- NAIVE BASELINES ---")
for f in sorted(glob.glob(base + "/**/EMEKLILIK_NAIVE*", recursive=True)):
    if '2018-2026' in f:
        print(f"  File: {f}")
        with open(f, 'r', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                print(f"  {dict(row)}")
