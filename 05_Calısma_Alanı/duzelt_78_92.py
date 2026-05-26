# -*- coding: utf-8 -*-
"""
78,92 — paragraf seviyesinde bul ve düzelt
DOCX'te bir "78,92" bir paragrafın birden fazla run'una yayılmış olabilir.
"""
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import zipfile,re
from lxml import etree

DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
NSMAP = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DST,'r') as z:
    contents = {n:z.read(n) for n in z.namelist()}

tree = etree.fromstring(contents['word/document.xml'])
body = tree.find('.//w:body', NSMAP)

def para_text(para):
    return ''.join(t.text or '' for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))

# Parag seviyesinde ara
CHANGES = []
for para in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    pt = para_text(para)
    if '78,92' in pt and ('LSTM' in pt or 'rapor' in pt):
        print(f"\n[PARA] {pt[:200]}")
        # Bu paragrafta yanlış LSTM atfı var mı?
        if 'LSTM raporuna' in pt and '78,92' in pt:
            # Run'ları tek tek değiştir
            for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    if 'LSTM raporuna' in t.text:
                        old = t.text
                        t.text = t.text.replace(
                            'en yüksek LSTM raporuna (%78,92)',
                            'ARIMA Technical en yüksek değerine (%78,92)'
                        )
                        if t.text != old:
                            print(f"  [DEG] '{old[:80]}'→'{t.text[:80]}'")
                            CHANGES.append('K3-LSTM-rapor-78.92')
                    elif '78,92' in t.text:
                        print(f"  [RUN-78.92] '{t.text}'")
        elif '78,92' in pt:
            print(f"  [INFO] 78,92 başka bağlamda — dokunma")

# Kaydet
if CHANGES:
    new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    contents['word/document.xml'] = new_xml
    with zipfile.ZipFile(DST,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in contents.items(): z.writestr(name,data)
    print(f"\n✅ Kaydedildi: {len(CHANGES)} değişiklik")
else:
    print("\n[INFO] Değişiklik yapılmadı — 78,92 mevcut bağlamda kabul edildi")
    print("NOT: Bu değer artık ARIMA Technical maks olarak açıklanmalı")
    print("      Metin: '...Van der Burgt şampiyon konfigürasyonunun (%80,21) Van der Burgt'un en yüksek LSTM raporuna (%78,92)'")
    print("      Bu cümle hâlâ yanlış atıf içeriyor ama run'lara bölünmüş.")
    
    # Ham replace ile dene
    xml_str = contents['word/document.xml'].decode('utf-8', errors='replace')
    old_str = 'yüksek LSTM raporuna (%78,92)'
    new_str = 'ARIMA Technical en yüksek değerine (%78,92)'
    if old_str in xml_str:
        xml_str2 = xml_str.replace(old_str, new_str)
        contents['word/document.xml'] = xml_str2.encode('utf-8')
        with zipfile.ZipFile(DST,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in contents.items(): z.writestr(name,data)
        print(f"\n✅ Ham string replace ile kaydedildi!")
        CHANGES.append('ham-replace')
    else:
        print(f"\n[YOK] '{old_str}' ham XML'de de bulunamadı — parçalı run")
        print("Bu değer için MAKALE'yi Word'de manuel olarak düzeltmeniz gerekiyor:")
        print("  Bul: 'en yüksek LSTM raporuna (%78,92)'")
        print("  Yaz: 'ARIMA Technical en yüksek değerine (%78,92)'")
