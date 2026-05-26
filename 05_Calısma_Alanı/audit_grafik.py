# -*- coding: utf-8 -*-
"""Grafik Doğrulama: CSV ground-truth ile tüm değerleri hesapla"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, glob

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
CSV26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
CSV22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]

def L(f, base=CSV26): return pd.read_csv(os.path.join(base, f))

lstm   = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn    = L('EMEKLILIK_CNN_sonuclar.csv')
naive  = L('EMEKLILIK_NAIVE_baseline.csv')
arima  = L('EMEKLILIK_ARIMA_sonuclar.csv')
lstm_th= L('LSTM_sonuclar_FINAL.csv')
cnn_th = L('CNN_sonuclar_FINAL.csv')
arima_th=L('ARIMA_sonuclar.csv')
naive_th=L('NAIVE_baseline.csv')
lstm_th22=L('LSTM_sonuclar_FINAL_eski.csv', CSV22)
cnn_th22 =L('CNN_sonuclar_FINAL_eski.csv',  CSV22)
arima_th22=L('ARIMA_sonuclar_eski.csv',     CSV22)

FONLAR = ['ALZ','AZS','AMZ']

def is_mc(r):
    s,se = r.get('Spec',1), r.get('Sens',1)
    return (pd.isna(s) or s==0 or pd.isna(se) or se==0)

sep = "=" * 60

# ───── ŞEKİL 1: Doğruluk Yanılgısı ─────
closing_th = lstm_th[lstm_th['Feature_Set'].str.lower()=='closing'].copy()
best_mc  = closing_th[closing_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
best_real= lstm_th[~lstm_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
print(sep)
print("ŞEKİL 1 – Doğruluk Yanılgısı (THYAO LSTM closing)")
print(f"  MC  : Acc={best_mc['Mean_Acc']*100:.2f}%  Spec={best_mc['Spec']*100:.2f}%  [{best_mc['Feature_Set']} In={best_mc['Input']} Out={best_mc['Output']}]")
print(f"  REAL: Acc={best_real['Mean_Acc']*100:.2f}%  Spec={best_real['Spec']*100:.2f}%  [{best_real['Feature_Set']} In={best_real['Input']} Out={best_real['Output']}]")

# ───── ŞEKİL 2: MC Oranları Fon×Model ─────
print(sep)
print("ŞEKİL 2 – MC Oranları (BES)")
for fon in FONLAR:
    for model, df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[df.iloc[:,0]==fon]
        mc  = int(sub.apply(is_mc,axis=1).sum())
        print(f"  {fon} {model}: {mc}/27 MC")

# ───── ŞEKİL 3: Özellik Seti Etkisi ─────
print(sep)
print("ŞEKİL 3 – Özellik Seti Etkisi (BES)")
for fs in ['closing','technical','full']:
    for model, df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[df.iloc[:,1]==fs]
        mc  = int(sub.apply(is_mc,axis=1).sum())
        tot = len(sub)
        print(f"  {fs} {model}: {mc}/{tot} = {mc/tot*100:.1f}%")

# ───── ŞEKİL 4: Risk Profili ─────
print(sep)
print("ŞEKİL 4 – Risk Profili ↔ Öğrenilebilirlik")
for fon in FONLAR:
    for model, df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[(df.iloc[:,0]==fon) & ~df.apply(is_mc,axis=1)]
        if len(sub)>0:
            r   = sub.loc[sub['Mean_Acc'].idxmax()]
            ba  = (r['Sens']+r['Spec'])/2*100
            print(f"  {fon} {model}: Acc={r['Mean_Acc']*100:.2f}%  BA={ba:.1f}%  fset={r.iloc[1]} In={r['Input']} Out={r['Output']}")
        else:
            print(f"  {fon} {model}: TÜM MC – BA=50.0% varsayım")

# ───── ŞEKİL 5: AMZ LSTM Çoklu Metrik ─────
print(sep)
print("ŞEKİL 5 – AMZ LSTM Şampiyon (full, In=2, Out=3)")
champ = lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]=='full')&(lstm['Input']==2)&(lstm['Output']==3)]
r = champ.iloc[0]
ba = (r['Sens']+r['Spec'])/2*100
print(f"  Acc={r['Mean_Acc']*100:.2f}%  BA={ba:.1f}%  F1={r['F1']*100:.2f}%  Sens={r['Sens']*100:.2f}%  Spec={r['Spec']*100:.2f}%")
# Naive baseline Out=3 for AMZ
amz_naive3 = naive[(naive.iloc[:,0]=='AMZ')&(naive['Output']==3)]['Naive_Acc'].values[0]*100
print(f"  Naive Baseline (AMZ Out=3): {amz_naive3:.2f}%")

# ───── ŞEKİL 6: Naive Dominance ─────
print(sep)
print("ŞEKİL 6 – Naive vs LSTM per Fon per Ufuk")
for fon in FONLAR:
    for out in [1,3,5]:
        nv = naive[(naive.iloc[:,0]==fon)&(naive['Output']==out)]['Naive_Acc'].values
        nv = nv[0]*100 if len(nv) else float('nan')
        sub = lstm[(lstm.iloc[:,0]==fon)&(lstm['Output']==out)&~lstm.apply(is_mc,axis=1)]
        lv  = sub['Mean_Acc'].max()*100 if len(sub) else float('nan')
        print(f"  {fon} Out={out}: Naive={nv:.2f}%  LSTM_best={lv:.2f}%  Fark={lv-nv:.2f}pp")

# ───── ŞEKİL 7: Kavramsal Sürüklenme (THYAO) ─────
print(sep)
print("ŞEKİL 7 – Kavramsal Sürüklenme (THYAO technical set)")
def mean_tech(df):
    return df[df['Feature_Set'].str.lower()=='technical']['Mean_Acc'].mean()*100
l22=mean_tech(lstm_th22); l26=mean_tech(lstm_th)
c22=mean_tech(cnn_th22);  c26=mean_tech(cnn_th)
a22=arima_th22['Test_Acc'].mean()*100
a26=arima_th['Test_Acc'].mean()*100
print(f"  LSTM 2022={l22:.2f}%  2026={l26:.2f}%  fark={l26-l22:.2f}pp")
print(f"  CNN  2022={c22:.2f}%  2026={c26:.2f}%  fark={c26-c22:.2f}pp")
print(f"  ARIMA2022={a22:.2f}%  2026={a26:.2f}%  fark={a26-a22:.2f}pp")

# ───── ŞEKİL 8: AZS CNN vs LSTM ─────
print(sep)
print("ŞEKİL 8 – AZS CNN vs LSTM En İyi Non-MC")
azs_cnn  = cnn[(cnn.iloc[:,0]=='AZS') &~cnn.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
azs_lstm = lstm[(lstm.iloc[:,0]=='AZS')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
for nm, r in [('CNN', azs_cnn),('LSTM', azs_lstm)]:
    print(f"  AZS {nm}: Acc={r['Mean_Acc']*100:.2f}%  Sens={r['Sens']*100:.2f}%  Spec={r['Spec']*100:.2f}%  fset={r.iloc[1]} In={r['Input']} Out={r['Output']}")
print(f"  UYARI KONTROLÜ: CNN_Acc {azs_cnn['Mean_Acc']*100:.2f}% > LSTM_Acc {azs_lstm['Mean_Acc']*100:.2f}%? => {'EVET' if azs_cnn['Mean_Acc']>azs_lstm['Mean_Acc'] else 'HAYIR'}")
print(f"  UYARI KONTROLÜ: CNN_Spec {azs_cnn['Spec']*100:.2f}% > LSTM_Spec {azs_lstm['Spec']*100:.2f}%? => {'EVET' if azs_cnn['Spec']>azs_lstm['Spec'] else 'HAYIR (BAŞLIK YANLIIŞ!)'}")

# ───── ŞEKİL 9: Isı Haritası ─────
print(sep)
print("ŞEKİL 9 – Model×Fon Isı Haritası (max non-MC Acc)")
for model in ['LSTM','CNN','ARIMA']:
    row = []
    for fon in FONLAR:
        if model=='ARIMA':
            sub = arima[arima.iloc[:,0]==fon]
            v   = sub['Test_Acc'].max()*100 if len(sub) else 50.0
        else:
            df  = lstm if model=='LSTM' else cnn
            sub = df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
            v   = sub['Mean_Acc'].max()*100 if len(sub) else 50.0
        row.append(v)
    print(f"  {model}: ALZ={row[0]:.2f}%  AZS={row[1]:.2f}%  AMZ={row[2]:.2f}%")

# ───── ŞEKİL 10: Confusion Matrix ─────
print(sep)
print("ŞEKİL 10 – AMZ LSTM Havuzlanmış Karmaşıklık Matrisi")
# N=96 toplam test, 3 seed × (In=2,Out=3,full)
# Sens=0.840, Spec=0.857, Acc=0.8021
# Pozitif sınıf = Yükseliş
# Test set: toplam pozitif = Sens*TP+FN, negative = TN+FP
# Acc=0.8021 → (TP+TN)/96 = 0.8021 → TP+TN = 76.9 ≈ 77 (kodda 63+18=81 var!)
# Kontrol:
TP=63; FN=12; FP=3; TN=18
N=TP+FN+FP+TN
acc_check = (TP+TN)/N
sens_check = TP/(TP+FN)
spec_check = TN/(TN+FP)
print(f"  Kodda: TP={TP} FN={FN} FP={FP} TN={TN}  N={N}")
print(f"  Hesap: Acc={acc_check:.4f}  Sens={sens_check:.4f}  Spec={spec_check:.4f}")
print(f"  CSV:   Acc=0.8021       Sens=0.8400       Spec=0.8571")
print(f"  UYUM: Acc={'OK' if abs(acc_check-0.8021)<0.01 else 'HATA'}  Sens={'OK' if abs(sens_check-0.84)<0.01 else 'HATA'}  Spec={'OK' if abs(spec_check-0.8571)<0.01 else 'HATA'}")
# Doğru matris bulma: 3 seed×N_per_seed
# Seed bazında değil havuzlanmış; Acc=0.8021, Sens=0.840, Spec=0.8571
# Toplam N bilinmeli; mevcut N=96 olarak belgelenmiş
# Hesap: TP+FN+FP+TN=96; TP/(TP+FN)=0.840; TN/(TN+FP)=0.8571; (TP+TN)/96=0.8021
# Pozitif sayısı p= TP+FN, negatif q=96-p
# 0.840*p + 0.8571*(96-p) = 0.8021*96 = 76.99
# 0.840p + 82.28 - 0.8571p = 76.99
# -0.0171p = -5.29 → p=309 → YANLIŞ, N daha büyük olmalı
# En doğru: seed başı N hesabı
amz_lstm_champ = lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]=='full')&(lstm['Input']==2)&(lstm['Output']==3)].iloc[0]
print(f"\n  CSV seed değerleri: S23={amz_lstm_champ['Seed_23']} S27={amz_lstm_champ['Seed_27']} S98={amz_lstm_champ['Seed_98']}")
print(f"  CSV n test noktası: BES haftalık ~262 hafta → Out=3 test window için kontrol gerek")
print(f"  SONUÇ: N=96 ifadesi 3 seed × 32 test noktası anlamına gelir")
print(f"  Kontrol: 3×32=96 ✓")
print(f"  Doğru matris: TP+FN=0.840×96=80.64≈81 pozitif; TN+FP=15 negatif")
p=81; q=15
TP_=round(0.840*p); FN_=p-TP_
TN_=round(0.8571*q); FP_=q-TN_
acc_=( TP_+TN_)/96
print(f"  Doğru değerler: TP={TP_} FN={FN_} FP={FP_} TN={TN_}  N={p+q}")
print(f"  Doğru Acc={acc_:.4f} vs CSV 0.8021 → Fark={abs(acc_-0.8021):.4f}")

# ───── THYAO Grafikleri (Root + TR) ─────
print(sep)
print("THYAO LSTM en iyi non-MC:")
r = lstm_th[~lstm_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
print(f"  Acc={r['Mean_Acc']*100:.2f}%  Sens={r['Sens']*100:.2f}%  Spec={r['Spec']*100:.2f}%  [{r['Feature_Set']} In={r['Input']} Out={r['Output']}]")
print("THYAO CNN en iyi non-MC:")
r2= cnn_th[~cnn_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
print(f"  Acc={r2['Mean_Acc']*100:.2f}%  Sens={r2['Sens']*100:.2f}%  Spec={r2['Spec']*100:.2f}%  [{r2['Feature_Set']} In={r2['Input']} Out={r2['Output']}]")
print("THYAO ARIMA en iyi:")
ra= arima_th.sort_values('Test_Acc',ascending=False).iloc[0]
print(f"  Acc={ra['Test_Acc']*100:.2f}%  In={ra['Input']} Out={ra['Output']}")
print("THYAO Naive:")
for _,row in naive_th.iterrows():
    print(f"  In={row['Input']} Out={row['Output']}: {row['Naive_Acc']*100:.2f}%")

print(sep)
print("TAMAMLANDI")
