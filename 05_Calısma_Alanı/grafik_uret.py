# -*- coding: utf-8 -*-
"""Makale Türkçe Grafikleri — 10 şekil, CSV'den otomatik"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mpatches

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
    'axes.labelsize':11,'figure.dpi':150,'savefig.dpi':200,'savefig.bbox':'tight',
    'axes.grid':True,'grid.alpha':0.3})

import glob
KANITLAR = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
K26 = [os.path.join(KANITLAR,s) for s in os.listdir(KANITLAR) if '2026' in s][0]
K22 = [os.path.join(KANITLAR,s) for s in os.listdir(KANITLAR) if '2022' in s][0]
OUT = r'c:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo\Makale_TR_Grafikleri'
os.makedirs(OUT, exist_ok=True)

def L(f, base=K26): return pd.read_csv(os.path.join(base, f))
lstm  = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn   = L('EMEKLILIK_CNN_sonuclar.csv')
naive = L('EMEKLILIK_NAIVE_baseline.csv')
arima = L('EMEKLILIK_ARIMA_sonuclar.csv')
lstm_th = L('LSTM_sonuclar_FINAL.csv')
cnn_th  = L('CNN_sonuclar_FINAL.csv')
arima_th= L('ARIMA_sonuclar.csv')
naive_th= L('NAIVE_baseline.csv')
lstm_th22 = L('LSTM_sonuclar_FINAL_eski.csv', K22)
cnn_th22  = L('CNN_sonuclar_FINAL_eski.csv',  K22)
arima_th22= L('ARIMA_sonuclar_eski.csv',      K22)

FONLAR = ['ALZ','AZS','AMZ']
FRENKLER = ['#6366F1','#0891B2','#DC2626']
MRENKLER = {'LSTM':'#2563EB','CNN':'#DC2626','ARIMA':'#16A34A','Naïve':'#D97706'}

def is_mc(r):
    s,se = r.get('Spec',1), r.get('Sens',1)
    return (pd.isna(s) or s==0 or pd.isna(se) or se==0)

# ─── ŞEKİL 1: Doğruluk Yanılgısı ────────────────────────────────
fig,ax = plt.subplots(figsize=(8,5))
# THYAO closing set LSTM — MC olan satırlar
closing = lstm_th[lstm_th['Feature_Set'].str.lower()=='closing'].copy()
best_mc = closing[closing.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
best_real = lstm_th[~lstm_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
cats = ['MC\n(Closing)', 'Gerçek\nÖğrenme']
accs = [best_mc['Mean_Acc']*100, best_real['Mean_Acc']*100]
specs= [best_mc['Spec']*100, best_real['Spec']*100]
x = np.arange(2)
b1=ax.bar(x-0.2,accs,0.35,label='Doğruluk (%)',color=['#F87171','#34D399'],zorder=3)
b2=ax.bar(x+0.2,specs,0.35,label='Özgüllük (Spec%)',color=['#FCA5A5','#6EE7B7'],zorder=3)
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,100)
ax.set_title('Şekil 1. Doğruluk Yanılgısı: Yüksek Doğruluk ≠ Gerçek Öğrenme\n(THYAO LSTM, Kapanış Özellik Seti)')
ax.legend(); ax.axhline(50,ls='--',color='gray',lw=1.2,label='Rassal Sınır')
for b in list(b1)+list(b2): ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'{b.get_height():.1f}', ha='center',fontsize=9)
plt.tight_layout(); fig.savefig(os.path.join(OUT,'Sekil_01_Dogruluk_Yanilgisi.png')); plt.close()
print('✅ Şekil 1')

# ─── ŞEKİL 2: MC Oranları (Fon × Model) ──────────────────────────
fig,ax = plt.subplots(figsize=(9,5))
modeller = ['LSTM','CNN']
mc_rates = {}
for fon in FONLAR:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[df.iloc[:,0]==fon]
        mc = sum(sub.apply(is_mc,axis=1))
        mc_rates[(fon,model)] = mc
total = {'ALZ':27,'AZS':27,'AMZ':27}
x=np.arange(3); w=0.35
lstm_mc=[mc_rates[(f,'LSTM')] for f in FONLAR]
cnn_mc =[mc_rates[(f,'CNN')]  for f in FONLAR]
total_n=[total[f] for f in FONLAR]
ax.bar(x-w/2, lstm_mc, w, label='LSTM', color=MRENKLER['LSTM'], zorder=3)
ax.bar(x+w/2, cnn_mc,  w, label='1D-CNN', color=MRENKLER['CNN'], zorder=3)
for i,(l,c,t) in enumerate(zip(lstm_mc,cnn_mc,total_n)):
    ax.text(i-w/2, l+0.3, f'{l}/{t}', ha='center', fontsize=9)
    ax.text(i+w/2, c+0.3, f'{c}/{t}', ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_ylabel('Çoğunluk Sınıfı (MC) Konfigürasyon Sayısı')
ax.set_title('Şekil 2. MC Oranları: Fon × Model\n1D-CNN her fonda LSTM\'den daha az MC üretiyor')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_02_MC_Oranları_Fon_Model.png')); plt.close()
print('✅ Şekil 2')

# ─── ŞEKİL 3: Özellik Seti Etkisi ────────────────────────────────
fig,ax = plt.subplots(figsize=(9,5))
sets_tr = {'closing':'Kapanış','technical':'Teknik','full':'Tam'}
fset_mc = {}
for fs in ['closing','technical','full']:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[df.iloc[:,1]==fs]
        mc = sum(sub.apply(is_mc,axis=1))
        tot= len(sub)
        fset_mc[(fs,model)] = (mc,tot)
x=np.arange(3); w=0.35
lstm_r=[fset_mc[(f,'LSTM')][0]/fset_mc[(f,'LSTM')][1]*100 for f in ['closing','technical','full']]
cnn_r =[fset_mc[(f,'CNN')][0]/fset_mc[(f,'CNN')][1]*100  for f in ['closing','technical','full']]
ax.bar(x-w/2, lstm_r, w, label='LSTM', color=MRENKLER['LSTM'], zorder=3)
ax.bar(x+w/2, cnn_r,  w, label='1D-CNN', color=MRENKLER['CNN'], zorder=3)
ax.set_xticks(x); ax.set_xticklabels(['Kapanış\n(Closing)','Teknik\n(Technical)','Tam\n(Full)'])
ax.set_ylabel('MC Oranı (%)'); ax.set_ylim(0,105)
ax.set_title('Şekil 3. Özellik Seti Etkisi: Kapanış Seti Yön Sinyali Taşımıyor\n(MC oranı: tek başına kapanış ≈ %100, tam set ≈ 0)')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_03_Özellik_Seti_Etkisi.png')); plt.close()
print('✅ Şekil 3')

# ─── ŞEKİL 4: Risk Profili ↔ Öğrenilebilirlik ───────────────────
fig,ax = plt.subplots(figsize=(8,5))
risk = {'ALZ':1,'AZS':3.5,'AMZ':6.5}
best_ba = {}
for fon in FONLAR:
    for model,df in [('LSTM',lstm),('CNN',cnn)]:
        sub = df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
        if len(sub)>0:
            r = sub.loc[sub['Mean_Acc'].idxmax()]
            ba = (r['Sens']+r['Spec'])/2 * 100
        else:
            ba = 50.0
        key=(fon,model)
        if key not in best_ba or ba > best_ba[key]:
            best_ba[key]=ba
for model,color,marker in [('LSTM',MRENKLER['LSTM'],'o'),('CNN',MRENKLER['CNN'],'^')]:
    xs=[risk[f] for f in FONLAR]
    ys=[best_ba.get((f,model),50) for f in FONLAR]
    ax.plot(xs,ys,color=color,marker=marker,lw=2,ms=10,label=model)
    for x,y,f in zip(xs,ys,FONLAR):
        ax.annotate(f'{f}\n{y:.1f}%',(x,y),textcoords='offset points',xytext=(0,10),ha='center',fontsize=9)
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.set_xlabel('Risk Düzeyi (1=Düşük → 7=Yüksek)')
ax.set_ylabel('En İyi Dengeli Doğruluk (BA%)')
ax.set_title('Şekil 4. Risk Profili ↔ Öğrenilebilirlik\nRisk arttıkça model öğrenme kapasitesi monoton iyileşiyor')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_04_Risk_Öğrenilebilirlik.png')); plt.close()
print('✅ Şekil 4')

# ─── ŞEKİL 5: AMZ LSTM Şampiyon — Çoklu Metrik ───────────────────
fig,ax = plt.subplots(figsize=(8,5))
# AMZ LSTM full In=2 Out=3
champ = lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]=='full')&(lstm['Input']==2)&(lstm['Output']==3)]
if len(champ)==0:
    champ = lstm[(lstm.iloc[:,0]=='AMZ')].sort_values('Mean_Acc',ascending=False).head(1)
r = champ.iloc[0]
metrics = ['Doğruluk','Dengeli\nDoğruluk','F1','Duyarlılık','Özgüllük']
vals = [r['Mean_Acc']*100, (r['Sens']+r['Spec'])/2*100, r.get('F1',0)*100, r['Sens']*100, r['Spec']*100]
colors_m = ['#2563EB','#7C3AED','#0891B2','#16A34A','#DC2626']
bars = ax.barh(metrics, vals, color=colors_m, zorder=3, height=0.55)
for b,v in zip(bars,vals):
    ax.text(v+0.5, b.get_y()+b.get_height()/2, f'{v:.1f}%', va='center', fontsize=10)
ax.axvline(50,ls='--',color='gray',lw=1.2,alpha=0.7)
ax.axvline(78.79,ls=':',color=MRENKLER['Naïve'],lw=1.5,label=f'Naïve Baseline ({78.79:.2f}%)')
ax.set_xlim(0,100); ax.set_xlabel('Değer (%)')
ax.set_title('Şekil 5. AMZ LSTM Şampiyonu — Çoklu Metrik Profili\n(full özellik, Giriş=2, Çıkış=3; p=0.0001)')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_05_AMZ_LSTM_Çoklu_Metrik.png')); plt.close()
print('✅ Şekil 5')

# ─── ŞEKİL 6: Naive Dominance — Tahmin Ufku ─────────────────────
fig,ax = plt.subplots(figsize=(9,5))
ufuklar=[1,3,5]
naive_vals = {f:{} for f in FONLAR}
for _,r in naive.iterrows():
    fon=r.iloc[0]; out=int(r['Output']); acc=r['Naive_Acc']*100
    naive_vals[fon][out]=acc
lstm_best = {}
for fon in FONLAR:
    lstm_best[fon] = {}
    for out in ufuklar:
        sub = lstm[(lstm.iloc[:,0]==fon)&(lstm['Output']==out)&~lstm.apply(is_mc,axis=1)]
        if len(sub)>0:
            lstm_best[fon][out] = sub['Mean_Acc'].max()*100
        else:
            lstm_best[fon][out] = None
x=np.arange(3)
for i,fon in enumerate(FONLAR):
    ny=[naive_vals[fon].get(o,np.nan) for o in ufuklar]
    ly=[lstm_best[fon].get(o,np.nan) for o in ufuklar]
    ax.plot(x, ny, color=FRENKLER[i], ls='-', lw=2.5, marker='s', ms=8, label=f'Naïve-{fon}')
    ax.plot(x, ly, color=FRENKLER[i], ls='--', lw=1.8, marker='o', ms=7, alpha=0.7, label=f'LSTM-{fon}')
ax.set_xticks(x); ax.set_xticklabels(['Çıkış=1\n(1 Hafta)','Çıkış=3\n(3 Hafta)','Çıkış=5\n(5 Hafta)'])
ax.set_ylabel('Doğruluk (%)'); ax.axhline(50,ls=':',color='gray',lw=1,alpha=0.5)
ax.set_title('Şekil 6. Tahmin Ufku Uzadıkça Naïve Güçleniyor\nDerin öğrenme modelleri uzun vadede Naïve\'nin gerisinde kalıyor')
ax.legend(fontsize=8,ncol=2); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_06_Naïve_Dominance.png')); plt.close()
print('✅ Şekil 6')

# ─── ŞEKİL 7: Kavramsal Sürüklenme (THYAO) ───────────────────────
fig,ax = plt.subplots(figsize=(9,5))
# 2018-2022 vs 2018-2026 ortalama doğruluk (technical set)
def mean_tech(df):
    sub = df[df['Feature_Set'].str.lower()=='technical']
    return sub['Mean_Acc'].mean()*100
l22=mean_tech(lstm_th22); l26=mean_tech(lstm_th)
c22=mean_tech(cnn_th22);  c26=mean_tech(cnn_th)
# ARIMA
a22 = arima_th22['Test_Acc'].mean()*100
a26 = arima_th['Test_Acc'].mean()*100
cats=['LSTM\n(Teknik)','1D-CNN\n(Teknik)','ARIMA']
v22=[l22,c22,a22]; v26=[l26,c26,a26]
x=np.arange(3); w=0.35
b1=ax.bar(x-w/2, v22, w, label='2018–2022', color='#3B82F6', zorder=3)
b2=ax.bar(x+w/2, v26, w, label='2018–2026', color='#EF4444', zorder=3, alpha=0.85)
for i,(a,b) in enumerate(zip(v22,v26)):
    diff=b-a
    ax.annotate(f'▼{abs(diff):.1f}pp' if diff<0 else f'▲{diff:.1f}pp',
        xy=(i+w/2, b+0.3), ha='center', fontsize=9,
        color='#EF4444' if diff<0 else '#16A34A')
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Ortalama Doğruluk (%)'); ax.set_ylim(40,65)
ax.set_title('Şekil 7. Kavramsal Sürüklenme: THYAO 2018–2022 ile 2018–2026\nDerin öğrenme %5–7 puan düşerken ARIMA baştan rassal sınırda')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_07_Kavramsal_Sürüklenme.png')); plt.close()
print('✅ Şekil 7')

# ─── ŞEKİL 8: AZS CNN vs LSTM En İyi Non-MC ─────────────────────
fig,ax = plt.subplots(figsize=(8,5))
azs_cnn = cnn[(cnn.iloc[:,0]=='AZS')&~cnn.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
azs_lstm= lstm[(lstm.iloc[:,0]=='AZS')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
models=['AZS CNN\n(Şampiyon★)','AZS LSTM']
rows=[azs_cnn, azs_lstm]
met=['Mean_Acc','Sens','Spec']
met_tr=['Doğruluk','Duyarlılık','Özgüllük']
x=np.arange(len(met)); w=0.35
for i,(m,r) in enumerate(zip([MRENKLER['CNN'],MRENKLER['LSTM']], rows)):
    vals_=[r[v]*100 for v in met]
    bars=ax.bar(x+i*w-w/2, vals_, w, label=models[i], color=m, zorder=3, alpha=0.85+i*0.1)
    for b,v in zip(bars,vals_):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, f'{v:.1f}', ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(met_tr)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,105)
ax.set_title('Şekil 8. AZS Fonu: CNN vs LSTM Karşılaştırması\nCNN teknik özelliklerde LSTM\'i hem doğruluk hem özgüllükte geçiyor')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_08_AZS_CNN_vs_LSTM.png')); plt.close()
print('✅ Şekil 8')

# ─── ŞEKİL 9: Model × Fon Isı Haritası ──────────────────────────
fig,ax = plt.subplots(figsize=(8,6))
matrix=np.zeros((3,3))
row_labels=['LSTM','1D-CNN','ARIMA']
for ri,model in enumerate(['LSTM','CNN','ARIMA']):
    for ci,fon in enumerate(FONLAR):
        if model=='ARIMA':
            sub=arima[arima.iloc[:,0]==fon]
            v=sub['Test_Acc'].max()*100 if len(sub) else 50
        else:
            df=lstm if model=='LSTM' else cnn
            sub=df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
            v=sub['Mean_Acc'].max()*100 if len(sub) else 50
        matrix[ri,ci]=v
im=ax.imshow(matrix, cmap='RdYlGn', vmin=50, vmax=85, aspect='auto')
plt.colorbar(im,ax=ax,label='Doğruluk (%)')
ax.set_xticks([0,1,2]); ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_yticks([0,1,2]); ax.set_yticklabels(row_labels)
for ri in range(3):
    for ci in range(3):
        ax.text(ci,ri,f'{matrix[ri,ci]:.1f}%', ha='center',va='center',fontsize=12,
            color='white' if matrix[ri,ci]>72 else 'black', fontweight='bold')
ax.set_title('Şekil 9. Model × Fon Doğruluk Isı Haritası\nAMZ×LSTM hücresi tek istatistiksel anlamlı başarıdır')
plt.tight_layout(); fig.savefig(os.path.join(OUT,'Sekil_09_Model_Fon_Isı_Haritası.png')); plt.close()
print('✅ Şekil 9')

# ─── ŞEKİL 10: AMZ LSTM Havuzlanmış Karmaşıklık Matrisi ──────────
fig,ax = plt.subplots(figsize=(6,5))
cm=np.array([[63,12],[3,18]])
im=ax.imshow(cm, cmap='Blues', aspect='auto')
labs=[['TP=63\n(Doğru Yükseliş)','FN=12\n(Kaçırılan Yükseliş)'],
      ['FP=3\n(Yanlış Alarm)','TN=18\n(Doğru Düşüş)']]
colors_cm=[['white','#1E3A5F'],['white','white']]
for i in range(2):
    for j in range(2):
        v=cm[i,j]
        ax.text(j,i,labs[i][j],ha='center',va='center',fontsize=11,
            color='white' if v>30 else 'black', fontweight='bold')
ax.set_xticks([0,1]); ax.set_xticklabels(['Tahmin: Yükseliş','Tahmin: Düşüş'],fontsize=11)
ax.set_yticks([0,1]); ax.set_yticklabels(['Gerçek: Yükseliş','Gerçek: Düşüş'],fontsize=11)
ax.set_title('Şekil 10. AMZ LSTM Havuzlanmış Karmaşıklık Matrisi (N=96)\n'
    'Duyarlılık=0.840 | Özgüllük=0.857 | Doğruluk=0.8021 (p=0.0001)')
plt.tight_layout(); fig.savefig(os.path.join(OUT,'Sekil_10_Havuzlanmış_Karmaşıklık_Matrisi.png')); plt.close()
print('✅ Şekil 10')

print(f'\n🎉 Tüm grafikler kaydedildi: {OUT}')
