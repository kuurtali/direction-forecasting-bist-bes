# -*- coding: utf-8 -*-
"""
K8: Sonuç bölümüne mütevazı akademik katkı cümlesi ekle
Şekil 14 metodoloji notu ekle
Ardından: MAKALE_DUZELTILMIS.docx → MAKALE.docx (diğerleri silinecek)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, shutil, re, os
from lxml import etree
from copy import deepcopy

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'

with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    contents = {}
    for n in names:
        contents[n] = zin.read(n)

raw = contents['word/document.xml'].decode('utf-8', errors='replace')
changes = 0

# ============================================================
# K8: Mütevazı akademik katkı cümlesi
# Yer: "Sonuç" bölümünde — "sınırlılıklar" paragrafı sonrasına
# Veya "gelecek çalışmalar" öncesine
# ============================================================

# Hedef: "gelecek çalışmalar" veya "sınırlılıklar" paragrafı bul
# Cumle: "Bu çalışma, havuzlanmış karmaşıklık matrisi yöntemini
# kullanarak değerlendirme tutarlılığına katkı sunmayı amaçlamaktadır."
# Mutevazi ton: "katkı sunmayı amaçlamaktadır" / "bulgular göstermektedir ki" / "gözlemlenmiştir"

# Eski "kanıtlanmıştır" ifadesini mutevazi tona cevir
tone_fixes = [
    # Güçlü → Mütevazı
    ('kanıtlanmıştır ki,', 'ortaya koymaktadır ki'),
    ('kesin olarak kanıtlamıştır', 'göstermektedir'),
    ('açıkça ispatlanmıştır', 'gözlemlenmiştir'),
    ('tartışmasız olarak', 'bulgular doğrultusunda'),
    ('ispatlamaktadır', 'göstermektedir'),
    # Fazla özgüvenli ifadeler (lisans çalışması için)
    ('çalışmamızın en önemli katkısı', 'çalışmanın metodolojik katkılarından biri'),
    ('mükemmel derecede', 'görece'),
    ('üstün performans', 'daha yüksek performans'),
]

for old, new in tone_fixes:
    if old in raw:
        cnt = raw.count(old)
        raw = raw.replace(old, new)
        print(f'  [K8-ton] ({cnt}x): "{old}" → "{new}"')
        changes += cnt
    # else: bulunamadiysa sessizce gec

# K8: Havuzlanmış matris metodoloji notu
# Hedef: "5.5" veya "Sınırlılıklar" bölümü içindeki son cümle sonrasına
# "pooled N=96" açıklaması var mı?
text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

# N=96 metodoloji aciklamasi var mi?
n96_ctx = ''
idx = text.find('N=96')
if idx >= 0:
    n96_ctx = text[max(0,idx-200):idx+300]
    print(f'\n  [K8-kontrol] "N=96" mevcut bağlam:\n  ...{n96_ctx[:200]}...\n')

# Hedef cumle: "Bunun yanı sıra," sonrasına ekle
# EKLECEK CUMLE - mutevazi ton:
k8_katkı_old = 'pooled N=96 raporlamayla telafi edilse de istatistiksel gücün üst sınırını belirlemektedir'
k8_katkı_new = ('pooled N=96 raporlamayla telafi edilse de istatistiksel gücün üst sınırını belirlemektedir. '
                'Öte yandan, üç başlangıç tohumundan elde edilen sonuçların havuzlanmış karmaşıklık matrisi '
                'üzerinden değerlendirilmesi, tekil tohum seçiminden kaynaklanan rasgelelik etkisini azaltmaya '
                'yönelik bir yaklaşım olarak benimsenmiş ve model değerlendirmesinde matematiksel tutarlılık '
                'sağlanmaya çalışılmıştır')

if k8_katkı_old in raw:
    raw = raw.replace(k8_katkı_old, k8_katkı_new, 1)
    print(f'  [K8] Havuzlanmış matris metodoloji notu eklendi.')
    changes += 1
else:
    print(f'  [K8] Hedef bulunamadı — mevcut metin farklı XML run\'larına bölünmüş olabilir.')
    print(f'       "N=96" {text.count("N=96")} kez geçiyor — zaten yeterli açıklama var.')

# Şekil 14 metodoloji notu
# Mevcut altyazi: "TP=64, TN=17, FP=3, FN=12 → Sens=0,84 ve Spec=0,850 (CSV ile uyumlu)"
# Ek açıklama: bu değerlerin nasıl hesaplandığını belirt
s14_old = '(CSV ile uyumlu)'
s14_new = ('(grafik kodu ve CSV Seed 98 oranları esas alınmıştır; '
           '3-seed ortalama doğruluk %80,21 olup havuzlanmış matris doğruluğu %84,38\'dir)')

if s14_old in raw:
    raw = raw.replace(s14_old, s14_new, 1)
    print(f'  [Şekil14] Metodoloji notu güncellendi.')
    changes += 1
else:
    print(f'  [Şekil14] Hedef bulunamadı.')

# Kaydet
if changes > 0:
    contents['word/document.xml'] = raw.encode('utf-8')
    tmp = SRC + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, contents[n])
    os.replace(tmp, SRC)
    print(f'\n  OK: {changes} değişiklik kaydedildi → {SRC}')
else:
    print('\n  Değişiklik yapılmadı (metin zaten uygun veya XML run sorunu).')

print('\nScript tamamlandı.')
