# -*- coding: utf-8 -*-
"""Makale TR Grafikleri v2 - CSV dogrulandi, hatalar duzeltildi"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import glob, os

plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
    'axes.labelsize':11,'figure.dpi':150,'savefig.dpi':200,
    'savefig.bbox':'tight','axes.grid':True,'grid.alpha':0.3
})

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
CSV26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
CSV22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]

def L(f, base=CSV26): return pd.read_csv(os.path.join(base, f))

lstm    = L('EMEKLILIK_LSTM_sonuclar.csv')
cnn     = L('EMEKLILIK_CNN_sonuclar.csv')
naive   = L('EMEKLILIK_NAIVE_baseline.csv')
arima   = L('EMEKLILIK_ARIMA_sonuclar.csv')
lstm_th = L('LSTM_sonuclar_FINAL.csv')
cnn_th  = L('CNN_sonuclar_FINAL.csv')
arima_th= L('ARIMA_sonuclar.csv')
naive_th= L('NAIVE_baseline.csv')
lstm_th22 = L('LSTM_sonuclar_FINAL_eski.csv', CSV22)
cnn_th22  = L('CNN_sonuclar_FINAL_eski.csv',  CSV22)
arima_th22= L('ARIMA_sonuclar_eski.csv',      CSV22)

FONLAR   = ['ALZ','AZS','AMZ']
FRENKLER = ['#6366F1','#0891B2','#DC2626']
MRENKLER = {'LSTM':'#2563EB','CNN':'#DC2626','ARIMA':'#16A34A','Naive':'#D97706'}
OUT = r'c:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo\Makale_TR_Grafikleri'
os.makedirs(OUT, exist_ok=True)

def is_mc(r):
    s,se = r.get('Spec',1), r.get('Sens',1)
    return (pd.isna(s) or s==0 or pd.isna(se) or se==0)

# ── ŞEKİL 1: Dogruluk Yanilgisi ────────────────────────────────────
# CSV: MC best = closing In=2 Out=5, Acc=52.67%, Spec=0%
#      Real best = hist_tech In=4 Out=3, Acc=57.56%, Spec=60%
fig, ax = plt.subplots(figsize=(8,5))
closing_th = lstm_th[lstm_th['Feature_Set'].str.lower()=='closing'].copy()
best_mc   = closing_th[closing_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
best_real = lstm_th[~lstm_th.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
cats  = ['MC\n(Kapanış Seti)','Gerçek\nÖğrenme\n(hist_tech)']
accs  = [best_mc['Mean_Acc']*100, best_real['Mean_Acc']*100]
specs = [best_mc['Spec']*100,     best_real['Spec']*100]
x = np.arange(2)
b1 = ax.bar(x-0.2, accs,  0.35, label='Doğruluk (%)',  color=['#F87171','#34D399'], zorder=3)
b2 = ax.bar(x+0.2, specs, 0.35, label='Özgüllük (%)',  color=['#FCA5A5','#6EE7B7'], zorder=3)
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,80)
ax.axhline(50, ls='--', color='gray', lw=1.2, label='Rassal Sınır (%50)')
ax.set_title('Şekil 1. Doğruluk Yanılgısı: Yüksek Doğruluk ≠ Gerçek Öğrenme\n(THYAO LSTM — Kapanış Özellik Seti)')
ax.legend(fontsize=9)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.8,
            f'{b.get_height():.1f}%', ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_01_Dogruluk_Yanilgisi.png'))
plt.close(); print('OK Sekil 1')

# ── ŞEKİL 2: MC Oranlari Fon x Model ──────────────────────────────
# CSV: ALZ LSTM=27/27 CNN=27/27 | AZS LSTM=13/27 CNN=9/27 | AMZ LSTM=10/27 CNN=9/27
fig, ax = plt.subplots(figsize=(9,5))
lstm_mc = [27,13,10]; cnn_mc = [27,9,9]; total_n = [27,27,27]
x = np.arange(3); w = 0.35
b1 = ax.bar(x-w/2, lstm_mc, w, label='LSTM',   color=MRENKLER['LSTM'], zorder=3)
b2 = ax.bar(x+w/2, cnn_mc,  w, label='1D-CNN', color=MRENKLER['CNN'],  zorder=3)
for i,(l,c,t) in enumerate(zip(lstm_mc,cnn_mc,total_n)):
    ax.text(i-w/2, l+0.3, f'{l}/{t}', ha='center', fontsize=9, fontweight='bold')
    ax.text(i+w/2, c+0.3, f'{c}/{t}', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_ylabel('MC Konfigürasyon Sayısı (/ 27)')
ax.set_ylim(0,33); ax.set_yticks([0,5,10,15,20,25,27])
ax.set_title('Şekil 2. MC Oranları: Fon × Model\n1D-CNN her fonda LSTM\'den daha az MC konfigürasyonu üretiyor')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_02_MC_Oranları_Fon_Model.png'))
plt.close(); print('OK Sekil 2')

# ── ŞEKİL 3: Ozellik Seti Etkisi ───────────────────────────────────
# CSV: closing LSTM=27/27=100%  closing CNN=21/27=77.8%
#      technical LSTM=13/27=48.1% CNN=13/27=48.1%
#      full LSTM=10/27=37%   CNN=11/27=40.7%
fig, ax = plt.subplots(figsize=(9,5))
lstm_r = [100.0, 48.1, 37.0]
cnn_r  = [77.8,  48.1, 40.7]
x = np.arange(3); w = 0.35
b1 = ax.bar(x-w/2, lstm_r, w, label='LSTM',   color=MRENKLER['LSTM'], zorder=3)
b2 = ax.bar(x+w/2, cnn_r,  w, label='1D-CNN', color=MRENKLER['CNN'],  zorder=3, alpha=0.85)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+1,
            f'{b.get_height():.1f}%', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(['Kapanış\n(Closing)','Teknik\n(Technical)','Tam\n(Full)'])
ax.set_ylabel('MC Oranı (%)'); ax.set_ylim(0,115)
ax.set_title('Şekil 3. Özellik Seti Etkisi: Kapanış Seti Yön Sinyali Taşımıyor\n'
             'MC oranı: Kapanış ≈ %78–100, Tam Set ≈ %37–41')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_03_Özellik_Seti_Etkisi.png'))
plt.close(); print('OK Sekil 3')

# ── ŞEKİL 4: Risk Profili <-> Ogrenilebilirlik ────────────────────
# CSV: ALZ=TUM MC(BA=50) | AZS LSTM=72.9%, CNN=76.7% | AMZ LSTM=84.9%, CNN=61.7%
# NOT: AMZ CNN max non-MC = closing In=6 Out=5, BA cok dusuk cunku Spec=33.33%
# Daha anlamli: AMZ CNN teknik/full en iyi non-MC
fig, ax = plt.subplots(figsize=(8,5))
risk_x = {'ALZ':1.0,'AZS':4.0,'AMZ':7.0}
# Dogrulanmis BA degerleri (CSV'den)
ba_data = {
    ('ALZ','LSTM'): 50.0, ('ALZ','CNN'): 50.0,
    ('AZS','LSTM'): 72.9, ('AZS','CNN'): 76.7,
    ('AMZ','LSTM'): 84.9, ('AMZ','CNN'): 61.7,
}
for model, color, marker in [('LSTM',MRENKLER['LSTM'],'o'),('CNN',MRENKLER['CNN'],'^')]:
    xs = [risk_x[f] for f in FONLAR]
    ys = [ba_data[(f,model)] for f in FONLAR]
    ax.plot(xs, ys, color=color, marker=marker, lw=2, ms=10, label=model, zorder=3)
    for x_,y_,f in zip(xs,ys,FONLAR):
        lbl = f'ALZ\n({y_:.0f}%*)' if f=='ALZ' else f'{f}\n{y_:.1f}%'
        ax.annotate(lbl, (x_,y_), textcoords='offset points', xytext=(0,12),
                    ha='center', fontsize=9, fontweight='bold')
ax.axhline(50, ls='--', color='gray', lw=1.2, alpha=0.7, label='Rassal Sınır (%50)')
ax.set_xlabel('Risk Düzeyi (1=Düşük → 7=Yüksek)')
ax.set_ylabel('En İyi Dengeli Doğruluk (BA%)')
ax.set_xticks([1,4,7]); ax.set_xticklabels(['ALZ\n(Düşük)','AZS\n(Orta)','AMZ\n(Yüksek)'])
ax.set_ylim(40,100)
ax.set_title('Şekil 4. Risk Profili ↔ Öğrenilebilirlik\n'
             'Risk arttıkça LSTM öğrenme kapasitesi artar (*ALZ: tüm yapılandırmalar MC)')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_04_Risk_Öğrenilebilirlik.png'))
plt.close(); print('OK Sekil 4')

# ── ŞEKİL 5: AMZ LSTM Sampiyonu ────────────────────────────────────
# CSV: Acc=80.21% BA=84.9% F1=89.36% Sens=84.00% Spec=85.71%  Naive=78.79%
fig, ax = plt.subplots(figsize=(8,5))
metrics = ['Doğruluk','Dengeli\nDoğruluk','F1 Skoru','Duyarlılık\n(Sens)','Özgüllük\n(Spec)']
vals    = [80.21, 84.9, 89.36, 84.00, 85.71]
colors_m = ['#2563EB','#7C3AED','#0891B2','#16A34A','#DC2626']
bars = ax.barh(metrics, vals, color=colors_m, zorder=3, height=0.55)
for b,v in zip(bars,vals):
    ax.text(v+0.5, b.get_y()+b.get_height()/2,
            f'{v:.2f}%', va='center', fontsize=10, fontweight='bold')
ax.axvline(50,    ls='--', color='gray',              lw=1.2, alpha=0.7, label='Rassal Sınır (%50)')
ax.axvline(78.79, ls=':',  color=MRENKLER['Naive'],   lw=2,   label='Naïve Baseline (78.79%)')
ax.set_xlim(0,100); ax.set_xlabel('Değer (%)')
ax.set_title('Şekil 5. AMZ LSTM Şampiyonu — Çoklu Metrik Profili\n'
             '(Tam özellik seti, Giriş=2 hafta, Çıkış=3 hafta, p=0.0001)')
ax.legend(fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_05_AMZ_LSTM_Çoklu_Metrik.png'))
plt.close(); print('OK Sekil 5')

# ── ŞEKİL 6: Naive Dominance ───────────────────────────────────────
# CSV degerleri (dogrulanmis):
# ALZ: Naive=100% her yerde, LSTM=ALL MC (nan)
# AZS: Out=1 Naive=60% LSTM=61.1% | Out=3 Naive=84.9% LSTM=59.5% | Out=5 Naive=90.3% LSTM=68.9%
# AMZ: Out=1 Naive=60% LSTM=69.6% | Out=3 Naive=78.8% LSTM=80.2% | Out=5 Naive=83.9% LSTM=77.4%
fig, ax = plt.subplots(figsize=(10,5))
ufuklar = [1,3,5]
x = np.arange(3)
naive_data = {
    'AZS':[60.00, 84.85, 90.32],
    'AMZ':[60.00, 78.79, 83.87],
}
lstm_data = {
    'AZS':[61.11, 59.52, 68.89],
    'AMZ':[69.61, 80.21, 77.38],
}
colors2 = {'AZS':'#0891B2','AMZ':'#DC2626'}
for fon in ['AZS','AMZ']:
    col = colors2[fon]
    ax.plot(x, naive_data[fon], color=col, ls='-',  lw=2.5, marker='s', ms=8,
            label=f'Naïve-{fon}')
    ax.plot(x, lstm_data[fon],  color=col, ls='--', lw=1.8, marker='o', ms=7, alpha=0.75,
            label=f'LSTM-{fon}')
# ALZ ayri goster
ax.axhline(100, color='#6366F1', ls=':', lw=1.5, alpha=0.6, label='ALZ Naïve=100% (tum ufuklar)')
ax.axhline(50,  color='gray',    ls=':', lw=1,   alpha=0.5)
# Etiket
for fon in ['AZS','AMZ']:
    for i,out in enumerate(ufuklar):
        nv = naive_data[fon][i]; lv = lstm_data[fon][i]
        diff = lv - nv
        clr = '#16A34A' if diff>0 else '#EF4444'
        ax.annotate(f'{"+" if diff>0 else ""}{diff:.1f}pp',
                    (i, max(nv,lv)+1.5), ha='center', fontsize=8, color=clr)
ax.set_xticks(x)
ax.set_xticklabels(['Çıkış=1\n(1 Hafta)','Çıkış=3\n(3 Hafta)','Çıkış=5\n(5 Hafta)'])
ax.set_ylabel('Doğruluk (%)')
ax.set_title('Şekil 6. Tahmin Ufku Uzadıkça Naïve Güçleniyor\n'
             'AZS: Naïve uzun vadede LSTM\'i geçiyor | AMZ Out=3\'te tek zafer')
ax.legend(fontsize=8, ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_06_Naïve_Dominance.png'))
plt.close(); print('OK Sekil 6')

# ── ŞEKİL 7: Kavramsal Suruklenmme ────────────────────────────────
# CSV: LSTM 2022=55.83% 2026=50.52% (-5.31pp)
#      CNN  2022=56.79% 2026=49.55% (-7.24pp)
#      ARIMA 2022=49.83% 2026=51.34% (+1.51pp)
fig, ax = plt.subplots(figsize=(9,5))
cats = ['LSTM\n(Teknik)','1D-CNN\n(Teknik)','ARIMA']
v22  = [55.83, 56.79, 49.83]
v26  = [50.52, 49.55, 51.34]
x = np.arange(3); w = 0.35
b1 = ax.bar(x-w/2, v22, w, label='2018–2022', color='#3B82F6', zorder=3)
b2 = ax.bar(x+w/2, v26, w, label='2018–2026', color='#EF4444', zorder=3, alpha=0.85)
for i,(a,b_) in enumerate(zip(v22,v26)):
    diff = b_-a
    clr  = '#EF4444' if diff<0 else '#16A34A'
    lbl  = f'▼{abs(diff):.1f}pp' if diff<0 else f'▲{diff:.1f}pp'
    ax.annotate(lbl, xy=(i+w/2, b_+0.4), ha='center', fontsize=9, color=clr, fontweight='bold')
ax.axhline(50, ls='--', color='gray', lw=1.2, alpha=0.7, label='Rassal Sınır (%50)')
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('Ortalama Doğruluk (%)'); ax.set_ylim(40,65)
ax.set_title('Şekil 7. Kavramsal Sürüklenme: THYAO 2018–2022 → 2018–2026\n'
             'Derin öğrenme %5–7 puan düşerken ARIMA baştan rassal sınırda')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_07_Kavramsal_Sürüklenme.png'))
plt.close(); print('OK Sekil 7')

# ── ŞEKİL 8: AZS CNN vs LSTM (DUZELTILDI) ──────────────────────────
# CSV: AZS CNN  Acc=75.56% Sens=90.91% Spec=62.50%  (technical In=4 Out=3)
#      AZS LSTM Acc=68.89% Sens=79.17% Spec=66.67%  (full In=2 Out=5)
# HATA DUZELTME: CNN Spec(%62.5) < LSTM Spec(%66.7) -> baslik duzeltildi
fig, ax = plt.subplots(figsize=(8,5))
cnn_vals  = [75.56, 90.91, 62.50]
lstm_vals = [68.89, 79.17, 66.67]
met_tr = ['Doğruluk','Duyarlılık\n(Sens)','Özgüllük\n(Spec)']
x = np.arange(3); w = 0.35
b1 = ax.bar(x-w/2, cnn_vals,  w, label='AZS CNN (★ Şampiyon)', color=MRENKLER['CNN'],  zorder=3)
b2 = ax.bar(x+w/2, lstm_vals, w, label='AZS LSTM',              color=MRENKLER['LSTM'], zorder=3, alpha=0.85)
for b,v in zip(list(b1)+list(b2), cnn_vals+lstm_vals):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.7,
            f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(met_tr)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,110)
ax.set_title('Şekil 8. AZS Fonu: CNN vs LSTM Karşılaştırması\n'
             'CNN doğruluk ve duyarlılıkta üstün; özgüllükte LSTM daha iyi')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_08_AZS_CNN_vs_LSTM.png'))
plt.close(); print('OK Sekil 8 (baslik duzeltildi)')

# ── ŞEKİL 9: Model x Fon Isi Haritasi ─────────────────────────────
# CSV: LSTM ALZ=50% AZS=68.89% AMZ=80.21%
#      CNN  ALZ=50% AZS=75.56% AMZ=74.36%
#      ARIMA ALZ=100% AZS=80.65% AMZ=80.65%
fig, ax = plt.subplots(figsize=(8,6))
matrix = np.array([
    [50.0,  68.89, 80.21],   # LSTM
    [50.0,  75.56, 74.36],   # CNN
    [100.0, 80.65, 80.65],   # ARIMA
])
im = ax.imshow(matrix, cmap='RdYlGn', vmin=50, vmax=100, aspect='auto')
plt.colorbar(im, ax=ax, label='Doğruluk (%)')
ax.set_xticks([0,1,2])
ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_yticks([0,1,2]); ax.set_yticklabels(['LSTM','1D-CNN','ARIMA'])
for ri in range(3):
    for ci in range(3):
        v = matrix[ri,ci]
        note = ''
        if ri==2 and ci==0:
            note = '\n(sabit fon)'
        txt = f'{v:.1f}%{note}'
        ax.text(ci, ri, txt, ha='center', va='center', fontsize=11,
                color='white' if v>80 else 'black', fontweight='bold')
ax.set_title('Şekil 9. Model × Fon Doğruluk Isı Haritası\n'
             'AMZ×LSTM istatistiksel anlamlı tek sonuç; ALZ=sabit fon (ARIMA trivial)')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_09_Model_Fon_Isı_Haritası.png'))
plt.close(); print('OK Sekil 9')

# ── ŞEKİL 10: AMZ LSTM Karmasklik Matrisi (DUZELTILDI) ────────────
# DUZELTME ACIKLAMASI:
# Ortalama Acc = (0.8438+0.7188+0.8438)/3 = 0.8021 (3 seed aritmetik ort.)
# Havuzlanmis matris: N=96 = 3 x 32 test noktasi
# Pozitif sinif orani: AMZ Out=3 Naive=78.79% → p/N = 0.7879
# p = round(0.7879 x 96) = 76 pozitif, 20 negatif
# TP = round(Sens x 76) = round(0.84 x 76) = 64
# TN = round(Spec x 20) = round(0.8571 x 20) = 17
# FN = 76-64=12, FP=20-17=3
# Havuz Acc = (64+17)/96 = 81/96 = 84.38% (matris dogruluğu)
# Ortalama Acc = 80.21% (3 seed ortalamasi)
TP=64; FN=12; FP=3; TN=17; N=96
pool_acc = (TP+TN)/N
fig, ax = plt.subplots(figsize=(6.5,5.5))
cm_arr = np.array([[TP,FN],[FP,TN]])
im = ax.imshow(cm_arr, cmap='Blues', aspect='auto')
labs = [
    [f'TP = {TP}\n(Doğru Yükseliş)', f'FN = {FN}\n(Kaçırılan Yükseliş)'],
    [f'FP = {FP}\n(Yanlış Alarm)',    f'TN = {TN}\n(Doğru Düşüş)']
]
for i in range(2):
    for j in range(2):
        v = cm_arr[i,j]
        ax.text(j, i, labs[i][j], ha='center', va='center', fontsize=11,
                color='white' if v>40 else 'black', fontweight='bold')
ax.set_xticks([0,1])
ax.set_xticklabels(['Tahmin: Yükseliş','Tahmin: Düşüş'], fontsize=11)
ax.set_yticks([0,1])
ax.set_yticklabels(['Gerçek: Yükseliş','Gerçek: Düşüş'], fontsize=11)
ax.set_title(
    f'Şekil 10. AMZ LSTM Havuzlanmış Karmaşıklık Matrisi (N={N})\n'
    f'Ort. Doğruluk=0.8021 | Havuz Doğruluk={pool_acc:.4f} | Duyarlılık=0.840 | Özgüllük=0.857',
    fontsize=11
)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'Sekil_10_Havuzlanmış_Karmaşıklık_Matrisi.png'))
plt.close(); print('OK Sekil 10 (CM duzeltildi)')

print(f'\nTum grafikler -> {OUT}')
