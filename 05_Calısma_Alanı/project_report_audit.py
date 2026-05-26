# -*- coding: utf-8 -*-
"""
PROJECT_REPORT.txt — SATIRSAL DOĞRULUK + TEKRAR + EKSİKLİK DENETİMİ
CSV ground-truth ile çapraz kontrol
"""
import sys, io, csv, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from collections import Counter

BASE = Path(r"c:\Users\Kurt\Desktop\Proje")
PR = BASE / "01_Savunma_ve_Ana_Metinler" / "PROJECT_REPORT.txt"
CSV_DIR = BASE / "02_Akademik_Kanıtlar" / "2018-2026 c¦ğ¦-kt¦-lar"

# CSV yükle
def load_csv(name):
    with open(CSV_DIR / name, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

lstm = load_csv("EMEKLILIK_LSTM_sonuclar.csv")
cnn = load_csv("EMEKLILIK_CNN_sonuclar.csv")
naive = load_csv("EMEKLILIK_NAIVE_baseline.csv")
arima = load_csv("EMEKLILIK_ARIMA_sonuclar.csv")

# Ground truth değerler (CSV'den)
GT = {
    "AMZ LSTM full 2 3 Acc": 0.8021,
    "AMZ LSTM full 2 3 Sens": 0.84,
    "AMZ LSTM full 2 3 Spec": 0.8571,
    "AMZ LSTM full 2 3 F1": 0.8936,
    "AMZ LSTM full 2 3 p": 1e-04,
    "AMZ LSTM full 2 3 Seed23": 0.8438,
    "AMZ LSTM full 2 3 Seed27": 0.7188,
    "AMZ LSTM full 2 3 Seed98": 0.8438,
    "AZS CNN tech 4 3 Acc": 0.7556,
    "AZS CNN tech 4 3 Sens": 0.9091,
    "AZS CNN tech 4 3 Spec": 0.6250,
    "Naive AMZ Out3": 0.7879,
    "Naive AZS Out3": 0.8485,
    "Naive AZS Out5": 0.9032,
    "Naive AMZ Out5": 0.8387,
    "THYAO LSTM best": 0.5756,
    "THYAO CNN best": 0.5397,
    "THYAO ARIMA best": 0.5578,
}

content = PR.read_text(encoding='utf-8', errors='replace')
lines = content.split('\n')

print(f"PROJECT_REPORT.txt: {len(lines)} satir, {len(content)} byte")

# ======================================================================
# DENETIM 1: KRİTİK SAYISAL DEĞERLERİN DOĞRULUĞU
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 1: KRITIK SAYISAL DEGERLER")
print("=" * 80)

checks = [
    ("80.21", "%80,21", "AMZ LSTM Acc"),
    ("84.86", "%84,86", "AMZ LSTM BA"),
    ("0.8936", "0,8936", "AMZ LSTM F1"),
    ("0.84", "0,84", "AMZ LSTM Sens"),
    ("0.8571", "0,8571", "AMZ LSTM Spec"),
    ("75.56", "%75,56", "AZS CNN Acc"),
    ("90.91", "90,91", "AZS CNN Sens"),
    ("62.50", "62,50", "AZS CNN Spec"),
    ("78.79", "%78,79", "Naive AMZ Out3"),
    ("84.85", "%84,85", "Naive AZS Out3"),
    ("57.56", "%57,56", "THYAO LSTM best"),
    ("55.78", "%55,78", "THYAO ARIMA best"),
]

for val_en, val_tr, label in checks:
    count = content.count(val_en) + content.count(val_tr)
    print(f"  {label} ({val_en}): {count} kez bulundu {'OK' if count > 0 else 'EKSIK!'}")

# ======================================================================
# DENETIM 2: BÖLÜM YAPISI — TEKRAR VE EKSİKLİK
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 2: BOLUM YAPISI")
print("=" * 80)

sections = []
for i, line in enumerate(lines):
    # BÖLÜM başlıkları
    if re.match(r'^\s*(BÖLÜM|KISIM|EK-)\s', line) or '╔═' in line:
        sections.append((i+1, line.strip()[:100]))

print(f"Toplam bolum/baslik: {len(sections)}")
for line_no, title in sections:
    print(f"  Satir {line_no}: {title}")

# ======================================================================
# DENETIM 3: ENCODING KALINTILARI
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 3: ENCODING HATALARI")
print("=" * 80)

encoding_patterns = ['Ã', 'â€', 'Ã¢', 'ÃƒÅ', 'Ã¶', 'Ã¼', 'Ã§', 'Ã–']
total_encoding_errors = 0
for pattern in encoding_patterns:
    matches = [(i+1, lines[i].strip()[:100]) for i in range(len(lines)) if pattern in lines[i]]
    if matches:
        total_encoding_errors += len(matches)
        print(f"  '{pattern}': {len(matches)} satir")
        for ln, txt in matches[:3]:
            print(f"    Satir {ln}: {txt}")

print(f"\n  TOPLAM encoding hatasi: {total_encoding_errors}")

# ======================================================================
# DENETIM 4: TEKRARLANAN İÇERİK
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 4: TEKRARLANAN SATIRLAR (5+ karakter, 2+ tekrar)")
print("=" * 80)

# Uzun satırları say (kısa satırlar doğal tekrar)
line_counts = Counter()
for line in lines:
    stripped = line.strip()
    if len(stripped) > 50:
        line_counts[stripped] += 1

duplicates = [(count, text[:100]) for text, count in line_counts.items() if count > 1]
duplicates.sort(reverse=True)
print(f"  {len(duplicates)} tekrarlanan uzun satir")
for count, text in duplicates[:10]:
    print(f"    {count}x: {text}")

# ======================================================================
# DENETIM 5: MC SAYILARI DOĞRULAMA
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 5: MC SAYILARI CSV ILE KARSILASTIRMA")
print("=" * 80)

# CSV'den MC say
def count_mc(data, fon, model_name):
    mc = 0
    total = 0
    for row in data:
        if row['Fon'] == fon:
            total += 1
            spec = row.get('Spec', '')
            sens = row.get('Sens', '')
            if spec in ('0', 'NA', '') or sens in ('0', 'NA', ''):
                mc += 1
    return mc, total

mc_checks = [
    ("AZS", lstm, "LSTM", "13/27"),
    ("AZS", cnn, "CNN", "9/27"),
    ("AMZ", lstm, "LSTM", "10/27"),
    ("AMZ", cnn, "CNN", "9/27"),
]

for fon, data, model, expected in mc_checks:
    mc, total = count_mc(data, fon, model)
    actual = f"{mc}/{total}"
    status = "OK" if actual == expected else f"FARK! CSV={actual}"
    in_report = expected in content
    print(f"  {fon} {model}: CSV={actual}, Raporda '{expected}' {'var' if in_report else 'YOK'} {status}")

# ======================================================================
# DENETIM 6: N=96 TUTARLILIĞI
# ======================================================================
print("\n" + "=" * 80)
print("DENETIM 6: N=96 TUTARLILIGI")
print("=" * 80)

n96_values = {
    "77/96": 0, "81/96": 0, "80.21": 0, "84.38": 0,
    "TP=63": 0, "TP=60": 0, "TN=18": 0, "TN=17": 0,
}
for key in n96_values:
    n96_values[key] = content.count(key)
    print(f"  '{key}': {n96_values[key]} kez")

# Uyarılar
if n96_values["TP=63"] > 0 and n96_values["TP=60"] > 0:
    print("  UYARI: Hem TP=63 (pseudo-pooled) hem TP=60 (true-pooled) var — dual yaklaşım dokümante mi?")
if n96_values["81/96"] > 0:
    print("  NOT: 81/96 = pseudo-pooled (Seed 98 oranları × N=96). UYIK sunumda kullanılıyor.")
if n96_values["77/96"] > 0:
    print("  NOT: 77/96 = true pooled (per-seed CM toplamı). Headline = Mean ile aynı.")

print("\n" + "=" * 80)
print("DENETIM TAMAMLANDI")
print("=" * 80)
