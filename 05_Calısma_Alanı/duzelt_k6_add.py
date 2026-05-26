# -*- coding: utf-8 -*-
"""
K6: Test seti N aciklamasini bul ve dogru yere ekle
=====
PROJECT_REPORT 2.3'e gore:
  ALZ: Egitim 174, Dogrulama 37, Test 38
  AZS: Egitim 182, Dogrulama 39, Test 40
  AMZ: Egitim 183, Dogrulama 39, Test 40
Bu bilgi makalede §2.6 veya veri bolumunde bulunmali.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, shutil, re, os
from lxml import etree

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
BAK = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS_onceki_k6.docx'
shutil.copy2(SRC, BAK)

with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for n in names:
        contents[n] = zin.read(n)

raw = contents['word/document.xml'].decode('utf-8', errors='replace')
text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

# Test seti n bilgisinin nerede eklenmesi gerektigini bul
# "262 hafta" veya "TEFAS" veya "Emeklilik" bölümünü bul
print('=== TEST SETİ AÇIKLAMASI ARAMA ===')
for kw in ['262 hafta', 'haftalık', '%15 test', 'test seti', 'Veri bölme', 'Çalışmada',
           'veri bölünmesi', '70/15', 'Tablo 7', 'Çizelge 7']:
    idx = text.find(kw)
    if idx >= 0:
        print(f'\n  "{kw}" bulundu:')
        ctx = text[max(0, idx-150):idx+300]
        print(f'  ...{ctx}...')
        break

print()
# Test seti satiri var mi kontrol
for phrase in ['ALZ fonuna ait test', 'Test setleri', 'test seti boyutu', 'Test seti n', 'gözlem hafta']:
    cnt = text.count(phrase)
    if cnt:
        print(f'  MEVCUT: "{phrase}": {cnt}x')

# Ekleyecegimiz yer: "Çizelge 7" veya "veri bölünmesi" paragrafinin sonuna
# Alternatif: "%70/%15/%15" sonrasina
for target_kw in ['%70/%15/%15', '70 / 15 / 15', 'Çizelge 7', 'veri bölünmesi', 'bölme oranı']:
    idx = raw.find(target_kw)
    if idx >= 0:
        print(f'\n  HEDEF BULUNAN KW: "{target_kw}" @ {idx}')
        # XML kontekst
        xml_ctx = raw[max(0,idx-200):idx+400]
        print(f'  XML kontekst: ...{xml_ctx[:300]}...')
        break

# K6 aciklamasinin eklenmesi gereken yeri bul:
# "Her fon için %70/%15/%15 kronolojik bölme" veya "Çizelge 7" sonuna
# Eklence cumle: "Test seti gözlem sayıları: ALZ=38, AZS=40, AMZ=40 haftalık gözlemdir."

# Hedef: "Veri bölme" veya "2.1" bölümünde "test seti" sonraki paragraf
fix_k6_old = 'haftalık frekansına uygun olarak kronolojik sıralamayla bölünmüştür'
fix_k6_new = ('haftalık frekansına uygun olarak kronolojik sıralamayla bölünmüştür. '
              'Test seti gözlem sayıları sırasıyla ALZ için 38, AZS için 40 ve AMZ için 40 haftalık gözlemdir '
              '(toplam emeklilik testi N_test = 118 hafta)')

if fix_k6_old in raw:
    raw = raw.replace(fix_k6_old, fix_k6_new, 1)
    print(f'\n  [K6] EKLENDİ: test seti N aciklamasi')
    change = True
else:
    # Alternatif hedef bul
    alts = [
        '70, 15 ve 15',
        'Tablo 7',
        'haftalık gözlem',
        'ALZ (düşük',
    ]
    for alt in alts:
        if alt in raw:
            idx = raw.find(alt)
            print(f'\n  Alternatif hedef bulunan: "{alt}" @ {idx}')
            xml_ctx = raw[max(0,idx-100):idx+200]
            print(f'  ...{xml_ctx[:200]}...')
            break
    change = False
    print('\n  [K6] NOT: Hedef metin bulunamadi. Asagidaki alternatif seçenekleri incele.')

# Kaydet
if change:
    contents['word/document.xml'] = raw.encode('utf-8')
    tmp = SRC + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, contents[n])
    os.replace(tmp, SRC)
    print(f'Kaydedildi: {SRC}')
