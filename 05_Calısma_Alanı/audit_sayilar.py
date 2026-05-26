# -*- coding: utf-8 -*-
"""MAKALE sayısal tutarlılık ve şekil açıklama analizi"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import zipfile, re

DST = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE_DUZELTILMIS.docx'
with zipfile.ZipFile(DST, 'r') as z:
    raw = z.read('word/document.xml').decode('utf-8', errors='replace')

text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

print('=== SAYI TUTARLILIK KONTROLU ===')
critical_patterns = {
    '80,21': 'AMZ LSTM Acc',
    '84,38': 'Pooled Acc',
    '78,79': 'AMZ Naive Out=3',
    '75,56': 'AZS CNN Acc',
    '57,56': 'THYAO LSTM Acc',
    '84,86': 'AMZ LSTM BA',
    'N=96': 'Pooled N',
    'p=0,0001': 'AMZ p-value',
    'TP=64': 'Pooled TP (duzeltilmis)',
    'TP=63': 'ESKI TP - YANLIS!',
    'TN=17': 'Pooled TN (duzeltilmis)',
    'TN=18': 'ESKI TN - YANLIS!',
    '82,22': 'VdB LSTM max',
    '66,93': 'VdB LSTM ort',
    '71,92': 'VdB CNN max',
    '67,57': 'VdB ARIMA ort',
    'Spec=0,850': 'Spec duzeltilmis (CSV-rate pooled)',
    'Spec=0,857': 'ESKI Spec - kontrol et',
}

for pattern, desc in critical_patterns.items():
    count = text.count(pattern)
    if count > 0:
        symbol = 'OK' if 'YANLIS' not in desc and 'ESKI' not in desc else 'DIKKAT'
        print(f'  [{symbol}] "{pattern}" ({desc}): {count} kez')
    else:
        if 'YANLIS' in desc or 'ESKI' in desc:
            print(f'  [TEMIZ] "{pattern}" bulunamadi - temizlenmis')

print()
print('=== SEKIL ACIKLAMALARI ===')
sekil_map = {}
for m in re.finditer(r'Sekil\s+(\d+)\.\s+([^S]{0,400})', text):
    no = int(m.group(1)) if m.group(1).isdigit() else -1
    if no > 0 and no not in sekil_map:
        sekil_map[no] = m.group(2)[:120]

# Turkce sekil
for m in re.finditer(r'\u015eekil\s+(\d+)\.\s+(.{0,200})', text):
    try:
        no = int(m.group(1))
    except:
        continue
    if no not in sekil_map:
        sekil_map[no] = m.group(2)[:120]

for no in sorted(sekil_map.keys()):
    print(f'  Sekil {no:2d}: {sekil_map[no][:100]}')
