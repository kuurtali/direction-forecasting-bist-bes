from docx import Document
doc = Document(r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx")

fixes = 0
for p in doc.paragraphs:
    orig = p.text
    new = orig
    new = new.replace("göre üstünlüğünü göstermiş", "göre avantajını göstermiş")
    new = new.replace("modellere üstünlüğünü teyit", "modellere avantajını teyit")
    new = new.replace("tahminlerinde üstün olduğunu", "tahminlerinde daha yüksek doğruluk ürettiğini")
    new = new.replace("model üstünlüğünü", "model avantajını")
    new = new.replace("deşifre etmemektedir", "ortaya koymamaktadır")
    new = new.replace("deşifre ederek", "ortaya koyarak")
    new = new.replace("en güçlü Naive", "en belirgin Naive")
    new = new.replace("ekonomik olarak üstün olduğunun", "ekonomik olarak avantajlı olduğunun")
    new = new.replace("metodolojik bir üstünlük", "metodolojik bir avantaj")
    if new != orig:
        if p.runs:
            p.runs[0].text = new
            for r in p.runs[1:]:
                r.text = ""
            fixes += 1
            import difflib
            for i, s in enumerate(difflib.ndiff(orig.split(), new.split())):
                if s.startswith("- "):
                    print(f"  - {s[2:]}", end=" ")
                elif s.startswith("+ "):
                    print(f"+ {s[2:]}")

doc.save(r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx")
print(f"\nToplam {fixes} paragraf duzeltildi.")
