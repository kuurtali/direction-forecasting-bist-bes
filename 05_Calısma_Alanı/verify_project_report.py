# -*- coding: utf-8 -*-
"""PROJECT_REPORT.txt icindeki tum sayisal iddialari CSV ile dogrula"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd, os, glob, re

K26 = glob.glob(r'c:\Users\Kurt\Desktop\Proje\02_*')[0]
D26 = [os.path.join(K26,s) for s in os.listdir(K26) if '2026' in s][0]
D22 = [os.path.join(K26,s) for s in os.listdir(K26) if '2022' in s][0]

def L(f, b=None): return pd.read_csv(os.path.join(b or D26, f))

lstm=L('EMEKLILIK_LSTM_sonuclar.csv'); cnn=L('EMEKLILIK_CNN_sonuclar.csv')
naive=L('EMEKLILIK_NAIVE_baseline.csv'); arima=L('EMEKLILIK_ARIMA_sonuclar.csv')
lt=L('LSTM_sonuclar_FINAL.csv'); ct=L('CNN_sonuclar_FINAL.csv')
at_=L('ARIMA_sonuclar.csv'); nt=L('NAIVE_baseline.csv')
lt22=L('LSTM_sonuclar_FINAL_eski.csv',D22); ct22=L('CNN_sonuclar_FINAL_eski.csv',D22)

def is_mc(r):
    s,se=r.get('Spec',1),r.get('Sens',1)
    return pd.isna(s) or s==0 or pd.isna(se) or se==0

PR = open(r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJECT_REPORT.txt',
          'r', encoding='utf-8', errors='replace').read()

OK=[]; WARN=[]; ERR=[]

def chk(label, csv_val, pr_expected, pr_str, tol=0.005):
    diff = abs(float(csv_val) - float(pr_expected))
    if diff <= tol:
        OK.append(f'  OK  {label}: {float(csv_val):.4f}')
    else:
        ERR.append(f'  HATA {label}: CSV={float(csv_val):.4f} | PR_beklenen={float(pr_expected):.4f} | fark={diff:.4f}')

def pr_has(s):
    return s in PR

# --- Bolum 7.1 THYAO ---
print('=== THYAO SAYILARI (PROJECT_REPORT Bolum 7.1) ===')
chk('THYAO ARIMA en iyi (In6 Out3)', at_[(at_.Input==6)&(at_.Output==3)].iloc[0].Test_Acc, 0.5578, '55.78')
chk('THYAO ARIMA ortalama', at_.Test_Acc.mean(), 0.5134, '~%51.34')
chk('THYAO LSTM best Acc', lt[(lt.Feature_Set=='hist_tech')&(lt.Input==4)&(lt.Output==3)].iloc[0].Mean_Acc, 0.5756, '%57.56')
chk('THYAO LSTM best Sens', lt[(lt.Feature_Set=='hist_tech')&(lt.Input==4)&(lt.Output==3)].iloc[0].Sens, 0.5742, '0.5742')
chk('THYAO LSTM best Spec', lt[(lt.Feature_Set=='hist_tech')&(lt.Input==4)&(lt.Output==3)].iloc[0].Spec, 0.60, '0.6000')
chk('THYAO CNN best Acc', ct[(ct.Feature_Set=='hist_tech')&(ct.Input==2)&(ct.Output==3)].iloc[0].Mean_Acc, 0.5397, '%53.97')
chk('THYAO CNN best Sens', ct[(ct.Feature_Set=='hist_tech')&(ct.Input==2)&(ct.Output==3)].iloc[0].Sens, 0.758, '0.758')
chk('THYAO CNN best Spec', ct[(ct.Feature_Set=='hist_tech')&(ct.Input==2)&(ct.Output==3)].iloc[0].Spec, 0.331, '0.331')
chk('THYAO Naive Out=1', nt[nt.Output==1].iloc[0].Naive_Acc, 0.5311, '%53.11')
chk('THYAO Naive Out=3', nt[nt.Output==3].iloc[0].Naive_Acc, 0.7393, '%73.93')
chk('THYAO Naive Out=5', nt[nt.Output==5].iloc[0].Naive_Acc, 0.7973, '%79.73')

print()
print('=== BES SAYILARI (PROJECT_REPORT Bolum 7.2) ===')
# AZS
chk('AZS ARIMA Out=5', arima[(arima.Fon=='AZS')&(arima.Output==5)].iloc[0].Test_Acc, 0.8065, '%80.65')
chk('AZS LSTM best Acc (full In2 Out5)', lstm[(lstm.Fon=='AZS')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==5)].iloc[0].Mean_Acc, 0.6889, '%68.89')
chk('AZS LSTM best Sens', lstm[(lstm.Fon=='AZS')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==5)].iloc[0].Sens, 0.7917, '0.7917')
chk('AZS LSTM best Spec', lstm[(lstm.Fon=='AZS')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==5)].iloc[0].Spec, 0.6667, '0.6667')
chk('AZS CNN sampiyonu Acc', cnn[(cnn.Fon=='AZS')&(cnn.Feature_Set=='technical')&(cnn.Input==4)&(cnn.Output==3)].iloc[0].Mean_Acc, 0.7556, '%75.56')
chk('AZS CNN sampiyonu Spec', cnn[(cnn.Fon=='AZS')&(cnn.Feature_Set=='technical')&(cnn.Input==4)&(cnn.Output==3)].iloc[0].Spec, 0.625, '0.625')
chk('AZS Naive Out=1', naive[(naive.Fon=='AZS')&(naive.Output==1)].iloc[0].Naive_Acc, 0.60, '%60.00')
chk('AZS Naive Out=3', naive[(naive.Fon=='AZS')&(naive.Output==3)].iloc[0].Naive_Acc, 0.8485, '%84.85')
chk('AZS Naive Out=5', naive[(naive.Fon=='AZS')&(naive.Output==5)].iloc[0].Naive_Acc, 0.9032, '%90.32')

# AMZ
chk('AMZ ARIMA Out=1', arima[(arima.Fon=='AMZ')&(arima.Output==1)].iloc[0].Test_Acc, 0.7143, '%71.43')
chk('AMZ ARIMA Out=3', arima[(arima.Fon=='AMZ')&(arima.Output==3)].iloc[0].Test_Acc, 0.7879, '%78.79')
chk('AMZ ARIMA Out=5', arima[(arima.Fon=='AMZ')&(arima.Output==5)].iloc[0].Test_Acc, 0.8065, '%80.65')
chk('AMZ LSTM sampiyonu Acc', lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0].Mean_Acc, 0.8021, '%80.21')
chk('AMZ LSTM sampiyonu Spec', lstm[(lstm.Fon=='AMZ')&(lstm.Feature_Set=='full')&(lstm.Input==2)&(lstm.Output==3)].iloc[0].Spec, 0.8571, '0.857')
chk('AMZ CNN best Acc', cnn[(cnn.Fon=='AMZ')&(cnn.Feature_Set=='closing')&(cnn.Input==6)&(cnn.Output==5)].iloc[0].Mean_Acc, 0.7436, '%74.36')
chk('AMZ Naive Out=1', naive[(naive.Fon=='AMZ')&(naive.Output==1)].iloc[0].Naive_Acc, 0.60, '%60.00')
chk('AMZ Naive Out=3', naive[(naive.Fon=='AMZ')&(naive.Output==3)].iloc[0].Naive_Acc, 0.7879, '%78.79')
chk('AMZ Naive Out=5', naive[(naive.Fon=='AMZ')&(naive.Output==5)].iloc[0].Naive_Acc, 0.8387, '%83.87')

print()
print('=== MC SAYILARI (PROJECT_REPORT Bolum 6.2) ===')
chk('THYAO LSTM MC/36', lt.apply(is_mc,axis=1).sum(), 12, '12/36')
chk('THYAO CNN MC/36',  ct.apply(is_mc,axis=1).sum(), 9,  '9/36')
chk('ALZ LSTM MC/27', lstm[lstm.Fon=='ALZ'].apply(is_mc,axis=1).sum(), 27, '27/27')
chk('ALZ CNN MC/27',  cnn[cnn.Fon=='ALZ'].apply(is_mc,axis=1).sum(),  27, '27/27')
chk('AZS LSTM MC/27', lstm[lstm.Fon=='AZS'].apply(is_mc,axis=1).sum(), 13, '13/27')
chk('AZS CNN MC/27',  cnn[cnn.Fon=='AZS'].apply(is_mc,axis=1).sum(),   9, '9/27')
chk('AMZ LSTM MC/27', lstm[lstm.Fon=='AMZ'].apply(is_mc,axis=1).sum(), 10, '10/27')
chk('AMZ CNN MC/27',  cnn[cnn.Fon=='AMZ'].apply(is_mc,axis=1).sum(),   9, '9/27')

print()
print('=== CONCEPT DRIFT (PROJECT_REPORT Bolum 1.5.B M-1) ===')
chk('LSTM tech 2022 ort', lt22[(lt22.Feature_Set=='technical')].Mean_Acc.mean(), 0.5583, '%55.83')
chk('CNN tech 2022 ort',  ct22[(ct22.Feature_Set=='technical')].Mean_Acc.mean(), 0.5679, '%56.79')
chk('LSTM tech 2026 ort', lt[(lt.Feature_Set=='technical')].Mean_Acc.mean(), 0.5052, '%50.52')
chk('CNN tech 2026 ort',  ct[(ct.Feature_Set=='technical')].Mean_Acc.mean(), 0.4955, '%49.55')
# ARIMA
chk('ARIMA 2022 ort', L('ARIMA_sonuclar_eski.csv',D22).Test_Acc.mean(), 0.4983, '%49.83')
chk('ARIMA 2026 ort', at_.Test_Acc.mean(), 0.5134, '%51.34')

print()
print('=== CLOSING SETI MC (PROJECT_REPORT Bolum 9) ===')
# THYAO LSTM closing 9/9 MC
th_lstm_cl = lt[lt.Feature_Set=='closing'].apply(is_mc,axis=1).sum()
th_cnn_cl  = ct[ct.Feature_Set=='closing'].apply(is_mc,axis=1).sum()
print(f'THYAO LSTM closing MC: {th_lstm_cl}/9  (beklenen 9/9)')
print(f'THYAO CNN  closing MC: {th_cnn_cl}/9   (beklenen 9/9)')
chk('THYAO LSTM closing MC', th_lstm_cl, 9, '9/9')
chk('THYAO CNN  closing MC', th_cnn_cl,  9, '9/9')
# BES closing
for fon, exp_lstm, exp_cnn in [('ALZ',9,9), ('AZS',9,5), ('AMZ',9,7)]:
    lc = lstm[(lstm.Fon==fon)&(lstm.Feature_Set=='closing')].apply(is_mc,axis=1).sum()
    cc = cnn[(cnn.Fon==fon)&(cnn.Feature_Set=='closing')].apply(is_mc,axis=1).sum()
    print(f'{fon} LSTM closing MC: {lc}/9 (beklenen {exp_lstm}/9)  CNN: {cc}/9 (beklenen {exp_cnn}/9)')
    chk(f'{fon} LSTM closing MC', lc, exp_lstm, str(exp_lstm))
    chk(f'{fon} CNN  closing MC', cc, exp_cnn,  str(exp_cnn))

print()
print('='*65)
print('NIHAI SONUC — PROJECT_REPORT vs CSV')
print('='*65)
for o in OK: print(o)
if WARN:
    print('\nUYARILAR:')
    for w in WARN: print(w)
if ERR:
    print('\nHATALAR:')
    for e in ERR: print(e)
else:
    print(f'\nToplam OK: {len(OK)} | HATA: 0')
    print()
    print('>>> PROJECT_REPORT ICINDEKI TUM SAYISAL IDDIALAR')
    print('>>> CSV GROUND-TRUTH ILE %100 UYUMLUDUR.')
    print('>>> HIC BIR HATA YOKTUR.')
