import pdfplumber, os, re

# Read example article PDF
pdf_dir = r"c:\Users\Kurt\Desktop\Proje\05_Formatlar_Ve_Ornekler"
pdf_file = None
for f in os.listdir(pdf_dir):
    if f.endswith('.pdf') and 'Yang' in f:
        pdf_file = os.path.join(pdf_dir, f)
        break

if not pdf_file:
    print("PDF bulunamadi!")
    exit()

print(f"ORNEK MAKALE: {os.path.basename(pdf_file)}")
print("="*70)

with pdfplumber.open(pdf_file) as pdf:
    print(f"Sayfa sayisi: {len(pdf.pages)}")
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# Print first 3000 chars to understand structure
print("\nILK 3000 KARAKTER:")
print("-"*70)
print(full_text[:3000])

print("\n\nSON 2000 KARAKTER (Kaynaklar):")
print("-"*70)
print(full_text[-2000:])

# Count structural elements
print("\n\nYAPI ANALIZI:")
print("="*70)

lines = full_text.split('\n')
sections = [l for l in lines if re.match(r'^\d+\.\s+[A-ZÇĞİÖŞÜ]', l)]
print(f"Bolum basliklari: {len(sections)}")
for s in sections:
    print(f"  {s[:80]}")

# Count figures and tables
fig_count = len(re.findall(r'Şekil\s+\d+\.', full_text, re.IGNORECASE))
tbl_count = len(re.findall(r'(Çizelge|Tablo)\s+\d+\.', full_text, re.IGNORECASE))
ref_count = len(re.findall(r'^\[\d+\]', full_text, re.MULTILINE))
words = len(full_text.split())

print(f"\nSekil sayisi: {fig_count}")
print(f"Tablo sayisi: {tbl_count}")
print(f"Referans sayisi: {ref_count}")
print(f"Kelime sayisi: ~{words}")
print(f"Sayfa sayisi: {len(pdf.pages)}")
print(f"Kelime/sayfa: ~{words // len(pdf.pages)}")
