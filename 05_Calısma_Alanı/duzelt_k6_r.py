# -*- coding: utf-8 -*-
"""
K6 + R v4.5.2: Makaleye test seti n aciklamasi ve R surumu ekle
===============================================================
K6: §2.6 veya veri bolümüne ALZ=38, AZS=40, AMZ=40 aciklamasi ekle
R:  §2.1 veya metodoloji bolumune R v4.5.2 surumunu ekle
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, shutil, re, os
from lxml import etree

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
BAK = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS_k6r.docx'
shutil.copy2(SRC, BAK)

with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for n in names:
        contents[n] = zin.read(n)

raw = contents['word/document.xml'].decode('utf-8', errors='replace')
changes = 0

# ============================================================
# K6: test seti aciklamasi ekle
# "test seti" olan yerleri bul - ilk gececek cümleye test seti n bilgisini ekle
# PROJECT_REPORT 2.3: ALZ=38, AZS=40, AMZ=40 haftalik gozlem
# ============================================================

# Mevcut metinde "test set" aciklamasi arayalim ve uygun yeri bulalim
# "Her fon için %15 kronolojik test bölümü kullanılmıştır" benzeri cümle sonrasına ekle

# Strateji: bölme oranı (70/15/15) yazan yere ekle
k6_fixes = [
    # "test seti" yazan ve hemen sonra tahmin ufku veya N gelmiyorsa ekle
    (
        '%70/%15/%15 oranında kronolojik',
        '%70/%15/%15 oranında kronolojik'  # kontrol
    ),
]

# R v4.5.2 eklemesi: "Keras3 v3.13.2" olan yere R v4.5.2 ekle
r_fix_old = 'Keras3 v3.13.2 / TensorFlow v2.21.0'
r_fix_new = 'Keras3 v3.13.2 / TensorFlow v2.21.0 (R v4.5.2)'

if r_fix_old in raw:
    raw = raw.replace(r_fix_old, r_fix_new)
    print(f'[R] Eklendi: "{r_fix_new}"')
    changes += 1
else:
    # Farkli format dene
    alt_old = 'Keras3 v3.13.2'
    if alt_old in raw:
        cnt = raw.count(alt_old)
        print(f'[R] "{alt_old}" bulundu ({cnt}x) — tam format kontrolu:')
        # Kontekst goster
        idx = raw.find(alt_old)
        print(f'    Kontekst: ...{raw[max(0,idx-50):idx+80]}...')
    else:
        print(f'[R] "{alt_old}" bulunamadi')

# K6 test seti N aciklamasi — XML'e bak
text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

# Veri bölümü paragraflarini bul
print()
print('=== VERİ BÖLÜMÜ PARAGRAFLARInın İÇERİĞİ ===')
# "%70" veya "bölme" veya "kronolojik" iceren kismi bul
for kw in ['kronolojik', '%70', 'bölme oran', 'split']:
    idx = text.find(kw)
    if idx > 0:
        print(f'  "{kw}" @ pozisyon {idx}:')
        print(f'  ...{text[max(0,idx-100):idx+200]}...')
        print()
        break

# ALZ/AZS/AMZ test seti n bilgisi var mi?
for phrase in ['test 38', 'test 40', 'test 39', 'Test 38', 'Test=38', 'n=38', 'n=40']:
    cnt = text.count(phrase)
    if cnt:
        print(f'  "{phrase}": {cnt} kez bulundu')

print()
# Mevcut durum ozeti
print('=== SONUÇ ===')
print(f'R v4.5.2 eklemesi: {"YAPILDI" if changes > 0 else "YAPILMADI (format farklı)"}')

# Kaydet
if changes > 0:
    contents['word/document.xml'] = raw.encode('utf-8')
    tmp = SRC + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, contents[n])
    os.replace(tmp, SRC)
    print(f'Kaydedildi: {SRC}')
