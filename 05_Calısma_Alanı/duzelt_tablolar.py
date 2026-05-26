# -*- coding: utf-8 -*-
"""
K1, K2, K3 tablo hücre düzeltmeleri
Tablo 17 (Pooled CM): TP=63→64, TN=18→17
Tablo 18 (Çizelge 19 VdB): 5 satır yanlış değer düzelt
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, shutil, copy
from lxml import etree

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'

NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(SRC, 'r') as z:
    contents = {name: z.read(name) for name in z.namelist()}

xml_bytes = contents['word/document.xml']
tree = etree.fromstring(xml_bytes)
body = tree.find('.//w:body', NSMAP)
tables = body.findall('.//w:tbl', NSMAP)

CHANGES = []

def cell_text(cell):
    return ''.join(t.text or '' for t in cell.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))

def set_cell_text(cell, new_text):
    """Bir hücredeki tüm metni değiştir"""
    # İlk w:t'yi bul, metnini yaz, diğerlerini temizle
    ts = list(cell.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
    if ts:
        ts[0].text = new_text
        for t in ts[1:]:
            t.text = ''

def replace_cell_exact(cell, old_val, new_val, desc):
    ct = cell_text(cell).strip()
    if ct == old_val:
        set_cell_text(cell, new_val)
        print(f"  [OK] {desc}: '{old_val}' → '{new_val}'")
        CHANGES.append(f"{desc}: '{old_val}'→'{new_val}'")
        return True
    return False

def replace_in_cell_partial(cell, old_val, new_val, desc):
    """Hücre metninin içinde kısmi değiştirme"""
    for t in cell.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text and old_val in t.text:
            t.text = t.text.replace(old_val, new_val)
            print(f"  [OK] {desc}: '{old_val}'→'{new_val}'")
            CHANGES.append(f"{desc}: '{old_val}'→'{new_val}'")
            return True
    return False

# ═══════════════════════════════════════════════════════════════════════════════
# K1+K2: TABLO 17 (Pooled CM) — TP=63→64, TN=18→17
# ═══════════════════════════════════════════════════════════════════════════════
print("="*60)
print("K1+K2: Tablo 17 Pooled CM TP/TN düzeltmesi")
print("="*60)
# Satır 5: AMZ LSTM Pooled Aritmetik | 96 | 63 | 18 | 3 | 12 | %84,38
# CSV: TP=64, TN=17, FP=3, FN=12 (doğru)
tbl17 = tables[17]  # 0-indexed
rows = tbl17.findall('.//w:tr', NSMAP)
for row_i, row in enumerate(rows):
    cells = row.findall('.//w:tc', NSMAP)
    row_text = [cell_text(c).strip() for c in cells]
    row_joined = '|'.join(row_text)
    
    # Pooled satırını bul (AMZ LSTM Pooled Aritmetik)
    if 'Pooled' in row_joined and 'AMZ' in row_joined:
        print(f"\n  Pooled satırı bulundu (row {row_i}): {row_joined}")
        # Hücreler: 0=Konfigürasyon, 1=N, 2=TP, 3=TN, 4=FP, 5=FN, 6=Acc, 7=Sens, 8=Spec
        if len(cells) >= 6:
            # TP hücresi (index 2)
            replace_cell_exact(cells[2], '63', '64', 'K1-TP')
            # TN hücresi (index 3)
            replace_cell_exact(cells[3], '18', '17', 'K1-TN')
            # FP ve FN kontrol (doğru olmalı: FP=3, FN=12)
            tp_val = cell_text(cells[2]).strip()
            tn_val = cell_text(cells[3]).strip()
            fp_val = cell_text(cells[4]).strip() if len(cells) > 4 else '?'
            fn_val = cell_text(cells[5]).strip() if len(cells) > 5 else '?'
            print(f"  Düzeltme sonrası: TP={tp_val}, TN={tn_val}, FP={fp_val}, FN={fn_val}")
            # Acc kontrolü: (64+17)/96 = 84.375 → %84,38 (hücrede %84,38 varsa doğru)
            acc_val = cell_text(cells[6]).strip() if len(cells) > 6 else '?'
            print(f"  Acc={acc_val} (beklenen %84,38) — {'OK' if '84,38' in acc_val else 'KONTROL ET'}")

# ═══════════════════════════════════════════════════════════════════════════════
# K3: TABLO 18 (Çizelge 19) — Van der Burgt yanlış değerler
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("="*60)
print("K3: Tablo 18 (Çizelge 19) VdB değerleri")
print("="*60)
# Mevcut tablo:
# Satır 1: LSTM en yüksek  | %78,92 (Out=5, In=4)        | AMZ LSTM...%80,21
# Satır 2: LSTM ortalama   | %67,57                       | THYAO LSTM...%57,56
# Satır 3: CNN en yüksek   | %75,14 (Out=5, In=4)         | AMZ CNN...%74,36
# Satır 4: CNN ortalama    | %63,42                       | THYAO CNN...%53,97
# Satır 5: ARIMA ortalama  | %55,78                       | THYAO ARIMA...%51,34
#
# DOĞRU (MAKALE_YAPILACAKLAR'a göre VdB tezi):
# Satır 1: LSTM en yüksek (Technical)  | %82,22 (Out=5, In=2)  | ...
# Satır 2: LSTM ortalama (Technical)   | %66,93               | ...
# Satır 3: CNN en yüksek (Hist+Tech)   | %71,92 (Out=5, In=4) | ...
# Satır 4: CNN ortalama (Hist+Tech)    | %58,24               | ...
# Satır 5: ARIMA ortalama (Technical)  | %67,57               | ... (bu satır model=ARIMA, değer doğru)

tbl18 = tables[18]
rows18 = tbl18.findall('.//w:tr', NSMAP)
for row_i, row in enumerate(rows18):
    cells = row.findall('.//w:tc', NSMAP)
    row_text = [cell_text(c).strip() for c in cells]
    print(f"\n  Satır {row_i}: {' | '.join(row_text)}")
    
    if len(cells) < 2:
        continue

    label = cell_text(cells[0]).strip()
    vdb_cell = cells[1] if len(cells) > 1 else None
    
    if vdb_cell is None:
        continue
    
    vdb_val = cell_text(vdb_cell).strip()
    
    # Satır 1: LSTM en yüksek → düzelt
    if 'LSTM en yüksek' in label:
        if '78,92' in vdb_val or '78.92' in vdb_val:
            replace_in_cell_partial(vdb_cell, '%78,92 (Out=5, In=4)', '%82,22 (Out=5, In=2)', 'K3-LSTM-maks')
            replace_in_cell_partial(vdb_cell, '78,92', '82,22', 'K3-LSTM-maks-78.92')
            replace_in_cell_partial(vdb_cell, 'In=4)', 'In=2)', 'K3-LSTM-maks-In4→2')
    
    # Satır 2: LSTM ortalama → zaten K3-a metinden değişti (67,57→66,93 metin içinde)
    # Ama tablo hücresinde ayrıca var mı?
    if 'LSTM ortalama' in label:
        replace_in_cell_partial(vdb_cell, '%67,57', '%66,93', 'K3-LSTM-ort')
        replace_in_cell_partial(vdb_cell, '67,57', '66,93', 'K3-LSTM-ort-raw')
    
    # Satır 3: CNN en yüksek → 75,14 → 71,92; In=4 → In=4 (In=4 doğru aslında)
    if 'CNN en yüksek' in label:
        replace_in_cell_partial(vdb_cell, '%75,14', '%71,92', 'K3-CNN-maks')
        replace_in_cell_partial(vdb_cell, '75,14', '71,92', 'K3-CNN-maks-raw')
    
    # Satır 4: CNN ortalama → 63,42 → 58,24
    if 'CNN ortalama' in label:
        replace_in_cell_partial(vdb_cell, '%63,42', '%58,24', 'K3-CNN-ort')
        replace_in_cell_partial(vdb_cell, '63,42', '58,24', 'K3-CNN-ort-raw')
    
    # Satır 5: ARIMA ortalama → 55,78 → 67,57 (aslında ARIMA Technical'ın ortalaması)
    if 'ARIMA ortalama' in label:
        replace_in_cell_partial(vdb_cell, '%55,78', '%67,57', 'K3-ARIMA-ort')
        replace_in_cell_partial(vdb_cell, '55,78', '67,57', 'K3-ARIMA-ort-raw')

# ═══════════════════════════════════════════════════════════════════════════════
# Doğrulama: düzeltilmiş tablo 18 çıktısı
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("="*60)
print("Düzeltme sonrası Tablo 18 (Çizelge 19):")
print("="*60)
rows18_after = tbl18.findall('.//w:tr', NSMAP)
for row_i, row in enumerate(rows18_after):
    cells = row.findall('.//w:tc', NSMAP)
    row_text = [cell_text(c).strip() for c in cells]
    print(f"  Satır {row_i}: {' | '.join(row_text)}")

# ═══════════════════════════════════════════════════════════════════════════════
# Kaydet
# ═══════════════════════════════════════════════════════════════════════════════
new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
contents['word/document.xml'] = new_xml
with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in contents.items():
        zout.writestr(name, data)

print(f"\n✅ Kaydedildi: {DST}")
print(f"\nToplam değişiklik: {len(CHANGES)}")
for c in CHANGES:
    print(f"  • {c}")
