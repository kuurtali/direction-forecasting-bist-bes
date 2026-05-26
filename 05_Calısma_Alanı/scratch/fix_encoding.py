import sys
import os

def fix_encoding(filepath):
    # Dosyayi once raw bytes olarak oku
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    # BOM varsa kaldir
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    
    # Latin-1 gibi oku (double-UTF8 durumunu c,oz)
    try:
        content = raw.decode('utf-8')
    except:
        content = raw.decode('latin-1')
    
    # Double-encoded UTF-8 kaliplari duzeltt (Turkce harfler icin)
    double_enc_map = {
        # u umlaut
        '\xc3\xbc': 'u', 'Ã¼': 'u',
        # o umlaut  
        '\xc3\xb6': 'o', 'Ã¶': 'o',
        # c cedilla
        '\xc3\xa7': 'c', 'Ã§': 'c',
        # dotless i
        '\xc4\xb1': 'i', 'Ä±': 'i',
        # dotted I
        '\xc4\xb0': 'I', 'Ä°': 'I',
        # g breve
        '\xc4\x9f': 'g', 'ÄŸ': 'g', 'Ã„Å¸': 'g',
        # G breve
        '\xc4\x9e': 'G', 'Ã„Å¾': 'G',
        # s cedilla
        '\xc5\x9f': 's', 'Å\u009f': 's', 'Ã…Å¸': 's',
        # S cedilla
        '\xc5\x9e': 'S', 'Å\u009e': 'S', 'Ã…Åž': 'S',
        # O umlaut capital
        '\xc3\x96': 'O', 'Ã–': 'O',
        # U umlaut capital
        '\xc3\x9c': 'U', 'Ãœ': 'U',
        # C cedilla capital
        '\xc3\x87': 'C', 'Ã‡': 'C',
        # Remaining multi-byte patterns
        'ÃƒÂ¼': 'u', 'ÃƒÂ¶': 'o', 'ÃƒÂ§': 'c',
        'ÃƒÂ–': 'O', 'ÃƒÅ"': 'U', 'ÃƒÂ‡': 'C',
        'Ã„Â±': 'i', 'Ã„Â°': 'I',
    }
    
    for old, new in double_enc_map.items():
        content = content.replace(old, new)
    
    # Unicode Turkce -> ASCII
    unicode_map = {
        '\u011f': 'g', '\u011e': 'G',  # g/G breve
        '\u015f': 's', '\u015e': 'S',  # s/S cedilla
        '\u0131': 'i', '\u0130': 'I',  # dotless i / dotted I
        '\u00fc': 'u', '\u00dc': 'U',  # u/U umlaut
        '\u00f6': 'o', '\u00d6': 'O',  # o/O umlaut
        '\u00e7': 'c', '\u00c7': 'C',  # c/C cedilla
        # Noktalama
        '\u2014': '-', '\u2013': '-',   # em/en dash
        '\u2019': "'", '\u2018': "'",   # smart quotes single
        '\u201c': '"', '\u201d': '"',   # smart quotes double
        '\u2022': '*',                   # bullet
        '\u2192': '->',                  # right arrow
        '\u2190': '<-',                  # left arrow
        '\u00d7': 'x',                   # multiplication sign
        '\u2713': '(v)',                 # check mark
        '\u00ab': '"', '\u00bb': '"',   # guillemets
        '\ufeff': '',                    # BOM
        '\u00ae': '(R)',                 # registered sign
        # Eski raporlarda gorulen karmas.ik kaliplar
        'Ã¢â‚¬â€"': '-',
        'Ã¢â‚¬â€': '-',
        'Ã¢â€šÂ¬': 'EUR',
        'Ã¢â€ â€™': '->',
        'Ã¢Å"â€œ': '(v)',
        'Ã¢â‚¬Â¢': '*',
    }
    
    for old, new in unicode_map.items():
        content = content.replace(old, new)
    
    # Sonucu UTF-8 olarak kaydet
    with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)
    
    print(f"Tamamlandi: {os.path.basename(filepath)}")

if __name__ == '__main__':
    for fp in sys.argv[1:]:
        fix_encoding(fp)
