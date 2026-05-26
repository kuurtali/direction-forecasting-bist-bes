# -*- coding: utf-8 -*-
"""Final doğrulama — tüm değişiklikler"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

# 1. PROJECT_REPORT kontrol
with open(r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\PROJECT_REPORT.txt', encoding='utf-8', errors='replace') as f:
    pr = f.read()

print('=== PROJECT_REPORT.txt KONTROL ===')
checks = {
    'Ghost Feature uyarisi': 'GHOST FEATURE UYARISI' in pr,
    'Grafik esleme tablosu (15.EK)': 'BÖLÜM 15.EK' in pr,
    'AZS dual aday': 'DUAL ADAY' in pr,
    'Bolum 1.5.B MAKALE': '1.5.B' in pr,
    'Ek Operasyonel 5.3.1': '5.3.1' in pr,
    'ARIMA direncli YANLIS notu (PR B-1.4)': 'ARIMA' in pr and ('dirençli' in pr or 'direncli' in pr.lower()),
    'Grafik 01-10 eşleme satırları': '01_Accuracy_Illusion.png' in pr,
}
for k, v in checks.items():
    icon = '✅' if v else '❌'
    print(f'  {icon} {k}')

lines = pr.split('\n')
print(f'\n  Toplam satır: {len(lines)}')

# 2. MAKALE.docx kontrol
print()
print('=== MAKALE.docx KONTROL ===')
doc = Document(r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx')
full_text = ' '.join(p.text for p in doc.paragraphs)

checks2 = {
    '[85] ARIMA uyarı cümlesi eklendi': 'muafiyet sayılamaz' in full_text,
    '[86] "muaf kalırken" KALDIRILDI': 'muaf kalırken' not in full_text,
    '[136] "dirençli kalması" KALDIRILDI': 'dirençli kalması' not in full_text,
    '[136] "stabil... rassal" ifade var': 'rassal tahmin sınırında seyretmenin' in full_text,
}
for k, v in checks2.items():
    icon = '✅' if v else '❌'
    print(f'  {icon} {k}')

print()
print('=== ÖZET ===')
pr_ok = all(checks.values())
mk_ok = all(checks2.values())
print(f'  PROJECT_REPORT: {"✅ TAMAM" if pr_ok else "❌ EKSİK"}')
print(f'  MAKALE.docx:    {"✅ TAMAM" if mk_ok else "❌ EKSİK"}')
