import os
import re

# Restoration Map for the specific corrupted encoding found in the project
restoration_map = {
    "THşaO": "THYAO",
    "Uşarlama": "Uyarlama",
    "Aralışı": "Aralığı",
    "GoNCEL": "GÜNCEL",
    "değili": "dili",
    "-Yrenme": "Öğrenme",
    "-ĞRENME": "ÖĞRENME",
    "-ZET": "ÖZET",
    "?alışma": "Çalışma",
    "Türkişe": "Türkiye",
    "pişasası": "piyasası",
    "edeğilmiYtir": "edilmiştir",
    "edeğilmiYtir": "edilmiştir",
    "illüzşonu": "illüzyonu",
    "B-LoM": "BÖLÜM",
    "değiYtirme": "değiştirme",
    "deşiYtirme": "değiştirme",
    "şarar": "yarar",
    "BaşaYlanır": "Bağlanır",
    "BaşaYlanır": "Bağlanır",
    "BaşaYlantısı": "Bağlantısı",
    "BaşaYlantısı": "Bağlantısı",
    "deşeriyle": "değeriyle",
    "şüklü": "yüklü",
    "çakıYma": "çakışma",
    "şans": "şans",
    "BaşaYlangıç": "Başlangıç",
    "BaşaYlangıç": "Başlangıç",
    "Yöyle": "şöyle",
    "iYlemi": "işlemi",
    "iYlev": "işlev",
    "iYlet": "işlet",
    "iYlem": "işlem",
    "karşılaştır": "karşılaştır",
    "şekilde": "şekilde",
    "şirket": "şirket",
    "düşüY": "düşüş",
    "şükseliY": "yükseliş",
    "düşüY": "düşüş",
    "şükseliY": "yükseliş",
    "Başaşarı": "Başarı",
    "Başaşarı": "Başarı",
    "şeter": "yeter",
    "şatırım": "yatırım",
    "öre": "göre",
    "öster": "göster",
    "ön": "yön",
    "özlem": "gözlem",
    "üç": "güç",
    "üven": "güven",
    "o": "ü",
    "-": "Ö",
    "?": "Ç",
    "Y": "ş",
    "ş": "ş",
    "": " ", # Fallback for unknown
    "şa": "ya",
    "şu": "yu",
    "şo": "yo",
    "şe": "ye",
    "şı": "yı",
    "eği": "i",
    "deği": "di",
    "RStudeğio": "RStudio",
    "indeğir": "indir",
}

# More patterns found in logs
restoration_map.update({
    "şap": "yap",
    "şol": "yol",
    "şüksek": "yüksek",
    "veşa": "veya",
    "Başazı": "Bazı",
    "saşısı": "sayısı",
    "BaşaYlı": "Bağlı",
    "saYla": "sağla",
    "deşiY": "değiş",
    "karşılaYt": "karşılaşt",
})

target_dirs = [
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler",
    r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Ekler",
    r"c:\Users\Kurt\Desktop\Proje\03_Makale_Yazim_Sureci",
    r"c:\Users\Kurt\Desktop\Proje\07_Denetim_ve_Kanit_Arsivi"
]

def restore_file(file_path):
    if not os.path.isfile(file_path): return
    if not file_path.endswith(".txt"): return
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        original = content
        for bad, good in restoration_map.items():
            content = content.replace(bad, good)
            
        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"RESTORED: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"ERROR on {file_path}: {e}")

for d in target_dirs:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                restore_file(os.path.join(root, file))

print("Turkish Language Restoration Complete.")
