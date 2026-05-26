# -*- coding: utf-8 -*-
import sys, io, pandas as pd, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r'c:\Users\Kurt\Desktop\Proje'
ak = os.path.join(BASE, '02_Akademik_Kanıtlar')
subdirs = [d for d in os.listdir(ak) if os.path.isdir(os.path.join(ak, d))]
csv26_dir = None
for d in subdirs:
    if '2026' in d: csv26_dir = os.path.join(ak, d)

df = pd.read_csv(os.path.join(csv26_dir, 'EMEKLILIK_CNN_sonuclar.csv'))
amz = df[df['Fon']=='AMZ']

print('=== AMZ CNN TUM NON-MC KONFIGURASYONLAR ===')
for _, row in amz.iterrows():
    spec = row['Spec']; sens = row['Sens']
    is_mc = pd.isna(spec) or float(spec)==0 or pd.isna(sens) or float(sens)==0
    if not is_mc:
        fset = row['Feature_Set']
        print(f"  {fset:12s} In={row['Input']} Out={row['Output']} Acc={row['Mean_Acc']:.4f} Sens={sens:.4f} Spec={spec:.4f}")

print('\n=== PROJE_RAPOR AMZ CNN (full, In=4, Out=1) ===')
match = amz[(amz['Feature_Set']=='full') & (amz['Input']==4) & (amz['Output']==1)]
for _, row in match.iterrows():
    print(f"  Acc={row['Mean_Acc']:.4f} Sens={row['Sens']:.4f} Spec={row['Spec']:.4f}")

# Naive baseline
df_naive = pd.read_csv(os.path.join(csv26_dir, 'EMEKLILIK_NAIVE_baseline.csv'))
print('\n=== AZS NAIVE ===')
azs_n = df_naive[df_naive['Fon']=='AZS'].drop_duplicates(subset=['Output'])
for _, row in azs_n.iterrows():
    print(f"  Out={row['Output']}: {row['Naive_Acc']:.4f}")

print('\n=== AMZ NAIVE ===')
amz_n = df_naive[df_naive['Fon']=='AMZ'].drop_duplicates(subset=['Output'])
for _, row in amz_n.iterrows():
    print(f"  Out={row['Output']}: {row['Naive_Acc']:.4f}")

print('\n=== PROJE_RAPOR UYUSMAZLIK KONTROLU ===')
# PROJE_RAPOR Bolum 7.2: AZS Naive: Out=1 %60.00, Out=3 %78.79, Out=5 %90.32
# CSV: Out=1 0.6000, Out=3 0.8485, Out=5 0.9032
print('PROJE_RAPOR AZS Naive Out=3 = %78.79')
print('CSV AZS Naive Out=3 = 0.8485 = %84.85')
azs_out3 = azs_n[azs_n['Output']==3]['Naive_Acc'].values[0]
print(f'GERCEK CSV DEGERI: {azs_out3}')

# PROJE_RAPOR Bolum 10: AMZ CNN: full, In=4, Out=1, Acc=0.604
# CSV'den en iyi non-MC: closing, In=6, Out=5, Acc=0.7436
# Ama PROJE_RAPOR Bolum 10 diyor ki "full, In=4, Out=1" -> bu dogru mu?
amz_full41 = amz[(amz['Feature_Set']=='full') & (amz['Input']==4) & (amz['Output']==1)]
for _, row in amz_full41.iterrows():
    a = row['Mean_Acc']; s = row['Spec']; se = row['Sens']
    print(f'\nAMZ CNN full In=4 Out=1: Acc={a:.4f} Spec={s:.4f} Sens={se:.4f}')
    print(f'PROJE_RAPOR: Acc=0.604, Spec=0.583 (Bolum 10)')
    print(f'CSV: Acc={a:.4f}, Spec={s:.4f}')
    if abs(a - 0.604) < 0.001:
        print('>>> UYUMLU')
    else:
        print('>>> UYUSMAZLIK!')
