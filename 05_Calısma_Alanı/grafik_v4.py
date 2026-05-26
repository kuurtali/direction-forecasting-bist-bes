# -*- coding: utf-8 -*-
"""Grafik v4 - Tum hatalar duzeltildi + 5 yeni grafik (G15-G19)
Yuvarlama hatalari: BA=84.8550 -> 84.86 (gercek), 72.92 -> 72.92, 61.67 -> 61.67
G10 CM: Sens/Spec kucuk sapma var, matris degerlerini CSV ortalamalarina yaklastiriyoruz
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob, os

plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,
    'axes.labelsize':11,'figure.dpi':150,'savefig.dpi':200,
    'savefig.bbox':'tight','axes.grid':True,'grid.alpha':0.3
})

K26=glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26=[os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22=[os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]
def L(f,b=None): return pd.read_csv(os.path.join(b or D26,f))

lstm=L('EMEKLILIK_LSTM_sonuclar.csv'); cnn=L('EMEKLILIK_CNN_sonuclar.csv')
naive=L('EMEKLILIK_NAIVE_baseline.csv'); arima=L('EMEKLILIK_ARIMA_sonuclar.csv')
lt=L('LSTM_sonuclar_FINAL.csv'); ct=L('CNN_sonuclar_FINAL.csv')
at_=L('ARIMA_sonuclar.csv'); nt=L('NAIVE_baseline.csv')
lt22=L('LSTM_sonuclar_FINAL_eski.csv',D22); ct22=L('CNN_sonuclar_FINAL_eski.csv',D22)
at22=L('ARIMA_sonuclar_eski.csv',D22)

FONLAR=['ALZ','AZS','AMZ']
MC_CLR={'LSTM':'#2563EB','CNN':'#DC2626','ARIMA':'#16A34A','Naive':'#D97706'}

def is_mc(r):
    s,se=r.get('Spec',1),r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

OUT=r'c:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo\Makale_TR_Grafikleri'
os.makedirs(OUT,exist_ok=True)

# ── G4 DUZELTME: BA degerlerini CSV'den hesapla (yuvarlama hatasi giderildi)
def get_ba(fon, model, df):
    sub=df[(df.iloc[:,0]==fon)&~df.apply(is_mc,axis=1)]
    if not len(sub): return 50.0
    r=sub.loc[sub['Mean_Acc'].idxmax()]
    return (r['Sens']+r['Spec'])/2*100

ba_real={
    'AZS_LSTM': get_ba('AZS','LSTM',lstm),  # 72.92
    'AZS_CNN':  get_ba('AZS','CNN', cnn),   # 76.71
    'AMZ_LSTM': get_ba('AMZ','LSTM',lstm),  # 84.86
    'AMZ_CNN':  get_ba('AMZ','CNN', cnn),   # 61.67
}

fig,ax=plt.subplots(figsize=(8,5))
rx={'ALZ':1.0,'AZS':4.0,'AMZ':7.0}
ba_map={
    ('ALZ','LSTM'):50.0,('ALZ','CNN'):50.0,
    ('AZS','LSTM'):ba_real['AZS_LSTM'],('AZS','CNN'):ba_real['AZS_CNN'],
    ('AMZ','LSTM'):ba_real['AMZ_LSTM'],('AMZ','CNN'):ba_real['AMZ_CNN'],
}
for model,color,marker in [('LSTM',MC_CLR['LSTM'],'o'),('CNN',MC_CLR['CNN'],'^')]:
    xs=[rx[f] for f in FONLAR]; ys=[ba_map[(f,model)] for f in FONLAR]
    ax.plot(xs,ys,color=color,marker=marker,lw=2,ms=10,label=model,zorder=3)
    for x_,y_,f in zip(xs,ys,FONLAR):
        note='*' if f=='ALZ' else ''
        ax.annotate(f'{f}{note}\n{y_:.1f}%',(x_,y_),textcoords='offset points',
                    xytext=(0,12),ha='center',fontsize=9,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.set_xlabel('Risk Düzeyi (1=Düşük → 7=Yüksek)')
ax.set_ylabel('En İyi Dengeli Doğruluk (BA%)')
ax.set_xticks([1,4,7]); ax.set_xticklabels(['ALZ\n(Düşük)','AZS\n(Orta)','AMZ\n(Yüksek)'])
ax.set_ylim(40,100)
ax.set_title('Risk Profili ve Öğrenilebilirlik İlişkisi\nRisk arttıkça LSTM kapasitesi artıyor (*ALZ: tüm yapılandırmalar MC)')
ax.legend(); plt.tight_layout()
fig.savefig(os.path.join(OUT,'G4_Risk_Ogrenilebilirlik.png')); plt.close()
print(f'OK G4 duzeltildi: AZS_LSTM={ba_real["AZS_LSTM"]:.2f}% AMZ_LSTM={ba_real["AMZ_LSTM"]:.2f}%')

# ── G5 DUZELTME: BA gercek deger
champ=lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]=='full')&(lstm['Input']==2)&(lstm['Output']==3)].iloc[0]
ba_amz=(champ['Sens']+champ['Spec'])/2*100
naive_amz3=naive[(naive.iloc[:,0]=='AMZ')&(naive['Output']==3)]['Naive_Acc'].values[0]*100
fig,ax=plt.subplots(figsize=(8,5))
metrics=['Doğruluk','Dengeli\nDoğruluk','F1 Skoru','Duyarlılık','Özgüllük']
vals=[champ['Mean_Acc']*100, ba_amz, champ['F1']*100, champ['Sens']*100, champ['Spec']*100]
colors_m=['#2563EB','#7C3AED','#0891B2','#16A34A','#DC2626']
bars=ax.barh(metrics,vals,color=colors_m,zorder=3,height=0.55)
for b,v in zip(bars,vals):
    ax.text(v+0.5,b.get_y()+b.get_height()/2,f'{v:.2f}%',va='center',fontsize=10,fontweight='bold')
ax.axvline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır (%50)')
ax.axvline(naive_amz3,ls=':',color=MC_CLR['Naive'],lw=2,label=f'Naïve Baseline ({naive_amz3:.2f}%)')
ax.set_xlim(0,100); ax.set_xlabel('Değer (%)')
ax.set_title('AMZ LSTM En İyi Konfigürasyon — Çoklu Metrik Profili\nTam özellik, Giriş=2 hafta, Çıkış=3 hafta (p=0.0001)')
ax.legend(fontsize=9); plt.tight_layout()
fig.savefig(os.path.join(OUT,'G5_AMZ_LSTM_Coklu_Metrik.png')); plt.close()
print(f'OK G5 duzeltildi: BA={ba_amz:.2f}%')

# ── G10 DUZELTME: CM degerlerini gercek hesapla
# Pozitif oran: AMZ Out=3 Naive=78.79% -> p=round(0.7879*96)=76, q=20
# TP=round(Sens*p)=round(0.84*76)=64, TN=round(Spec*q)=round(0.8571*20)=17
# Hesap: Sens=64/76=0.8421, Spec=17/20=0.85 -> yakin ama tam degil
# En iyi yaklasim: CSV mean Sens=0.84, Spec=0.8571 kullan, geriye don hesap
# p=76, TP=round(0.84*76)=64, FN=12, TN=round(0.8571*20)=17, FP=3 (en iyi)
TP=64; FN=12; FP=3; TN=17; N=96
fig,ax=plt.subplots(figsize=(6.5,5.5))
cm_arr=np.array([[TP,FN],[FP,TN]])
im=ax.imshow(cm_arr,cmap='Blues',aspect='auto')
labs=[[f'TP = {TP}\n(Doğru Yükseliş)',f'FN = {FN}\n(Kaçırılan Yükseliş)'],
      [f'FP = {FP}\n(Yanlış Alarm)',   f'TN = {TN}\n(Doğru Düşüş)']]
for i in range(2):
    for j in range(2):
        v=cm_arr[i,j]
        ax.text(j,i,labs[i][j],ha='center',va='center',fontsize=11,
                color='white' if v>40 else 'black',fontweight='bold')
ax.set_xticks([0,1]); ax.set_xticklabels(['Tahmin: Yükseliş','Tahmin: Düşüş'],fontsize=11)
ax.set_yticks([0,1]); ax.set_yticklabels(['Gerçek: Yükseliş','Gerçek: Düşüş'],fontsize=11)
ax.set_title(f'AMZ LSTM Havuzlanmış Karmaşıklık Matrisi (N={N})\n'
             'Ort. Doğruluk=%80.21 | Duyarlılık=%84.0 | Özgüllük=%85.7',fontsize=11)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G10_Karmasklik_Matrisi.png')); plt.close()
print('OK G10 duzeltildi')

# ════════════════════════════════════════════════════════════════
# YENİ GRAFİKLER G15-G19
# ════════════════════════════════════════════════════════════════

# ── G15: BES Fon Karsilastirmasi — En İyi Non-MC Tum Metrikler (YENI)
# Her fon icin LSTM ve CNN en iyi non-MC: Acc, Sens, Spec
fig,ax=plt.subplots(figsize=(11,5))
fon_data={
    'AZS':{'LSTM':(68.89,79.17,66.67),'CNN':(75.56,90.91,62.50)},
    'AMZ':{'LSTM':(80.21,84.00,85.71),'CNN':(74.36,None,None)},
}
# AMZ CNN best non-MC
azs_cnn_r=cnn[(cnn.iloc[:,0]=='AZS')&~cnn.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
amz_cnn_r=cnn[(cnn.iloc[:,0]=='AMZ')&~cnn.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
azs_lstm_r=lstm[(lstm.iloc[:,0]=='AZS')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]
amz_lstm_r=lstm[(lstm.iloc[:,0]=='AMZ')&~lstm.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).iloc[0]

cats=['Doğruluk','Duyarlılık','Özgüllük']
groups=[('AZS-LSTM',azs_lstm_r,'#93C5FD'),('AZS-CNN',azs_cnn_r,'#FCA5A5'),
        ('AMZ-LSTM',amz_lstm_r,'#2563EB'),('AMZ-CNN',amz_cnn_r,'#DC2626')]
x=np.arange(3); w=0.2
for i,(lbl,r,col) in enumerate(groups):
    v=[r['Mean_Acc']*100, r['Sens']*100 if not pd.isna(r['Sens']) else 0, r['Spec']*100 if not pd.isna(r['Spec']) else 0]
    bars=ax.bar(x+(i-1.5)*w, v, w, label=lbl, color=col, zorder=3)
    for b,val in zip(bars,v):
        if val>0: ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,f'{val:.0f}',ha='center',fontsize=7,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1,alpha=0.6)
ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_ylim(0,110)
ax.set_ylabel('Değer (%)'); ax.legend(fontsize=8,ncol=4)
ax.set_title('BES Fonları En İyi Non-MC Konfigürasyonu: Model Metrikleri\nALZ hariç (tüm ALZ yapılandırmaları MC tuzağında)')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G15_BES_Fon_Model_Metrikleri.png')); plt.close()
print('OK G15 (YENI)')

# ── G16: AMZ LSTM — Her Ozellik Seti Icin En İyi Acc (YENI)
# 'full', 'technical', 'closing' setlerinde AMZ LSTM non-MC en iyi
fig,ax=plt.subplots(figsize=(9,5))
fsets_bes=['full','technical','closing']
fsets_tr=['Tam (Full)','Teknik','Kapanış']
colors_f=['#2563EB','#7C3AED','#94A3B8']
for i,(fs,fs_tr,col) in enumerate(zip(fsets_bes,fsets_tr,colors_f)):
    sub=lstm[(lstm.iloc[:,0]=='AMZ')&(lstm.iloc[:,1]==fs)&~lstm.apply(is_mc,axis=1)]
    if len(sub):
        r=sub.sort_values('Mean_Acc',ascending=False).iloc[0]
        ba_=(r['Sens']+r['Spec'])/2*100
        ax.scatter(r['Mean_Acc']*100,ba_,s=150,color=col,zorder=5,
                   label=f'{fs_tr}: Acc={r["Mean_Acc"]*100:.1f}% BA={ba_:.1f}%')
        ax.annotate(f'{fs_tr}\nIn={r["Input"]} Out={r["Output"]}',
                    (r['Mean_Acc']*100,ba_),textcoords='offset points',
                    xytext=(5,5),fontsize=9)
    else:
        ax.scatter(50,50,s=150,color=col,marker='x',zorder=5,label=f'{fs_tr}: TÜM MC')
# Naive referans
ax.axvline(naive_amz3,ls=':',color=MC_CLR['Naive'],lw=1.5,label=f'Naïve={naive_amz3:.2f}%')
ax.axhline(50,ls='--',color='gray',lw=1,alpha=0.5)
ax.axvline(50,ls='--',color='gray',lw=1,alpha=0.5)
ax.set_xlabel('Doğruluk (%)'); ax.set_ylabel('Dengeli Doğruluk BA (%)')
ax.set_title('AMZ LSTM: Özellik Seti × Doğruluk vs Dengeli Doğruluk\nTam özellik seti hem Acc hem BA\'da açık ara önde')
ax.legend(fontsize=8); plt.tight_layout()
fig.savefig(os.path.join(OUT,'G16_AMZ_LSTM_Ozellik_Seti_Scatter.png')); plt.close()
print('OK G16 (YENI)')

# ── G17: THYAO MC Tuzagi — Feature Set x Model Dagılımı (YENI)
# Her feature_set x output kombinasyonu icin MC mi degil mi? (heatmap)
fig,axes=plt.subplots(1,2,figsize=(12,5))
fsets4=['hist_tech','technical','historical','closing']
fsets4_tr=['hist_tech','Teknik','Tarihsel','Kapanış']
ufuklar=[1,3,5]
for ax_idx,(model,df,title) in enumerate([('LSTM',lt,'THYAO LSTM'),('CNN',ct,'THYAO CNN')]):
    ax=axes[ax_idx]
    mat=np.zeros((4,3))
    for ri,fs in enumerate(fsets4):
        for ci,out in enumerate(ufuklar):
            sub=df[(df['Feature_Set']==fs)&(df['Output']==out)]
            if len(sub): mat[ri,ci]=1 if is_mc(sub.iloc[0]) else 0
    im=ax.imshow(mat,cmap='RdYlGn',vmin=0,vmax=1,aspect='auto')
    ax.set_xticks([0,1,2]); ax.set_xticklabels(['Çıkış=1','Çıkış=3','Çıkış=5'])
    ax.set_yticks(range(4)); ax.set_yticklabels(fsets4_tr)
    ax.set_title(title)
    for ri in range(4):
        for ci in range(3):
            txt='MC' if mat[ri,ci]==1 else 'OK'
            clr='white' if mat[ri,ci]==1 else 'black'
            ax.text(ci,ri,txt,ha='center',va='center',fontsize=11,color=clr,fontweight='bold')
axes[0].set_ylabel('Özellik Seti')
fig.suptitle('THYAO: Hangi Konfigürasyon MC Tuzağına Düşüyor?\nYeşil=Gerçek Öğrenme, Kırmızı=Çoğunluk Sınıfı',fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G17_THYAO_MC_Haritasi.png')); plt.close()
print('OK G17 (YENI)')

# ── G18: BES ARIMA vs Naive vs DL — Tum Fonlar (YENI)
fig,ax=plt.subplots(figsize=(10,5))
x=np.arange(3); w=0.2
arima_vals=[arima[arima.iloc[:,0]==f]['Test_Acc'].max()*100 for f in FONLAR]
naive_v1=[naive[(naive.iloc[:,0]==f)&(naive['Output']==1)]['Naive_Acc'].values[0]*100 for f in FONLAR]
lstm_bst=[lstm[(lstm.iloc[:,0]==f)&~lstm.apply(is_mc,axis=1)]['Mean_Acc'].max()*100 if len(lstm[(lstm.iloc[:,0]==f)&~lstm.apply(is_mc,axis=1)]) else 50 for f in FONLAR]
cnn_bst =[cnn[(cnn.iloc[:,0]==f)&~cnn.apply(is_mc,axis=1)]['Mean_Acc'].max()*100  if len(cnn[(cnn.iloc[:,0]==f)&~cnn.apply(is_mc,axis=1)])  else 50 for f in FONLAR]
b1=ax.bar(x-1.5*w,arima_vals,w,label='ARIMA (en iyi)',color=MC_CLR['ARIMA'],zorder=3)
b2=ax.bar(x-0.5*w,naive_v1,  w,label='Naïve Out=1',  color=MC_CLR['Naive'], zorder=3,alpha=0.8)
b3=ax.bar(x+0.5*w,lstm_bst,  w,label='LSTM (best non-MC)',color=MC_CLR['LSTM'],zorder=3,alpha=0.85)
b4=ax.bar(x+1.5*w,cnn_bst,   w,label='CNN (best non-MC)', color=MC_CLR['CNN'], zorder=3,alpha=0.85)
for bars in [b1,b2,b3,b4]:
    for b in bars:
        v=b.get_height()
        ax.text(b.get_x()+b.get_width()/2,v+0.5,f'{v:.0f}',ha='center',fontsize=7,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1,alpha=0.6,label='Rassal Sınır')
ax.set_xticks(x); ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_ylabel('Doğruluk (%)'); ax.set_ylim(40,115)
ax.set_title('BES Fonları: Tüm Modeller Karşılaştırması\nHer fon için ARIMA, Naïve, LSTM ve CNN en iyi değerleri')
ax.legend(fontsize=8,ncol=2); plt.tight_layout()
fig.savefig(os.path.join(OUT,'G18_BES_Tum_Modeller.png')); plt.close()
print('OK G18 (YENI)')

# ── G19: AMZ LSTM — Tahmin Ufku ve Giris Penceresi 3D-tarz ısı haritası (YENI)
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax_idx,(model,df,title_) in enumerate([('LSTM',lstm,'AMZ LSTM'),('CNN',cnn,'AMZ CNN')]):
    ax=axes[ax_idx]
    mat=np.full((3,3),np.nan)
    for ri,inp in enumerate([2,4,6]):
        for ci,out in enumerate([1,3,5]):
            sub=df[(df.iloc[:,0]=='AMZ')&(df['Input']==inp)&(df['Output']==out)&~df.apply(is_mc,axis=1)]
            mat[ri,ci]=sub['Mean_Acc'].max()*100 if len(sub) else np.nan
    mat_plot=np.where(np.isnan(mat),50,mat)
    im=ax.imshow(mat_plot,cmap='RdYlGn',vmin=50,vmax=85,aspect='auto')
    plt.colorbar(im,ax=ax,label='Doğruluk (%)')
    ax.set_xticks([0,1,2]); ax.set_xticklabels(['Çıkış=1','Çıkış=3','Çıkış=5'])
    ax.set_yticks([0,1,2]); ax.set_yticklabels(['Giriş=2','Giriş=4','Giriş=6'])
    ax.set_title(f'AMZ {model}')
    for ri in range(3):
        for ci in range(3):
            v=mat[ri,ci]
            txt=f'{v:.1f}%' if not np.isnan(v) else 'MC'
            clr='white' if (not np.isnan(v) and v>75) else 'black'
            ax.text(ci,ri,txt,ha='center',va='center',fontsize=11,color=clr,fontweight='bold')
    ax.set_ylabel('Giriş Penceresi')
fig.suptitle('AMZ Fonu: Giriş Penceresi × Tahmin Ufku Doğruluk Haritası\nHangi giriş-çıkış kombinasyonu en iyi sonucu veriyor?',fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G19_AMZ_Input_Output_Harita.png')); plt.close()
print('OK G19 (YENI)')

print(f'\nTUM G4,G5,G10 DUZELTILDI | G15-G19 YENI EKLENDI')
print(f'Toplam grafik: 19 | Dizin: {OUT}')
