import zipfile,re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
SRC=r'c:\Users\Kurt\Desktop\Proje\01_Savunma_ve_Ana_Metinler\MAKALE.docx'
with zipfile.ZipFile(SRC,'r') as z:
    raw=z.read('word/document.xml').decode('utf-8',errors='replace')
text=re.sub(r'<[^>]+>',' ',raw)
text=re.sub(r'\s+',' ',text)
for kw in ['matematiksel', 'tutarlilik', 'tutarl', 'havuzlanm', 'rasgelelik', 'tohum', 'seed']:
    cnt=text.count(kw)
    if cnt: print(f'  "{kw}": {cnt}x')
# K8 cumlesini bul
idx = text.find('matematiksel')
if idx >= 0:
    print()
    print(f'Baglam: ...{text[max(0,idx-100):idx+300]}...')
