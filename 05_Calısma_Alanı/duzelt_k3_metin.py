# -*- coding: utf-8 -*-
"""
K3 metin düzeltmesi devam — §4.1 ve §5.4 gövde cümleleri
"""
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import zipfile
from lxml import etree

DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
NSMAP = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DST,'r') as z:
    contents = {n:z.read(n) for n in z.namelist()}

tree = etree.fromstring(contents['word/document.xml'])
CHANGES = []

def replace_all(tree, old, new, desc):
    cnt = 0
    for t in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text and old in t.text:
            t.text = t.text.replace(old, new)
            cnt += 1
    if cnt > 0:
        print(f"  [OK] {desc}: {cnt} yer — '{old}'→'{new}'")
        CHANGES.append(f"{desc} ({cnt}x)")
    else:
        print(f"  [---] {desc}: Bulunamadı '{old}'")
    return cnt

print("=== K3 Metin Gövdesi Düzeltmesi ===\n")

# §4.1'deki yanlış cümle: "LSTM ortalamasını %67,57 ve en yüksek konfigürasyonunu (Out=5, In=4) %78,92"
# Bu zaten K3-a ile değiştirildi (duzelt_makale.py).
# Ama audit_makale.py eski kaynak dosyayı test ediyordu.
# Şimdi DST'deki yeni metni kontrol edelim.

# 1. "Out=5, In=4) %78,92" → ARIMA bağlamında DOĞRU (tablo 18 artık düzeltildi)
#    Ama metin içinde "LSTM" + "78,92" birlikteliği varsa → düzelt
# 2. "AMZ closing (%74,36) ise Van der Burgt CNN en iyisine (%75,14)" 
#    Bu bağlam YANLIŞ değil — karşılaştırma bağlamı.
#    "%75,14" ARIMA Historical'ın değeri ama cümle "CNN en iyisi" diyor → YANLIŞ atıf

# Cümle: "AMZ closing (%74,36) ise Van der Burgt CNN en iyisine (%75,14) çok yakındır"
# DOĞRUSU: Van der Burgt CNN Hist+Tech en iyisi %71,92 (önerilen model).
# Hem 75,14 (ARIMA Historical maks) hem 71,92 (CNN Hist+Tech maks) kullanılabilir.
# MAKALE_YAPILACAKLAR'a göre doğru CNN maks = %71,92

replace_all(tree,
    "Van der Burgt CNN en iyisine (%75,14)",
    "Van der Burgt CNN (hist+tech) en iyisine (%71,92)",
    "K3-CNN-metin-75.14")

# 3. "LSTM ortalamasını %66,93 ve en yüksek konfigürasyonunu (Out=5, In=4) %78,92"
# Bu duzelt_makale.py tarafından değiştirildi. Ancak hâlâ Out=5,In=4 var mı?
# Doğrusu: LSTM Technical en yüksek Out=5,In=2 → %82,22 (zaten değiştirildi)
# Ama In=4 hâlâ metin içinde varsa:
replace_all(tree,
    "Out=5, In=4) %78,92",
    "Out=5, In=2) %82,22",
    "K3-maks-metinde-78.92-In4")

replace_all(tree,
    "Out=5, In=4) %82,22",
    "Out=5, In=2) %82,22",
    "K3-In4→In2 duzeltme")

# 4. Hâlâ kalan 78,92 → bağlamı kontrol et
#    Eğer "ARIMA" + "78,92" → DOĞRU (tezden alınan ARIMA Technical maks)
#    Eğer "LSTM" + "78,92" → YANLIŞ → 82,22 yap
#    Metin içinde tam aramak için:
replace_all(tree,
    "LSTM ortalamasını %66,93 ve en yüksek konfigürasyonunu (Out=5, In=4) %82,22",
    "LSTM Technical konfigürasyonunda ortalama %66,93, en yüksek (Out=5, In=2) %82,22",
    "K3-LSTM-metin-In4-cleanup")

# 5. 55,78 (eski ARIMA ort) artık tablo içinde 67,57 oldu
#    Metinde hâlâ "ARIMA ortalama %55,78" varsa → hem burası hem §5.4 VdB bağlamında yanlış
#    Not: 55,78 THYAO ARIMA (biz) değil, VdB ARIMA'yı göstermesi gerekiyor
#    §5.4 kıyaslama cümlelerinde kontrol:
replace_all(tree,
    "Van der Burgt ARIMA ortalamasını %55,78",
    "Van der Burgt ARIMA Technical ortalamasını %67,57",
    "K3-ARIMA-metin-55.78")

replace_all(tree,
    "ARIMA ortalama %55,78 |",
    "ARIMA ortalama %67,57 |",
    "K3-ARIMA-tablo-55.78")

# Kaydet
new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
contents['word/document.xml'] = new_xml
with zipfile.ZipFile(DST,'w',zipfile.ZIP_DEFLATED) as z:
    for name, data in contents.items():
        z.writestr(name, data)

print(f"\n✅ Kaydedildi: {DST}")
print(f"Toplam {len(CHANGES)} değişiklik:")
for c in CHANGES: print(f"  • {c}")
