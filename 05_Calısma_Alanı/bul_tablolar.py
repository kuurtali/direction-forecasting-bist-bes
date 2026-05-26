# -*- coding: utf-8 -*-
"""
K3 Çizelge 19 tablo hücreleri + K1+K2 Spec/Sens bulma
Tabloları tara, 63,42 / 55,78 / diğer yanlış değerleri bul
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, re
from lxml import etree

# Düzeltilmiş dosya üzerinde çalış
DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DST, 'r') as z:
    xml_bytes = z.read('word/document.xml')
    all_names = z.namelist()

tree = etree.fromstring(xml_bytes)
body = tree.find('.//w:body', NSMAP)

def cell_text(cell):
    return ''.join(t.text or '' for t in cell.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))

print("="*70)
print("Çizelge 19 içeriği — VAN DER BURGT tablosu")
print("="*70)

tables = body.findall('.//w:tbl', NSMAP)
print(f"Toplam tablo sayısı: {len(tables)}")

# Çizelge 19'u bul: VdB sayılarını içeren tablo
# 67,57 veya 66,93 veya 63,42 içeren tablo
target_tokens = ['63,42', '66,93', '67,57', '58,24', '82,22', '78,92']

for tbl_idx, tbl in enumerate(tables):
    rows = tbl.findall('.//w:tr', NSMAP)
    tbl_text = ''.join(cell_text(c) for r in rows for c in r.findall('.//w:tc', NSMAP))
    if any(tok in tbl_text for tok in target_tokens):
        print(f"\n[TABLO {tbl_idx}] VdB değerleri içeren tablo bulundu!")
        for row_i, row in enumerate(rows):
            cells = row.findall('.//w:tc', NSMAP)
            row_texts = [cell_text(c).strip() for c in cells]
            print(f"  Satır {row_i}: {' | '.join(row_texts)}")

print()
print("="*70)
print("Çizelge 8 ve 18 — Sens/Spec değerleri")
print("="*70)
# Sens %84,0 veya Spec %85,7 içeren tablolar
sens_spec_tokens = ['84,0', '85,7', '84,00', '85,71', '0,857', '0,840']

for tbl_idx, tbl in enumerate(tables):
    rows = tbl.findall('.//w:tr', NSMAP)
    tbl_text = ''.join(cell_text(c) for r in rows for c in r.findall('.//w:tc', NSMAP))
    if any(tok in tbl_text for tok in sens_spec_tokens):
        print(f"\n[TABLO {tbl_idx}] Sens/Spec değerleri içeren tablo:")
        for row_i, row in enumerate(rows):
            cells = row.findall('.//w:tc', NSMAP)
            row_texts = [cell_text(c).strip() for c in cells]
            row_joined = ' | '.join(row_texts)
            if any(tok in row_joined for tok in sens_spec_tokens + ['AMZ','AZS','80,21','75,56']):
                print(f"  Satır {row_i}: {row_joined}")

print()
print("="*70)
print("Pooled CM sayıları (TP=64, FN=12, FP=3, TN=17)")
print("="*70)
cm_tokens = ['TP', 'TN', 'FP', 'FN', 'N=96', 'havuzlanmış', 'Havuzlanmış']
for tbl_idx, tbl in enumerate(tables):
    rows = tbl.findall('.//w:tr', NSMAP)
    tbl_text = ''.join(cell_text(c) for r in rows for c in r.findall('.//w:tc', NSMAP))
    if any(tok in tbl_text for tok in cm_tokens):
        print(f"\n[TABLO {tbl_idx}] Pooled CM tablosu:")
        for row_i, row in enumerate(rows):
            cells = row.findall('.//w:tc', NSMAP)
            row_texts = [cell_text(c).strip() for c in cells]
            row_joined = ' | '.join(row_texts)
            if any(tok in row_joined for tok in ['64','17','12','TP','TN','FP','FN','N=96','80,21','84,38']):
                print(f"  Satır {row_i}: {row_joined}")
