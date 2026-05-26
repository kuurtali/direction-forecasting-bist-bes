import os

# Ultra-safe restoration: Only fixes structure and the most critical proper nouns
safe_word_map = {
    "THyAO": "THYAO",
    "THşaO": "THYAO",
    "B-LoM": "BÖLÜM",
    "ÖZET": "ÖZET",
    "ÖĞRENME": "ÖĞRENME",
    "fiyatşön": "fiyat yön",
    "Senedeği": "Senedi",
    "Uyarlama": "Uyarlama",
    "Türkiye": "Türkiye",
}

target_dirs = [
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler",
    r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Ekler",
    r"c:\Users\Kurt\Desktop\Proje\03_Makale_Yazim_Sureci",
    r"c:\Users\Kurt\Desktop\Proje\07_Denetim_ve_Kanit_Arsivi"
]

def safe_repair(file_path):
    if not os.path.isfile(file_path): return
    if not file_path.endswith(".txt"): return
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # 1. Remove double newlines (the 'gap' issue)
        # We replace \n\n with \n, but carefully
        content = content.replace("\n\n", "\n")
        
        # 2. Apply ONLY safe word fixes
        for bad, good in safe_word_map.items():
            content = content.replace(bad, good)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SAFE REPAIR: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"ERROR: {e}")

for d in target_dirs:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                safe_repair(os.path.join(root, file))

print("Safe Recovery Complete. Formatting restored.")
