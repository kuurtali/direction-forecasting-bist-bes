# -*- coding: utf-8 -*-
"""Faz 1: 20 CSV Ground Truth + PROJE_RAPOR Uyuşmazlık Kontrolü"""
import pandas as pd, os, json, math

BASE = r"c:\Users\Kurt\Desktop\Proje"
CSV26 = os.path.join(BASE, "02_Akademik_Kanıtlar", "2018-2026 cıktılar")
CSV22 = os.path.join(BASE, "02_Akademik_Kanıtlar", "2018-2022 cıktılar")

# Try to find actual folder names (encoding issues)
ak_dir = os.path.join(BASE, "02_Akademik_Kanıtlar")
subdirs = [d for d in os.listdir(ak_dir) if os.path.isdir(os.path.join(ak_dir, d))]
print("02 subdirs:", subdirs)

csv26_dir = None
csv22_dir = None
for d in subdirs:
    full = os.path.join(ak_dir, d)
    if "2026" in d or "2026" in d:
        csv26_dir = full
    elif "2022" in d or "2022" in d:
        csv22_dir = full

print(f"CSV26 dir: {csv26_dir}")
print(f"CSV22 dir: {csv22_dir}")

def load_csvs(folder, suffix=""):
    results = {}
    if not folder or not os.path.exists(folder):
        print(f"WARN: folder not found: {folder}")
        return results
    for f in os.listdir(folder):
        if f.endswith(".csv"):
            path = os.path.join(folder, f)
            try:
                df = pd.read_csv(path)
                results[f] = df
                print(f"  Loaded {f}: {len(df)} rows, cols={list(df.columns)}")
            except Exception as e:
                print(f"  ERROR loading {f}: {e}")
    return results

print("\n=== 2018-2026 CSV'ler ===")
csvs_26 = load_csvs(csv26_dir)

print("\n=== 2018-2022 CSV'ler ===")
csvs_22 = load_csvs(csv22_dir)

# --- MC Analysis ---
def count_mc(df, model_name):
    """Count MC rows: Spec=0 OR Sens=0 OR Spec=NA"""
    mc_count = 0
    total = len(df)
    spec_col = None
    sens_col = None
    for c in df.columns:
        cl = c.lower().strip()
        if 'spec' in cl or 'specificity' in cl:
            spec_col = c
        if 'sens' in cl or 'sensitivity' in cl:
            sens_col = c
    if spec_col is None or sens_col is None:
        return None, total  # Not applicable (ARIMA/Naive)
    for _, row in df.iterrows():
        spec = row[spec_col]
        sens = row[sens_col]
        is_mc = False
        if pd.isna(spec) or (isinstance(spec, str) and spec.strip().upper() in ['NA','NAN','']):
            is_mc = True
        elif float(spec) == 0:
            is_mc = True
        if pd.isna(sens) or (isinstance(sens, str) and sens.strip().upper() in ['NA','NAN','']):
            is_mc = True
        elif float(sens) == 0:
            is_mc = True
        if is_mc:
            mc_count += 1
    return mc_count, total

print("\n=== MC SAYIMLARI (2018-2026) ===")
mc_results_26 = {}
for name, df in csvs_26.items():
    mc, total = count_mc(df, name)
    if mc is not None:
        print(f"  {name}: MC={mc}/{total}")
        mc_results_26[name] = (mc, total)

print("\n=== MC SAYIMLARI (2018-2022) ===")
mc_results_22 = {}
for name, df in csvs_22.items():
    mc, total = count_mc(df, name)
    if mc is not None:
        print(f"  {name}: MC={mc}/{total}")
        mc_results_22[name] = (mc, total)

# --- Champion configs verification ---
print("\n=== ŞAMPİYON KONFİGÜRASYON DOĞRULAMASI ===")

def find_best(df, fon=None, non_mc_only=True):
    """Find best non-MC config"""
    spec_col = sens_col = acc_col = fset_col = in_col = out_col = None
    for c in df.columns:
        cl = c.lower().strip()
        if 'spec' in cl: spec_col = c
        if 'sens' in cl: sens_col = c
        if 'mean_acc' in cl or 'test_acc' in cl: acc_col = c
        if 'feature' in cl: fset_col = c
        if cl in ['input','input_len']: in_col = c
        if cl in ['output','output_len']: out_col = c
    if acc_col is None:
        return None
    
    best_acc = -1
    best_row = None
    for _, row in df.iterrows():
        if fon and 'Fon' in df.columns and row['Fon'] != fon:
            continue
        if non_mc_only and spec_col and sens_col:
            spec = row[spec_col]
            sens = row[sens_col]
            if pd.isna(spec) or float(spec) == 0:
                continue
            if pd.isna(sens) or float(sens) == 0:
                continue
        acc = float(row[acc_col])
        if acc > best_acc:
            best_acc = acc
            best_row = row
    return best_row

# THYAO LSTM best
for fname in ['LSTM_sonuclar_FINAL.csv']:
    if fname in csvs_26:
        best = find_best(csvs_26[fname])
        if best is not None:
            print(f"\nTHYAO LSTM best non-MC:")
            for c in csvs_26[fname].columns:
                print(f"  {c}: {best[c]}")

# THYAO CNN best
for fname in ['CNN_sonuclar_FINAL.csv']:
    if fname in csvs_26:
        best = find_best(csvs_26[fname])
        if best is not None:
            print(f"\nTHYAO CNN best non-MC:")
            for c in csvs_26[fname].columns:
                print(f"  {c}: {best[c]}")

# Emeklilik best configs
for fname in ['EMEKLILIK_LSTM_sonuclar.csv']:
    if fname in csvs_26:
        for fon in ['AZS','AMZ']:
            best = find_best(csvs_26[fname], fon=fon)
            if best is not None:
                print(f"\n{fon} LSTM best non-MC:")
                for c in csvs_26[fname].columns:
                    print(f"  {c}: {best[c]}")

for fname in ['EMEKLILIK_CNN_sonuclar.csv']:
    if fname in csvs_26:
        for fon in ['AZS','AMZ']:
            best = find_best(csvs_26[fname], fon=fon)
            if best is not None:
                print(f"\n{fon} CNN best non-MC:")
                for c in csvs_26[fname].columns:
                    print(f"  {c}: {best[c]}")

# --- ARIMA & Naive ---
print("\n=== ARIMA SONUÇLARI ===")
for fname in ['ARIMA_sonuclar.csv','EMEKLILIK_ARIMA_sonuclar.csv']:
    if fname in csvs_26:
        print(f"\n{fname}:")
        print(csvs_26[fname].to_string(index=False))

print("\n=== NAIVE BASELINE ===")
for fname in ['NAIVE_baseline.csv','EMEKLILIK_NAIVE_baseline.csv']:
    if fname in csvs_26:
        print(f"\n{fname}:")
        print(csvs_26[fname].to_string(index=False))

# --- PROJE_RAPOR values to verify ---
print("\n=== PROJE_RAPOR KARŞILAŞTIRMA ===")
expected = {
    "THYAO LSTM MC (2026)": ("12/36", mc_results_26.get('LSTM_sonuclar_FINAL.csv')),
    "THYAO CNN MC (2026)": ("9/36", mc_results_26.get('CNN_sonuclar_FINAL.csv')),
    "THYAO LSTM MC (2022)": ("16/36", mc_results_22.get('LSTM_sonuclar_FINAL_eski.csv')),
    "THYAO CNN MC (2022)": ("8/36", mc_results_22.get('CNN_sonuclar_FINAL_eski.csv')),
}

# Emeklilik MC counts per fund
for fname_pattern, model in [('EMEKLILIK_LSTM_sonuclar', 'LSTM'), ('EMEKLILIK_CNN_sonuclar', 'CNN')]:
    for period, csvs, suffix in [('2026', csvs_26, '.csv'), ('2022', csvs_22, '_eski.csv')]:
        fname = fname_pattern + suffix
        if fname in csvs:
            df = csvs[fname]
            spec_col = sens_col = None
            for c in df.columns:
                cl = c.lower().strip()
                if 'spec' in cl: spec_col = c
                if 'sens' in cl: sens_col = c
            if spec_col and sens_col and 'Fon' in df.columns:
                for fon in ['ALZ','AZS','AMZ']:
                    sub = df[df['Fon'] == fon]
                    mc = 0
                    for _, row in sub.iterrows():
                        spec = row[spec_col]
                        sens = row[sens_col]
                        is_mc = False
                        if pd.isna(spec) or float(spec) == 0: is_mc = True
                        if pd.isna(sens) or float(sens) == 0: is_mc = True
                        if is_mc: mc += 1
                    print(f"  {fon} {model} MC ({period}): {mc}/{len(sub)}")

print("\n=== SCRIPT TAMAMLANDI ===")
