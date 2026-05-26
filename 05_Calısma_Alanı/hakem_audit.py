"""
HAKEM GÖZLEMİ — Akademik makale kalite denetimi
Şablon: Makale_Formatı.docx kuralları
Örnek: İstatistikçiler Dergisi yayın standardı
"""
from docx import Document
import re

doc = Document(r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx")
paras = [(p.text.strip(), p) for p in doc.paragraphs]
texts = [t for t, _ in paras if t]

full = '\n'.join(texts)
issues = []

# ============ 1. ÖZ/ABSTRACT UZUNLUK ============
print("="*70)
print("1. ÖZ ve ABSTRACT UZUNLUK")
print("="*70)

oz_text = ""
abs_text = ""
in_oz = False
in_abs = False
for t in texts:
    if t == "Öz" or t.startswith("Öz "):
        in_oz = True
        continue
    if t.startswith("Anahtar sözcükler"):
        in_oz = False
        continue
    if t == "Abstract":
        in_abs = True
        continue
    if t.startswith("Keywords:"):
        in_abs = False
        continue
    if in_oz:
        oz_text += t + " "
    if in_abs:
        abs_text += t + " "

oz_words = len(oz_text.split())
abs_words = len(abs_text.split())
print(f"  TR Öz: {oz_words} kelime", end="")
if oz_words < 100:
    issues.append(f"TR Öz çok kısa ({oz_words} kelime) — 150-250 kelime önerilir")
    print(" ⚠ KISA")
elif oz_words > 300:
    issues.append(f"TR Öz çok uzun ({oz_words} kelime)")
    print(" ⚠ UZUN")
else:
    print(" ✓")

print(f"  EN Abstract: {abs_words} kelime", end="")
if abs_words < 100:
    issues.append(f"EN Abstract çok kısa ({abs_words} kelime)")
    print(" ⚠ KISA")
elif abs_words > 300:
    issues.append(f"EN Abstract çok uzun ({abs_words} kelime)")
    print(" ⚠ UZUN")
else:
    print(" ✓")

# ============ 2. GİRİŞ — Yapı kontrol ============
print("\n" + "="*70)
print("2. GİRİŞ BÖL. — Akademik yapı")
print("="*70)

# Check if Giriş has: problem statement, literature gap, contribution
giris_text = ""
in_giris = False
for t in texts:
    if t.startswith("1. Giriş"):
        in_giris = True
        continue
    if re.match(r'^2\.\s', t):
        in_giris = False
    if in_giris:
        giris_text += t + " "

giris_words = len(giris_text.split())
print(f"  Giriş kelime: {giris_words}")

# Check for key academic phrases
checks = {
    "problem tanımı": any(x in giris_text.lower() for x in ["bu çalışma", "amacı", "ele alınmaktadır", "araştır"]),
    "literatür boşluğu": any(x in giris_text.lower() for x in ["boşluk", "eksik", "yetersiz", "ihmal", "sınırlı sayıda"]),
    "çalışma katkısı": any(x in giris_text.lower() for x in ["katkı", "özgün", "farklı", "ilk kez", "yenilik"]),
    "makale yapısı": any(x in giris_text.lower() for x in ["bölüm", "organize", "yapı", "sırasıyla"]),
}
for check, found in checks.items():
    status = "✓" if found else "⚠ EKSİK"
    print(f"  {check}: {status}")
    if not found:
        issues.append(f"Giriş: '{check}' ifadesi eksik")

# ============ 3. YÖNTEM — Formül numaralandırma ============
print("\n" + "="*70)
print("3. YÖNTEM — Formül kontrolü")
print("="*70)

formulas = []
for t in texts:
    if re.search(r'\(\d+\)$', t):
        formulas.append(t[:80])
print(f"  Formül sayısı: {len(formulas)}")
for f in formulas:
    print(f"    {f}")
if len(formulas) < 3:
    issues.append("Yöntem bölümünde formül sayısı az — ARIMA, LSTM, CNN formülleri gerekli")

# ============ 4. SONUÇ — Akademik yapı ============
print("\n" + "="*70)
print("4. SONUÇ BÖL. — Akademik yapı")
print("="*70)

sonuc_text = ""
in_sonuc = False
for t in texts:
    if t.startswith("6. Sonuç"):
        in_sonuc = True
        continue
    if re.match(r'^(Kaynaklar|KAYNAKÇA)', t):
        in_sonuc = False
    if in_sonuc:
        sonuc_text += t + " "

sonuc_words = len(sonuc_text.split())
print(f"  Sonuç kelime: {sonuc_words}")

sonuc_checks = {
    "ana bulguların özetlenmesi": any(x in sonuc_text.lower() for x in ["bulgu", "sonuç", "göster", "ortaya"]),
    "pratik implikasyon": any(x in sonuc_text.lower() for x in ["yatırımcı", "uygulamacı", "pratik", "politika"]),
    "gelecek çalışma önerisi": any(x in sonuc_text.lower() for x in ["gelecek", "ileriki", "öneri", "genişlet"]),
    "sınırlılık tekrarı": any(x in sonuc_text.lower() for x in ["sınır", "kısıt", "limit"]),
}
for check, found in sonuc_checks.items():
    status = "✓" if found else "⚠ EKSİK"
    print(f"  {check}: {status}")
    if not found:
        issues.append(f"Sonuç: '{check}' ifadesi eksik")

# ============ 5. ATIF STİLİ ============
print("\n" + "="*70)
print("5. ATIF STİLİ")
print("="*70)

# Check for in-text citation style [N]
cite_pattern = re.compile(r'\[(\d+)\]')
cite_count = 0
cite_in_sentence = 0  # citations at end of sentence vs inline
for t in texts:
    matches = cite_pattern.findall(t)
    cite_count += len(matches)
    for m in matches:
        # Check if citation is part of sentence like "Doe [5] found..."
        idx = t.find(f"[{m}]")
        if idx > 0 and t[idx-1] == ' ' and idx + len(f"[{m}]") < len(t):
            cite_in_sentence += 1

print(f"  Toplam atıf kullanımı: {cite_count}")
print(f"  Cümle içi atıf: {cite_in_sentence}")

# ============ 6. TABLO/ŞEKİL ATIF KALİTESİ ============
print("\n" + "="*70)
print("6. TABLO/ŞEKİL ATIF KALİTESİ")
print("="*70)

# Check quality of references - not just "Şekil X'te" but explanatory
for t in texts:
    m = re.search(r'(Şekil|Çizelge)\s+(\d+)', t)
    if m and not t.startswith(m.group()):
        # This is a body reference, check if it has explanation
        if len(t) < 40:
            print(f"  KISA ATIF: {t[:80]}")
            issues.append(f"Kısa şekil/çizelge atıfı: {t[:60]}")

# ============ 7. PARAGRAF UZUNLUKLARI ============
print("\n" + "="*70)
print("7. PARAGRAF UZUNLUK ANALİZİ")
print("="*70)

very_long = []
very_short = []
for i, t in enumerate(texts):
    words = len(t.split())
    if words > 200:
        very_long.append((i, words, t[:60]))
    if words < 15 and not re.match(r'^(\d+\.|Şekil|Çizelge|Not:|Kaynaklar|Öz|Abstract|Anahtar|Keywords|Model|Acc)', t):
        very_short.append((i, words, t[:60]))

print(f"  Çok uzun paragraflar (>200 kelime): {len(very_long)}")
for idx, wc, txt in very_long[:3]:
    print(f"    P{idx}: {wc} kelime — {txt}...")
    issues.append(f"P{idx}: {wc} kelimelik çok uzun paragraf")

print(f"  Çok kısa paragraflar (<15 kelime): {len(very_short)}")
for idx, wc, txt in very_short[:3]:
    print(f"    P{idx}: {wc} kelime — {txt}")

# ============ 8. TEKRAR EDEN İFADELER ============
print("\n" + "="*70)
print("8. TEKRAR EDEN İFADELER")
print("="*70)

# Count repeated phrases
from collections import Counter
phrase_counts = Counter()
for t in texts:
    words = t.lower().split()
    for size in [3, 4]:
        for j in range(len(words) - size + 1):
            phrase = ' '.join(words[j:j+size])
            if len(phrase) > 15:
                phrase_counts[phrase] += 1

print("  En çok tekrar eden 3+ kelimelik ifadeler:")
for phrase, count in phrase_counts.most_common(15):
    if count >= 5:
        print(f"    [{count}x] {phrase}")

# ============ 9. SAYFA/KELIME SINIRI ============
print("\n" + "="*70)
print("9. DERGI SAYFA SINIRI")
print("="*70)

total_words = sum(len(t.split()) for t in texts)
total_figs = 23
total_tables = 20
print(f"  Kelime: {total_words}")
print(f"  Şekil: {total_figs}")
print(f"  Çizelge: {total_tables}")
print(f"  Toplam görsel element: {total_figs + total_tables}")
if total_figs + total_tables > 30:
    issues.append(f"Toplam {total_figs + total_tables} görsel element — çoğu dergi max 15-20 kabul eder")
    print(f"  ⚠ {total_figs + total_tables} görsel element fazla olabilir (bazı dergiler 15-20 sınırı koyar)")

# ============ SUMMARY ============
print("\n" + "="*70)
print(f"HAKEM RİSK RAPORU — TOPLAM {len(issues)} BULGU")
print("="*70)
for i, iss in enumerate(issues, 1):
    print(f"  {i}. {iss}")
