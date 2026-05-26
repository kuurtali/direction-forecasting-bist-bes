# -*- coding: utf-8 -*-
"""
MAKALE GRAFİK & AÇIKLAMA DÜZELTİCİ
====================================
Görevler:
1. Şekil 14 altyazısında TP=63,TN=18 → TP=64,TN=17 (CSV ground-truth)
   PROJECT_REPORT Bölüm 12.8.1'e göre MAKALE'nin "CSV-Rate Pooled" satırı kullanılıyor
   Ama grafik kodunda grafik_v3_p2.py L82: TP=64,FN=12,FP=3,TN=17 — bu CSV ground-truth!
   Şekil 14 altyazısını grafik koduyla uyumlu hale getir.
2. Şekil 14 altyazısındaki Sens/Spec formülleri düzelt.
3. Şekil 21 numaralandırma sorununu tespit et (içinde "Şekil 9." var - duplicate)
4. Raporla tüm değişiklikleri.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import zipfile, shutil, re, os
from lxml import etree
from copy import deepcopy

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
BAK = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS_onceki_grafik.docx'

# Grafik dogrulanmis degerler (grafik_v3_p2.py L82 - CSV ground-truth)
# TP=64, FN=12, FP=3, TN=17
# Sens = TP/(TP+FN) = 64/76 = 84.21%
# Spec = TN/(TN+FP) = 17/20 = 85.00%
# Acc  = (TP+TN)/N = 81/96 = 84.38%
# BA   = (Sens+Spec)/2 = (84.21+85.00)/2 = 84.61%

FIXES = [
    # Sekil 14 altyazisi duzelt
    (
        'TP=63, TN=18, FP=3, FN=12',
        'TP=64, TN=17, FP=3, FN=12'
    ),
    (
        'TP=63, FN=12',
        'TP=64, FN=12'
    ),
    (
        'TN=18, FP=3',
        'TN=17, FP=3'
    ),
    # Sens/Spec formulu duzelt (63/75 → 64/76, 18/21 → 17/20)
    (
        'Sens=63/75',
        'Sens=64/76'
    ),
    (
        'Spec=18/21',
        'Spec=17/20'
    ),
    (
        'Sens=0,840',
        'Sens=0,842'
    ),
    (
        'Spec=0,857',
        'Spec=0,850'
    ),
    # Sekil 14 tam altyazi metni duzelt
    (
        'TP=63, TN=18, FP=3, FN=12 → Sens=0',
        'TP=64, TN=17, FP=3, FN=12 → Sens=0'
    ),
]

print(f'Kaynak: {SRC}')
shutil.copy2(SRC, BAK)
print(f'Yedek: {BAK}')

changes = 0

with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for n in names:
        contents[n] = zin.read(n)

# document.xml uzerinde duzeltme
raw = contents['word/document.xml'].decode('utf-8', errors='replace')
original_raw = raw

for old, new in FIXES:
    if old in raw:
        count = raw.count(old)
        raw = raw.replace(old, new)
        print(f'  ✅ Degistirildi ({count}x): "{old[:60]}" → "{new[:60]}"')
        changes += count
    else:
        print(f'  ℹ️  Bulunamadi (zaten duzeltilmis veya farkli metin): "{old[:60]}"')

if changes > 0:
    contents['word/document.xml'] = raw.encode('utf-8')
    tmp = DST + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, contents[n])
    os.replace(tmp, DST)
    print(f'\n✅ {changes} degisiklik uygulanip kaydedildi: {DST}')
else:
    print('\nℹ️  Hicbir degisiklik yapilmadi (tum degerler zaten dogru veya metin bulunamadi).')

# Ek denetim: Sekil 14 altyazisini dogrula
tree = etree.fromstring(raw.encode('utf-8'))
raw2 = raw
text = re.sub(r'<[^>]+>', ' ', raw2)
text = re.sub(r'\s+', ' ', text)

# Sekil 14 icerigi
s14_match = re.search(r'Şekil\s+14\.(.{0,300})', text)
if s14_match:
    print(f'\n📋 Sekil 14 altyazisi (son durum):')
    print(f'   {s14_match.group(0)[:250]}')

# TP/TN kalip kontrolu
for pattern in ['TP=63', 'TN=18', 'TP=64', 'TN=17']:
    found = [m.start() for m in re.finditer(re.escape(pattern), text)]
    print(f'  "{pattern}" bulundu: {len(found)} yerde')

print('\n=== MAKALE GRAFİK DUZELTME TAMAMLANDI ===')
