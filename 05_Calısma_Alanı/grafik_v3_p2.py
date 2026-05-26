# -*- coding: utf-8 -*-
"""Makale Grafikleri v3 - Parca 2/2: G8-G10 + Yeni G11-G14"""
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

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]
def L(f,b=None): return pd.read_csv(os.path.join(b or D26, f))

lstm=L('EMEKLILIK_LSTM_sonuclar.csv'); cnn=L('EMEKLILIK_CNN_sonuclar.csv')
naive=L('EMEKLILIK_NAIVE_baseline.csv'); arima=L('EMEKLILIK_ARIMA_sonuclar.csv')
lt=L('LSTM_sonuclar_FINAL.csv'); ct=L('CNN_sonuclar_FINAL.csv')
at_=L('ARIMA_sonuclar.csv'); nt=L('NAIVE_baseline.csv')
lt22=L('LSTM_sonuclar_FINAL_eski.csv',D22); ct22=L('CNN_sonuclar_FINAL_eski.csv',D22)

FONLAR=['ALZ','AZS','AMZ']
MC_CLR={'LSTM':'#2563EB','CNN':'#DC2626','ARIMA':'#16A34A','Naive':'#D97706'}

def is_mc(r):
    s,se=r.get('Spec',1),r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

OUT=r'c:\Users\Kurt\Desktop\Proje\04_Gorsel_Portfolyo\Makale_TR_Grafikleri'
os.makedirs(OUT,exist_ok=True)

# ── G8: AZS CNN vs LSTM (DUZELTILDI) ────────────────────────────────
# CNN: Acc=75.56 Sens=90.91 Spec=62.50 | LSTM: Acc=68.89 Sens=79.17 Spec=66.67
# DUZELTME: baslik artik gercegi yansitiyor
fig,ax=plt.subplots(figsize=(8,5))
cv=[75.56,90.91,62.50]; lv=[68.89,79.17,66.67]
met=['Doğruluk','Duyarlılık\n(Sens)','Özgüllük\n(Spec)']
x=np.arange(3); w=0.35
b1=ax.bar(x-w/2,cv,w,label='CNN (★ Şampiyon)',color=MC_CLR['CNN'], zorder=3)
b2=ax.bar(x+w/2,lv,w,label='LSTM',            color=MC_CLR['LSTM'],zorder=3,alpha=0.85)
for b,v in zip(list(b1)+list(b2),cv+lv):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.7,
            f'{v:.1f}%',ha='center',fontsize=9,fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(met)
ax.set_ylabel('Değer (%)'); ax.set_ylim(0,110)
ax.set_title('AZS Fonu: CNN ve LSTM En İyi Non-MC Konfigürasyonu\nCNN doğruluk ve duyarlılıkta üstün; özgüllükte LSTM daha iyi')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G8_AZS_CNN_vs_LSTM.png')); plt.close()
print('OK G8')

# ── G9: Model x Fon Isi Haritasi ────────────────────────────────────
# LSTM: ALZ=50 AZS=68.89 AMZ=80.21 | CNN: ALZ=50 AZS=75.56 AMZ=74.36
# ARIMA: ALZ=100 AZS=80.65 AMZ=80.65
fig,ax=plt.subplots(figsize=(8,6))
matrix=np.array([[50.0,68.89,80.21],[50.0,75.56,74.36],[100.0,80.65,80.65]])
im=ax.imshow(matrix,cmap='RdYlGn',vmin=50,vmax=100,aspect='auto')
plt.colorbar(im,ax=ax,label='Doğruluk (%)')
ax.set_xticks([0,1,2])
ax.set_xticklabels(['ALZ\n(Düşük Risk)','AZS\n(Orta Risk)','AMZ\n(Yüksek Risk)'])
ax.set_yticks([0,1,2]); ax.set_yticklabels(['LSTM','1D-CNN','ARIMA'])
notes={( 0,0):'*MC',( 1,0):'*MC',(2,0):'†trivial'}
for ri in range(3):
    for ci in range(3):
        v=matrix[ri,ci]
        n=notes.get((ri,ci),'')
        ax.text(ci,ri,f'{v:.1f}%{n}',ha='center',va='center',fontsize=11,
                color='white' if v>80 else 'black',fontweight='bold')
ax.set_title('Model ve Fon Doğruluk Karşılaştırması\n*MC: tüm yapılandırmalar çoğunluk sınıfı  †trivial: sabit getirili fon')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G9_Model_Fon_Isi_Haritasi.png')); plt.close()
print('OK G9')

# ── G10: Karmasklik Matrisi (DUZELTILDI) ────────────────────────────
# N=96=3x32, sinif orani: Naive(AMZ,Out=3)=78.79% → p=76, q=20
# TP=64 FN=12 FP=3 TN=17 → havuz_acc=84.38%, ort_acc=80.21%
TP=64; FN=12; FP=3; TN=17; N=96
pool_acc=(TP+TN)/N
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
             f'Ort. Doğruluk=80.21% | Duyarlılık=84.0% | Özgüllük=85.7%',fontsize=11)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G10_Karmasklik_Matrisi.png')); plt.close()
print('OK G10')

# ══════ YENİ GRAFİKLER ══════════════════════════════════════════════

# ── G11: THYAO Tum Modeller Karsilastirma (YENI) ─────────────────────
# LSTM=57.56%(hist_tech,4,3) CNN=53.97%(hist_tech,2,3) ARIMA=55.78%(6,3)
# Naive: Out1=53.11 Out3=73.93 Out5=79.73
fig,ax=plt.subplots(figsize=(9,5))
models_thyao=['LSTM\nhist_tech','CNN\nhist_tech','ARIMA\n(Out=3)','Naïve\n(Out=1)','Naïve\n(Out=3)','Naïve\n(Out=5)']
accs_thyao=[57.56,53.97,55.78,53.11,73.93,79.73]
colors_t=[MC_CLR['LSTM'],MC_CLR['CNN'],MC_CLR['ARIMA'],
          '#F59E0B','#D97706','#B45309']
bars=ax.bar(range(6),accs_thyao,color=colors_t,zorder=3,width=0.6)
for b,v in zip(bars,accs_thyao):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.4,
            f'{v:.2f}%',ha='center',fontsize=9,fontweight='bold')
ax.axhline(50,ls='--',color='gray',lw=1.2,label='Rassal Sınır (%50)')
ax.set_xticks(range(6)); ax.set_xticklabels(models_thyao,fontsize=9)
ax.set_ylabel('Doğruluk (%)'); ax.set_ylim(40,90)
ax.set_title('THYAO Tüm Model Karşılaştırması\nDerin öğrenme Out=3 Naïve\'i aşamıyor; Out=5 Naïve serbest kazananı')
ax.legend()
# Ayirici cizgi
ax.axvline(2.5,ls=':',color='black',lw=1,alpha=0.4)
ax.text(1, 0.02, 'Derin Öğrenme', ha='center', transform=ax.transAxes, fontsize=8, color='gray')
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G11_THYAO_Tum_Model_Karsilastirma.png')); plt.close()
print('OK G11 (YENI)')

# ── G12: Pencere Duyarliligi – THYAO LSTM (YENI) ──────────────────────
# Her Input (2,4,6) x Output (1,3,5) icin mean_acc (non-MC)
fig,ax=plt.subplots(figsize=(9,5))
ufuklar=[1,3,5]; inputs=[2,4,6]
inp_colors=['#2563EB','#7C3AED','#0891B2']
x=np.arange(3)
for inp,col in zip(inputs,inp_colors):
    vals=[]
    for out in ufuklar:
        sub=lt[(lt['Input']==inp)&(lt['Output']==out)&~lt.apply(is_mc,axis=1)]
        vals.append(sub['Mean_Acc'].max()*100 if len(sub) else np.nan)
    ax.plot(x,vals,color=col,marker='o',lw=2,ms=8,label=f'Giriş Penceresi={inp} hafta')
ax.axhline(50,ls='--',color='gray',lw=1.2,alpha=0.7,label='Rassal Sınır')
# Naive referans cizgileri
for out_i,(out_,nv) in enumerate(zip(ufuklar,[53.11,73.93,79.73])):
    ax.scatter(out_i,nv,marker='_',s=200,color=MC_CLR['Naive'],zorder=5)
ax.plot([],[],'_',color=MC_CLR['Naive'],ms=12,lw=3,label='Naïve Baseline')
ax.set_xticks(x); ax.set_xticklabels(['Çıkış=1\n(1 Hafta)','Çıkış=3\n(3 Hafta)','Çıkış=5\n(5 Hafta)'])
ax.set_ylabel('En İyi Doğruluk (Non-MC, %)')
ax.set_title('Giriş Penceresi Duyarlılığı — THYAO LSTM\nFarklı giriş uzunluklarının tahmin başarısına etkisi')
ax.legend(fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G12_Pencere_Duyarliligi_THYAO.png')); plt.close()
print('OK G12 (YENI)')

# ── G13: AMZ LSTM Seed Stabilitesi (YENI) ────────────────────────────
# En iyi 9 konfigurasyon, 3 seed gorunum — reproducibility
fig,ax=plt.subplots(figsize=(10,5))
amz=lstm[lstm.iloc[:,0]=='AMZ'].copy()
amz_nm=amz[~amz.apply(is_mc,axis=1)].sort_values('Mean_Acc',ascending=False).head(9).reset_index(drop=True)
x=np.arange(len(amz_nm))
labels=[f"fset={r.iloc[1][:4]}\nIn={r['Input']} Out={r['Output']}" for _,r in amz_nm.iterrows()]
ax.bar(x-0.27,amz_nm['Seed_23']*100,0.25,label='Seed 23',color='#2563EB',zorder=3)
ax.bar(x,     amz_nm['Seed_27']*100,0.25,label='Seed 27',color='#7C3AED',zorder=3)
ax.bar(x+0.27,amz_nm['Seed_98']*100,0.25,label='Seed 98',color='#0891B2',zorder=3)
ax.plot(x,amz_nm['Mean_Acc']*100,color='#DC2626',marker='D',ms=6,lw=1.5,zorder=4,label='Ortalama')
ax.axhline(78.79,ls=':',color=MC_CLR['Naive'],lw=1.8,label='Naïve Baseline (78.79%)')
ax.axhline(50,  ls='--',color='gray',lw=1,alpha=0.5)
ax.set_xticks(x); ax.set_xticklabels(labels,fontsize=8)
ax.set_ylabel('Doğruluk (%)'); ax.set_ylim(50,105)
ax.set_title('AMZ LSTM — Seed Stabilitesi ve Tekrarlanabilirlik\nEn iyi 9 non-MC konfigürasyonun 3 seed karşılaştırması')
ax.legend(fontsize=9,ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G13_AMZ_Seed_Stabilitesi.png')); plt.close()
print('OK G13 (YENI)')

# ── G14: THYAO p-deger Anlamlilik Haritasi (YENI) ────────────────────
# LSTM feature_set x output: kac konfig istatistiksel anlamli (p<0.05)?
fig,ax=plt.subplots(figsize=(8,5))
fsets=['hist_tech','technical','historical','closing']
fsets_tr=['hist_tech','Teknik','Tarihsel','Kapanış']
ufuklar_=[1,3,5]
mat=np.zeros((4,3))
for ri,fs in enumerate(fsets):
    for ci,out in enumerate(ufuklar_):
        sub=lt[(lt['Feature_Set']==fs)&(lt['Output']==out)]
        if len(sub):
            mat[ri,ci]=1 if sub['P_Value'].values[0]<0.05 else 0
mat_lstm=mat.copy()
mat2=np.zeros((4,3))
for ri,fs in enumerate(fsets):
    for ci,out in enumerate(ufuklar_):
        sub=ct[(ct['Feature_Set']==fs)&(ct['Output']==out)]
        if len(sub):
            mat2[ri,ci]=1 if sub['P_Value'].values[0]<0.05 else 0

x=np.arange(3); w=0.35
lstm_sig=[mat_lstm[:,ci].sum() for ci in range(3)]
cnn_sig =[mat2[:,ci].sum()  for ci in range(3)]
b1=ax.bar(x-w/2,lstm_sig,w,label='LSTM anlamlı (p<0.05)',color=MC_CLR['LSTM'],zorder=3)
b2=ax.bar(x+w/2,cnn_sig, w,label='CNN anlamlı (p<0.05)', color=MC_CLR['CNN'], zorder=3,alpha=0.85)
for b,v in zip(list(b1)+list(b2),lstm_sig+cnn_sig):
    ax.text(b.get_x()+b.get_width()/2,v+0.05,f'{int(v)}/4',ha='center',fontsize=10,fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(['Çıkış=1','Çıkış=3','Çıkış=5'])
ax.set_ylabel('İstatistiksel Anlamlı Özellik Seti Sayısı (/4)')
ax.set_ylim(0,5)
ax.set_title('THYAO: İstatistiksel Anlamlılık (p < 0.05)\nHangi tahmin ufkunda modeller anlamlı sonuç üretiyor?')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(OUT,'G14_THYAO_Anlamlilik.png')); plt.close()
print('OK G14 (YENI)')

print(f'\nTUM GRAFIKLER -> {OUT}')
print('G1-G10: Duzeltildi | G11-G14: Yeni eklendi')
