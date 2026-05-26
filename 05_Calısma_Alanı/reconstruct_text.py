import os
import re

def reconstruct_line(line):
    # Rule: Two spaces '  ' -> represent a single actual space ' '
    # Rule: Single space between characters 'P R O J E' -> should be collapsed 'PROJE'
    
    # 1. Protect actual spaces by converting '  ' to a special marker
    protected = line.replace("  ", "___SPACE___")
    
    # 2. Remove single spaces that are likely artifacts
    # (Matches a letter/digit followed by a space followed by a letter/digit)
    collapsed = ""
    i = 0
    while i < len(protected):
        collapsed += protected[i]
        if protected[i] != " " and i + 2 < len(protected) and protected[i+1] == " " and protected[i+2] != " ":
            # This is an artifact space, skip it
            i += 2
        else:
            i += 1
            
    # 3. Restore actual spaces
    final = collapsed.replace("___SPACE___", " ")
    
    # 4. Final Polish - Turkish Character cleanup
    final = final.replace("THyAO", "THYAO")
    final = final.replace("->", "->").replace("-", "-")
    final = final.replace("y ö n", "yön").replace("yyön", "yön")
    final = final.replace("m ü d e l", "model").replace("müdel", "model")
    final = final.replace("piyasası n", "piyasasın")
    final = final.replace("ÖZET", "ÖZET").replace("ÖĞRENME", "ÖĞRENME").replace("ÖYRENME", "ÖĞRENME")
    final = final.replace(" y", "ş").replace(" y", "ş")
    final = final.replace("", "") # Strip remaining artifacts
    
    return final

target_dirs = [
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler",
    r"c:\Users\Kurt\Desktop\Proje\02_Akademik_Ekler",
    r"c:\Users\Kurt\Desktop\Proje\03_Makale_Yazim_Sureci",
    r"c:\Users\Kurt\Desktop\Proje\07_Denetim_ve_Kanit_Arsivi"
]

def process_file(file_path):
    if not os.path.isfile(file_path): return
    if not file_path.endswith(".txt"): return
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        reconstructed = [reconstruct_line(line) for line in lines]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(reconstructed)
        print(f"RECONSTRUCTED: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"ERROR on {file_path}: {e}")

for d in target_dirs:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                process_file(os.path.join(root, file))

print("Reconstructive Restoration Complete.")
