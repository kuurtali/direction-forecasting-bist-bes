# -*- coding: utf-8 -*-
"""Makale Grafikleri v3 - Baslik duzeltme + yeni grafikler (Parca 1/2: Sekil 1-7)"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import glob, os

plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,
    'axes.labelsize':11,'figure.dpi':150,'savefig.dpi':200,
    'savefig.bbox':'tight','axes.grid':True,'grid.alpha':0.3
})

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]
def L(f,b=None): return pd.read_csv(os.path.join(b or D26, f))

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
at22   = L('ARIMA_sonuclar_eski.csv', D22)

FONLAR = ['ALZ','AZS','AMZ']
MC = {'LSTM':'#2563EB','CNN':'#DC2626','ARIMA':'#16A34A','Naive':'#D97706'}
FR = ['#6366F1','#0891B2','#DC2626']

def is_mc(r):
    s,se = r.get('Spec',1), r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

OUT = r'c:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo\Makale_TR_Grafikleri'
os.makedirs(OUT, exist_ok=True)

# ── G1: Dogruluk Yanilgisi ──────────────────────────────────────────
# MC: closing In=2 Out=5 Acc=52.67% Spec=0%
# REAL: hist_tech In=4 Out=3 Acc=57.56% Spec=60%
fig,ax = plt.subplots(figsize=(8,5))
cats  = ['MC Konfigürasyon\n(Kapanış Seti)','Gerçek Öğrenme\n(hist_tech Seti)']
accs  = [52.67, 57.56]
specs = [0.0,   60.00]
x = np.arange(2)
b1=ax.bar(x-0.2, accs,  0.35, label='Doğruluk (%)',color=['#F87171','#34D399'],zorder=3)
b2=ax.bar(x+0.2, specs, 0.35, label='Özgüllük (%)',color=['#FCA5A5','#6EE7B7'],zorder=3)
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,80)
ax.axhline(50,ls='--',color='gray',lw=1.2,label='Rassal Sınır (%50)')
ax.set_title('Yüksek Doğruluk ≠ Gerçek Öğrenme\nTHYAO LSTM — Kapanış Özellik Seti')
ax.legend(fontsize=9)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.8,
            f'{b.get_height():.1f}%',ha='center',fontsize=9,fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G1_Dogruluk_Yanilgisi.png')); plt.close()
print('OK G1')

# ── G2: MC Oranlari Fon x Model ────────────────────────────────────
# ALZ LSTM=27 CNN=27 | AZS LSTM=13 CNN=9 | AMZ LSTM=10 CNN=9
fig,ax = plt.subplots(figsize=(9,5))
lstm_mc=[27,13,10]; cnn_mc=[27,9,9]
x=np.arange(3); w=0.35
b1=ax.bar(x-w/2,lstm_mc,w,label='LSTM',  color=MC['LSTM'],zorder=3)
b2=ax.bar(x+w/2,cnn_mc, w,label='1D-CNN',color=MC['CNN'], zorder=3)
for i,(l,c) in enumerate(zip(lstm_mc,cnn_mc)):
    ax.text(i-w/2,l+0.3,f'{l}/27',ha='center',fontsize=9,fontweight='bold')
    ax.text(i+w/2,c+0.3,f'{c}/27',ha='center',fontsize=9,fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_ylabel('MC Konfigürasyon Sayısı'); ax.set_ylim(0,33)
ax.set_title('Çoğunluk Sınıfı (MC) Tuzağı: Fon ve Model Bazında\n1D-CNN her fonda LSTM\'den daha az MC üretiyor')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G2_MC_Oranlari.png')); plt.close()
print('OK G2')

# ── G3: Ozellik Seti Etkisi ─────────────────────────────────────────
# closing LSTM=100% CNN=77.8% | technical LSTM=48.1% CNN=48.1% | full LSTM=37% CNN=40.7%
fig,ax = plt.subplots(figsize=(9,5))
lstm_r=[100.0,48.1,37.0]; cnn_r=[77.8,48.1,40.7]
x=np.arange(3); w=0.35
b1=ax.bar(x-w/2,lstm_r,w,label='LSTM',  color=MC['LSTM'],zorder=3)
b2=ax.bar(x+w/2,cnn_r, w,label='1D-CNN',color=MC['CNN'], zorder=3,alpha=0.85)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+1,
            f'{b.get_height():.1f}%',ha='center',fontsize=9,fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['Kapanış\n(Closing)','Teknik\n(Technical)','Tam\n(Full)'])
ax.set_ylabel('MC Oranı (%)'); ax.set_ylim(0,115)
ax.set_title('Özellik Seti Seçimi ve MC Tuzağı\nKapanış seti yön sinyali taşımıyor; tam set riski büyük ölçüde azaltıyor')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G3_Ozellik_Seti_Etkisi.png')); plt.close()
print('OK G3')

# ── G4: Risk Profili ─────────────────────────────────────────────────
# ALZ=50*(MC) | AZS LSTM=72.9 CNN=76.7 | AMZ LSTM=84.9 CNN=61.7
fig,ax = plt.subplots(figsize=(8,5))
rx={'ALZ':1.0,'AZS':4.0,'AMZ':7.0}
ba={'ALZ_LSTM':50.0,'ALZ_CNN':50.0,'AZS_LSTM':72.9,'AZS_CNN':76.7,'AMZ_LSTM':84.9,'AMZ_CNN':61.7}
for model,color,marker in [('LSTM',MC['LSTM'],'o'),('CNN',MC['CNN'],'^')]:
    xs=[rx[f] for f in FONLAR]
    ys=[ba[f+'_'+model] for f in FONLAR]
    ax.plot(xs,ys,color=color,marker=marker,lw=2,ms=10,label=model,zorder=3)
    for x_,y_,f in zip(xs,ys,FONLAR):
        note='*' if f=='ALZ' else ''
        ax.annotate(f'{f}{note}\n{y_:.1f}%',(x_,y_),
                    textcoords='offset points',xytext=(0,12),ha='center',fontsize=9,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.set_xlabel('Risk Düzeyi (1=Düşük → 7=Yüksek)')
ax.set_ylabel('En İyi Dengeli Doğruluk (BA%)')
ax.set_xticks([1,4,7]); ax.set_xticklabels(['ALZ\n(Düşük)','AZS\n(Orta)','AMZ\n(Yüksek)'])
ax.set_ylim(40,100)
ax.set_title('Risk Profili ve Öğrenilebilirlik İlişkisi\nRisk arttıkça LSTM kapasitesi artıyor (*ALZ: tüm yapılandırmalar MC)')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G4_Risk_Ogrenilebilirlik.png')); plt.close()
print('OK G4')

# ── G5: AMZ LSTM Sampiyonu ──────────────────────────────────────────
# Acc=80.21 BA=84.9 F1=89.36 Sens=84.00 Spec=85.71 | Naive=78.79
fig,ax = plt.subplots(figsize=(8,5))
metrics=['Doğruluk','Dengeli\nDoğruluk','F1 Skoru','Duyarlılık','Özgüllük']
vals=[80.21,84.9,89.36,84.00,85.71]
colors_m=['#2563EB','#7C3AED','#0891B2','#16A34A','#DC2626']
bars=ax.barh(metrics,vals,color=colors_m,zorder=3,height=0.55)
for b,v in zip(bars,vals):
    ax.text(v+0.5,b.get_y()+b.get_height()/2,f'{v:.2f}%',va='center',fontsize=10,fontweight='bold')
ax.axvline(50,  ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.axvline(78.79,ls=':',color=MC['Naive'],lw=2,label='Naïve Baseline (78.79%)')
ax.set_xlim(0,100); ax.set_xlabel('Değer (%)')
ax.set_title('AMZ LSTM En İyi Konfigürasyon — Çoklu Metrik Profili\nTam özellik, Giriş=2 hafta, Çıkış=3 hafta (p=0.0001)')
ax.legend(fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G5_AMZ_LSTM_Coklu_Metrik.png')); plt.close()
print('OK G5')

# ── G6: Naive Dominance ─────────────────────────────────────────────
# AZS: Out1 N=60 L=61.1 | Out3 N=84.9 L=59.5 | Out5 N=90.3 L=68.9
# AMZ: Out1 N=60 L=69.6 | Out3 N=78.8 L=80.2 | Out5 N=83.9 L=77.4
fig,ax = plt.subplots(figsize=(10,5))
x=np.arange(3)
nd={'AZS':[60.00,84.85,90.32],'AMZ':[60.00,78.79,83.87]}
ld={'AZS':[61.11,59.52,68.89],'AMZ':[69.61,80.21,77.38]}
cols={'AZS':'#0891B2','AMZ':'#DC2626'}
for fon in ['AZS','AMZ']:
    c=cols[fon]
    ax.plot(x,nd[fon],color=c,ls='-', lw=2.5,marker='s',ms=8,label=f'Naïve-{fon}')
    ax.plot(x,ld[fon],color=c,ls='--',lw=1.8,marker='o',ms=7,alpha=0.75,label=f'LSTM-{fon}')
ax.axhline(100,color='#6366F1',ls=':',lw=1.5,alpha=0.6,label='ALZ Naïve=100% (tüm ufuklar)')
ax.axhline(50, color='gray',   ls=':',lw=1,  alpha=0.5)
for fon in ['AZS','AMZ']:
    for i,out in enumerate([1,3,5]):
        diff=ld[fon][i]-nd[fon][i]
        clr='#16A34A' if diff>0 else '#EF4444'
        ax.annotate(f'{"+" if diff>0 else ""}{diff:.1f}pp',
                    (i,max(nd[fon][i],ld[fon][i])+1.8),ha='center',fontsize=8,color=clr)
ax.set_xticks(x)
ax.set_xticklabels(['Çıkış=1\n(1 Hafta)','Çıkış=3\n(3 Hafta)','Çıkış=5\n(5 Hafta)'])
ax.set_ylabel('Doğruluk (%)')
ax.set_title('Tahmin Ufku Uzadıkça Naïve Baseline Güçleniyor\nAMZ Out=3 dışında derin öğrenme Naïve\'in gerisinde')
ax.legend(fontsize=8,ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G6_Naive_Dominance.png')); plt.close()
print('OK G6')

# ── G7: Kavramsal Surukleme ─────────────────────────────────────────
# LSTM: 2022=55.83 2026=50.52 | CNN: 2022=56.79 2026=49.55 | ARIMA: 2022=49.83 2026=51.34
fig,ax = plt.subplots(figsize=(9,5))
cats=['LSTM\n(Teknik)','1D-CNN\n(Teknik)','ARIMA']
v22=[55.83,56.79,49.83]; v26=[50.52,49.55,51.34]
x=np.arange(3); w=0.35
ax.bar(x-w/2,v22,w,label='2018–2022',color='#3B82F6',zorder=3)
ax.bar(x+w/2,v26,w,label='2018–2026',color='#EF4444',zorder=3,alpha=0.85)
for i,(a,b_) in enumerate(zip(v22,v26)):
    diff=b_-a
    clr='#EF4444' if diff<0 else '#16A34A'
    ax.annotate(f'{"▼" if diff<0 else "▲"}{abs(diff):.1f}pp',
                xy=(i+w/2,b_+0.4),ha='center',fontsize=9,color=clr,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Ortalama Doğruluk (%)'); ax.set_ylim(40,65)
ax.set_title('Kavramsal Sürüklenme: THYAO 2018–2022 → 2018–2026\nDerin öğrenme %5–7 puan düşerken ARIMA baştan rassal sınırda')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G7_Kavramsal_Surukleme.png')); plt.close()
print('OK G7')

print('PARCA 1 TAMAM')
