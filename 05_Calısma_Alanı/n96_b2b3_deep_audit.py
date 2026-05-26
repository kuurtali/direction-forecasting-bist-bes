# -*- coding: utf-8 -*-
"""
N=96 & B2/B3 DEEP AUDIT — ASKERİ DİSİPLİN
CSV ground-truth ile BES_Pension_Fund_Report.docx çapraz denetim
"""
import csv, os, sys, json, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"c:\Users\Kurt\Desktop\Proje")
CSV_DIR = BASE / "02_Akademik_Kanıtlar" / "2018-2026 c¦ğ¦-kt¦-lar"
OUT_DIR = BASE / "06_Kodlar"

# ======================================================================
# PHASE 1: CSV GROUND-TRUTH LOADING
# ======================================================================
def load_csv(filename):
    path = CSV_DIR / filename
    if not path.exists():
        print(f"[HATA] Dosya bulunamadı: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

print("=" * 80)
print("PHASE 1: CSV GROUND-TRUTH YÜKLEME")
print("=" * 80)

lstm_data = load_csv("EMEKLILIK_LSTM_sonuclar.csv")
cnn_data = load_csv("EMEKLILIK_CNN_sonuclar.csv")
naive_data = load_csv("EMEKLILIK_NAIVE_baseline.csv")
arima_data = load_csv("EMEKLILIK_ARIMA_sonuclar.csv")

print(f"LSTM satır: {len(lstm_data)}")
print(f"CNN satır: {len(cnn_data)}")
print(f"Naive satır: {len(naive_data)}")
print(f"ARIMA satır: {len(arima_data)}")

# ======================================================================
# PHASE 2: AMZ LSTM — N=96 POOLED MATRİS ANALİZİ
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 2: N=96 POOLED MATRIX DERİN ANALİZ")
print("=" * 80)

# Şampiyon: AMZ LSTM full In=2 Out=3
champion = None
for row in lstm_data:
    if (row['Fon'] == 'AMZ' and row['Feature_Set'] == 'full' 
        and row['Input'] == '2' and row['Output'] == '3'):
        champion = row
        break

if champion:
    print("\n--- AMZ LSTM ŞAMPİYON KONFİGÜRASYON ---")
    print(f"Feature: {champion['Feature_Set']} | In={champion['Input']} | Out={champion['Output']}")
    print(f"Optimizer: {champion['Optimizer']} | Activation: {champion['Activation']} | Dropout: {champion['Dropout']}")
    print(f"Seed_23: {champion['Seed_23']}")
    print(f"Seed_27: {champion['Seed_27']}")
    print(f"Seed_98: {champion['Seed_98']}")
    print(f"Mean_Acc: {champion['Mean_Acc']}")
    print(f"SD: {champion['SD']}")
    print(f"P_Value: {champion['P_Value']}")
    print(f"F1: {champion['F1']}")
    print(f"Sens: {champion['Sens']}")
    print(f"Spec: {champion['Spec']}")
    
    # N=96 hesaplama
    seeds = [float(champion['Seed_23']), float(champion['Seed_27']), float(champion['Seed_98'])]
    mean_acc = float(champion['Mean_Acc'])
    sens = float(champion['Sens'])
    spec = float(champion['Spec'])
    
    # AMZ Out=3 test seti boyutu: ~32 hafta (PROJECT_REPORT: Eğitim 183, Doğr. 39, Test 40)
    # Ama Out=3 sliding window kaydırması nedeniyle etkili test ~32
    # (40 - Out + 1 = 40 - 3 + 1 = 38? veya başka kural?)
    # Seed bazlı hesaplama:
    print("\n--- SEED BAZLI TEST SETİ BÜYÜKLÜĞÜ HESABI ---")
    for i, (seed_name, seed_acc) in enumerate([("Seed_23", seeds[0]), ("Seed_27", seeds[1]), ("Seed_98", seeds[2])]):
        # Tam sayı doğru tahmin sayısı bulmak için N'yi arıyoruz
        # N * acc = tam sayı olmalı
        for n in range(25, 45):
            correct = round(n * seed_acc)
            if abs(correct / n - seed_acc) < 0.001:
                print(f"  {seed_name}: Acc={seed_acc:.4f} → N={n}, Doğru={correct} (kontrol: {correct/n:.4f})")
                break
    
    # Seed 23 = 0.8438 → 27/32 = 0.84375 ✓
    # Seed 27 = 0.7188 → 23/32 = 0.71875 ✓  
    # Seed 98 = 0.8438 → 27/32 = 0.84375 ✓
    n_per_seed = 32
    print(f"\n--- N=32 DOĞRULAMASI ---")
    for seed_name, seed_acc in [("Seed_23", seeds[0]), ("Seed_27", seeds[1]), ("Seed_98", seeds[2])]:
        correct = round(n_per_seed * seed_acc)
        print(f"  {seed_name}: {correct}/{n_per_seed} = {correct/n_per_seed:.4f} (CSV: {seed_acc:.4f})")
    
    total_correct = sum(round(n_per_seed * s) for s in seeds)
    total_n = n_per_seed * 3
    pooled_acc = total_correct / total_n
    
    print(f"\n--- POOLED N=96 HESABI ---")
    print(f"  Toplam doğru tahmin: {total_correct}")
    print(f"  Toplam N: {total_n}")
    print(f"  Pooled Acc: {total_correct}/{total_n} = {pooled_acc:.4f} ({pooled_acc*100:.2f}%)")
    print(f"  CSV Mean Acc: {mean_acc:.4f} ({mean_acc*100:.2f}%)")
    print(f"  Aritmetik ortalama: ({seeds[0]}+{seeds[1]}+{seeds[2]})/3 = {sum(seeds)/3:.4f}")
    
    # Confusion Matrix analizi
    # AMZ Out=3 test seti sınıf dağılımı (EK-C'den): 30 Up / 7 Down (per seed? veya toplam?)
    # PROJECT_REPORT EK-C: AMZ Out=3: 30 Up / 7 Down → ama bu test=40 için
    # Etkili test (sliding window sonrası) = 32 → yaklaşık 25 Up / 7 Down
    print(f"\n--- CSV'DEKİ SENS/SPEC ANALİZİ ---")
    print(f"  CSV Sens: {sens} (= TP / (TP + FN))")
    print(f"  CSV Spec: {spec} (= TN / (TN + FP))")
    print(f"  ÖNEMLİ: Bu değerler POOLED DEĞİL, yalnızca SON SEED'den (Seed 98) loglanmış!")
    
    # Pooled N=96 sınıf dağılımı tahmini
    # Eğer her seed için ~25 Up ve ~7 Down varsa:
    # Pooled: ~75 Up ve ~21 Down
    # Sens=0.84 → TP = 0.84 * 75 = 63 (eğer Pooled alınırsa)
    # Spec=0.8571 → TN = 0.8571 * 21 = 18 (eğer Pooled alınırsa)
    # TP + TN = 63 + 18 = 81
    # Ama 77/96 = 0.8021 ise TP+TN=77 olmalı
    # 81 ≠ 77 → ÇELİŞKİ
    
    print(f"\n--- N=96 ARİTMETİK KRİTİK ANALİZ ---")
    print(f"  Senaryo A (Mean Acc = 80.21%):")
    print(f"    77/96 = 0.8021 → TP+TN = 77")
    print(f"  Senaryo B (Pooled Acc = 84.38%):")
    print(f"    {total_correct}/96 = {pooled_acc:.4f} → TP+TN = {total_correct}")
    print(f"")
    print(f"  FARK: {total_correct} - 77 = {total_correct - 77}")
    print(f"")
    print(f"  Eğer Sens ve Spec pooled matris oranlarıysa:")
    # Varsayalım her seed'de AMZ Out=3 için ~25 Up, ~7 Down (toplam per seed=32)
    # Pooled: 75 Up, 21 Down → toplam 96
    up_per_seed = 25  # yaklaşık
    down_per_seed = 7  # yaklaşık
    total_up = up_per_seed * 3
    total_down = down_per_seed * 3
    
    tp_from_sens = round(sens * total_up)
    fn_from_sens = total_up - tp_from_sens
    tn_from_spec = round(spec * total_down)
    fp_from_spec = total_down - tn_from_spec
    
    print(f"    Tahmini sınıf dağılımı: {total_up} Up, {total_down} Down")
    print(f"    Sens={sens} → TP ≈ {tp_from_sens}, FN ≈ {fn_from_sens}")
    print(f"    Spec={spec} → TN ≈ {tn_from_spec}, FP ≈ {fp_from_spec}")
    print(f"    TP+TN = {tp_from_sens + tn_from_spec}")
    print(f"    Hesaplanan Acc = {(tp_from_sens + tn_from_spec)}/96 = {(tp_from_sens + tn_from_spec)/96:.4f}")
    
    # Ama gerçek sınıf dağılımını PROJECT_REPORT EK-C'den alalım
    # EK-C: AMZ Out=3: 30 Up / 7 Down (test n=40 üzerinden)
    # Sliding window sonrası etkili test muhtemelen 32
    # 30/37 oranı korunursa: 32 * (30/37) ≈ 26 Up, 32 * (7/37) ≈ 6 Down
    # Veya test=32 için → ~25-26 Up, ~6-7 Down
    
    print(f"\n  SONUÇ:")
    print(f"  ──────────────────────────────────────────────────────")
    print(f"  Mean Acc (3-seed aritmetik ortalama) = {mean_acc:.4f} = 80.21%")
    print(f"  Pooled Acc (3-seed toplam doğru/96)  = {pooled_acc:.4f} = {pooled_acc*100:.2f}%")
    print(f"  CSV Sens/Spec = SON SEED (Seed 98) değerleri, pooled DEĞİL")
    print(f"  ──────────────────────────────────────────────────────")
    print(f"  Mean ≠ Pooled çünkü: aritmetik ortalama ≠ toplam doğru/toplam N")
    print(f"  Seed 27'nin düşük performansı (71.88%) ortalamayi aşağı çekiyor")
    print(f"  ama pooled'da 23/32 doğru hala havuza katılıyor → pooled yükseliyor")

# ======================================================================
# PHASE 3: AMZ LSTM TÜM KONFİGÜRASYONLAR — MC ANALİZİ
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 3: AMZ LSTM — MC vs NON-MC DAĞILIMI")
print("=" * 80)

amz_lstm_mc = 0
amz_lstm_nonmc = 0
amz_lstm_rows = []
for row in lstm_data:
    if row['Fon'] == 'AMZ':
        is_mc = (row['Spec'] == '0' or row['Sens'] == '0' or row['Spec'] == 'NA' or row['Sens'] == 'NA')
        mc_label = "MC" if is_mc else "non-MC"
        if is_mc:
            amz_lstm_mc += 1
        else:
            amz_lstm_nonmc += 1
        amz_lstm_rows.append({
            'set': row['Feature_Set'], 'in': row['Input'], 'out': row['Output'],
            'acc': row['Mean_Acc'], 'sens': row['Sens'], 'spec': row['Spec'],
            'mc': mc_label
        })

print(f"AMZ LSTM: {amz_lstm_mc}/27 MC, {amz_lstm_nonmc}/27 non-MC")
print(f"\nMC dağılımı:")
for fs in ['full', 'technical', 'closing']:
    mc_count = sum(1 for r in amz_lstm_rows if r['set'] == fs and r['mc'] == 'MC')
    total = sum(1 for r in amz_lstm_rows if r['set'] == fs)
    print(f"  {fs}: {mc_count}/{total} MC")

# ======================================================================
# PHASE 4: BES_Pension_Fund_Report.docx — TABLO B2 DENETİMİ
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 4: TABLO B2 (AMZ DETAILED) — CSV ÇAPRAZ DENETİM")
print("=" * 80)

# B2'de rapor edilen değerler (PROJECT_REPORT Bölüm 13.3'ten):
b2_claimed = [
    {"label": "LSTM full 2 3",      "acc": 80.21, "sens": None, "spec": None},
    {"label": "LSTM full 4 5",      "acc": 77.38, "sens": None, "spec": None},
    {"label": "LSTM full 2 1",      "acc": 69.61, "sens": None, "spec": None},
    {"label": "LSTM full 6 3",      "acc": 75.00, "sens": None, "spec": None},
    {"label": "LSTM technical 2 1", "acc": 67.86, "sens": None, "spec": None},
    {"label": "CNN closing 6 5",    "acc": 74.36, "sens": None, "spec": None},
    {"label": "CNN full 4 1",       "acc": 60.42, "sens": 58.33, "spec": 67.86},
    {"label": "CNN technical 2 3",  "acc": 72.92, "sens": 78.57, "spec": 58.33},
]

print("\n--- TABLO B2 SATIR SATIR CSV KARŞILAŞTIRMASI ---")
print(f"{'Etiket':<25} {'Tablo Acc':>10} {'CSV Acc':>10} {'CSV Set':>12} {'Durum':>10}")
print("-" * 75)

for b2 in b2_claimed:
    parts = b2['label'].split()
    model = parts[0]  # LSTM or CNN
    claimed_set = parts[1]  # full, technical, closing
    in_val = parts[2]
    out_val = parts[3]
    
    # CSV'de ara
    data = lstm_data if model == 'LSTM' else cnn_data
    csv_match = None
    for row in data:
        if (row['Fon'] == 'AMZ' and row['Feature_Set'] == claimed_set 
            and row['Input'] == in_val and row['Output'] == out_val):
            csv_match = row
            break
    
    if csv_match:
        csv_acc = float(csv_match['Mean_Acc']) * 100
        status = "✓" if abs(csv_acc - b2['acc']) < 0.1 else f"✗ FARK={csv_acc - b2['acc']:.2f}"
        print(f"{b2['label']:<25} {b2['acc']:>9.2f}% {csv_acc:>9.2f}% {claimed_set:>12} {status:>10}")
    else:
        print(f"{b2['label']:<25} {b2['acc']:>9.2f}% {'YOK':>10} {claimed_set:>12} {'CSV YOK':>10}")

# Şimdi "yanlış etiket" hipotezini test et — bu Acc değerleri hangi satırlardan geliyor?
print("\n--- YANLIŞ ETİKET TESPİTİ: Bu değerler gerçekte nereden geliyor? ---")
for b2 in b2_claimed:
    parts = b2['label'].split()
    model = parts[0]
    target_acc = b2['acc'] / 100
    
    data = lstm_data if model == 'LSTM' else cnn_data
    matches = []
    for row in data:
        if row['Fon'] == 'AMZ':
            csv_acc = float(row['Mean_Acc'])
            if abs(csv_acc - target_acc) < 0.005:
                matches.append(f"{row['Feature_Set']} In={row['Input']} Out={row['Output']} Acc={csv_acc:.4f}")
    
    if matches:
        csv_match_label = f" | CSV KAYNAK: {', '.join(matches)}"
    else:
        csv_match_label = " | CSV'DE BU DEĞER BULUNAMADI"
    print(f"  {b2['label']} Acc={b2['acc']:.2f}% → {csv_match_label}")

# ======================================================================
# PHASE 5: APPENDIX DOSYALARI ANALİZİ
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 5: APPENDIX DOSYALARI — N=96 REFERANSLARI")
print("=" * 80)

appendix_dir = BASE / "03_Appendix"
for f in sorted(appendix_dir.iterdir()):
    content = f.read_text(encoding='utf-8', errors='replace')
    if 'N=96' in content or 'pooled' in content.lower() or 'havuz' in content.lower():
        print(f"\n[{f.name}] — N=96/pooled referansı bulundu:")
        for i, line in enumerate(content.split('\n')):
            if 'N=96' in line or 'pooled' in line.lower() or 'havuz' in line.lower():
                print(f"  Satır {i+1}: {line.strip()[:120]}")

# ======================================================================
# PHASE 6: PROJECT_REPORT'TA N=96 REFERANSLARI
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 6: PROJECT_REPORT — N=96 TÜM REFERANSLAR")
print("=" * 80)

pr_path = BASE / "01_Savunma_ve_Ana_Metinler" / "PROJECT_REPORT.txt"
pr_content = pr_path.read_text(encoding='utf-8', errors='replace')
pr_lines = pr_content.split('\n')

n96_refs = []
for i, line in enumerate(pr_lines):
    if 'N=96' in line or 'N = 96' in line or '96' in line and ('pooled' in line.lower() or 'havuz' in line.lower()):
        n96_refs.append((i+1, line.strip()[:150]))

print(f"Toplam N=96 referansı: {len(n96_refs)}")
for line_no, text in n96_refs[:30]:
    print(f"  Satır {line_no}: {text}")

# ======================================================================
# PHASE 7: SONUÇ RAPORU
# ======================================================================
print("\n" + "=" * 80)
print("PHASE 7: SONUÇ RAPORU")
print("=" * 80)

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  N=96 NEDİR?                                                        ║
╚══════════════════════════════════════════════════════════════════════╝

N=96 = 3 seed × 32 test gözlemi = 96 toplam tahmin

PROBLEM: CSV'de Mean_Acc 3 seed'in ortalaması, ama Sens/Spec yalnızca 
         son seed'den (Seed 98) loglanmış. Bu ikisi aynı tabloya 
         konulunca aritmetik tutmuyor.

ÇÖZÜM (PROJECT_REPORT Bölüm 12): 3 seed'in confusion matrix'lerini 
       toplayıp tek bir Pooled Confusion Matrix oluşturmak.

SORUN: R kodunda her seed'in ayrı CM'si kaydedilmemiş — sadece 
       Mean_Acc (3-seed ort.) ve son seed'in Sens/Spec'i loglanmış.
       Bu yüzden "gerçek" pooled matris hesaplanamıyor.

╔══════════════════════════════════════════════════════════════════════╗
║  İKİ FARKLI "DOĞRULUK" — HEADLINE vs POOLED                        ║
╚══════════════════════════════════════════════════════════════════════╝

1. HEADLINE (3-seed Mean):
   Mean_Acc = (84.38 + 71.88 + 84.38) / 3 = 80.21%
   Bu "aritmetik ortalama" → modelin ortalama performansı

2. POOLED (toplam doğru / toplam N):
   Doğru = 27 + 23 + 27 = 77
   Pooled_Acc = 77/96 = 80.21%
   
   BEKLE — bu sefer 77/96 tam olarak 80.21% ediyor!
   27/32 = 0.84375, 23/32 = 0.71875, 27/32 = 0.84375
   (27+23+27)/(32+32+32) = 77/96 = 0.80208... ≈ 0.8021
   
   SONUÇ: Mean_Acc ve Pooled_Acc BU DURUMDA YAKLAŞIK EŞİT!
   (Eşit olmaları tesadüf değil — basit aritmetik ortalama ile 
    toplam/N aynı N'lerde eşdeğerdir)
""")

# Kesin hesap
s23_correct = round(32 * 0.8438)  # 27
s27_correct = round(32 * 0.7188)  # 23
s98_correct = round(32 * 0.8438)  # 27
total_correct_exact = s23_correct + s27_correct + s98_correct
pooled_exact = total_correct_exact / 96

print(f"KESİN HESAP:")
print(f"  Seed 23: {s23_correct}/32 = {s23_correct/32:.4f}")
print(f"  Seed 27: {s27_correct}/32 = {s27_correct/32:.4f}")
print(f"  Seed 98: {s98_correct}/32 = {s98_correct/32:.4f}")
print(f"  Toplam: {total_correct_exact}/96 = {pooled_exact:.6f} ({pooled_exact*100:.4f}%)")
print(f"  CSV Mean: 0.8021")
print(f"  Fark: {abs(pooled_exact - 0.8021):.6f}")

# Ama B3'teki sorun SENS/SPEC ile Acc'nin tutmaması
# B3'te TP=63, TN=18 yazılmış → TP+TN=81 → 81/96=84.38% ≠ 80.21%
# Bu, Sens/Spec'in gerçekten pooled olmamasından kaynaklanıyor
print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  TABLO B3 SORUNU — KESİN TEŞHİS                                    ║
╚══════════════════════════════════════════════════════════════════════╝

B3'te yazılan:
  Acc = 77/96 = 80.21% (✓ Bu DOĞRU — Headline Mean ile eşdeğer)
  TP = 63, TN = 18, FP = 3, FN = 12  (✗ BU YANLIŞ)
  
  Kontrol: TP+TN = 63+18 = 81 → 81/96 = 84.38% ≠ 80.21%
  
HATA NEDENİ:
  TP=63, TN=18 değerleri Sens={sens} ve Spec={spec} oranlarından 
  "pooled N=96 varmış gibi" hesaplanmış.
  Ama CSV'deki Sens/Spec SON SEED'e (Seed 98) ait.
  Seed 98 Acc=84.38% → bu yüzden TP+TN=81 çıkıyor (84.38%'in sayıları).
  
  Yani TP=63, TN=18 aslında SEED 98'İN DEĞERLERİ × 3 
  (sanki her seed aynı sonucu üretmiş gibi hesaplanmış).
  
ÇÖZÜM:
  Acc=77/96=80.21% DOĞRU kalmalı.
  TP/TN/FP/FN satırları ya düzeltilmeli ya da silinmeli.
  Gerçek pooled CM için her seed'in ayrı CM'si gerekir 
  (R kodunda kayıtlı mı kontrol edilmeli).
""")
