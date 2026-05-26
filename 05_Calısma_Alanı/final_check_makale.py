# -*- coding: utf-8 -*-
import zipfile, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx'
with zipfile.ZipFile(SRC,'r') as z:
    raw = z.read('word/document.xml').decode('utf-8', errors='replace')
text = re.sub(r'<[^>]+>', ' ', raw)
text = re.sub(r'\s+', ' ', text)

checks = {
    'TP=64': ('OK', 'Pooled TP duzeltilmis'),
    'TN=17': ('OK', 'Pooled TN duzeltilmis'),
    'TP=63': ('BAD', 'ESKI - OLMAMALI'),
    'TN=18': ('BAD', 'ESKI - OLMAMALI'),
    'Spec=0,850': ('OK', 'Spec duzeltilmis'),
    'Spec=0,857': ('BAD', 'ESKI - OLMAMALI'),
    'R v4.5.2': ('OK', 'R surumu eklenmis'),
    'matematiksel tutarlilik': ('OK', 'K8 katkı cümlesi'),
    '80,21': ('OK', 'AMZ Acc'),
    '84,38': ('OK', 'Pooled Acc'),
    '78,79': ('OK', 'Naive baseline'),
    'p=0,0001': ('OK', 'p-deger'),
    'N=96': ('OK', 'Pooled N'),
}
print('=== MAKALE.docx FINAL KONTROL ===')
errors = []
for k, (kind, desc) in checks.items():
    cnt = text.count(k)
    if kind == 'BAD':
        sym = 'HATA!' if cnt > 0 else 'TEMIZ'
        if cnt > 0:
            errors.append(k)
    else:
        sym = 'OK' if cnt > 0 else 'EKSIK'
        if cnt == 0:
            errors.append(k)
    print(f'  [{sym}] "{k}" ({desc}): {cnt}x')

print()
size_kb = os.path.getsize(SRC) / 1024
if errors:
    print(f'SORUNLU: {errors}')
else:
    print(f'>>> MAKALE.docx temiz ve hazir. Boyut: {size_kb:.1f} KB <<<')
