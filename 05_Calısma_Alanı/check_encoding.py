import chardet
import os

files = [
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJE_RAPOR.txt",
    r"c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJE_ADIMLAR.txt"
]

for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as raw:
            data = raw.read(1000)
            result = chardet.detect(data)
            print(f"{os.path.basename(f)}: {result}")
