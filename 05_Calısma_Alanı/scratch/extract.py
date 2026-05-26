import docx
import os

path = r"C:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\DOC2 Appendix Koleksiyonu.docx"
out = r"C:\Users\Kurt\Desktop\Proje\06_Kodlar\scratch\doc2_dump.md"

def extract(path):
    doc = docx.Document(path)
    res = []
    current_table = None
    for item in doc.element.body:
        if item.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(item, doc)
            res.append(p.text)
        elif item.tag.endswith('tbl'):
            table = docx.table.Table(item, doc)
            res.append("\n--- TABLE START ---")
            for row in table.rows:
                res.append(" | ".join([c.text.replace('\n', ' ') for c in row.cells]))
            res.append("--- TABLE END ---\n")
    return "\n".join(res)

with open(out, 'w', encoding='utf-8') as f:
    f.write(extract(path))
