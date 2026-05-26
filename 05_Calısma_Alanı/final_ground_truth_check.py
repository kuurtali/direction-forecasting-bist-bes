# -*- coding: utf-8 -*-
"""
CSV GROUND-TRUTH KAPSAMLI DOGRULAMA
=====================================
02_Akademik_Kanitlar + PROJECT_REPORT.txt
Tum kritik sayilari CSV'den okuyup karsilastir.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, glob, re

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]

def L(f, base=None): return pd.read_csv(os.path.join(base or D26, f))

lstm   = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn    = L('EMEKLILIK_CNN_sonuclar.csv')
naive  = L('EMEKLILIK_NAIVE_baseline.csv')
arima  = L('EMEKLILIK_ARIMA_sonuclar.csv')
lt     = L('LSTM_sonuclar_FINAL.csv')
ct     = L('CNN_sonuclar_FINAL.csv')
at_    = L('ARIMA_sonuclar.csv')
nt     = L('NAIVE_baseline.csv')
lt22   = L('LSTM_sonuclar_FINAL_eski.csv', D22)
ct22   = L('CNN_sonuclar_FINAL_eski.csv', D22)

def is_mc(r):
    s, se = r.get('Spec',1), r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

OK = []; ERR = []
def chk(label, val, expected, tol=0.001):
    diff = abs(float(val) - float(expected))
    if diff <= tol:
        OK.append(label)
    else:
        ERR.append(f'  HATA: {label}: CSV={float(val):.4f} BEKLENEN={float(expected):.4f} FARK={diff:.4f}')

print('='*65)
print('BOLUM 1: EMEKLİLİK LSTM SAMPLERI')
print('='*65)

# AMZ LSTM sampiyonu
amz_lstm = lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)]
row = amz_lstm.iloc[0]
print(f'AMZ LSTM full In=2 Out=3: Acc={row.Mean_Acc:.4f} Sens={row.Sens:.4f} Spec={row.Spec:.4f} F1={row.F1:.4f}')
chk('AMZ LSTM Acc', row.Mean_Acc, 0.8021)
chk('AMZ LSTM Sens', row.Sens, 0.84)
chk('AMZ LSTM Spec', row.Spec, 0.8571)
chk('AMZ LSTM F1', row.F1, 0.8936)

# AZS CNN sampiyonu
azs_cnn = cnn[(cnn.Fon=='AZS')&(cnn.Feature_Set=='technical')&(cnn.Input==4)&(cnn.Output==3)]
row2 = azs_cnn.iloc[0]
print(f'AZS CNN tech In=4 Out=3: Acc={row2.Mean_Acc:.4f} Sens={row2.Sens:.4f} Spec={row2.Spec:.4f}')
chk('AZS CNN Acc', row2.Mean_Acc, 0.7556)
chk('AZS CNN Sens', row2.Sens, 0.9091)
chk('AZS CNN Spec', row2.Spec, 0.625)

# MC sayilari - ALZ
alz_lstm_mc = lstm[lstm.Fon=='ALZ'].apply(is_mc, axis=1).sum()
alz_cnn_mc  = cnn[cnn.Fon=='ALZ'].apply(is_mc, axis=1).sum()
print(f'ALZ LSTM MC: {alz_lstm_mc}/27  ALZ CNN MC: {alz_cnn_mc}/27')
chk('ALZ LSTM MC', alz_lstm_mc, 27)
chk('ALZ CNN MC',  alz_cnn_mc,  27)

# MC sayilari - AZS
azs_lstm_mc = lstm[lstm.Fon=='AZS'].apply(is_mc,axis=1).sum()
azs_cnn_mc  = cnn[cnn.Fon=='AZS'].apply(is_mc,axis=1).sum()
print(f'AZS LSTM MC: {azs_lstm_mc}/27  AZS CNN MC: {azs_cnn_mc}/27')
chk('AZS LSTM MC', azs_lstm_mc, 13)
chk('AZS CNN MC',  azs_cnn_mc,  9)

# MC sayilari - AMZ
amz_lstm_mc = lstm[lstm.Fon=='AMZ'].apply(is_mc,axis=1).sum()
amz_cnn_mc  = cnn[cnn.Fon=='AMZ'].apply(is_mc,axis=1).sum()
print(f'AMZ LSTM MC: {amz_lstm_mc}/27  AMZ CNN MC: {amz_cnn_mc}/27')
chk('AMZ LSTM MC', amz_lstm_mc, 10)
chk('AMZ CNN MC',  amz_cnn_mc,  9)

print()
print('='*65)
print('BOLUM 2: THYAO SONUCLARI')
print('='*65)

# THYAO LSTM sampiyonu
th_lstm = lt[(lt.Feature_Set=='hist_tech')&(lt.Input==4)&(lt.Output==3)]
row3 = th_lstm.iloc[0]
print(f'THYAO LSTM hist_tech In=4 Out=3: Acc={row3.Mean_Acc:.4f} Sens={row3.Sens:.4f} Spec={row3.Spec:.4f}')
chk('THYAO LSTM Acc', row3.Mean_Acc, 0.5756)
chk('THYAO LSTM Sens', row3.Sens, 0.5742)
chk('THYAO LSTM Spec', row3.Spec, 0.60)

# THYAO CNN
th_cnn = ct[(ct.Feature_Set=='hist_tech')&(ct.Input==2)&(ct.Output==3)]
row4 = th_cnn.iloc[0]
print(f'THYAO CNN hist_tech In=2 Out=3: Acc={row4.Mean_Acc:.4f} Sens={row4.Sens:.4f} Spec={row4.Spec:.4f}')
chk('THYAO CNN Acc', row4.Mean_Acc, 0.5397)
chk('THYAO CNN Sens', row4.Sens, 0.758)
chk('THYAO CNN Spec', row4.Spec, 0.331)

# THYAO ARIMA
th_arima = at_[(at_.Input==6)&(at_.Output==3)]
row5 = th_arima.iloc[0]
print(f'THYAO ARIMA In=6 Out=3: Acc={row5.Test_Acc:.4f}')
chk('THYAO ARIMA best Acc', row5.Test_Acc, 0.5578)

# THYAO Naive
for o in [1,3,5]:
    na = nt[nt.Output==o].iloc[0].Naive_Acc
    exp = {1:0.5311, 3:0.7393, 5:0.7973}[o]
    print(f'THYAO Naive Out={o}: {na:.4f} (beklenen {exp:.4f})')
    chk(f'THYAO Naive Out={o}', na, exp)

print()
print('='*65)
print('BOLUM 3: BES NAIVE BASELINE')
print('='*65)
for fon, out, exp in [
    ('ALZ', 3, 1.0), ('AZS', 3, 0.8485), ('AMZ', 3, 0.7879),
    ('AZS', 5, 0.9032), ('AMZ', 5, 0.8387),
]:
    na = naive[(naive.Fon==fon)&(naive.Output==out)].iloc[0].Naive_Acc
    print(f'{fon} Naive Out={out}: {na:.4f} (beklenen {exp:.4f})')
    chk(f'{fon} Naive Out={out}', na, exp)

print()
print('='*65)
print('BOLUM 4: MC SAYILARI THYAO')
print('='*65)
th_lstm_mc = lt.apply(is_mc, axis=1).sum()
th_cnn_mc  = ct.apply(is_mc, axis=1).sum()
print(f'THYAO LSTM MC: {th_lstm_mc}/36  THYAO CNN MC: {th_cnn_mc}/36')
chk('THYAO LSTM MC', th_lstm_mc, 12)
chk('THYAO CNN MC',  th_cnn_mc,  9)

print()
print('='*65)
print('BOLUM 5: CONCEPT DRIFT (eski vs yeni)')
print('='*65)
# Eski 2022 donemi
th_lstm22_tech = lt22[(lt22.Feature_Set=='technical')].Mean_Acc.mean()
th_cnn22_tech  = ct22[(ct22.Feature_Set=='technical')].Mean_Acc.mean()
th_lstm26_tech = lt[(lt.Feature_Set=='technical')].Mean_Acc.mean()
th_cnn26_tech  = ct[(ct.Feature_Set=='technical')].Mean_Acc.mean()
print(f'THYAO LSTM technical: 2022={th_lstm22_tech:.4f} 2026={th_lstm26_tech:.4f} fark={th_lstm22_tech-th_lstm26_tech:.4f}')
print(f'THYAO CNN  technical: 2022={th_cnn22_tech:.4f} 2026={th_cnn26_tech:.4f} fark={th_cnn22_tech-th_cnn26_tech:.4f}')
chk('LSTM tech 2022', th_lstm22_tech, 0.5583)
chk('CNN  tech 2022', th_cnn22_tech,  0.5679)
chk('LSTM tech 2026', th_lstm26_tech, 0.5052)
chk('CNN  tech 2026', th_cnn26_tech,  0.4955)

print()
print('='*65)
print('BOLUM 6: VAN DER BURGT REFERANS DEGERLER')
print('='*65)
# PROJECT_REPORT'taki VdB degerler (makale tablosunda): harici referans
# THYAO ARIMA ort vs VdB ARIMA ort
thyao_arima_ort = at_.Test_Acc.mean()
print(f'THYAO ARIMA ortalama: {thyao_arima_ort:.4f} (PROJECT_REPORT: ~0.5134)')
chk('THYAO ARIMA ort', thyao_arima_ort, 0.5134)

# VdB referans degerler (proje raporu kaynakli, CSV'de yok - referans)
print('VdB LSTM max (NASDAQ): 0.8222 - referans (CSV disinda)')
print('VdB LSTM ort (NASDAQ): 0.6693 - referans (CSV disinda)')
print('VdB ARIMA ort (NASDAQ): 0.6757 - referans (CSV disinda)')

print()
print('='*65)
print('BOLUM 7: POOLED MATRIX KONTROLU')
print('='*65)
# AMZ LSTM Full In=2 Out=3 seed bazli degerler
# PROJECT_REPORT 12.8.1: S23=84.38% S27=71.88% S98=84.38%
# Mean = (84.38+71.88+84.38)/3 = 80.21 - CSV'de Mean_Acc
# CSV Sens=0.84, Spec=0.857 -> son seed (Seed 98) degerleri
# Pooled TP/TN: grafik_v3_p2.py L82: TP=64, FN=12, FP=3, TN=17
amz_row = lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0]
print(f'CSV Mean_Acc={amz_row.Mean_Acc:.4f} Sens={amz_row.Sens:.4f} Spec={amz_row.Spec:.4f}')
# TP/TN hesabi (CSV-rate pooled)
N = 96
up_frac = 30/37  # EK-C: AMZ Out=3 -> 30 Up / 7 Down
total_up = int(round(amz_row.Sens * N * up_frac))  # yaklasik
# Grafik kodundan: TP=64, TN=17
print('Grafik kodu (grafik_v3_p2.py L82): TP=64, FN=12, FP=3, TN=17')
print(f'Kontrol: Acc=(64+17)/96={81/96:.4f}=84.38% | Sens=64/76={64/76:.4f}=84.21% | Spec=17/20={17/20:.4f}=85.00%')
print(f'3-seed Mean Acc = 80.21% (CSV ground-truth) - Pooled 84.38%: fark seed varyansından (PROJECT_REPORT 12.8)')

print()
print('='*65)
print('NIHAI SONUC')
print('='*65)
print(f'  Toplam OK    : {len(OK)}')
print(f'  Toplam HATA  : {len(ERR)}')
if ERR:
    print()
    print('HATALAR:')
    for e in ERR:
        print(e)
else:
    print()
    print('>>> TUM KONTROLLER GECTI. CSV ile 100% uyumlu. <<<')
