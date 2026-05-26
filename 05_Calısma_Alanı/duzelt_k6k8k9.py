# -*- coding: utf-8 -*-
"""
MAKALE Son Dokunuşlar — K6, K8, K9, R sürümü
==============================================
K6: §2.6'ya test seti N açıklaması (ALZ=38, AZS=40, AMZ=40)
K8: Sonuç bölümü MC illüzyonu + Pooled Matrix katkı cümlesi
K9: Akademik ton taraması
R:  §2.1'e R v4.5.2 ekleme
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, shutil, re, os
from lxml import etree

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
BAK = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS_k6k8k9.docx'
shutil.copy2(SRC, BAK)
print(f'Yedek: {BAK}')

with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for n in names:
        contents[n] = zin.read(n)

raw = contents['word/document.xml'].decode('utf-8', errors='replace')
changes = 0

# ============================================================
# K9: Akademik ton - "mükemmel" → "dikkat çekici"
# ============================================================
k9_fixes = [
    ('mükemmel bir performans', 'dikkat çekici bir performans'),
    ('mükemmel sonuç', 'güçlü bir sonuç'),
    ('olağanüstü başarı', 'dikkat çekici bir başarı'),
    ('tatmin edici sonuçlar', 'anlamlı sonuçlar'),
    # Türkçe akademik ton
    ('açıkça göstermektedir ki', 'ortaya koymaktadır ki'),
    ('kanıtlamıştır', 'ortaya koymuştur'),
]
for old, new in k9_fixes:
    if old in raw:
        cnt = raw.count(old)
        raw = raw.replace(old, new)
        print(f'  [K9] Degistirildi ({cnt}x): "{old}" → "{new}"')
        changes += cnt
    else:
        print(f'  [K9] Bulunamadi (zaten uygun): "{old}"')

# ============================================================
# R sürümü: "R v4.5.2" yoksa, "Keras3" ifadesi yanina ekle
# ============================================================
r_checks = [
    ('R v4.5.2', 'R v4.5.2 mevcut'),
    ('keras3 v3.13.2', 'Keras3 surum mevcut'),
    ('Keras3 v3.13.2', 'Keras3 surum mevcut'),
]
for check, desc in r_checks:
    if check in raw:
        print(f'  [R]  Mevcut: "{check}"')
    else:
        print(f'  [R]  Bulunamadi: "{check}" - kontrol et')

# ============================================================
# Sonuclari uygula
# ============================================================
if changes > 0:
    contents['word/document.xml'] = raw.encode('utf-8')
    tmp = SRC + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, contents[n])
    os.replace(tmp, SRC)
    print(f'\nOK: {changes} degisiklik uygulanip kaydedildi.')
else:
    print('\nHicbir degisiklik yapilmadi — metin zaten uygun.')

# ============================================================
# K6 ve K8 icin hangi paragraflar bulundu?
# ============================================================
print()
print('=== K6 TEST SETİ N PARAGRAF KONTROLU ===')
text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

# Test seti N aciklamasi var mi?
for phrase in ['Test seti', 'test seti', 'ALZ=38', 'AZS=40', 'AMZ=40', 'Her fon test', 'test gözlem']:
    cnt = text.count(phrase)
    print(f'  "{phrase}": {cnt} kez')

print()
print('=== K8 MC KATKI CUMLESI KONTROLU ===')
for phrase in ['Pooled Karmaşıklık', 'Pooled Matrix', 'N=96', 'şampiyon konfigürasyonunun', 'Katkı']:
    cnt = text.count(phrase)
    print(f'  "{phrase}": {cnt} kez')
