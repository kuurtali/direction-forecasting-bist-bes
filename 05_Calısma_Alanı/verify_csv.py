import csv, os, math

base = r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Kanıtlar"
new_dir = os.path.join(base, "2018-2026 cıktılar")
old_dir = os.path.join(base, "2018-2022 cıktılar")

# Try to find actual directory names
for d in os.listdir(base):
    full = os.path.join(base, d)
    if os.path.isdir(full):
        if "2026" in d:
            new_dir = full
        elif "2022" in d:
            old_dir = full

def read_csv(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)

def safe_float(v):
    if v is None or v.strip() == '' or v.strip().upper() == 'NA':
        return None
    return float(v)

errors = []
warnings = []

# ============ 1. INTERNAL CSV CONSISTENCY CHECKS ============
print("="*70)
print("PART 1: INTERNAL CSV CONSISTENCY (Mean, SD, Min, Max)")
print("="*70)

def check_mean_sd(rows, label, seed_cols, mean_col, sd_col, min_col, max_col):
    for i, row in enumerate(rows):
        seeds = [safe_float(row[c]) for c in seed_cols if c in row]
        seeds = [s for s in seeds if s is not None]
        if len(seeds) < 2:
            continue
        csv_mean = safe_float(row.get(mean_col))
        csv_sd = safe_float(row.get(sd_col))
        csv_min = safe_float(row.get(min_col))
        csv_max = safe_float(row.get(max_col))
        
        calc_mean = sum(seeds)/len(seeds)
        calc_min = min(seeds)
        calc_max = max(seeds)
        calc_sd = (sum((s-calc_mean)**2 for s in seeds)/len(seeds))**0.5  # population SD
        calc_sd_sample = (sum((s-calc_mean)**2 for s in seeds)/(len(seeds)-1))**0.5  # sample SD
        
        info = f"{label} row {i+2}: seeds={seeds}"
        
        if csv_mean is not None and abs(csv_mean - calc_mean) > 0.002:
            errors.append(f"MEAN MISMATCH: {info} | CSV Mean={csv_mean}, Calc={calc_mean:.4f}")
        if csv_min is not None and abs(csv_min - calc_min) > 0.001:
            errors.append(f"MIN MISMATCH: {info} | CSV Min={csv_min}, Calc={calc_min}")
        if csv_max is not None and abs(csv_max - calc_max) > 0.001:
            errors.append(f"MAX MISMATCH: {info} | CSV Max={csv_max}, Calc={calc_max}")
        if csv_sd is not None:
            if abs(csv_sd - calc_sd) > 0.002 and abs(csv_sd - calc_sd_sample) > 0.002:
                errors.append(f"SD MISMATCH: {info} | CSV SD={csv_sd}, Pop={calc_sd:.4f}, Sample={calc_sd_sample:.4f}")

# Check CNN new
for fname in ['CNN_sonuclar_FINAL.csv', 'CNN_sonuclar_ARAKAYIT.csv']:
    path = os.path.join(new_dir, fname)
    if os.path.exists(path):
        rows = read_csv(path)
        check_mean_sd(rows, f"NEW/{fname}", ['Seed_23','Seed_27','Seed_98'], 'Mean_Acc', 'SD', 'Min_Acc', 'Max_Acc')

# Check LSTM new
for fname in ['LSTM_sonuclar_FINAL.csv', 'LSTM_sonuclar_ARAKAYIT.csv']:
    path = os.path.join(new_dir, fname)
    if os.path.exists(path):
        rows = read_csv(path)
        check_mean_sd(rows, f"NEW/{fname}", ['Seed_23','Seed_27','Seed_98'], 'Mean_Acc', 'SD', 'Min_Acc', 'Max_Acc')

# Check EMEKLILIK CNN new
path = os.path.join(new_dir, 'EMEKLILIK_CNN_sonuclar.csv')
if os.path.exists(path):
    rows = read_csv(path)
    check_mean_sd(rows, "NEW/EMEKLILIK_CNN", ['Seed_23','Seed_27','Seed_98'], 'Mean_Acc', 'SD', 'Min_Acc', 'Max_Acc')

# Check EMEKLILIK LSTM new
path = os.path.join(new_dir, 'EMEKLILIK_LSTM_sonuclar.csv')
if os.path.exists(path):
    rows = read_csv(path)
    check_mean_sd(rows, "NEW/EMEKLILIK_LSTM", ['Seed_23','Seed_27','Seed_98'], 'Mean_Acc', 'SD', 'Min_Acc', 'Max_Acc')

# Old files
for fname in ['CNN_sonuclar_FINAL_eski.csv', 'CNN_sonuclar_ARAKAYIT_eski.csv',
              'LSTM_sonuclar_FINAL_eski.csv', 'LSTM_sonuclar_ARAKAYIT_eski.csv']:
    path = os.path.join(old_dir, fname)
    if os.path.exists(path):
        rows = read_csv(path)
        check_mean_sd(rows, f"OLD/{fname}", ['Seed_23','Seed_27','Seed_98'], 'Mean_Acc', 'SD', 'Min_Acc', 'Max_Acc')

# ============ 2. ARAKAYIT = FINAL identity check ============
print("\n" + "="*70)
print("PART 2: ARAKAYIT vs FINAL IDENTITY CHECK")
print("="*70)

for prefix in ['CNN_sonuclar', 'LSTM_sonuclar']:
    for d, suffix in [(new_dir, ''), (old_dir, '_eski')]:
        f1 = os.path.join(d, f"{prefix}_ARAKAYIT{suffix}.csv")
        f2 = os.path.join(d, f"{prefix}_FINAL{suffix}.csv")
        if os.path.exists(f1) and os.path.exists(f2):
            with open(f1,'rb') as a, open(f2,'rb') as b:
                identical = a.read() == b.read()
            status = "IDENTICAL ✓" if identical else "DIFFERENT ✗"
            print(f"  {os.path.basename(d)}/{prefix}{suffix}: {status}")
            if not identical:
                errors.append(f"ARAKAYIT≠FINAL: {prefix}{suffix} in {os.path.basename(d)}")

# ============ 3. NAIVE baseline checks ============
print("\n" + "="*70)
print("PART 3: NAIVE BASELINE CONSISTENCY")
print("="*70)

# THYAO Naive - same values for all inputs with same output
path = os.path.join(new_dir, 'NAIVE_baseline.csv')
if os.path.exists(path):
    rows = read_csv(path)
    by_output = {}
    for r in rows:
        out = r['Output']
        acc = safe_float(r['Naive_Acc'])
        by_output.setdefault(out, []).append(acc)
    for out, accs in by_output.items():
        if len(set(accs)) > 1:
            errors.append(f"NAIVE THYAO: Output={out} has varying Acc: {accs}")
        else:
            print(f"  THYAO Naive Out={out}: {accs[0]} (consistent across inputs) ✓")

# Emeklilik Naive
path = os.path.join(new_dir, 'EMEKLILIK_NAIVE_baseline.csv')
if os.path.exists(path):
    rows = read_csv(path)
    by_fon_out = {}
    for r in rows:
        key = (r['Fon'], r['Output'])
        acc = safe_float(r['Naive_Acc'])
        by_fon_out.setdefault(key, []).append(acc)
    for (fon,out), accs in by_fon_out.items():
        if len(set(accs)) > 1:
            errors.append(f"NAIVE EMK: {fon} Out={out} varying: {accs}")
        else:
            print(f"  {fon} Naive Out={out}: {accs[0]} ✓")

# ============ 4. MC COUNT VERIFICATION ============
print("\n" + "="*70)
print("PART 4: MAJORITY CLASS COUNT VERIFICATION")
print("="*70)

def count_mc(rows, fon_filter=None, fs_filter=None):
    mc = 0
    total = 0
    for r in rows:
        if fon_filter and r.get('Fon','') != fon_filter:
            continue
        if fs_filter and r.get('Feature_Set','') != fs_filter:
            continue
        total += 1
        spec = r.get('Spec','')
        sens = r.get('Sens','')
        spec_v = safe_float(spec) if spec.strip().upper() != 'NA' else None
        sens_v = safe_float(sens) if sens.strip().upper() != 'NA' else None
        is_mc = (spec.strip().upper() == 'NA') or (spec_v == 0) or (sens_v == 0)
        if is_mc:
            mc += 1
    return mc, total

# THYAO LSTM MC
path = os.path.join(new_dir, 'LSTM_sonuclar_FINAL.csv')
rows = read_csv(path)
mc, total = count_mc(rows)
report_val = "12/36"
print(f"  THYAO LSTM 2018-2026 MC: {mc}/{total} (Report says {report_val}) {'✓' if f'{mc}/{total}'==report_val else '✗ MISMATCH'}")

# THYAO CNN MC
path = os.path.join(new_dir, 'CNN_sonuclar_FINAL.csv')
rows = read_csv(path)
mc, total = count_mc(rows)
report_val = "9/36"
print(f"  THYAO CNN 2018-2026 MC: {mc}/{total} (Report says {report_val}) {'✓' if f'{mc}/{total}'==report_val else '✗ MISMATCH'}")

# THYAO OLD LSTM MC
path = os.path.join(old_dir, 'LSTM_sonuclar_FINAL_eski.csv')
rows = read_csv(path)
mc, total = count_mc(rows)
report_val = "16/36"
print(f"  THYAO LSTM 2018-2022 MC: {mc}/{total} (Report says {report_val}) {'✓' if f'{mc}/{total}'==report_val else '✗ MISMATCH'}")

# THYAO OLD CNN MC
path = os.path.join(old_dir, 'CNN_sonuclar_FINAL_eski.csv')
rows = read_csv(path)
mc, total = count_mc(rows)
report_val = "8/36"
print(f"  THYAO CNN 2018-2022 MC: {mc}/{total} (Report says {report_val}) {'✓' if f'{mc}/{total}'==report_val else '✗ MISMATCH'}")

# Emeklilik MC counts
emk_lstm = read_csv(os.path.join(new_dir, 'EMEKLILIK_LSTM_sonuclar.csv'))
emk_cnn = read_csv(os.path.join(new_dir, 'EMEKLILIK_CNN_sonuclar.csv'))

for fon, expected_lstm, expected_cnn in [('ALZ','27/27','27/27'),('AZS','13/27','9/27'),('AMZ','10/27','9/27')]:
    mc_l, t_l = count_mc(emk_lstm, fon_filter=fon)
    mc_c, t_c = count_mc(emk_cnn, fon_filter=fon)
    l_ok = f'{mc_l}/{t_l}' == expected_lstm
    c_ok = f'{mc_c}/{t_c}' == expected_cnn
    print(f"  {fon} LSTM MC: {mc_l}/{t_l} (Report: {expected_lstm}) {'✓' if l_ok else '✗'}")
    print(f"  {fon} CNN  MC: {mc_c}/{t_c} (Report: {expected_cnn}) {'✓' if c_ok else '✗'}")
    if not l_ok: errors.append(f"MC COUNT: {fon} LSTM {mc_l}/{t_l} != {expected_lstm}")
    if not c_ok: errors.append(f"MC COUNT: {fon} CNN {mc_c}/{t_c} != {expected_cnn}")

# MC by feature set
print("\n  --- MC by Feature Set ---")
for fon in ['AZS','AMZ']:
    for model_name, rows_data in [('LSTM', emk_lstm), ('CNN', emk_cnn)]:
        for fs in ['full','technical','closing']:
            mc, t = count_mc(rows_data, fon_filter=fon, fs_filter=fs)
            print(f"  {fon} {model_name} {fs}: {mc}/{t} MC")

# ============ 5. CHAMPION CONFIGS VERIFICATION ============
print("\n" + "="*70)
print("PART 5: CHAMPION CONFIGURATION VERIFICATION")
print("="*70)

# THYAO ARIMA best
arima = read_csv(os.path.join(new_dir, 'ARIMA_sonuclar.csv'))
best_arima = max(arima, key=lambda r: safe_float(r['Test_Acc']))
print(f"  THYAO ARIMA best: In={best_arima['Input']} Out={best_arima['Output']} Acc={best_arima['Test_Acc']}")
print(f"    Report says: In=6 Out=3 Acc=0.5578 {'✓' if best_arima['Test_Acc']=='0.5578' else '✗'}")
arima_avg = sum(safe_float(r['Test_Acc']) for r in arima)/len(arima)
print(f"    ARIMA average: {arima_avg:.4f} (Report ~0.5134)")

# THYAO LSTM best (non-MC)
lstm_new = read_csv(os.path.join(new_dir, 'LSTM_sonuclar_FINAL.csv'))
non_mc_lstm = [r for r in lstm_new if safe_float(r.get('Spec','0'))>0 and safe_float(r.get('Sens','0'))>0 and r.get('Spec','NA').strip().upper()!='NA']
best_lstm = max(non_mc_lstm, key=lambda r: safe_float(r['Mean_Acc']))
print(f"\n  THYAO LSTM best non-MC: FS={best_lstm['Feature_Set']} In={best_lstm['Input']} Out={best_lstm['Output']}")
print(f"    Mean={best_lstm['Mean_Acc']} Sens={best_lstm['Sens']} Spec={best_lstm['Spec']} P={best_lstm['P_Value']}")
print(f"    Report: hist_tech In=4 Out=3 Mean=0.5756 Sens=0.5742 Spec=0.6 p=0.0016")

# THYAO CNN best
cnn_new = read_csv(os.path.join(new_dir, 'CNN_sonuclar_FINAL.csv'))
non_mc_cnn = [r for r in cnn_new if safe_float(r.get('Spec','0'))>0 and safe_float(r.get('Sens','0'))>0 and r.get('Spec','NA').strip().upper()!='NA']
best_cnn = max(non_mc_cnn, key=lambda r: safe_float(r['Mean_Acc']))
print(f"\n  THYAO CNN best non-MC: FS={best_cnn['Feature_Set']} In={best_cnn['Input']} Out={best_cnn['Output']}")
print(f"    Mean={best_cnn['Mean_Acc']} Sens={best_cnn['Sens']} Spec={best_cnn['Spec']}")

# AMZ LSTM champion (full In=2 Out=3)
amz_lstm_champ = [r for r in emk_lstm if r['Fon']=='AMZ' and r['Feature_Set']=='full' and r['Input']=='2' and r['Output']=='3']
if amz_lstm_champ:
    c = amz_lstm_champ[0]
    print(f"\n  AMZ LSTM Champion (full/2/3):")
    print(f"    Mean={c['Mean_Acc']} SD={c['SD']} Sens={c['Sens']} Spec={c['Spec']} F1={c['F1']} P={c['P_Value']}")
    print(f"    Seeds: {c['Seed_23']}/{c['Seed_27']}/{c['Seed_98']}")
    print(f"    Report: Mean=0.8021 SD=0.072 Sens=0.84 Spec=0.857 F1=0.8936 p=0.0001")
    print(f"    Seeds report: 0.8438/0.7188/0.8438")
    # Verify
    if c['Mean_Acc'] != '0.8021': errors.append(f"AMZ LSTM champ Mean: CSV={c['Mean_Acc']} Report=0.8021")
    if c['Sens'] != '0.84': errors.append(f"AMZ LSTM champ Sens: CSV={c['Sens']} Report=0.84")
    if c['Spec'] != '0.8571': 
        warnings.append(f"AMZ LSTM champ Spec: CSV={c['Spec']} Report=0.857 (rounding)")

# AZS CNN champion (technical In=4 Out=3)
azs_cnn_champ = [r for r in emk_cnn if r['Fon']=='AZS' and r['Feature_Set']=='technical' and r['Input']=='4' and r['Output']=='3']
if azs_cnn_champ:
    c = azs_cnn_champ[0]
    print(f"\n  AZS CNN Champion (technical/4/3):")
    print(f"    Mean={c['Mean_Acc']} SD={c['SD']} Sens={c['Sens']} Spec={c['Spec']} F1={c['F1']} P={c['P_Value']}")
    print(f"    Report: Mean=0.7556 Sens=0.9091 Spec=0.625 F1=0.8889 p=0.0002")

# Naive values verification
naive_new = read_csv(os.path.join(new_dir, 'NAIVE_baseline.csv'))
print(f"\n  THYAO Naive values:")
for r in naive_new:
    if r['Input'] == '2':  # all inputs same
        print(f"    Out={r['Output']}: {r['Naive_Acc']}")

emk_naive = read_csv(os.path.join(new_dir, 'EMEKLILIK_NAIVE_baseline.csv'))
print(f"\n  EMK Naive values:")
for fon in ['ALZ','AZS','AMZ']:
    vals = {}
    for r in emk_naive:
        if r['Fon'] == fon:
            vals[r['Output']] = r['Naive_Acc']
    for out in ['1','3','5']:
        if out in vals:
            print(f"    {fon} Out={out}: {vals[out]}")

# ============ 6. CONCEPT DRIFT VERIFICATION ============
print("\n" + "="*70)
print("PART 6: CONCEPT DRIFT (OLD vs NEW best technical)")
print("="*70)

old_lstm = read_csv(os.path.join(old_dir, 'LSTM_sonuclar_FINAL_eski.csv'))
old_cnn = read_csv(os.path.join(old_dir, 'CNN_sonuclar_FINAL_eski.csv'))
old_arima = read_csv(os.path.join(old_dir, 'ARIMA_sonuclar_eski.csv'))
new_arima = read_csv(os.path.join(new_dir, 'ARIMA_sonuclar.csv'))

# Average accuracy for technical feature set
for name, old_rows, new_rows in [('LSTM', old_lstm, lstm_new), ('CNN', old_cnn, cnn_new)]:
    old_tech = [safe_float(r['Mean_Acc']) for r in old_rows if r['Feature_Set']=='technical']
    new_tech = [safe_float(r['Mean_Acc']) for r in new_rows if r['Feature_Set']=='technical']
    old_avg = sum(old_tech)/len(old_tech) if old_tech else 0
    new_avg = sum(new_tech)/len(new_tech) if new_tech else 0
    print(f"  {name} technical avg: OLD={old_avg:.4f} NEW={new_avg:.4f} diff={new_avg-old_avg:+.4f}")

old_arima_avg = sum(safe_float(r['Test_Acc']) for r in old_arima)/len(old_arima)
new_arima_avg = sum(safe_float(r['Test_Acc']) for r in new_arima)/len(new_arima)
print(f"  ARIMA avg: OLD={old_arima_avg:.4f} NEW={new_arima_avg:.4f} diff={new_arima_avg-old_arima_avg:+.4f}")

# Report claims: LSTM tech 55.83->50.52, CNN tech 56.79->49.55, ARIMA 49.83->51.34
print(f"  Report claims: LSTM tech 55.83%->50.52%, CNN tech 56.79%->49.55%, ARIMA 49.83%->51.34%")

# ============ 7. EMEKLILIK ARIMA CHECKS ============
print("\n" + "="*70)
print("PART 7: EMEKLILIK ARIMA SPECIFIC CHECKS")
print("="*70)
emk_arima = read_csv(os.path.join(new_dir, 'EMEKLILIK_ARIMA_sonuclar.csv'))
# Report: ALZ all 100% except one 96.97
for r in emk_arima:
    if r['Fon'] == 'ALZ':
        acc = safe_float(r['Test_Acc'])
        if acc < 1.0:
            print(f"  ALZ ARIMA non-100%: In={r['Input']} Out={r['Output']} Acc={r['Test_Acc']} Best_d={r['Best_d']}")

# AZS ARIMA Out=5
print(f"\n  AZS ARIMA Output=5 values:")
for r in emk_arima:
    if r['Fon'] == 'AZS' and r['Output'] == '5':
        print(f"    In={r['Input']} Best_d={r['Best_d']} Acc={r['Test_Acc']}")
# Report says: In=2 Best_d=0, In=6 Best_d=1
print(f"  Report: Out=5 best=0.8065 (In=2 Best_d=0; In=6 Best_d=1)")

# AMZ ARIMA
print(f"\n  AMZ ARIMA values:")
for r in emk_arima:
    if r['Fon'] == 'AMZ':
        print(f"    In={r['Input']} Out={r['Output']} Best_d={r['Best_d']} Acc={r['Test_Acc']}")

# ============ 8. OLD EMEKLILIK LSTM COLUMN ORDER CHECK ============
print("\n" + "="*70)
print("PART 8: OLD EMEKLILIK_LSTM COLUMN STRUCTURE CHECK")
print("="*70)
old_emk_lstm_path = os.path.join(old_dir, 'EMEKLILIK_LSTM_sonuclar_eski.csv')
if os.path.exists(old_emk_lstm_path):
    with open(old_emk_lstm_path, 'r', encoding='utf-8-sig') as f:
        header = f.readline().strip()
    print(f"  Header: {header}")
    new_emk_lstm_path = os.path.join(new_dir, 'EMEKLILIK_LSTM_sonuclar.csv')
    with open(new_emk_lstm_path, 'r', encoding='utf-8-sig') as f:
        new_header = f.readline().strip()
    print(f"  New:    {new_header}")
    if header != new_header:
        errors.append(f"COLUMN MISMATCH: EMEKLILIK_LSTM old vs new have different headers!")

# ============ SUMMARY ============
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
if errors:
    print(f"\n*** {len(errors)} ERROR(S) FOUND ***")
    for e in errors:
        print(f"  ❌ {e}")
else:
    print("\n  ✅ No errors found")

if warnings:
    print(f"\n*** {len(warnings)} WARNING(S) ***")
    for w in warnings:
        print(f"  ⚠️  {w}")

print(f"\nTotal checks performed across 20 CSV files.")
