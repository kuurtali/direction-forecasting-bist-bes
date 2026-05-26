# -*- coding: utf-8 -*-
"""JURI_SAVUNMA 2. gecis - kalan encoding sorunlari"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\JURI_SAVUNMA_VE_BILINMESI_GEREKENLER.txt'

with open(SRC, 'r', encoding='utf-8') as f:
    text = f.read()

# 2. gecis - kalan ü→o düzeltmeleri
fixes2 = [
    ('Hücanın', 'Hocanın'),
    ('ediyür', 'ediyor'),
    ('illuzyün', 'illüzyon'),
    ('ülcum', 'ölçüm'),
    ('şüntem', 'yöntem'),
    ('cükmus', 'çökmüş'),
    ('buyüzden', 'bu yüzden'),
    ('clüsing', 'closing'),
    ('histürical', 'historical'),
    ('Clüsing', 'Closing'),
    ('ülabilir', 'olabilir'),
    ('ülarak', 'olarak'),
    ('ülustur', 'oluştur'),
    ('ürtaya', 'ortaya'),
    ('Buyapısal', 'Bu yapısal'),
    ('düşüşyok', 'düşüş yok'),
    ('yükselis', 'yükseliş'),
    ('düşüşu', 'düşüşü'),
    ('ürnegin', 'örneğin'),
    ('Majürity', 'Majority'),
    ('dügru', 'doğru'),
    ('buyuk', 'büyük'),
    ('sünuclar', 'sonuçlar'),
    ('sinifini', 'sınıfını'),
    ('edemiyür', 'edemiyor'),
    ('yükselisyok', 'yükseliş yok'),
    ('düşüşyok', 'düşüş yok'),
    ('veyıllık', 've yıllık'),
    ('üluştur', 'oluştur'),
    ('küyma', 'koyma'),
    ('küsu', 'koşu'),
    ('başinayanıltıcı', 'başına yanıltıcı'),
    ('sinifland', 'sınıfland'),
    ('Ãƒâ€"nerisi', 'Önerisi'),
    ('ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â ', '— '),
    ('ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â\"', '—\"'),
    ('şani', 'yani'),
    ('şERDE', 'YERDE'),
    ('şararin', 'yararın'),
    ('ücum', 'ücum'), # keep
    ('HERşERDE', 'HER YERDE'),
    ('dügrulama', 'doğrulama'),
    ('nünÖMC', 'non-MC'),
    ('NünÖMC', 'Non-MC'),
    ('Cünfusiün', 'Confusion'),
    ('cünfusiün', 'confusion'),
    ('Drüpüut', 'Dropout'),
    ('drüpüut', 'dropout'),
    ('nürmaliz', 'normaliz'),
    ('Nürmaliz', 'Normaliz'),
    ('arttikca', 'arttıkça'),
    ('tühumlar', 'tohumlar'),
    ('Tühum', 'Tohum'),
    ('tühum', 'tohum'),
    ('dürüstçe', 'dürüstçe'), # keep
    ('Stüchastic', 'Stochastic'),
    ('Stükast', 'Stokast'),
    ('teknik rapürşeniden', 'teknik rapor yeniden'),
    ('Tühu', 'Tohu'),
    ('üverfitting', 'overfitting'),
    ('Üverfitting', 'Overfitting'),
    ('ünlendi', 'önlendi'),
    ('üptimiz', 'optimiz'),
    ('hypüthes', 'hypothes'),
    ('Hypüthes', 'Hypothes'),
    ('mümentum', 'momentum'),
    ('nüklee', 'nüklee'), # keep - nükleer
    ('nürün', 'nöron'),
    ('fraktal', 'fraktal'), # keep
    ('Classificati-n', 'Classification'),
    ('Predicti-n', 'Prediction'),
    ('Decisi-n', 'Decision'),
    ('Activati-n', 'Activation'),
    ('activati-n', 'activation'),
    ('Transacti-n', 'Transaction'),
    ('Ep-ch', 'Epoch'),
    ('P-sitive', 'Positive'),
    ('p-sitive', 'positive'),
    ('regresyün', 'regresyon'),
    ('regresyon', 'regresyon'),
    ('Randüm', 'Random'),
    ('randüm', 'random'),
    ('Cümputatiünal', 'Computational'),
    ('Micrüstructure', 'Microstructure'),
    ('AyKIRI', 'AYKIRI'),
    ('ONEMLI', 'ÖNEMLİ'),
    ('DOGRU', 'DOĞRU'),
    # remaining ü→o patterns
    ('üzetler', 'özetler'),
    ('ünemsenmedi', 'önemsenmedi'),
    ('üdünles', 'ödünleş'),
    ('üzere', 'üzere'), # keep - legitimate ü
    ('üstün', 'üstün'), # keep
    ('üzgü', 'üzgü'), # keep
    ('ücretsiz', 'ücretsiz'), # keep
]

fix_count = 0
for bad, good in fixes2:
    if bad != good and bad in text:
        text = text.replace(bad, good)
        fix_count += 1

# Fix remaining ÖÖÖÖ decorators → === 
text = re.sub(r'ÖÖÖÖ+', lambda m: '=' * len(m.group()), text)

# Fix remaining Ö between specific words
text = text.replace('F1-Score', 'F1-Score')
text = text.replace('F1-scüre', 'F1-score')
text = text.replace('F1-score', 'F1-Score')
text = text.replace('Cüst-sensitive', 'Cost-sensitive')
text = text.replace('cüst-sensitive', 'cost-sensitive')
text = text.replace('Train-only', 'Train-only')

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(text)

print('2. gecis tamamlandi, %d ek düzeltme' % fix_count)

# Count remaining problematic patterns
problems = ['müdel', 'ülarak', 'ediyür', 'cüncept', 'sünra', 'perfürm',
            'vülatil', 'Majürity', 'şani', 'şuzden', 'şerine']
for p in problems:
    c = text.lower().count(p.lower())
    if c > 0:
        print('  KALAN: "%s" x%d' % (p, c))
