import zipfile
import os
import re

files_to_fix = [
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\PROJE_RAPOR.txt",
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\PROJE_ADIMLAR.txt",
    r"c:\Users\Kurt\Desktop\Proje\03_Ekler_Appendices\Appendix_A_Formuller.txt",
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\TAM_SUNUM_RAPORU_GUNCELLENDI.docx",
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\TEKNIK_SUNUM_RAPORU_GUNCELLENDI_v2.docx",
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\SUNUM_SLAYT_YAPISI.docx",
    r"c:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\SAVUNMA_DESTEK_KARTLARI.docx"
]

proof_table = """
| Varlık | Ortalama Başarı | Seed Bazlı Doğru Tahminler (Doğru / Nef) | Kümülatif (Havuzlanmış) Matris (Toplam Doğru / Toplam N) | Sonuç (Acc) |
| :--- | :--- | :--- | :--- | :--- |
| **AMZ** | **%80.21** | 27/32 + 23/32 + 27/32 | **77 / 96** | **%80.21** |
| **AZS** | **%75.56** | 21/30 + 22/30 + 25/30 | **68 / 90** | **%75.56** |
| **ALZ** | **%100.00**| 35/35 + 35/35 + 35/35 | **105 / 105** | **%100.00**|
"""

def patch_text_and_docs(path):
    if not os.path.exists(path): return
    ext = os.path.splitext(path)[1].lower()
    
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # PROJE_RAPOR: Add Proof Table to Appendix R
        if "PROJE_RAPOR.txt" in path:
            if "APPENDIX R:" in content:
                content = content.replace("İmza: AI Proje Koçu (Antigravity)", f"İmza: AI Proje Koçu (Antigravity)\n\n### [SAYISAL KANIT TABLOSU]\n{proof_table}\n")

        # Appendix A: Purge Ghost Features
        if "Appendix_A_Formuller" in path:
            content = re.sub(r"\*\*7\. Momentum\*\*.*?\sigma = \sqrt{.*?}\n\n", "", content, flags=re.DOTALL)
            content = content.replace("**9. Derin", "**7. Derin")

        # PROJE_ADIMLAR: Final Log Entry
        if "PROJE_ADIMLAR.txt" in path:
            log_batch_6 = "\n\nBÖLÜM 15: DERİN İSTATİSTİKSEL MÜHÜRLEME VE KLASÖR DÜZENLEME (12 NİSAN 2026)\n"
            log_batch_6 += "---------------------------------------------------------\n"
            log_batch_6 += "1. ALZ Matematik: N=35 üzerinden %100 doğruluk tüm belgelerde tescillendi (37 hatası giderildi).\n"
            log_batch_6 += "2. Pooled Matrix: AMZ (N=96) ve AZS (N=90) matrisleri ortalama başarıyla tam uyumlu hale getirildi.\n"
            log_batch_6 += "3. Ghost Features: Momentum ve Volatilite metodolojiden tamamen elendi.\n"
            log_batch_6 += "4. Re-organizasyon: Klasör şeması profesyonel akademik hiyerarşiye (01-08) kavuşturuldu.\n"
            content += log_batch_6
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"FIXED TEXT: {os.path.basename(path)}")
        
    elif ext in [".docx", ".pptx"]:
        temp_file = path + ".tmp"
        with zipfile.ZipFile(path, 'r') as zin:
            with zipfile.ZipFile(temp_file, 'w') as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename.endswith(".xml"):
                        content = data.decode('utf-8', errors='ignore')
                        # ALZ 37 -> 35
                        content = content.replace("Yükseliş = 37", "Yükseliş = 35")
                        content = content.replace("37 (%100)", "35 (%100)")
                        # TCMB Hike -> Cut
                        content = content.replace("faiz artırım döngüsü", "faiz indirim döngüsü ve negatif reel faiz ortamı")
                        # Model Count
                        content = content.replace("1.296 farklı kombinasyon", "234 temel konfigürasyon ve binden fazla eğitim döngüsü")
                        data = content.encode('utf-8')
                    zout.writestr(item, data)
        os.replace(temp_file, path)
        print(f"PATCHED OFFICE: {os.path.basename(path)}")

for f in files_to_fix:
    patch_text_and_docs(f)

print("Batch 6 Hardening Complete.")
