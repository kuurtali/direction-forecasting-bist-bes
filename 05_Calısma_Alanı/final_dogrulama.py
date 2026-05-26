# -*- coding: utf-8 -*-
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import zipfile,re
from lxml import etree

DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
NSMAP = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DST,'r') as z:
    xml_bytes = z.read('word/document.xml')
tree = etree.fromstring(xml_bytes)
body = tree.find('.//w:body',NSMAP)
raw = re.sub(r'<[^>]+>',' ',xml_bytes.decode('utf-8',errors='replace'))
text = re.sub(r'\s+',' ',raw).strip()

print('=== FINAL DOGRULAMA ===\n')

# K3 tablo degerleri
tests = [
    ('K3 LSTM maks 82,22 VAR',       '82,22',            True),
    ('K3 LSTM maks 78,92 YOK',       '78,92',            False),
    ('K3 LSTM ort 66,93 VAR',        '66,93',            True),
    ('K3 LSTM ort 67,57 Metinden YOK','LSTM ortalamas',  False),
    ('K3 CNN maks 71,92 VAR',        '71,92',            True),
    ('K3 CNN maks 75,14 YOK',        '75,14',            False),
    ('K3 CNN ort 58,24 VAR',         '58,24',            True),
    ('K3 CNN ort 63,42 YOK',         '63,42',            False),
    ('K3 ARIMA ort 67,57 VAR (tablo)','67,57',           True),
    ('K4 McNemar YOK',               'McNemar',          False),
    ('K4 Binom testi VAR',           'Binom testi p',    True),
    ('K5 Sekil 22 YOK',              'ekil 22',          False),
    ('H4 TF surumu VAR',             'TensorFlow v2.21.0',True),
]
ok_count = 0
err_count = 0
for label, token, should_exist in tests:
    exists = token in text
    if exists == should_exist:
        print(f'  [OK] {label}')
        ok_count += 1
    else:
        status = 'MEVCUT AMA OLMAMALI' if exists else 'YOK AMA OLMALI'
        print(f'  [!!] {label} -> {status}')
        err_count += 1

# Pooled CM satiri
tables = body.findall('.//w:tbl',NSMAP)
tbl17 = tables[17]
def ct(c): return ''.join(t.text or '' for t in c.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
for row in tbl17.findall('.//w:tr',NSMAP):
    cells = row.findall('.//w:tc',NSMAP)
    vals  = [ct(c).strip() for c in cells]
    if len(vals)>6 and 'Pooled' in vals[0] and 'AMZ' in vals[0]:
        tp,tn,fp,fn = vals[2],vals[3],vals[4],vals[5]
        acc = vals[6]
        ok_cm = (tp=='64' and tn=='17' and fp=='3' and fn=='12')
        print(f'\n  [CM] Pooled satir: TP={tp} TN={tn} FP={fp} FN={fn} Acc={acc}')
        print(f'  [CM] Dogruluk: {"OK" if ok_cm else "HATA - kontrol et"}')
        if ok_cm: ok_count += 1
        else: err_count += 1

# Ciz 19 son hali
tbl18 = tables[18]
print('\n  [CIZ19] Son durum:')
for row in tbl18.findall('.//w:tr',NSMAP):
    cells = row.findall('.//w:tc',NSMAP)
    vals = [ct(c).strip() for c in cells]
    print(f'    {" | ".join(vals[:3])}')

print(f'\nSONUC: {ok_count} OK, {err_count} SORUN')
