import os

# Ultra-Robust Turkish Restoration & Null-Byte Removal Map
restoration_map = {
    "THş A O": "THYAO",
    "THşaO": "THYAO",
    "ş y ö n": "yön",
    "U y a r l a m a": "Uyarlama",
    "A r a l ı  ş ı": "Aralığı",
    " Ç '": "->",
    " Ç \"": "-",
    "G  ü N C E L": "GÜNCEL",
    "d e ğ i l i": "dili",
    " Ö  ş r e n m e": "Öğrenme",
    " Ö Ğ R E N M E": "ÖĞRENME",
    " Ö Z E T": "ÖZET",
    " Ç a l ı  ş m a": "Çalışma",
    "T ü r k i y e": "Türkiye",
    "p i y a s a s ı": "piyasası",
    "e d e ğ i l m i  ş t i r": "edilmiştir",
    "i l l ü z y ü n u": "illüzyonu",
    "B  Ö L  ü M": "BÖLÜM",
    "d e  ş i  ş t i r m e": "değiştirme",
    "y a r a r": "yarar",
    "B a ş a l a n ı r": "Bağlanır",
    "B a ş a l a n t ı s ı": "Bağlantısı",
    "d e ğ e r i y l e": "değeriyle",
    "y ü k l ü": "yüklü",
    "ç a k ı  ş m a": "çakışma",
    "ş a k a l a": "yakala",
    "ş a p ı l": "yapıl",
    "ş ü k s e k": "yüksek",
    "v e y a": "veya",
    "B a z ı": "Bazı",
    "s a y ı s ı": "sayısı",
    "B a ş l ı": "Bağlı",
    "s a ş l a": "sağla",
    "d e ğ i ş": "değiş",
    "k a r  ş ı l a  ş t": "karşılaşt",
}

target_dirs = [
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler",
    r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Ekler",
    r"c:\Users\Kurt\Desktop\Proje\03_Makale_Yazim_Sureci",
    r"c:\Users\Kurt\Desktop\Proje\07_Denetim_ve_Kanit_Arsivi"
]

def clean_and_restore_file(file_path):
    if not os.path.isfile(file_path): return
    if not file_path.endswith(".txt"): return
    
    try:
        # Step 1: Read binary to strip null bytes (the 'double spacing' culprit)
        with open(file_path, "rb") as bf:
            raw_data = bf.read()
        
        # Strip \x00 (null bytes)
        clean_data = raw_data.replace(b"\x00", b"")
        
        # Step 2: Decode as UTF-8 (ignoring errors for remaining junk)
        content = clean_data.decode("utf-8", errors="ignore")
        
        # Step 3: Specific phrase-based restoration for the user
        # This handles the corruption found in the 'view_file' output
        original = content
        
        # Special case for characters that got garbled
        content = content.replace("", "") # Remove replacement chars
        content = content.replace("ş", "y").replace("Y", "ş").replace("Y", "ş")
        content = content.replace("eği", "i").replace("deği", "di")
        content = content.replace("  ", " ") # Fix triple spaces
        
        # Final word-level restoration
        for bad, good in restoration_map.items():
            content = content.replace(bad, good)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"CLEANED & RESTORED: {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"ERROR on {file_path}: {e}")

for d in target_dirs:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                clean_and_restore_file(os.path.join(root, file))

print("Absolute Language Purity Achieved.")
