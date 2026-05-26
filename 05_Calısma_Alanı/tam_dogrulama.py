# -*- coding: utf-8 -*-
"""TAM DOGRULAMA: G1-G14 grafik degerleri CSV ve PROJECT_REPORT ile karsilastirma"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, glob, os

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]
def L(f,b=None): return pd.read_csv(os.path.join(b or D26, f))

lstm=L('EMEKLILIK_LSTM_sonuclar.csv'); cnn=L('EMEKLILIK_CNN_sonuclar.csv')
naive=L('EMEKLILIK_NAIVE_baseline.csv'); arima=L('EMEKLILIK_ARIMA_sonuclar.csv')
lt=L('LSTM_sonuclar_FINAL.csv'); ct=L('CNN_sonuclar_FINAL.csv')
at_=L('ARIMA_sonuclar.csv'); nt=L('NAIVE_baseline.csv')
lt22=L('LSTM_sonuclar_FINAL_eski.csv',D22); ct22=L('CNN_sonuclar_FINAL_eski.csv',D22)
at22=L('ARIMA_sonuclar_eski.csv',D22)

FONLAR=['ALZ','AZS','AMZ']

def is_mc(r):
    s,se=r.get('Spec',1),r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

def chk(name, expected, actual, tol=0.01):
    ok = abs(expected-actual) <= tol
    status = 'OK' if ok else 'HATA'
    if not ok:
        print(f'  [{status}] {name}: beklenen={expected:.4f} gercek={actual:.4f} fark={actual-expected:.4f}')
    return ok

errors=0; checks=0

print('='*60)
print('G1 DOGRULAMA — Dogruluk Yanilgisi')
# MC best: closing LSTM, is_mc=True, max acc
cl=lt[lt['Feature_Set'].str.lower()=='closing']
mc_best=cl[cl.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
real_best=lt[~lt.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
print(f'  MC best: Acc={mc_best["Mean_Acc"]*100:.2f}% Spec={mc_best["Spec"]*100:.2f}% [{mc_best["Feature_Set"]} In={mc_best["Input"]} Out={mc_best["Output"]}]')
print(f'  Real best: Acc={real_best["Mean_Acc"]*100:.2f}% Spec={real_best["Spec"]*100:.2f}% [{real_best["Feature_Set"]} In={real_best["Input"]} Out={real_best["Output"]}]')
for n,e,a in [('MC_Acc',52.67,mc_best['Mean_Acc']*100),('MC_Spec',0.0,mc_best['Spec']*100),
              ('Real_Acc',57.56,real_best['Mean_Acc']*100),('Real_Spec',60.0,real_best['Spec']*100)]:
    checks+=1
    if not chk(n,e,a): errors+=1

print('='*60)
print('G2 DOGRULAMA — MC Sayilari')
expected_mc={'ALZ_LSTM':27,'ALZ_CNN':27,'AZS_LSTM':13,'AZS_CNN':9,'AMZ_LSTM':10,'AMZ_CNN':9}
for fon in FONLAR:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub=df[df.iloc[:,0]==fon]
        mc=int(sub.apply(is_mc,axis=1).sum())
        exp=expected_mc[f'{fon}_{model}']
        checks+=1
        status='OK' if mc==exp else 'HATA'
        if mc!=exp: errors+=1
        print(f'  [{status}] {fon} {model}: {mc}/27 (beklenen={exp})')

print('='*60)
print('G3 DOGRULAMA — Ozellik Seti MC Oranlari (BES)')
expected_g3={('closing','LSTM'):(27,27),('closing','CNN'):(21,27),
             ('technical','LSTM'):(13,27),('technical','CNN'):(13,27),
             ('full','LSTM'):(10,27),('full','CNN'):(11,27)}
for fs in ['closing','technical','full']:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub=df[df.iloc[:,1]==fs]
        mc=int(sub.apply(is_mc,axis=1).sum()); tot=len(sub)
        exp_mc,exp_tot=expected_g3[(fs,model)]
        checks+=1
        status='OK' if (mc==exp_mc and tot==exp_tot) else 'HATA'
        if status=='HATA': errors+=1
        print(f'  [{status}] {fs} {model}: {mc}/{tot} (beklenen={exp_mc}/{exp_tot}) = {mc/tot*100:.1f}%')

print('='*60)
print('G4 DOGRULAMA — Risk Profili BA degerleri')
ba_exp={'AZS_LSTM':72.9,'AZS_CNN':76.7,'AMZ_LSTM':84.9,'AMZ_CNN':61.7}
for fon in ['AZS','AMZ']:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub=df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
        r=sub.loc[sub['Mean_Acc'].idxmax()]
        ba=(r['Sens']+r['Spec'])/2*100
        print(f'  {fon} {model}: BA={ba:.1f}% Acc={r["Mean_Acc"]*100:.2f}% fset={r.iloc[1]} In={r["Input"]} Out={r["Output"]}')
        checks+=1
        if not chk(f'{fon}_{model}_BA',ba_exp[f'{fon}_{model}'],ba): errors+=1

print('='*60)
print('G5 DOGRULAMA — AMZ LSTM Sampiyon')
champ=lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]=='full')&(lstm['Input']==2)&(lstm['Output']==3)].iloc[0]
ba=(champ['Sens']+champ['Spec'])/2*100
print(f'  Acc={champ["Mean_Acc"]*100:.4f}% Sens={champ["Sens"]*100:.4f}% Spec={champ["Spec"]*100:.4f}% F1={champ["F1"]*100:.4f}% BA={ba:.4f}%')
for n,e,a in [('Acc',80.21,champ['Mean_Acc']*100),('Sens',84.0,champ['Sens']*100),
              ('Spec',85.71,champ['Spec']*100),('F1',89.36,champ['F1']*100),('BA',84.9,ba)]:
    checks+=1
    if not chk(n,e,a): errors+=1
naive_amz3=naive[(naive.iloc[:,0]=='AMZ')&(naive['Output']==3)]['Naive_Acc'].values[0]*100
print(f'  Naive AMZ Out=3: {naive_amz3:.2f}%')
checks+=1
if not chk('Naive_AMZ3',78.79,naive_amz3): errors+=1

print('='*60)
print('G6 DOGRULAMA — Naive vs LSTM per Fon per Ufuk')
g6_exp={
    ('AZS',1):(60.00,61.11),('AZS',3):(84.85,59.52),('AZS',5):(90.32,68.89),
    ('AMZ',1):(60.00,69.61),('AMZ',3):(78.79,80.21),('AMZ',5):(83.87,77.38),
}
for fon in ['AZS','AMZ']:
    for out in [1,3,5]:
        nv=naive[(naive.iloc[:,0]==fon)&(naive['Output']==out)]['Naive_Acc'].values[0]*100
        sub=lstm[(lstm.iloc[:,0]==fon)&(lstm['Output']==out)&~lstm.apply(is_mc,axis=1)]
        lv=sub['Mean_Acc'].max()*100 if len(sub) else float('nan')
        en,el=g6_exp[(fon,out)]
        print(f'  {fon} Out={out}: Naive={nv:.2f}%(exp={en}) LSTM={lv:.2f}%(exp={el}) diff={lv-nv:.2f}pp')
        checks+=2
        if not chk(f'Naive_{fon}_{out}',en,nv): errors+=1
        if not np.isnan(lv) and not chk(f'LSTM_{fon}_{out}',el,lv): errors+=1

print('='*60)
print('G7 DOGRULAMA — Kavramsal Surukleme')
def mean_tech(df): return df[df['Feature_Set'].str.lower()=='technical']['Mean_Acc'].mean()*100
l22=mean_tech(lt22); l26=mean_tech(lt)
c22=mean_tech(ct22); c26=mean_tech(ct)
a22=at22['Test_Acc'].mean()*100; a26=at_['Test_Acc'].mean()*100
print(f'  LSTM: 2022={l22:.2f}% 2026={l26:.2f}% fark={l26-l22:.2f}pp')
print(f'  CNN:  2022={c22:.2f}% 2026={c26:.2f}% fark={c26-c22:.2f}pp')
print(f'  ARIMA:2022={a22:.2f}% 2026={a26:.2f}% fark={a26-a22:.2f}pp')
for n,e,a in [('LSTM22',55.83,l22),('LSTM26',50.52,l26),
              ('CNN22',56.79,c22), ('CNN26',49.55,c26),
              ('ARIMA22',49.83,a22),('ARIMA26',51.34,a26)]:
    checks+=1
    if not chk(n,e,a): errors+=1

print('='*60)
print('G8 DOGRULAMA — AZS CNN vs LSTM')
azs_cnn=cnn[(cnn.iloc[:,0]=='AZS')&~cnn.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
azs_lstm=lstm[(lstm.iloc[:,0]=='AZS')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
print(f'  CNN:  Acc={azs_cnn["Mean_Acc"]*100:.2f}% Sens={azs_cnn["Sens"]*100:.2f}% Spec={azs_cnn["Spec"]*100:.2f}%')
print(f'  LSTM: Acc={azs_lstm["Mean_Acc"]*100:.2f}% Sens={azs_lstm["Sens"]*100:.2f}% Spec={azs_lstm["Spec"]*100:.2f}%')
for n,e,a in [('CNN_Acc',75.56,azs_cnn['Mean_Acc']*100),('CNN_Sens',90.91,azs_cnn['Sens']*100),
              ('CNN_Spec',62.50,azs_cnn['Spec']*100),('LSTM_Acc',68.89,azs_lstm['Mean_Acc']*100),
              ('LSTM_Sens',79.17,azs_lstm['Sens']*100),('LSTM_Spec',66.67,azs_lstm['Spec']*100)]:
    checks+=1
    if not chk(n,e,a): errors+=1

print('='*60)
print('G9 DOGRULAMA — Isi Haritasi')
g9_exp={'LSTM_ALZ':50.0,'LSTM_AZS':68.89,'LSTM_AMZ':80.21,
        'CNN_ALZ':50.0,'CNN_AZS':75.56,'CNN_AMZ':74.36,
        'ARIMA_ALZ':100.0,'ARIMA_AZS':80.65,'ARIMA_AMZ':80.65}
for model in ['LSTM','CNN','ARIMA']:
    for fon in FONLAR:
        if model=='ARIMA':
            sub=arima[arima.iloc[:,0]==fon]
            v=sub['Test_Acc'].max()*100 if len(sub) else 50.0
        else:
            df=lstm if model=='LSTM' else cnn
            sub=df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
            v=sub['Mean_Acc'].max()*100 if len(sub) else 50.0
        exp=g9_exp[f'{model}_{fon}']
        print(f'  {model} {fon}: {v:.2f}% (beklenen={exp})')
        checks+=1
        if not chk(f'{model}_{fon}',exp,v): errors+=1

print('='*60)
print('G10 DOGRULAMA — Karmasklik Matrisi')
# N=96=3x32, AMZ naive Out=3=78.79% -> p=76, neg=20
# TP=64 FN=12 FP=3 TN=17
TP=64;FN=12;FP=3;TN=17;N=96
p_acc=(TP+TN)/N
sens=TP/(TP+FN); spec=TN/(TN+FP)
print(f'  TP={TP} FN={FN} FP={FP} TN={TN} N={N}')
print(f'  Hesap: pool_Acc={p_acc:.4f} Sens={sens:.4f} Spec={spec:.4f}')
print(f'  CSV:   ort_Acc=0.8021   Sens=0.8400   Spec=0.8571')
# Sens ve Spec CSV mean degerler, pool degerler yaklasik olmali
checks+=3
if not chk('CM_Sens',0.84,sens,tol=0.02): errors+=1
if not chk('CM_Spec',0.8571,spec,tol=0.02): errors+=1
if not chk('CM_pool_Acc',0.8438,p_acc,tol=0.005): errors+=1
ort_acc=(0.8438+0.7188+0.8438)/3
print(f'  Seed ort dogrulama: ({0.8438}+{0.7188}+{0.8438})/3={ort_acc:.4f} (beklenen=0.8021) HATA={abs(ort_acc-0.8021):.4f}')

print('='*60)
print('G11 DOGRULAMA — THYAO Tum Modeller')
lstm_best_th=lt[~lt.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
cnn_best_th=ct[~ct.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
arima_best=at_.sort_values('Test_Acc',ascending=False).iloc[0]
print(f'  LSTM best: {lstm_best_th["Mean_Acc"]*100:.2f}% [{lstm_best_th["Feature_Set"]} In={lstm_best_th["Input"]} Out={lstm_best_th["Output"]}]')
print(f'  CNN best:  {cnn_best_th["Mean_Acc"]*100:.2f}% [{cnn_best_th["Feature_Set"]} In={cnn_best_th["Input"]} Out={cnn_best_th["Output"]}]')
print(f'  ARIMA best:{arima_best["Test_Acc"]*100:.2f}% [In={arima_best["Input"]} Out={arima_best["Output"]}]')
for n,e,a in [('LSTM_th',57.56,lstm_best_th['Mean_Acc']*100),
              ('CNN_th',53.97,cnn_best_th['Mean_Acc']*100),
              ('ARIMA_th',55.78,arima_best['Test_Acc']*100)]:
    checks+=1
    if not chk(n,e,a): errors+=1
for out_,nv_ in [(1,53.11),(3,73.93),(5,79.73)]:
    sub=nt[nt['Output']==out_]['Naive_Acc'].values[0]*100
    checks+=1
    if not chk(f'Naive_th_{out_}',nv_,sub): errors+=1
    print(f'  Naive Out={out_}: {sub:.2f}% (beklenen={nv_})')

print('='*60)
print('G12 DOGRULAMA — Pencere Duyarliligi THYAO LSTM')
for inp in [2,4,6]:
    for out in [1,3,5]:
        sub=lt[(lt['Input']==inp)&(lt['Output']==out)&~lt.apply(is_mc,axis=1)]
        v=sub['Mean_Acc'].max()*100 if len(sub) else float('nan')
        print(f'  In={inp} Out={out}: {v:.2f}%' + (' [MC-tumu]' if np.isnan(v) else ''))

print('='*60)
print('G13 DOGRULAMA — AMZ Seed Stabilitesi (ilk 5 non-MC)')
amz_nm=lstm[(lstm.iloc[:,0]=='AMZ')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).head(5)
for _,r in amz_nm.iterrows():
    print(f'  fset={r.iloc[1]} In={r["Input"]} Out={r["Output"]}: S23={r["Seed_23"]:.4f} S27={r["Seed_27"]:.4f} S98={r["Seed_98"]:.4f} mean={r["Mean_Acc"]:.4f}')

print('='*60)
print('G14 DOGRULAMA — THYAO p-degeri anlamlilik')
fsets=['hist_tech','technical','historical','closing']
for out in [1,3,5]:
    for model,df in [('LSTM',lt),('CNN',ct)]:
        sig=0
        for fs in fsets:
            sub=df[(df['Feature_Set']==fs)&(df['Output']==out)]
            if len(sub) and sub['P_Value'].values[0]<0.05: sig+=1
        print(f'  Out={out} {model}: {sig}/4 anlamli (p<0.05)')

print('='*60)
print(f'\nSONUC: {checks} kontrol, {errors} hata')
if errors==0:
    print('TUM DEGERLER CSV ILE UYUMLU')
else:
    print(f'{errors} DEGER HATALI - duzeltme gerekli')
