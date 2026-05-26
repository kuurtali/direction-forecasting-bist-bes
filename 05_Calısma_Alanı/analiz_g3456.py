# -*- coding: utf-8 -*-
"""G3/G4/G5/G6 grafik kaynak analizi - THYAO CNN grafik_v3/v4 hangi filtreyi kullanıyor"""
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import pandas as pd, glob, os

base=glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26=[os.path.join(base,s) for s in os.listdir(base) if '2026' in s][0]
ct=pd.read_csv(os.path.join(D26,'CNN_sonuclar_FINAL.csv'))
lt=pd.read_csv(os.path.join(D26,'LSTM_sonuclar_FINAL.csv'))
nt=pd.read_csv(os.path.join(D26,'NAIVE_baseline.csv'))

def is_mc(r):
    s,se=r.get('Spec',1),r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

print("=== G3: Input Window XLSX vs CSV ===")
print("XLSX: In2=47.44, In4=49.55, In6=50.23")
print("Grafik kaynagi THYAO CNN (4 feature set, tum outputlar) mi?")
# Tum kombinasyonlar
for inp in [2,4,6]:
    a_cnn = ct[ct['Input']==inp]['Mean_Acc'].mean()
    a_lst = lt[lt['Input']==inp]['Mean_Acc'].mean()
    # Non-MC only
    a_cnn_nm = ct[(ct['Input']==inp)&~ct.apply(is_mc,axis=1)]['Mean_Acc'].mean()
    a_lst_nm = lt[(lt['Input']==inp)&~lt.apply(is_mc,axis=1)]['Mean_Acc'].mean()
    # Closing only
    a_cnn_cl = ct[(ct['Input']==inp)&(ct['Feature_Set']=='closing')]['Mean_Acc'].mean()
    print(f"In={inp}: CNN_all={a_cnn:.4f} CNN_nonMC={a_cnn_nm:.4f} CNN_closing={a_cnn_cl:.4f} | LSTM_all={a_lst:.4f}")

print()
print("=== G4: Horizon XLSX vs CSV ===")
print("XLSX: Out1=49.89, Out3=48.32, Out5=50.23")
for out in [1,3,5]:
    a_cnn = ct[ct['Output']==out]['Mean_Acc'].mean()
    a_lst = lt[lt['Output']==out]['Mean_Acc'].mean()
    a_cnn_cl = ct[(ct['Output']==out)&(ct['Feature_Set']=='closing')]['Mean_Acc'].mean()
    a_cnn_nm = ct[(ct['Output']==out)&~ct.apply(is_mc,axis=1)]['Mean_Acc'].mean()
    print(f"Out={out}: CNN_all={a_cnn:.4f} CNN_nonMC={a_cnn_nm:.4f} CNN_closing={a_cnn_cl:.4f} | LSTM_all={a_lst:.4f}")

print()
print("=== G5: Feature Set XLSX vs CSV ===")
print("XLSX: Closing=49.32/Spec=0, Historical=53.04/Spec=44.37, Technical=50.23/Spec=47.18")
for fs in ['closing','historical','technical','hist_tech']:
    cnn_acc  = ct[ct['Feature_Set']==fs]['Mean_Acc'].mean()
    cnn_spec = ct[ct['Feature_Set']==fs]['Spec'].mean()
    lst_acc  = lt[lt['Feature_Set']==fs]['Mean_Acc'].mean()
    lst_spec = lt[lt['Feature_Set']==fs]['Spec'].mean()
    print(f"FS={fs}: CNN_acc={cnn_acc:.4f} CNN_spec={cnn_spec:.4f} | LSTM_acc={lst_acc:.4f} LSTM_spec={lst_spec:.4f}")

print()
print("=== G5: Sadece spec=0 olanlari cikar (MC temizle) ===")
lt_nonmc = lt[~lt.apply(is_mc,axis=1)]
ct_nonmc = ct[~ct.apply(is_mc,axis=1)]
for fs in ['closing','historical','technical']:
    # LSTM non-MC
    lst_acc = lt_nonmc[lt_nonmc['Feature_Set']==fs]['Mean_Acc'].mean()
    lst_spec = lt_nonmc[lt_nonmc['Feature_Set']==fs]['Spec'].mean()
    print(f"FS={fs} LSTM_nonMC: acc={lst_acc:.4f} spec={lst_spec:.4f}")

print()
print("=== G6: THYAO Naive vs CNN ===")
print("XLSX: Naive Out3=73.93, Out5=79.73, CNN Out3=50.33, CNN Out5=50.23")
nt_cols = list(nt.columns)
print(f"NAIVE columns: {nt_cols}")
print(nt.to_string())

print()
print("=== GRAFIK KODU KONTROLU: grafik_v3_p1.py ===")
# Grafik kodunu oku ve G3/G4/G5 filtresini bul
gv3 = r'c:\Users\Kurt\Desktop\Proje\06_Kodlar\grafik_v3_p1.py'
with open(gv3, encoding='utf-8', errors='replace') as f:
    code = f.read()
# G3, G4, G5 ilgili satirlari bul
lines = code.split('\n')
for i,line in enumerate(lines):
    if any(x in line for x in ['G3','G4','G5','Input Window','Horizon','Feature Set']):
        print(f"  L{i+1}: {line.rstrip()}")
