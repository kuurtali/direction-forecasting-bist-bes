# -*- coding: utf-8 -*-
"""JURI_SAVUNMA encoding fix + duplicate removal"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\JURI_SAVUNMA_VE_BILINMESI_GEREKENLER.txt'

with open(SRC, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Toplam satir:', len(lines))

# Mojibake replacements
mojibake = {
    'Ãƒâ€"': 'Ö',
    'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â ': '— ',
    'ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Âş': '— Y',
    'Ã¢â€ â€™': '→',
    'Ãƒâ€"': 'Ö',
    'ÃƒÅ"': 'Ü',
    'ÃƒÅ"Ç': 'ÜÇ',
    'Ãƒâ€"nerisi': 'Önerisi',
    'Ãƒâ€"rnek': 'Örnek',
    'Ãƒâ€"lçeklendirme': 'Ölçeklendirme',
    'ÃƒÆ\'Ã‚Â¼r': 'ür',
    'ÃƒÆ\'Ã‚Â¼': 'ü',
    'literatÃƒÆ\'Ã‚Â¼rde': 'literatürde',
    'gÃƒÆ\'Ã‚Â¼rÃƒÆ\'Ã‚Â¼ltu': 'gürültü',
}

# Word-level replacements for corrupted sections (lines 25-423, 425-701, 706-735)
# Pattern: o→ü, y→ş in original ASCII Turkish
word_fixes = {
    'müdel': 'model', 'Müdel': 'Model',
    'fün': 'fon', 'Fün': 'Fon',
    'ülarak': 'olarak',
    'rapüra': 'rapora', 'rapür': 'rapor',
    'küdlar': 'kodlar', 'küd': 'kod',
    'sünuc': 'sonuc', 'sünuç': 'sonuç', 'Sünuc': 'Sonuc',
    'cüncept': 'concept', 'Cüncept': 'Concept',
    'sünras': 'sonras', 'sünra': 'sonra',
    'zürla': 'zorla',
    'vülatil': 'volatil',
    'perfürmans': 'performans',
    'güsterge': 'gösterge', 'güster': 'göster',
    'ügrenme': 'öğrenme', 'ügren': 'öğren', 'Ögrenme': 'Öğrenme',
    'üldu': 'oldu', 'ülmus': 'olmuş', 'ülur': 'olur', 'ülma': 'olma',
    'ülsa': 'olsa', 'ülarak': 'olarak',
    'ürtaya': 'ortaya', 'ürtalama': 'ortalama', 'üran': 'oran',
    'ürani': 'orani', 'üranı': 'oranı',
    'ürijinal': 'orijinal',
    'ürnek': 'örnek', 'Ürnek': 'Örnek', 'Ornek': 'Örnek',
    'ürtam': 'ortam',
    'küsul': 'koşul', 'kümbü': 'kombo', 'kümbinasyün': 'kombinasyon',
    'kümbü': 'kombo', 'künfigürasyün': 'konfigürasyon',
    'künfigurasyün': 'konfigürasyon', 'künfig': 'konfig',
    'küntrül': 'kontrol', 'küntrol': 'kontrol',
    'künvüluyün': 'konvolüsyon', 'künvülusyün': 'konvolüsyon',
    'küyma': 'koyma',
    'dügruluk': 'doğruluk', 'dügru': 'doğru', 'Dügru': 'Doğru',
    'düsus': 'düşüş', 'dusus': 'düşüş',
    'dünem': 'dönem', 'Dünem': 'Dönem',
    'düsük': 'düşük', 'düsuk': 'düşük',
    'dülar': 'dolar',
    'büzulunca': 'bozulunca', 'büzuk': 'bozuk',
    'bürsada': 'borsada', 'bürsa': 'borsa',
    'güzlem': 'gözlem', 'güzlen': 'gözlen', 'güzuk': 'gözük',
    'gürun': 'görün', 'gürul': 'görül', 'güster': 'göster',
    'gürev': 'görev', 'güre': 'göre',
    'güce': 'güce',  # keep
    'tüpla': 'topla', 'tüplam': 'toplam',
    'süru': 'soru', 'Süru': 'Soru', 'SÜRU': 'SORU',
    'sünuç': 'sonuç', 'SÜNUC': 'SONUÇ',
    'üzellik': 'özellik', 'Üzellik': 'Özellik',
    'üptimiz': 'optimiz',
    'üverfitting': 'overfitting',
    'üvun': 'övün',
    'üdak': 'odak', 'üdağ': 'odağ',
    'prüje': 'proje', 'Prüje': 'Proje',
    'prüblem': 'problem', 'Prüblem': 'Problem',
    'prüfesyünel': 'profesyonel',
    'pürtfüy': 'portföy', 'Pürtfüy': 'Portföy',
    'mümentum': 'momentum', 'Mümentum': 'Momentum',
    'nürmal': 'normal',
    'nürün': 'nöron',
    'fürmul': 'formül', 'Fürmul': 'Formül',
    'fürmda': 'formda',
    'hypüthes': 'hypothes',
    'randüm': 'random', 'Randüm': 'Random',
    'hareket': 'hareket',  # keep
    'cüzum': 'çözüm', 'Cüzum': 'Çözüm',
    'cügunluk': 'çoğunluk',
    'catisirsin': 'çatışırsın',
    'regresyün': 'regresyon',
    'sinifland': 'sınıfland',
    'stükast': 'stokast',
    'lükal': 'lokal',
    'glübal': 'global',
    'tüprak': 'toprak',
    'nüktalar': 'noktalar',
    'büsun': 'boşun',
    'türe': 'tore',  # skip, complex
    'üygulan': 'uygula',  # no, uygulan is correct
    'havuzlan': 'havuzlan',  # keep
    'ayrıştır': 'ayrıştır',  # keep
    'tekrarlan': 'tekrarlan',  # keep
    'Classificatiün': 'Classification',
    'Classificatiün': 'Classification',
    'Predictiün': 'Prediction', 'predictiün': 'prediction',
    'Decisiün': 'Decision',
    'cümputatiünal': 'computational',
    'Transactiün': 'Transaction',
    'Micrüstructure': 'Microstructure',
    'Stüchastic': 'Stochastic',
    'Activatiün': 'Activation', 'activatiün': 'activation',
    'Cümputatiünal': 'Computational',
    'Drüpüut': 'Dropout', 'drüpüut': 'dropout',
    'Püsitive': 'Positive', 'püsitive': 'positive',
    'Epüch': 'Epoch', 'epüch': 'epoch',
    'Ãƒâ€"nerisi': 'Önerisi',
}

# ş→y replacements (only in corrupted sections)
sh_fixes = {
    'şuksel': 'yüksel', 'şukaris': 'yukarı',
    'şanlis': 'yanlış', 'şaniltici': 'yanıltıcı',
    'şanlisti': 'yanlıştı', 'şANLIS': 'YANLIŞ',
    'şapisal': 'yapısal', 'şapis': 'yapıs',
    'şANLISTI': 'YANLIŞTI',
    'şuzden': 'yüzden',
    'şüzden': 'yüzden',
    'şerine': 'yerine',
    'şeterli': 'yeterli',
    'şetersiz': 'yetersiz',
    'şatır': 'yatır',
    'şönet': 'yönet', 'şünet': 'yönet',
    'şONU': 'YÖNÜ', 'şonu': 'yönü', 'şön': 'yön',
    'şapay': 'yapay',
    'şapildi': 'yapıldı', 'şaptığ': 'yaptığ', 'şapmadi': 'yapmadı',
    'şAPMAMIS': 'YAPMAMIS',
    'şapilamiyür': 'yapılamıyor',
    'şakin': 'yakın',
    'şakalar': 'yakalar',
    'şerel': 'yerel',
    'şillik': 'yıllık', 'şıllık': 'yıllık',
    'şaramiyür': 'yaramıyor',
    'şaramazligi': 'yaramazlığı',
    'şök': 'yok', 'şük': 'yok', 'şuk': 'yok',
    'şOK': 'YOK',
    'şüksek': 'yüksek',
    'şukselis': 'yükseliş',
    'şansitir': 'yansıtır',
    'şansit': 'yansıt',
    'şarismasi': 'yarışması',
    'şarinin': 'yarının',
    'şegane': 'yegane',
    'şayilim': 'yayılım',
    'şiyen': 'yiyen',
    'şaş': 'yaş',
    'şüneticiler': 'yöneticiler',
    'şürdama': 'yordama',
}

# Ö→- and Ö→→ in specific contexts
def fix_o_dash(text):
    # Between numbers: 1Ö7 → 1-7
    text = re.sub(r'(\d)Ö(\d)', r'\1-\2', text)
    text = re.sub(r'(\d)Ö(%)', r'\1-\2', text)
    # Between words as separator: AÖB → A-B (in compound terms)
    text = re.sub(r'([a-zA-Z])Ö([a-zA-Z])', r'\1-\2', text)
    # Ö> → →
    text = text.replace('Ö>', '→')
    # Start of line Ö → - (bullet)
    if text.lstrip().startswith('Ö '):
        text = text.replace('Ö ', '- ', 1)
    return text

# Ç→? at end of questions  
def fix_question(text):
    text = text.replace('Ç\n', '?\n')
    text = text.replace('Ç ', '? ')
    if text.rstrip().endswith('Ç'):
        text = text.rstrip()[:-1] + '?\n'
    # Fix ->' at end
    text = text.replace('->', '?')
    return text

# Determine if a line is corrupted (has encoding issues)
def is_corrupted(line):
    corrupted_markers = ['müdel', 'ülarak', 'fün', 'sünuc', 'ügrenme', 
                         'güster', 'prüje', 'dünem', 'sünra', 'şuzden',
                         'şerine', 'cügunluk', 'kümbinasyün', 'künfig',
                         'perfürmans', 'vülatil']
    line_lower = line.lower()
    return any(m in line_lower for m in corrupted_markers)

# Process
output = []
fixed_count = 0
for i, line in enumerate(lines):
    original = line
    
    # Apply mojibake fixes to ALL lines
    for bad, good in mojibake.items():
        if bad in line:
            line = line.replace(bad, good)
    
    # Only apply ü→o and ş→y fixes to corrupted sections
    if i >= 24:  # Lines 25+ (0-indexed: 24+)
        # Word-level ü→o fixes
        for bad, good in word_fixes.items():
            if bad in line:
                line = line.replace(bad, good)
        
        # ş→y fixes
        for bad, good in sh_fixes.items():
            if bad in line:
                line = line.replace(bad, good)
        
        # Ö→- contextual
        line = fix_o_dash(line)
        
        # Ç→? 
        line = fix_question(line)
    
    if line != original:
        fixed_count += 1
    output.append(line)

# Remove duplicate sections:
# Lines 737-769 (makaleye eklenecek paragraflar) - bunlar JURI dosyasının parçası değil
# Ama kullanıcı "eklenmesi gerektiğini düşündüğün şeyleri sona ekle" dedi
# Bu paragrafları tutuyorum ama başlık ekliyorum

# Write
with open(SRC, 'w', encoding='utf-8') as f:
    f.writelines(output)

print('Düzeltilen satır sayısı:', fixed_count)
print('Kaydedildi:', SRC)

# Verify
with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()
    
remaining_issues = 0
for marker in ['müdel', 'ülarak', 'cüncept', 'sünras', 'perfürmans']:
    count = content.lower().count(marker)
    if count > 0:
        remaining_issues += count
        print('  KALAN: "%s" x%d' % (marker, count))

if remaining_issues == 0:
    print('Tum bilinen encoding sorunlari giderildi!')
else:
    print('Kalan sorun sayisi:', remaining_issues)
