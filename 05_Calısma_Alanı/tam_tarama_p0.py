# -*- coding: utf-8 -*-
"""
GOD-MODE TAM TARAMA — 02 KLASÖRÜ + PROJECT_REPORT vs 20 CSV
============================================================
20 CSV: 10 x 2018-2026 + 10 x 2018-2022
02 klasöründeki TXT/HTML/DOCX/XLSX dosyaları CSV'ye göre çapraz doğrula
PROJECT_REPORT içindeki her sayısal iddia CSV'ye karşı test et
Eleştirel bak: tolerans 0.005 (yarım puan), küçük farkları da raporla
"""
import sys, io, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd

# ─── CSV YOLLARI ────────────────────────────────────────────────────────────
BASE = r'c:\Users\Kurt\Desktop\Proje\02_Akademik_Kan\u0131tlar'
import glob as gl
folders = gl.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')
BASE02 = folders[0] if folders else None
subs = [os.path.join(BASE02, d) for d in os.listdir(BASE02) if os.path.isdir(os.path.join(BASE02, d)) and 'kt' in d.lower()]
D26 = [s for s in subs if '2026' in os.path.basename(s) or '26' in os.path.basename(s)][0]
D22 = [s for s in subs if '2022' in os.path.basename(s) or '22' in os.path.basename(s)][0]

print(f'02 klasörü: {BASE02}')
print(f'2026 CSVler: {D26}')
print(f'2022 CSVler: {D22}')
print()

def load(fname, base=D26):
    return pd.read_csv(os.path.join(base, fname))

# ─── TÜM 20 CSV'Yİ YÜKLEYİP TANITIYIM ────────────────────────────────────
print('='*65)
print('BÖLÜM 0: 20 CSV DOSYA ENVANTERİ')
print('='*65)
csv_files_26 = sorted([f for f in os.listdir(D26) if f.endswith('.csv')])
csv_files_22 = sorted([f for f in os.listdir(D22) if f.endswith('.csv')])

print('2018-2026 CSVler:')
for i, f in enumerate(csv_files_26, 1):
    df = pd.read_csv(os.path.join(D26, f))
    print(f'  {i:2d}. {f:<45} {len(df)} satır, {list(df.columns)[:5]}')

print()
print('2018-2022 CSVler:')
for i, f in enumerate(csv_files_22, 1):
    df = pd.read_csv(os.path.join(D22, f))
    print(f'  {i:2d}. {f:<45} {len(df)} satır, {list(df.columns)[:5]}')
