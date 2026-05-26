import sys

# PROJE_ADIMLAR.txt fix
with open(r'C:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\PROJE_ADIMLAR.txt', 'r', encoding='latin-1') as f:
    lines = f.readlines()

# Restoration and BA fix
# Corrupted lines 2017-2024 (0-indexed 2016-2023)
start_idx = 2016
end_idx = 2023

restored_content = [
    '# - PROJE_RAPOR.txt Bolum 18: "Akademik Tartisma ve Savunma Stratejisi" \n',
    '#   Basaylisi altinda; F1 Illuzsonu, ARIMA Ezberi ve Naive Momentum \n',
    '#   paradoksu uzerine jurise hazir cevaplar eklendegi.\n',
    '# - Balanced Accuracy (Dengeli Dogruluk): Bu oturumda projenin tum \n',
    '#   tablolarina (Section 11, 13, 14) birincil savunma metrigi olarak \n',
    '#   entegre edildi. \n',
    '#   * Ornek: AMZ LSTM %84.86 Gercek Basari Kaniti muhurlendigi.\n',
    '#\n',
    '# SONUC: Ingilizce makale yazimi oncesi tum sayisal, gorsel ve \n',
    '# dokumantasyonel altyapi %100 tamamlanmistir. (Status: ARCHIVE READY)\n',
    '# =============================================================\n'
]

lines[start_idx:end_idx+1] = restored_content

with open(r'C:\Users\Kurt\Desktop\Proje\01_Ana_Raporlar\PROJE_ADIMLAR.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PROJE_ADIMLAR.txt fixed.")
