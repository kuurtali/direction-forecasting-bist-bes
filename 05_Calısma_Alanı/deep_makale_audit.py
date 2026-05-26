"""
MAKALE.docx Deep Audit Script
Extracts all text, figures, tables, references and cross-checks everything.
"""
import zipfile, re, xml.etree.ElementTree as ET
from collections import Counter, OrderedDict

DOCX = r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx"

def extract_text_from_docx(path):
    """Extract all paragraph text from docx."""
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(path) as z:
        tree = ET.parse(z.open('word/document.xml'))
    root = tree.getroot()
    paragraphs = []
    for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = []
        for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                texts.append(t.text)
        line = ''.join(texts)
        if line.strip():
            paragraphs.append(line.strip())
    return paragraphs

print("Extracting MAKALE.docx text...")
paragraphs = extract_text_from_docx(DOCX)
full_text = '\n'.join(paragraphs)
print(f"  Total paragraphs: {len(paragraphs)}")
print(f"  Total characters: {len(full_text)}")

# ============ 1. FIGURE NUMBERING AUDIT ============
print("\n" + "="*70)
print("1. FIGURE (ŞEKİL) NUMBERING AUDIT")
print("="*70)

# Find all "Şekil X" or "Sekil X" references
fig_pattern = re.compile(r'[Şş][Ee][Kk][İi][Ll]\s+(\d+)', re.IGNORECASE)
fig_refs = []
fig_definitions = []  # Lines that define/caption a figure
fig_body_refs = []    # Lines that reference a figure in body text

for i, p in enumerate(paragraphs):
    matches = fig_pattern.findall(p)
    for m in matches:
        fig_refs.append((int(m), i, p[:120]))
        # Check if this is a caption (starts with "Şekil X." or "Şekil X:")
        if re.match(r'^[Şş][Ee][Kk][İi][Ll]\s+\d+', p):
            fig_definitions.append((int(m), i, p[:120]))
        else:
            fig_body_refs.append((int(m), i, p[:120]))

# Find unique figure numbers defined as captions
defined_figs = sorted(set(n for n, _, _ in fig_definitions))
referenced_figs = sorted(set(n for n, _, _ in fig_body_refs))

print(f"\n  Defined figures (captions): {defined_figs}")
print(f"  Referenced figures (body): {referenced_figs}")

# Check for duplicates
fig_def_counts = Counter(n for n, _, _ in fig_definitions)
for num, count in fig_def_counts.items():
    if count > 1:
        print(f"  *** DUPLICATE CAPTION: Şekil {num} defined {count} times! ***")
        for n, idx, txt in fig_definitions:
            if n == num:
                print(f"      P{idx}: {txt}")

# Check for gaps
if defined_figs:
    expected = list(range(1, max(defined_figs)+1))
    missing = set(expected) - set(defined_figs)
    if missing:
        print(f"  *** MISSING FIGURES: {sorted(missing)} ***")

# Check for figures without body reference
for n in defined_figs:
    if n not in referenced_figs:
        print(f"  *** NO BODY REFERENCE: Şekil {n} has caption but no body text reference ***")
        for fn, fi, ft in fig_definitions:
            if fn == n:
                print(f"      Caption: {ft}")

# ============ 2. TABLE NUMBERING AUDIT ============
print("\n" + "="*70)
print("2. TABLE (ÇİZELGE) NUMBERING AUDIT")
print("="*70)

tbl_pattern = re.compile(r'[Çç][İi][Zz][Ee][Ll][Gg][Ee]\s+(\d+)', re.IGNORECASE)
tbl_definitions = []
tbl_body_refs = []

for i, p in enumerate(paragraphs):
    matches = tbl_pattern.findall(p)
    for m in matches:
        if re.match(r'^[Çç][İi][Zz][Ee][Ll][Gg][Ee]\s+\d+', p):
            tbl_definitions.append((int(m), i, p[:120]))
        else:
            tbl_body_refs.append((int(m), i, p[:120]))

defined_tbls = sorted(set(n for n, _, _ in tbl_definitions))
referenced_tbls = sorted(set(n for n, _, _ in tbl_body_refs))

print(f"\n  Defined tables (captions): {defined_tbls}")
print(f"  Referenced tables (body): {referenced_tbls}")

tbl_def_counts = Counter(n for n, _, _ in tbl_definitions)
for num, count in tbl_def_counts.items():
    if count > 1:
        print(f"  *** DUPLICATE CAPTION: Çizelge {num} defined {count} times! ***")

if defined_tbls:
    expected = list(range(1, max(defined_tbls)+1))
    missing = set(expected) - set(defined_tbls)
    if missing:
        print(f"  *** MISSING TABLES: {sorted(missing)} ***")

for n in defined_tbls:
    if n not in referenced_tbls:
        print(f"  *** NO BODY REFERENCE: Çizelge {n} has caption but no body text reference ***")

# ============ 3. REFERENCE AUDIT ============
print("\n" + "="*70)
print("3. REFERENCE [N] AUDIT")
print("="*70)

ref_pattern = re.compile(r'\[(\d+)\]')
ref_in_text = set()
ref_in_bibliography = set()

# Find bibliography section
bib_start = None
for i, p in enumerate(paragraphs):
    if 'KAYNAKÇA' in p.upper() or 'KAYNAKLAR' in p.upper() or 'REFERENCES' in p.upper():
        bib_start = i
        break

if bib_start:
    # Body text references
    for i, p in enumerate(paragraphs[:bib_start]):
        for m in ref_pattern.findall(p):
            ref_in_text.add(int(m))
    # Bibliography references
    for i, p in enumerate(paragraphs[bib_start:]):
        for m in ref_pattern.findall(p):
            ref_in_bibliography.add(int(m))
    
    print(f"  Bibliography starts at paragraph {bib_start}")
    print(f"  References cited in body: {sorted(ref_in_text)}")
    print(f"  References in bibliography: {sorted(ref_in_bibliography)}")
    
    cited_not_listed = ref_in_text - ref_in_bibliography
    listed_not_cited = ref_in_bibliography - ref_in_text
    
    if cited_not_listed:
        print(f"  *** CITED BUT NOT LISTED: {sorted(cited_not_listed)} ***")
    if listed_not_cited:
        print(f"  *** LISTED BUT NOT CITED: {sorted(listed_not_cited)} ***")
else:
    print("  Could not find bibliography section!")
    for i, p in enumerate(paragraphs):
        for m in ref_pattern.findall(p):
            ref_in_text.add(int(m))
    print(f"  All [N] references found: {sorted(ref_in_text)}")

# ============ 4. KEY NUMERICAL VALUES CHECK ============
print("\n" + "="*70)
print("4. KEY NUMERICAL VALUES IN TEXT")
print("="*70)

key_values = {
    '80,21': 'AMZ LSTM Acc',
    '75,56': 'AZS CNN Acc', 
    '57,56': 'THYAO LSTM Acc',
    '53,97': 'THYAO CNN Acc',
    '55,78': 'THYAO ARIMA best',
    '78,79': 'AMZ Naive Out=3',
    '90,32': 'AZS Naive Out=5',
    '12/36': 'THYAO LSTM MC',
    '9/36': 'THYAO CNN MC',
    '13/27': 'AZS LSTM MC',
    '9/27': 'AZS/AMZ CNN MC',
    '10/27': 'AMZ LSTM MC',
    '27/27': 'ALZ MC',
}

for val, label in key_values.items():
    count = full_text.count(val)
    if count == 0:
        print(f"  *** NOT FOUND: '{val}' ({label}) ***")
    else:
        print(f"  Found '{val}' ({label}): {count} occurrence(s)")

# ============ 5. SECTION STRUCTURE ============
print("\n" + "="*70)
print("5. SECTION STRUCTURE")
print("="*70)

section_pattern = re.compile(r'^(\d+\.[\d.]*)\s+(.+)')
for i, p in enumerate(paragraphs):
    m = section_pattern.match(p)
    if m:
        print(f"  P{i}: {m.group(1)} {m.group(2)[:60]}")

# ============ 6. SPECIFIC ERROR CHECKS ============
print("\n" + "="*70)
print("6. SPECIFIC ERROR CHECKS")
print("="*70)

# Check for encoding artifacts
encoding_errors = []
bad_chars = ['Ã', 'â€"', 'â€™', 'Ã¶', 'Ã¼', 'Ã§', 'ÃƒÂ', 'Â']
for i, p in enumerate(paragraphs):
    for bc in bad_chars:
        if bc in p:
            encoding_errors.append((i, bc, p[:80]))

if encoding_errors:
    print(f"  *** {len(encoding_errors)} ENCODING ARTIFACTS FOUND ***")
    for idx, bc, txt in encoding_errors[:10]:
        print(f"      P{idx}: '{bc}' in: {txt}")
else:
    print("  No encoding artifacts found ✓")

# Check for "Şekil 9" specifically in different contexts
print("\n  --- Şekil 9 context analysis ---")
for i, p in enumerate(paragraphs):
    if re.search(r'[Şş]ekil\s+9\b', p):
        print(f"  P{i}: {p[:120]}")

# Check for orphan stars
print("\n  --- Star (★) usage ---")
for i, p in enumerate(paragraphs):
    if '★' in p:
        print(f"  P{i}: {p[:120]}")

# Check email
print("\n  --- Email check ---")
for i, p in enumerate(paragraphs):
    if '@' in p:
        print(f"  P{i}: {p[:100]}")

print("\n" + "="*70)
print("AUDIT COMPLETE")
print("="*70)
