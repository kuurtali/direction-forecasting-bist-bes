# -*- coding: utf-8 -*-
"""
MAKALE.docx görev denetim scripti
Kritik görevleri K1-K6 kontrol eder ve düzeltme yerlerini raporlar
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, re, os

MAKALE = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx'

with zipfile.ZipFile(MAKALE) as z:
    xml = z.read('word/document.xml').decode('utf-8', errors='replace')

# XML'den temiz metin
raw = re.sub(r'<[^>]+>', ' ', xml)
text = re.sub(r'\s+', ' ', raw).strip()

FOUND   = []
MISSING = []
ISSUES  = []

def chk(label, token, context_chars=120):
    idx = text.find(token)
    if idx >= 0:
        ctx = text[max(0,idx-30):idx+context_chars]
        FOUND.append((label, token, ctx))
        print(f"  [MEVCUT]  {label}: '{token}'")
        print(f"            ...{ctx}...")
    else:
        MISSING.append((label, token))
        print(f"  [YOK]     {label}: '{token}'")

def issue(label, detail):
    ISSUES.append((label, detail))
    print(f"  [SORUN]   {label}: {detail}")

print("="*70)
print("K3: Çizelge 19 — Van der Burgt Yanlış Değerler")
print("="*70)
# Yanlış değerler — makalede olmamalı (ama varsa kötü model atıfla)
# LSTM'ye atfedilen ama aslında ARIMA değerleri
wrong_vdb = [
    ("VdB LSTM maks 78,92 (YANLIŞ)", "78,92"),
    ("VdB LSTM maks 78.92 (YANLIŞ)", "78.92"),
    ("VdB CNN maks 75,14 (YANLIŞ)",  "75,14"),
    ("VdB CNN maks 75.14 (YANLIŞ)",  "75.14"),
    ("VdB LSTM ort 67,57 (YANLIŞ)",  "67,57"),
    ("VdB LSTM ort 67.57 (YANLIŞ)",  "67.57"),
    ("VdB CNN ort 63,42 (YANLIŞ)",   "63,42"),
    ("VdB CNN ort 63.42 (YANLIŞ)",   "63.42"),
    ("VdB ARIMA ort 55,78 (YANLIŞ)", "55,78"),
    ("VdB ARIMA ort 55.78 (YANLIŞ)", "55.78"),
]
print("\n--- Yanlış atfedilen değerlerin varlığı ---")
found_wrong = []
for label, token in wrong_vdb:
    idx = text.find(token)
    if idx >= 0:
        ctx = text[max(0,idx-60):idx+80]
        print(f"  [VAR-KONTROL] {label}")
        print(f"                ...{ctx}...")
        found_wrong.append((label, token, ctx))
    else:
        print(f"  [YOK]         {label}")

# Doğru VdB değerleri var mı?
print("\n--- Doğru Van der Burgt değerleri ---")
correct_vdb = [
    ("VdB LSTM Technical ort %66,93",  "66,93"),
    ("VdB LSTM Technical ort %66.93",  "66.93"),
    ("VdB ARIMA Technical ort %67,57", "67,57"),
    ("VdB ARIMA Technical maks 78,92", "78,92"),
    ("VdB CNN Hist+Tech ort %58,24",   "58,24"),
    ("VdB CNN Hist+Tech ort %58.24",   "58.24"),
]
for label, token in correct_vdb:
    chk(label, token)

print()
print("="*70)
print("K1+K2: Pooled Matrix / Sens-Spec Değerleri")
print("="*70)
# Pooled CM degerleri
pooled_checks = [
    ("Pooled N=96 TP=64",   "64"),
    ("Pooled TN=17",        "17"),
    ("Pooled FN=12",        "12"),
    ("Pooled FP=3",         "FP"),
    ("Pooled Acc 84,38",    "84,38"),
    ("Pooled Acc 84.38",    "84.38"),
    ("Headline Acc 80,21",  "80,21"),
    ("Headline Acc 80.21",  "80.21"),
    ("Sens 84,00 veya 84,0","84,00"),
    ("Sens 84 (alternatif)","84,0"),
    ("Spec 85,71",          "85,71"),
    ("McNemar",             "McNemar"),
    ("Binom",               "Binom"),
    ("Binomial",            "Binomial"),
]
for label, token in pooled_checks:
    chk(label, token)

print()
print("="*70)
print("K4: McNemar / Binom Test Etiketi")
print("="*70)
if any(t[1]=="McNemar" and t in FOUND for t in FOUND):
    issue("K4","'McNemar' ifadesi makalede mevcut — Binom testi ile değiştirilmeli")
for label, token, ctx in FOUND:
    if token == "McNemar":
        issue("K4", f"'McNemar' bulundu: ...{ctx}...")

print()
print("="*70)
print("K5: Şekil 22 yanlış atıf")
print("="*70)
chk("K5 - Şekil 22 atfı (YANLIŞ olabilir)", "Şekil 22")
chk("K5 - Sekil 22 atfı", "ekil 22")
chk("K5 - Figure 22",     "igure 22")

print()
print("="*70)
print("K6: Test Seti Belirsizliği")
print("="*70)
chk("Test=32 hafta",  "32 hafta")
chk("Test=38",        "38 hafta")
chk("Test=40",        "40 hafta")
chk("N=32",           "N=32")
chk("N=96",           "N=96")

print()
print("="*70)
print("H3: Ondalık Ayraç Kontrolü")
print("="*70)
# TR Dizin standardı: virgül
# Nokta kullanan sayı örnekleri
nokta_sayilar = ["80.21", "75.56", "68.89", "57.56", "53.97", "78.79"]
for s in nokta_sayilar:
    idx = text.find(s)
    if idx >= 0:
        ctx = text[max(0,idx-20):idx+40]
        issue("H3", f"Nokta ondalık ayraç: '{s}' — ...{ctx}...")

virgul_sayilar = ["80,21", "75,56", "57,56"]
for s in virgul_sayilar:
    idx = text.find(s)
    if idx >= 0:
        print(f"  [VİRGÜL-OK] '{s}' mevcut")

print()
print("="*70)
print("H4: Yazılım Sürümleri")
print("="*70)
sw_checks = [
    ("R sürümü", "R v"),
    ("keras3 sürümü", "keras3"),
    ("TensorFlow sürüm", "TensorFlow"),
    ("forecast paketi", "forecast"),
]
for label, token in sw_checks:
    chk(label, token)

print()
print("="*70)
print("ÖZET")
print("="*70)
print(f"\n  Mevcut değerler: {len(FOUND)}")
print(f"  Eksik değerler:  {len(MISSING)}")
print(f"  Sorunlar:        {len(ISSUES)}")

if ISSUES:
    print("\n--- TESPİT EDİLEN SORUNLAR ---")
    for lbl, det in ISSUES:
        print(f"  [{lbl}] {det}")
