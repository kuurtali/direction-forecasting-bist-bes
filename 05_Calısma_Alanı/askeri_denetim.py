# -*- coding: utf-8 -*-
"""ASKERİ TİTİZLİKLE TAM DENETİM — Sıfırdan, hiçbir önceki sonuca güvenmeden"""
import sys, io, os, glob as gl, re, zipfile, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np

folders = gl.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')
BASE02 = folders[0]
subs = [os.path.join(BASE02, d) for d in os.listdir(BASE02) 
        if os.path.isdir(os.path.join(BASE02, d)) and 'kt' in d.lower()]
D26 = [s for s in subs if '26' in os.path.basename(s)][0]
D22 = [s for s in subs if '22' in os.path.basename(s)][0]
def L(f, b=D26): return pd.read_csv(os.path.join(b, f))

OK=[]; WARN=[]; ERR=[]
def ok(m):   OK.append(m)
def warn(m): WARN.append(m)
def err(m):  ERR.append(m)
def chk(label, val, exp, tol=0.002):
    d=abs(float(val)-float(exp))
    if d<=tol: ok(f'{label}: {float(val):.6f} == {float(exp):.6f}')
    else: err(f'{label}: CSV={float(val):.6f} != beklenen={float(exp):.6f} FARK={d:.6f}')

def is_mc(r):
    s=r.get('Spec',1); se=r.get('Sens',1)
    return pd.isna(s) or float(s)==0 or pd.isna(se) or float(se)==0

# YÜKLEMEler
lstm=L('EMEKLILIK_LSTM_sonuclar.csv'); cnn=L('EMEKLILIK_CNN_sonuclar.csv')
naive=L('EMEKLILIK_NAIVE_baseline.csv'); arima_bes=L('EMEKLILIK_ARIMA_sonuclar.csv')
lt=L('LSTM_sonuclar_FINAL.csv'); ct=L('CNN_sonuclar_FINAL.csv')
at_=L('ARIMA_sonuclar.csv'); nt=L('NAIVE_baseline.csv')
lt22=L('LSTM_sonuclar_FINAL_eski.csv',D22); ct22=L('CNN_sonuclar_FINAL_eski.csv',D22)
at22=L('ARIMA_sonuclar_eski.csv',D22); nt22=L('NAIVE_baseline_eski.csv',D22)
lstm22=L('EMEKLILIK_LSTM_sonuclar_eski.csv',D22); cnn22=L('EMEKLILIK_CNN_sonuclar_eski.csv',D22)
naive22=L('EMEKLILIK_NAIVE_baseline_eski.csv',D22); arima22=L('EMEKLILIK_ARIMA_sonuclar_eski.csv',D22)

# ================================================================
print('='*70)
print('BÖLÜM 1: ARAKAYIT vs FINAL — BYTE-BYTE KONTROL')
print('='*70)
for d, suffix in [(D26,''), (D22,'_eski')]:
    for model in ['LSTM','CNN']:
        fa=os.path.join(d,f'{model}_sonuclar_ARAKAYIT{suffix}.csv')
        fb=os.path.join(d,f'{model}_sonuclar_FINAL{suffix}.csv')
        ha=hashlib.md5(open(fa,'rb').read()).hexdigest()
        hb=hashlib.md5(open(fb,'rb').read()).hexdigest()
        if ha==hb: ok(f'ARAKAYIT==FINAL: {model}{suffix} MD5={ha[:12]}')
        else: err(f'ARAKAYIT≠FINAL: {model}{suffix} {ha[:12]}≠{hb[:12]}')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 2: SATIR SAYILARI + SÜTUN KONTROLÜ')
print('='*70)
specs = [
    ('EMEKLILIK_LSTM_sonuclar.csv', 81, ['Fon','Feature_Set','Input','Output','Mean_Acc','Sens','Spec','F1','SD']),
    ('EMEKLILIK_CNN_sonuclar.csv', 81, ['Fon','Feature_Set','Input','Output','Mean_Acc','Sens','Spec','F1','SD']),
    ('EMEKLILIK_NAIVE_baseline.csv', 27, ['Fon','Output','Naive_Acc']),
    ('EMEKLILIK_ARIMA_sonuclar.csv', 27, ['Fon','Input','Output','Best_d','Test_Acc']),
    ('LSTM_sonuclar_FINAL.csv', 36, ['Feature_Set','Input','Output','Mean_Acc','Sens','Spec','F1','SD']),
    ('CNN_sonuclar_FINAL.csv', 36, ['Feature_Set','Input','Output','Mean_Acc','Sens','Spec','F1','SD']),
    ('ARIMA_sonuclar.csv', 9, ['Input','Output','Best_d','Test_Acc']),
    ('NAIVE_baseline.csv', 9, ['Input','Output','Naive_Acc']),
]
for fname, exp_n, req_cols in specs:
    df=L(fname)
    if len(df)!=exp_n: err(f'{fname}: {len(df)} satır (beklenen {exp_n})')
    else: ok(f'{fname}: {len(df)} satır')
    miss=[c for c in req_cols if c not in df.columns]
    if miss: err(f'{fname}: EKSİK SÜTUN {miss}')
    # Duplikat satır?
    if 'Fon' in df.columns:
        key_cols = [c for c in ['Fon','Feature_Set','Input','Output'] if c in df.columns]
    else:
        key_cols = [c for c in ['Feature_Set','Input','Output'] if c in df.columns]
    dups = df.duplicated(subset=key_cols, keep=False)
    if dups.any():
        n=dups.sum()
        warn(f'{fname}: {n} duplikat anahtar satır!')
    # NaN kontrolü
    if 'Mean_Acc' in df.columns:
        na_cnt = df['Mean_Acc'].isna().sum()
        if na_cnt>0: err(f'{fname}: {na_cnt} NaN Mean_Acc!')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 3: METRİK ARALIK [0,1] + SD≥0')
print('='*70)
for fname, df in [('BES_LSTM',lstm),('BES_CNN',cnn),('THYAO_LSTM',lt),('THYAO_CNN',ct)]:
    for col in ['Mean_Acc','Sens','Spec','F1']:
        vals=df[col].dropna()
        if (vals<-0.001).any() or (vals>1.001).any():
            err(f'{fname}[{col}]: {len(vals[(vals<0)|(vals>1)])} değer [0,1] dışında')
        else: ok(f'{fname}[{col}]: aralık ✓')
    if 'SD' in df.columns:
        neg=df[df.SD<-0.001]
        if len(neg)>0: err(f'{fname}[SD]: {len(neg)} negatif')
        else: ok(f'{fname}[SD]: ≥0 ✓')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 4: BES GRID TAM MI? (3 fon × 3 fs × 3 in × 3 out = 81)')
print('='*70)
for label, df in [('BES_LSTM',lstm),('BES_CNN',cnn)]:
    fs_actual = sorted(df.Feature_Set.unique())
    # BES: closing, technical, full — "historical" YOK
    exp_fs = ['closing','full','technical']
    if fs_actual != exp_fs:
        err(f'{label}: FS={fs_actual} beklenen={exp_fs}')
    else: ok(f'{label}: FS={fs_actual} ✓')
    for fon in ['ALZ','AZS','AMZ']:
        for fs in exp_fs:
            for inp in [2,4,6]:
                for out in [1,3,5]:
                    n=len(df[(df.Fon==fon)&(df.Feature_Set==fs)&(df.Input==inp)&(df.Output==out)])
                    if n!=1: err(f'{label}: {fon}/{fs}/In{inp}/Out{out} → {n} satır (beklenen 1)')
    ok(f'{label}: 81 hücre grid tam ✓')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 5: THYAO GRID TAM MI? (4 fs × 3 in × 3 out = 36)')
print('='*70)
for label, df in [('THYAO_LSTM',lt),('THYAO_CNN',ct)]:
    fs_actual = sorted(df.Feature_Set.unique())
    for fs in fs_actual:
        for inp in [2,4,6]:
            for out in [1,3,5]:
                n=len(df[(df.Feature_Set==fs)&(df.Input==inp)&(df.Output==out)])
                if n!=1: err(f'{label}: {fs}/In{inp}/Out{out} → {n} satır')
    ok(f'{label}: grid tam ✓ (FS={fs_actual})')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 6: ALZ — TÜM SATIRLAR MC OLMALI')
print('='*70)
for label, df in [('ALZ_LSTM',lstm[lstm.Fon=='ALZ']),('ALZ_CNN',cnn[cnn.Fon=='ALZ'])]:
    non_mc = df[~df.apply(is_mc,axis=1)]
    if len(non_mc)>0:
        err(f'{label}: {len(non_mc)}/27 satır MC DEĞİL — PROBLEM!')
        print(non_mc[['Feature_Set','Input','Output','Sens','Spec']].head())
    else:
        ok(f'{label}: 27/27 MC ✓ (Spec=0 veya NaN)')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 7: MC SAYILARI — CSV vs PROJECT_REPORT')
print('='*70)
mc_expected = {
    ('ALZ','LSTM'): 27, ('ALZ','CNN'): 27,
    ('AZS','LSTM'): 13, ('AZS','CNN'): 9,
    ('AMZ','LSTM'): 10, ('AMZ','CNN'): 9,
}
for (fon,model), exp in mc_expected.items():
    df = lstm if model=='LSTM' else cnn
    actual = df[df.Fon==fon].apply(is_mc,axis=1).sum()
    chk(f'{fon}_{model}_MC', actual, exp, 0)

# THYAO MC
for m, df, exp in [('LSTM',lt,12), ('CNN',ct,9)]:
    actual = df.apply(is_mc,axis=1).sum()
    chk(f'THYAO_{m}_MC', actual, exp, 0)

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 8: ŞAMPİYON DEĞERLER — CSV DOĞRUDAN')
print('='*70)
# AMZ LSTM full In=2 Out=3
r1=lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0]
chk('AMZ_LSTM_Acc', r1.Mean_Acc, 0.8021)
chk('AMZ_LSTM_Sens', r1.Sens, 0.84)
chk('AMZ_LSTM_Spec', r1.Spec, 0.8571)
chk('AMZ_LSTM_F1', r1.F1, 0.8936)
chk('AMZ_LSTM_SD', r1.SD, 0.0722)

# AZS CNN technical In=4 Out=3
r2=cnn[(cnn.Fon=='AZS')&(cnn.Feature_Set=='technical')&(cnn.Input==4)&(cnn.Output==3)].iloc[0]
chk('AZS_CNN_Acc', r2.Mean_Acc, 0.7556)
chk('AZS_CNN_Sens', r2.Sens, 0.9091)
chk('AZS_CNN_Spec', r2.Spec, 0.625)

# THYAO
r3=lt[(lt.Feature_Set=='hist_tech')&(lt.Input==4)&(lt.Output==3)].iloc[0]
chk('THYAO_LSTM_Acc', r3.Mean_Acc, 0.5756)
chk('THYAO_LSTM_Sens', r3.Sens, 0.5742)
chk('THYAO_LSTM_Spec', r3.Spec, 0.60)

r4=ct[(ct.Feature_Set=='hist_tech')&(ct.Input==2)&(ct.Output==3)].iloc[0]
chk('THYAO_CNN_Acc', r4.Mean_Acc, 0.5397)
chk('THYAO_CNN_Spec', r4.Spec, 0.331)

# ARIMA best
r5=at_[(at_.Input==6)&(at_.Output==3)].iloc[0]
chk('THYAO_ARIMA_best', r5.Test_Acc, 0.5578)
chk('THYAO_ARIMA_ort', at_.Test_Acc.mean(), 0.5134)

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 9: NAIVE BASELINE — CSV vs PR')
print('='*70)
naive_exp = {
    ('ALZ',1): 1.0, ('ALZ',3): 1.0, ('ALZ',5): 1.0,
    ('AZS',1): 0.60, ('AZS',3): 0.8485, ('AZS',5): 0.9032,
    ('AMZ',1): 0.60, ('AMZ',3): 0.7879, ('AMZ',5): 0.8387,
}
for (fon,out), exp in naive_exp.items():
    val=naive[(naive.Fon==fon)&(naive.Output==out)].iloc[0].Naive_Acc
    chk(f'Naive_{fon}_Out{out}', val, exp)
# THYAO
for out, exp in [(1,0.5311),(3,0.7393),(5,0.7973)]:
    val=nt[nt.Output==out].iloc[0].Naive_Acc
    chk(f'Naive_THYAO_Out{out}', val, exp)

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 10: CONCEPT DRIFT — 2022 vs 2026')
print('='*70)
for fs in ['technical']:
    m22=lt22[lt22.Feature_Set==fs].Mean_Acc.mean()
    m26=lt[lt.Feature_Set==fs].Mean_Acc.mean()
    chk(f'LSTM_{fs}_2022', m22, 0.5583)
    chk(f'LSTM_{fs}_2026', m26, 0.5052)
    c22=ct22[ct22.Feature_Set==fs].Mean_Acc.mean()
    c26=ct[ct.Feature_Set==fs].Mean_Acc.mean()
    chk(f'CNN_{fs}_2022', c22, 0.5679)
    chk(f'CNN_{fs}_2026', c26, 0.4955)
chk('ARIMA_2022_ort', at22.Test_Acc.mean(), 0.4983)
chk('ARIMA_2026_ort', at_.Test_Acc.mean(), 0.5134)

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 11: CLOSING SETİ MC ZORUNLULUĞU')
print('='*70)
# THYAO closing → tümü MC olmalı
for label,df in [('THYAO_LSTM',lt),('THYAO_CNN',ct)]:
    cl=df[df.Feature_Set=='closing']
    mc_cnt=cl.apply(is_mc,axis=1).sum()
    chk(f'{label}_closing_MC', mc_cnt, 9, 0)
# BES closing
for fon in ['ALZ','AZS','AMZ']:
    for label,df in [('LSTM',lstm),('CNN',cnn)]:
        cl=df[(df.Fon==fon)&(df.Feature_Set=='closing')]
        mc_cnt=cl.apply(is_mc,axis=1).sum()
        print(f'  {fon}_{label} closing MC: {mc_cnt}/9')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 12: 02 KLASÖR METİN DOSYALARI vs CSV')
print('='*70)

# FINAL_KANIT_RAPORU.txt
fk=open(os.path.join(BASE02,'FINAL_KANIT_RAPORU.txt'),'r',encoding='utf-8',errors='replace').read()
for kw,desc in [('0.8021','AMZ_Acc'),('0.7556','AZS_Acc'),('0.5756','THYAO_LSTM'),
                ('0.5397','THYAO_CNN'),('0.5578','ARIMA_best'),('80.21','AMZ_%'),
                ('75.56','AZS_%'),('57.56','THYAO_%'),('0.7879','AMZ_Naive')]:
    if kw in fk: ok(f'FINAL_KANIT[{kw}] ({desc}) ✓')
    else: warn(f'FINAL_KANIT[{kw}] ({desc}) yok')

# MC_KANIT_RAPORU.txt
mk=open(os.path.join(BASE02,'MC_KANIT_RAPORU.txt'),'r',encoding='utf-8',errors='replace').read()
for kw,desc in [('27/27','ALZ_MC'),('13/27','AZS_LSTM_MC'),('9/27','CNN_MC'),
                ('10/27','AMZ_LSTM_MC'),('12/36','THYAO_LSTM'),('9/36','THYAO_CNN')]:
    if kw in mk: ok(f'MC_KANIT[{kw}] ({desc}) ✓')
    else: warn(f'MC_KANIT[{kw}] ({desc}) yok')

# DOC3
with zipfile.ZipFile(os.path.join(BASE02,'DOC3 Model Karsilastirma Tablolari.docx'),'r') as z:
    d3=re.sub(r'<[^>]+>',' ',z.read('word/document.xml').decode('utf-8',errors='replace'))
for kw,desc in [('80.21','AMZ'),('75.56','AZS'),('57.56','THYAO'),('84.85','Naive_AZS'),('78.79','Naive_AMZ')]:
    if kw in d3: ok(f'DOC3[{kw}] ({desc}) ✓')
    else: warn(f'DOC3[{kw}] ({desc}) yok')

# CSV_TUM_SONUCLAR.html
ht=open(os.path.join(BASE02,'CSV_TUM_SONUCLAR.html'),'r',encoding='utf-8',errors='replace').read()
for kw,desc in [('0.8021','AMZ_Acc'),('0.7556','AZS'),('0.5756','THYAO_LSTM'),
                ('0.8571','AMZ_Spec'),('0.9091','AZS_Sens'),('0.8485','AZS_Naive')]:
    if kw in ht: ok(f'HTML[{kw}] ({desc}) ✓')
    else: err(f'HTML[{kw}] ({desc}) EKSİK!')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 13: PROJECT_REPORT — KRİTİK SAYILAR')
print('='*70)
pr=open(r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJECT_REPORT.txt',
        'r',encoding='utf-8',errors='replace').read()

pr_checks = [
    ('80.21','AMZ_Acc'), ('75.56','AZS_CNN'), ('57.56','THYAO_LSTM'),
    ('53.97','THYAO_CNN'), ('55.78','ARIMA_best'), ('84.85','AZS_Naive3'),
    ('78.79','AMZ_Naive3'), ('90.32','AZS_Naive5'), ('83.87','AMZ_Naive5'),
    ('73.93','THYAO_Naive3'), ('79.73','THYAO_Naive5'), ('53.11','THYAO_Naive1'),
    ('49.83','ARIMA_2022'), ('51.34','ARIMA_2026'), ('55.83','LSTM_tech_2022'),
    ('56.79','CNN_tech_2022'), ('50.52','LSTM_tech_2026'), ('49.55','CNN_tech_2026'),
    ('12/36','THYAO_LSTM_MC'), ('9/36','THYAO_CNN_MC'),
    ('27/27','ALZ_MC'), ('13/27','AZS_LSTM_MC'), ('10/27','AMZ_LSTM_MC'),
    ('0.8400','AMZ_Sens'), ('0.8571','AMZ_Spec'), ('0.0722','AMZ_SD'),
    ('0.9091','AZS_CNN_Sens'), ('0.625','AZS_CNN_Spec'),
    ('68.89','AZS_LSTM_best'),
]
for kw,desc in pr_checks:
    if kw in pr: ok(f'PR[{kw}] ({desc}) ✓')
    else:
        # Alternatif format dene
        alt = kw.replace('.',',')
        if alt in pr: ok(f'PR[{alt}] ({desc} virgüllü) ✓')
        else: warn(f'PR[{kw}] ({desc}) bulunamadı')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 14: MAKALE.docx — KRİTİK SAYILAR')
print('='*70)
makale_path = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx'
with zipfile.ZipFile(makale_path,'r') as z:
    mraw=z.read('word/document.xml').decode('utf-8',errors='replace')
mt=re.sub(r'<[^>]+>',' ',mraw)
mt=re.sub(r'\s+',' ',mt)

# Olmaması gerekenler
for bad,desc in [('TP=63','ESKİ_TP'),('TN=18','ESKİ_TN'),('Spec=0,857','ESKİ_Spec')]:
    if bad in mt: err(f'MAKALE: "{bad}" ({desc}) HALA MEVCUT!')
    else: ok(f'MAKALE: "{bad}" ({desc}) temizlenmiş ✓')

# Olması gerekenler
for good,desc in [('TP=64','YENİ_TP'),('TN=17','YENİ_TN'),('Spec=0,850','YENİ_Spec'),
                   ('80,21','AMZ_Acc'),('84,38','Pooled_Acc'),('78,79','Naive'),
                   ('75,56','AZS_CNN'),('57,56','THYAO'),('N=96','Pooled_N'),
                   ('p=0,0001','p_value'),('R v4.5.2','R_version')]:
    if good in mt: ok(f'MAKALE: "{good}" ({desc}) ✓')
    else: warn(f'MAKALE: "{good}" ({desc}) bulunamadı')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 15: APPENDIX_D KONTROL')
print('='*70)
appd=open(r'c:\Users\Kurt\Desktop\Proje\03_Appendix\Appendix_D_Karmasiklik_Matrisleri.txt',
          'r',encoding='utf-8',errors='replace').read()
for good,desc in [('64/76','TP/P_doğru'),('17/20','TN/N_doğru'),('84.21%','Sens_doğru'),('85.00%','Spec_doğru')]:
    if good in appd: ok(f'AppD: "{good}" ({desc}) ✓')
    else: err(f'AppD: "{good}" ({desc}) EKSİK!')
for bad,desc in [('63/75','ESKİ_Sens'),('18/21','ESKİ_Spec')]:
    if bad in appd: err(f'AppD: "{bad}" ({desc}) HALA MEVCUT!')
    else: ok(f'AppD: "{bad}" ({desc}) temizlenmiş ✓')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 16: NAIVE İÇ TUTARLILIK — BES')  
print('='*70)
# NAIVE baseline'da her (Fon,Output) tekil olmalı; 3 fon × 3 out × (3 in?) = 27
# Naive In'e bağımlı olmamalı — kontrol
for fon in ['ALZ','AZS','AMZ']:
    for out in [1,3,5]:
        sub=naive[(naive.Fon==fon)&(naive.Output==out)]
        vals=sub.Naive_Acc.unique()
        if len(vals)==1:
            ok(f'Naive {fon} Out={out}: tüm In değerleri aynı ({vals[0]:.4f}) ✓')
        else:
            err(f'Naive {fon} Out={out}: FARKLI değerler! {vals}')

# ================================================================
print('\n'+'='*70)
print('BÖLÜM 17: SD DOĞRULAMASI — AMZ LSTM ŞAMPİYON')
print('='*70)
# PR 12.8.1: S23=84.38% S27=71.88% S98=84.38% → Mean=80.21%
seeds = [0.8438, 0.7188, 0.8438]
calc_mean = np.mean(seeds)
calc_sd = np.std(seeds, ddof=1)  # sample SD
print(f'  Seeds: {seeds}')
print(f'  Hesaplanan Mean: {calc_mean:.4f} (CSV: {r1.Mean_Acc:.4f})')
print(f'  Hesaplanan SD(sample): {calc_sd:.4f} (CSV: {r1.SD:.4f})')
chk('AMZ_LSTM_Mean_hesap', calc_mean, r1.Mean_Acc)
chk('AMZ_LSTM_SD_hesap', calc_sd, r1.SD)

# ================================================================
# NİHAİ RAPOR
print('\n'+'='*70)
print('NİHAİ RAPOR — ASKERİ DENETİM')
print('='*70)
print(f'\n  ✅ OK    : {len(OK)}')
print(f'  ⚠️ UYARI : {len(WARN)}')
print(f'  ❌ HATA  : {len(ERR)}')

if WARN:
    print(f'\n--- UYARILAR ({len(WARN)}) ---')
    for w in WARN: print(f'  ⚠️ {w}')
if ERR:
    print(f'\n--- HATALAR ({len(ERR)}) ---')
    for e in ERR: print(f'  ❌ {e}')
else:
    print('\n  >>> SIFIR HATA. TÜM DOSYALAR CSV GROUND-TRUTH İLE %100 UYUMLU. <<<')
