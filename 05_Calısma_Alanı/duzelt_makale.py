# -*- coding: utf-8 -*-
"""
MAKALE.docx — K3, K4, K5 otomatik düzeltme scripti
Çalıştır → MAKALE_DUZELTILMIS.docx üretir
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import zipfile, shutil, os, re, copy
from lxml import etree

SRC  = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx'
DST  = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'

shutil.copy2(SRC, DST)
print(f"Kaynak kopyalandı: {DST}")

# ── DOCX zip üzerinde çalış ─────────────────────────────────────────────────
NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_full_text_of_para(para):
    return ''.join(r.text or '' for r in para.findall('.//w:t', NSMAP))

def replace_in_run(run, old, new):
    t = run.find('w:t', NSMAP)
    if t is not None and t.text and old in t.text:
        t.text = t.text.replace(old, new)
        return True
    return False

def replace_in_doc(tree, replacements):
    """replacements: list of (old_str, new_str, description)"""
    counts = {old: 0 for old, _, _ in replacements}
    body = tree.find('.//w:body', NSMAP)
    for para in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
        t = para.find('w:t', NSMAP)
        if t is not None and t.text:
            for old, new, desc in replacements:
                if old in t.text:
                    t.text = t.text.replace(old, new)
                    counts[old] += 1
    return counts

with zipfile.ZipFile(DST, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for name in names:
        contents[name] = zin.read(name)

xml_bytes = contents['word/document.xml']
tree = etree.fromstring(xml_bytes)

CHANGES = []

# ═══════════════════════════════════════════════════════════════════════════════
# K3: Çizelge 19 — Van der Burgt yanlış atıflar
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- K3: Van der Burgt Çizelge 19 düzeltmesi ---")
# Audit sonucundan bilinen bağlam:
# "LSTM ortalamasını %67,57 ve en yüksek konfigürasyonunu (Out=5, In=4) %78,92 olarak raporlamıştır"
# Bu cümle YANLIŞ: 67,57 ve 78,92 ARIMA Technical'ın değerleri.
# DOĞRUSU: Van der Burgt LSTM Technical ortalaması %66,93, en yüksek %82,22
# Cümleyi düzelt:
k3_replacements = [
    # Yanlış cümle → doğru cümle (LSTM ortalaması %67,57)
    (
        "LSTM ortalamasını %67,57 ve en yüksek konfigürasyonunu (Out=5, In=4) %78,92 olarak raporlamıştır",
        "LSTM Technical konfigürasyonunu ortalama %66,93, en yüksek (Out=5, In=2) %82,22 olarak raporlamıştır",
        "K3-a: LSTM ort 67,57→66,93 ve maks 78,92→82,22"
    ),
    # Alternatif yazım biçimleri (noktalı)
    (
        "LSTM ortalamasını %67.57 ve en yüksek konfigürasyonunu (Out=5, In=4) %78.92 olarak raporlamıştır",
        "LSTM Technical konfigürasyonunu ortalama %66,93, en yüksek (Out=5, In=2) %82,22 olarak raporlamıştır",
        "K3-a-nokta"
    ),
    # CNN ortalama %63,42 yanlış (ARIMA Historical) → CNN Hist+Tech %58,24
    (
        "CNN ortalama (hist+tech) %63,42",
        "CNN ortalama (hist+tech) %58,24",
        "K3-b: CNN ort 63,42→58,24"
    ),
    (
        "CNN ortalama (hist+tech) %63.42",
        "CNN ortalama (hist+tech) %58,24",
        "K3-b-nokta"
    ),
]
counts_k3 = replace_in_doc(tree, k3_replacements)
for old, new, desc in k3_replacements:
    n = counts_k3[old]
    if n > 0:
        print(f"  [K3-OK] {desc}: {n} yerde değiştirildi")
        CHANGES.append(f"K3: {desc} ({n} değişiklik)")
    else:
        print(f"  [K3-YOK] {desc}: Bulunamadı (zaten doğru veya farklı format)")

# ═══════════════════════════════════════════════════════════════════════════════
# K4: McNemar → Binom testi
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- K4: McNemar → Binom testi düzeltmesi ---")
k4_replacements = [
    (
        "McNemar p-değeri",
        "Binom testi p-değeri (H₀: Acc=0,50)",
        "K4: McNemar→Binom"
    ),
    (
        "McNemar p değeri",
        "Binom testi p-değeri (H₀: Acc=0,50)",
        "K4: McNemar p değeri→Binom"
    ),
    (
        "McNemar testi",
        "kesin binom testi",
        "K4: McNemar testi→kesin binom testi"
    ),
    (
        "McNemar",
        "kesin binom testi",
        "K4: McNemar→kesin binom testi (genel)"
    ),
]
counts_k4 = replace_in_doc(tree, k4_replacements)
for old, new, desc in k4_replacements:
    n = counts_k4[old]
    if n > 0:
        print(f"  [K4-OK] {desc}: {n} yerde değiştirildi")
        CHANGES.append(f"K4: {desc} ({n} değişiklik)")

# ═══════════════════════════════════════════════════════════════════════════════
# K5: Şekil 22 → Şekil 9 (yanlış şekil atıf)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- K5: Şekil 22 → Şekil 9 düzeltmesi ---")
# Audit: "binasyonunun öne çıkması) ise Şekil 22'de görselleştirilmektedir"
# Çizelge 20 satır 6'da Şekil 22 → Şekil 9
k5_replacements = [
    (
        "Şekil 22'de görselleştirilmektedir",
        "Şekil 9'da görselleştirilmektedir",
        "K5: Şekil 22→9 (metin)"
    ),
    (
        "Şekil 22",
        "Şekil 9",
        "K5: Şekil 22→9 (genel)"
    ),
]
counts_k5 = replace_in_doc(tree, k5_replacements)
for old, new, desc in k5_replacements:
    n = counts_k5[old]
    if n > 0:
        print(f"  [K5-OK] {desc}: {n} yerde değiştirildi")
        CHANGES.append(f"K5: {desc} ({n} değişiklik)")
    else:
        print(f"  [K5-YOK] {desc}: Bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
# H3: İngilizce özet kısmındaki noktalı sayılar (TR'de virgül olmalı)
# Audit: 80.21, 57.56, 78.79 noktalı bulundu
# NOT: İngilizce Abstract'ta nokta DOĞRU. TR metin içinde virgül olmalı.
# Audit bağlamından: "reaches 80.21% accuracy" → İngilizce bölüm → DOKUNMA
# "rasyonu %71.46'dan %57.56'ya" → Türkçe metin → virgül yap
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- H3: Türkçe metin nokta→virgül (dikkatli) ---")
h3_replacements = [
    # Türkçe bağlamda geçen noktalı sayılar
    (
        "%71.46'dan %57.56'ya",
        "%71,46'dan %57,56'ya",
        "H3: 71.46 ve 57.56 virgül"
    ),
    (
        "%55.83'ten %50.52'ye",
        "%55,83'ten %50,52'ye",
        "H3: 55.83 ve 50.52 virgül"
    ),
    (
        "%56.79'dan %49.55'e",
        "%56,79'dan %49,55'e",
        "H3: 56.79 ve 49.55 virgül"
    ),
]
counts_h3 = replace_in_doc(tree, h3_replacements)
for old, new, desc in h3_replacements:
    n = counts_h3[old]
    if n > 0:
        print(f"  [H3-OK] {desc}: {n} yerde değiştirildi")
        CHANGES.append(f"H3: {desc} ({n} değişiklik)")
    else:
        print(f"  [H3-YOK] {desc}: Bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
# H4: Yazılım sürümleri — §2.1/2.2'ye ekle
# Audit: 'R v' yok, 'keras3' yok
# Strateji: "Keras3/TensorFlow" ifadesini sürümlerle zenginleştir
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- H4: Yazılım sürüm bilgisi ---")
h4_replacements = [
    (
        "Keras3/TensorFlow",
        "Keras3 v3.13.2 / TensorFlow v2.21.0",
        "H4: Keras3/TF sürüm ekleme"
    ),
    (
        "keras3/TensorFlow",
        "Keras3 v3.13.2 / TensorFlow v2.21.0",
        "H4: keras3/TF küçük harf"
    ),
    (
        "keras/TensorFlow",
        "Keras3 v3.13.2 / TensorFlow v2.21.0",
        "H4: keras/TF alternatif"
    ),
]
counts_h4 = replace_in_doc(tree, h4_replacements)
for old, new, desc in h4_replacements:
    n = counts_h4[old]
    if n > 0:
        print(f"  [H4-OK] {desc}: {n} yerde değiştirildi")
        CHANGES.append(f"H4: {desc} ({n} değişiklik)")
    else:
        print(f"  [H4-YOK] {desc}: Bulunamadı")

# ═══════════════════════════════════════════════════════════════════════════════
# Kaydet
# ═══════════════════════════════════════════════════════════════════════════════
new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
contents['word/document.xml'] = new_xml

with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in contents.items():
        zout.writestr(name, data)

print(f"\n✅ Kaydedildi: {DST}")
print(f"\n=== YAPILAN DEĞİŞİKLİKLER ({len(CHANGES)} adet) ===")
for c in CHANGES:
    print(f"  • {c}")

print("\n=== SONRAKI ADIMLAR (manuel) ===")
print("  K3-devam: Çizelge 19 tabloya doğru VdB değerleri elle girilmeli")
print("  K1+K2:    Çizelge 8 ve 18 Sens/Spec çelişkisi Word'de kontrol edilmeli")
print("  K6:       Test seti N belirsizliği (38-40 hafta vs 32 efektif) açıklanmalı")
print("  H1:       APA referans teyidi manuel yapılmalı")
print("  H2:       Şekil 8 ve 9 altyazı ayrımı")
