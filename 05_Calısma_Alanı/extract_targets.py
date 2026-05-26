"""Extract exact target paragraphs for surgical fixes."""
import zipfile, xml.etree.ElementTree as ET, re

DOCX = r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx"
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DOCX) as z:
    tree = ET.parse(z.open('word/document.xml'))
root = tree.getroot()

paragraphs = []
for p in root.iter(f'{{{ns["w"]}}}p'):
    texts = []
    for t in p.iter(f'{{{ns["w"]}}}t'):
        if t.text:
            texts.append(t.text)
    line = ''.join(texts).strip()
    if line:
        paragraphs.append(line)

# Show specific target paragraphs
targets = {
    'Sekil 9 context': [],
    'Sekil 11 context': [],
    'Sekil 22/23 context': [],
    'Cizelge 16 context': [],
    'Cizelge 19 context': [],
    'Cizelge 20 context': [],
    'Cizelge 7 context': [],
    'Email': [],
    'Anahtar': [],
}

for i, p in enumerate(paragraphs):
    if re.search(r'[Şş]ekil\s+9\b', p):
        targets['Sekil 9 context'].append((i, p))
    if re.search(r'[Şş]ekil\s+11\b', p):
        targets['Sekil 11 context'].append((i, p))
    if re.search(r'[Şş]ekil\s+2[23]\b', p):
        targets['Sekil 22/23 context'].append((i, p))
    if re.search(r'[Çç]izelge\s+16\b', p):
        targets['Cizelge 16 context'].append((i, p))
    if re.search(r'[Çç]izelge\s+19\b', p):
        targets['Cizelge 19 context'].append((i, p))
    if re.search(r'[Çç]izelge\s+20\b', p):
        targets['Cizelge 20 context'].append((i, p))
    if re.search(r'[Çç]izelge\s+7\b', p):
        targets['Cizelge 7 context'].append((i, p))
    if '@' in p:
        targets['Email'].append((i, p))
    if 'nahtar' in p.lower():
        targets['Anahtar'].append((i, p))

for category, items in targets.items():
    print(f"\n{'='*70}")
    print(f"  {category}")
    print(f"{'='*70}")
    for idx, text in items:
        print(f"  P{idx}: {text[:200]}")
        print()

# Also show §4.9 area (P717-P722)
print(f"\n{'='*70}")
print("  §4.9 AREA (P715-P725)")
print(f"{'='*70}")
for i in range(715, min(726, len(paragraphs))):
    print(f"  P{i}: {paragraphs[i][:200]}")
    print()

# Show around P329-P332
print(f"\n{'='*70}")
print("  §4.2 AREA (P327-P335)")  
print(f"{'='*70}")
for i in range(327, min(336, len(paragraphs))):
    print(f"  P{i}: {paragraphs[i][:200]}")
    print()

# Show around P363-P370
print(f"\n{'='*70}")
print("  §4.3 Sekil 11 AREA (P363-P370)")
print(f"{'='*70}")
for i in range(363, min(371, len(paragraphs))):
    print(f"  P{i}: {paragraphs[i][:200]}")
    print()
