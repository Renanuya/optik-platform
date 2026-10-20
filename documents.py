"""Dimensioned A3 engineering sheets, vector CAD views, and assembly notes."""
from pathlib import Path
import json,math,textwrap,csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from OCP.HLRBRep import HLRBRep_Algo,HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from validate import read

ROOT=Path(__file__).parent
W,H=landscape(A3); INK='#17313c'; MUTED='#55676d'; ACCENT='#287e89'
font_root=Path('/System/Library/Fonts/Supplemental')
regular=font_root/'Arial.ttf';bold=font_root/'Arial Bold.ttf'
if not regular.exists():regular=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');bold=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
pdfmetrics.registerFont(TTFont('Arial',str(regular)));pdfmetrics.registerFont(TTFont('ArialB',str(bold)))
parts=json.loads((ROOT/'parts.json').read_text())
BOM=[
 ('MG996R 360° servo','2','Mevcut. Sürekli dönüşlü sürüm kabulü; üçüncü servo yedek. Üç kablo açı telemetrisi değildir.'),
 ('Waveshare OV5640 Camera Board A','1','35.7 x 23.9 mm PCB, DVP; lens/header yükseklikleri gerçek kartla doğrulanacak.'),
 ('Picotronic DI650-0.4-3(8x21)','1','Üretici sınıfı Class 1, 0.4 mW, 3 V, D8 x 21 mm.'),
 ('Adafruit AS5600 #6357','2','20.32 x 12.70 mm delik aralığı; klon PCB doğrudan uyumlu kabul edilmez.'),
 ('Çap boyunca kutuplanmış mıknatıs','2','D6 x 2.5 mm; sensör alan aralığı gerçek donanımla ölçülecek.'),
 ('608 rulman','4','D8 iç / D22 dış / 7 mm en. Geçme kuponuna göre yatağı ayarlayın.'),
 ('D8 taşlanmış pan mili','1','Nominal 106 mm; montajda Z21.4-127.4. Uç ve bilezik ölçülerini karşılaştırın.'),
 ('D8 sıkmalı mil bileziği','2','Yaklaşık 6 mm en, en fazla D16 dış çap. İç bileziklere dayanır.'),
 ('Ara burç, ID8.2 / OD12','5','Pan 1 x 5 mm; tilt 1 x 3 mm, 2 x 4 mm, 1 x 2 mm.'),
 ('M8 x 35 DIN931 + M8 somun','1 set','Sol tilt mili, kısmi dişsiz gövde. Bir montaj vidası yerine kullanılamaz.'),
 ('ISO7379 D8 x 16 / M6 + somun','1 set','Sağ tilt mili, omuz 16 mm ve M6 diş. Tedarikçi baş/diş boyu kontrol edilir.'),
 ('Servo stok yuvarlak horn','2','MG996R spline uyumlu, en az D22; dişliler M2 radyal slotlardan tutturulur.'),
 ('ESP32-S3 N16R8 kart','1','Kullanıcının kartı. Görsel DevKitC-1 referansı 62.74 x 25.40 mm; gerçek PCB kimliği bekleniyor.'),
 ('Adafruit USB-C panel #4218','1','Nominal D22.2 dış kabuk deliği, D24 iç rahatlatma. Referans kablo 30 cm.'),
 ('Esnek USB uzatma / ince köşe fiş','1 set','Yaklaşık ilave 30 cm başlangıç; toplam uzunluk ve bükülme gerçek montajda ölçülür.'),
 ('M2 ısıl insert, yaklaşık D3.1 x 4','42 aday','Seçilen insertin üretici delik tavsiyesi + P24 kuponu esastır. Satın alma ön tahmini.'),
 ('M2 ısıl insert, yaklaşık D3.1 x 3','8 aday','Enkoder yatakları; gerçek insert geometrisiyle doğrulanır.'),
 ('M2 somun / geniş pul','1 takım','Yaklaşık 40 somun ve 30 pul alın; servo slotlarında en az D6 pul. Kesin adet montajda kapanır.'),
 ('M2 x 6','4','Pan enkoder PCB.'),
 ('M2 x 8','16','Enkoder/çekmece 6, ESP taşıyıcı 2, kapak iç çerçeveleri 8.'),
 ('M2 x 10','12','Taban kapak 4, kule taban 4, kamera kaseti 4.'),
 ('M2 x 12','15','Pan çıkış 3, servo kulakları 8, V2 taban dış kabuk 4.'),
 ('M2 x 14 / x16 / x18','12 / 10 / 3','Köprü+horn / dikme ve servo sehpası+optik kelepçe / pan kartuşu. Baş boyları kontrol edilir.'),
 ('M2 x 25 / x35 / x40 / x55','4 / 8 / 2 / 4','Sağ dış kapak / başlık ve sol kapak / rotor sıkma / dişli muhafazası. Uzun M2 burkulması kontrol edilir.'),
 ('Esnek kablo, bağ ve köpük','1 set','Kamera-ESP kısa DVP bağlantısı; kablo kanalı 12 x 4.5, ayak geçişi D8.5. R>=15 mm başlangıç hedefi.'),
 ('Taban ayakları','4','En az 5 mm; V1 alt bağlantıları ve V2 vida başları için.'),
 ('Regüle servo kaynağı','1','6 V / 5 A başlangıç adayı; gerçek servo akım/ısınma ölçümü gerekir. ESP ile ortak GND.'),
 ('I2C ayırma + güç geçişi','1 set','İki AS5600 aynı adreste: ayrı ESP I2C birimleri veya çoklayıcı; arka D10 güç geçişi.'),
]

def font(c,size=10,bold=False,color=INK):
    c.setFont('ArialB' if bold else 'Arial',size);c.setFillColor(color)

def wrapped(c,text,x,y,width,size=10,leading=15):
    words=text.split();line='';font(c,size)
    for word in words:
        trial=(line+' '+word).strip()
        if pdfmetrics.stringWidth(trial,'Arial',size)>width and line:
            c.drawString(x,y,line);y-=leading;line=word
        else:line=trial
    if line:c.drawString(x,y,line);y-=leading
    return y

def header(c,title,sub,page,total):
    c.setFillColor(INK);c.rect(0,H-80,W,80,fill=1,stroke=0)
    font(c,22,True,'#ffffff');c.drawString(36,H-39,title)
    font(c,10,False,'#d9e6e9');c.drawString(37,H-61,sub)
    c.setStrokeColor('#b7c5ca');c.setLineWidth(.5);c.rect(30,28,W-60,48)
    font(c,9,True);c.drawString(42,58,'OPTIK / R0.2 - MÜHENDİSLİK PROTOTİPİ')
    font(c,8);c.drawString(42,42,'20.10.2026 | Birim: mm | STEP ve STL geometrisi esas alınır. Fiziksel montaj ve baskı doğrulaması yapılmadı.')
    c.drawRightString(W-42,58,f'{page:02d} / {total:02d}')
    c.drawRightString(W-42,42,'Bambu Lab X1 Carbon / 0.4 mm nozül için başlangıç tasarımı')

def lines(s,normal,xdir):
    algo=HLRBRep_Algo();algo.Add(s)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0,0,0),gp_Dir(*normal),gp_Dir(*xdir))))
    algo.Update();algo.Hide();out=HLRBRep_HLRToShape(algo)
    paths=[];seen=set()
    for obj in (out.VCompound(),out.Rg1LineVCompound(),out.OutLineVCompound()):
      if obj.IsNull():continue
      ex=TopExp_Explorer(obj,TopAbs_EDGE)
      while ex.More():
        edge=TopoDS.Edge_s(ex.Current());curve=BRepAdaptor_Curve(edge)
        q=GCPnts_QuasiUniformDeflection(curve,.02)
        if q.IsDone() and q.NbPoints()>1:
            pts=[(q.Value(j).X(),q.Value(j).Y()) for j in range(1,q.NbPoints()+1)]
            key=tuple(round(v,4) for p in (pts[0],pts[-1],pts[len(pts)//2]) for v in p)
            rev=tuple(round(v,4) for p in (pts[-1],pts[0],pts[len(pts)//2]) for v in p)
            if key not in seen and rev not in seen:paths.append(pts);seen.add(key)
        ex.Next()
    return paths

def dimension(c,a,b,offset,label,vertical=False):
    c.setStrokeColor(MUTED);c.setLineWidth(.45);font(c,8,False,MUTED)
    if not vertical:
        x0,y0=a;x1,y1=b; yy=min(y0,y1)-offset
        c.line(x0,y0-3,x0,yy-4);c.line(x1,y1-3,x1,yy-4);c.line(x0,yy,x1,yy)
        for x,sign in ((x0,1),(x1,-1)):
            c.line(x,yy,x+sign*5,yy+2);c.line(x,yy,x+sign*5,yy-2)
        c.drawCentredString((x0+x1)/2,yy-11,label)
    else:
        x0,y0=a;x1,y1=b;xx=max(x0,x1)+offset
        c.line(x0+3,y0,xx+4,y0);c.line(x1+3,y1,xx+4,y1);c.line(xx,y0,xx,y1)
        for y,sign in ((y0,1),(y1,-1)):
            c.line(xx,y,xx+2,y+sign*5);c.line(xx,y,xx-2,y+sign*5)
        c.saveState();c.translate(xx+12,(y0+y1)/2);c.rotate(90);c.drawCentredString(0,0,label);c.restoreState()

def view(c,s,rect,normal,xdir,title):
    x,y,w,h=rect;pp=lines(s,normal,xdir)
    if not pp:raise ValueError('Empty CAD projection '+title)
    xs=[p[0] for path in pp for p in path];ys=[p[1] for path in pp for p in path]
    x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys)
    scale=min((w-92)/max(x1-x0,.1),(h-82)/max(y1-y0,.1))
    ox=x+w/2-(x0+x1)/2*scale-10;oy=y+h/2-(y0+y1)/2*scale+4
    font(c,10,True);c.drawString(x+4,y+h-12,title)
    c.setStrokeColor(INK);c.setLineWidth(.55)
    for path in pp:
        p=c.beginPath();p.moveTo(ox+path[0][0]*scale,oy+path[0][1]*scale)
        for xx,yy in path[1:]:p.lineTo(ox+xx*scale,oy+yy*scale)
        c.drawPath(p)
    lo=(ox+x0*scale,oy+y0*scale);hi=(ox+x1*scale,oy+y1*scale)
    dimension(c,lo,(hi[0],lo[1]),13,f'{x1-x0:.2f}')
    dimension(c,(hi[0],lo[1]),hi,13,f'{y1-y0:.2f}',True)
    font(c,7,False,MUTED);c.drawString(x+4,y+2,f'Görünüş ölçeği 1 mm = {scale:.2f} pt; ölçü rakamları esas alınır.')

def note_page(c,title,blocks,page,total):
    header(c,title,'Tasarım, donanım ve montaj notları',page,total)
    y=H-115
    for name,body in blocks:
        font(c,13,True,ACCENT);c.drawString(42,y,name);y-=23
        y=wrapped(c,body,42,y,W-90,10.4,15)-15
    c.showPage()

def main():
    total=len(parts)+6
    out=ROOT/'drawings'/'OPTIK-teknik-cizimler.pdf'
    c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
    c.setTitle('OPTIK R0.2 - Teknik çizimler ve montaj notları')
    header(c,'OPTIK / Kamera ve ışık platformu','İki eksen / rulmanlı mekanik / AS5600 konum geri bildirimi',1,total)
    c.drawImage(str(ROOT/'images'/'montaj-v2.png'),40,180,width=720,height=490,preserveAspectRatio=True,anchor='c',mask='auto')
    y=H-135
    for name,text in [
      ('TESLİM KAPSAMI','32 özgün parça; P13 iki, P26 altı adet. P24 test kuponu, P26 isteğe bağlı klipstir. Düzenlenebilir STEP, baskı yönünde STL, montaj görselleri ve bu ölçülü çizimler.'),
      ('DURUM','R0.2 prototip. Geometrik kontroller, fiziksel doğrulamanın yerine geçmez. Önce P24 geçme kuponunu basın.'),
      ('HAREKET','Pan: ±90°. Tilt: ±90°. Mekanik durdurucular mevcut. Gerçek açıklık kablo ve donanımla doğrulanır.'),
      ('GERİ BİLDİRİM','360° servolar hız/yön kumandalı kabul edildi. Açı iki AS5600 kartıyla ölçülür; bu paket çalışan kontrol yazılımı içermez.')]:
        font(c,12,True,ACCENT);c.drawString(805,y,name);y-=22
        y=wrapped(c,text,805,y,330,11,16)-25
    c.showPage()
    # Hardware BOM split over two pages.
    for page,start in ((2,0),(3,14)):
        header(c,'Satın alınan parçalar / bağlantı elemanları',f'BOM {1 if page==2 else 2}/2 - modelle birlikte değişebilir',page,total)
        y=H-110
        for name,qty,note in BOM[start:start+14]:
            font(c,10,True);c.drawString(42,y,f'{qty}  |  {name}')
            y=wrapped(c,note,290,y,W-335,9.4,13)-19
        c.showPage()
    note_page(c,'Montaj / yatak ve mil zinciri',[
      ('1 - Önce geçmeler','P24 kuponunu son parçada kullanacağınız filament ve profille basın. 608 dış çapı için delik sırası 21.95 / 22.05 / 22.15 / 22.25 mm. Rulmanı zorlayarak gövdeyi çatlatmayın. Seçilen kupona göre yatak parametresini değiştirip STEP/STL üretin.'),
      ('2 - Pan modülü','P09 kuleyi P01 tabana bağlayın. P11 çekmecesine AS5600 PCB takın. Mil, mıknatıs ve sensör merkezlerini çakıştırın. Alt 608 Z40-47, üst 608 Z52-59. İç bilezikler arasında 5 mm ara burç bulunur. İki sıkmalı mil bileziği eksenel boşluğu tutar; dış bileziklere gereksiz ön yük vermeyin.'),
      ('3 - Pan aktarımı','P12 sehpa + servo + stok horn + P13 tahrik dişlisi. P14 çıkış dişlisini P15 rotorun altına üç M2 ile bağlayın. Dişli merkez aralığı 49.5 mm; baskı boşluğu prototipte kontrol edilir. P20 muhafazayı kapatmadan mekanizmayı elle çevirin.'),
      ('4 - Köprü ve dikmeler','P16 köprüyü P15 flansa bağlayan dört M2 x 14 vida alttan taşmamalı; uzun vidalar durduruculara çarpabilir. P17/P18 dikmeleri dört M2 x 16 ile takın. Rulman merkezleri ortak X doğrusu üzerinde ve tabandan 227 mm yüksektedir.'),
      ('5 - Tilt mili','Sol: M8 x 35 DIN931 başı P19 dişlinin cebinde, ardından 3 mm dış burç + 608 + 4 mm iç burç. Sağ: D8 x 16/M6 omuz civatası, 2 mm dış + 608 + 4 mm iç burç. M6 somun sağ başlık cebinde. Standart dışı baş/omuz boyu almayın; tedarikçi çizimi ve parça zincirini karşılaştırın.'),
    ],4,total)
    note_page(c,'Optik montaj / elektrik ve hareket',[
      ('Kamera kaseti','P04 cebe nominal 35.7 x 23.9 mm PCB yerleşir. P05 baskı çerçevesi ve yaklaşık 0.5 mm yumuşak ara parça tutar. Dört M2 vida aralığı 41 x 29 mm kasete aittir; kameranın fabrika delik aralığı olarak kullanılmaz. Gerçek PCB üzerindeki header, lens konumu ve komponent yüksekliği kontrol edilir.'),
      ('Işık modülü','P07/P08 yalnız Ø8 x 21 mm optik modül içindir. D8.30 kanal ve 0.2 mm kapak aralığı tasarım değeridir. İki M2 x 16 vida ile aşırı sıkmadan tutun. Üreticinin Class 1 etiketi tüm montaj için otomatik bir sınıflandırma değildir; laboratuvarın optik güvenlik değerlendirmesi ayrıca yapılır.'),
      ('Enkoderler','AS5600 #6357 PCB ölçüsü 25.4 x 17.78 mm, dört delik merkezi 20.32 x 12.70 mm. Pan PCB altı Z10.5; nominal sensör-mıknatıs aralığı yaklaşık 1.5 mm. Sağ PCB altı X80, sensör yüzü içe bakar. Mıknatısın çap boyunca kutuplanması, alan şiddeti ve merkezleme gerçek sensörle doğrulanır.'),
      ('Besleme ve bağlantı','MG996R servoları ESP32 kartının 3.3 V pininden beslemeyin. Ayrı regüle servo kaynağı ve ortak GND kullanın. İki AS5600 aynı I2C adresindedir: ayrı I2C birimleri veya çoklayıcı gerekir. GPIO ataması, gerçek ESP32-S3 kart modeli ve kamera pin bütçesi bilinmeden verilmedi. L298N standart RC servo kontrolünde gerekli değildir.'),
      ('Kablo ve servis erişimi','ESP, P25 ile başlık sırtında; DVP kablosunu kısa tutun. Taban arkasındaki USB-C panel uzatması kartın gerçek USB portuna bağlanır. P16 altında 12 x 4.5 mm kanallar ve D8.5 dikme çıkışları vardır. Pan çevresinde yaklaşık R22-44 kablo halkası alanı bırakıldı. Kablo kesiti, esneklik ve 180 derece hareket prototipte ölçülmeden kapaklar kapatılmaz.'),
    ],5,total)
    note_page(c,'Baskı / kaynaklar / doğrulama sınırları',[
      ('Baskı başlangıç profili','Gövde ve dikmeler için PETG ile ilk prototip; üreticinin filament profili, 0.4 mm nozül, 0.20 mm katman, 5 duvar, 6 üst/alt katman ve %30 dolgu bir başlangıç önerisidir. Gerçek mukavemet veya isabet hassasiyeti bu ayarlardan türetilemez. V2 taban dış kabuğu yaklaşık 205 x 165 mm olup X1 Carbon nominal hacmi 256 x 256 x 256 mm içindedir.'),
      ('Yön ve destek','STL dosyaları belirtilen baskı yönüne döndürülüp Z=0 üzerine alınmıştır. P03/P04/P05/P06, Y normali; P17/P18/P19/P22/P23, X normali; P20 kapak yüzeyi aşağı. Özellikle dikmeler ve yan çıkıntılarda yerel destek gerekir. Bambu Studio önizlemesinde havada başlayan katmanları, rulman deliklerini ve destek temaslarını kontrol edin.'),
      ('Henüz doğrulanmayanlar','Baskı geçmeleri, gerçek servo boyutları ve horn delikleri; kabloların tüm hareket boyunca açıklığı; mıknatıs alanı; kamera pinleri ve kare hızı; yük altında boşluk, rijitlik ve kontrol kararlılığı. CAD hacimleri gerçek baskı ağırlığı değildir. İlk mekanik kurulumdan sonra ölçülerek revize edilmelidir.'),
      ('Geometri kontrolleri','Her STEP gövdesi topolojik geçerlilik, her STL kapalı ağ ve tabla hacmi kontrolünden geçirilir. Montaj için seçili pan/tilt açılarında kesişimler örneklenir; sonuçlar checks/assembly-checks.json içindedir. Bu örnekleme sürekli çarpışma testi veya sonlu eleman analizi değildir.'),
      ('Alüminyum revizyonu','Bu FDM gövdeleri doğrudan CNC üretim çizimi değildir. Önce P16 köprü ve dikmelerin düz plaka/ara parçalı metal revizyonu yapılır; yatak geçmeleri, bağlantı dişleri, kütle/atalet ve servo yeterliliği yeniden hesaplanır. ESP anteni metal kabukta uygun RF açıklığı ister. MuJoCo videoları yaklaşık dinamik değerlerle hareket gösterimidir; donanım kalibrasyonu yapılmadı.'),
      ('Üretici kaynakları','Tower Pro MG996R ürün sayfası; Waveshare OV5640 Board A; Espressif esp32-camera; Picotronic DI650-0.4-3(8x21); Adafruit #6357 ve yayımlanan Eagle PCB dosyası; Bambu Lab X1 Carbon teknik özellikleri. Tam bağlantılar GitHub README içinde verilmiştir. Temel geometri bu proje için üretilmiştir; üçüncü taraf PCB dosyası yeniden dağıtılmıyor.'),
    ],6,total)
    for idx,rec in enumerate(parts,7):
        print('DRAWING',rec['code'],flush=True)
        s=read(ROOT/'cad'/f"{rec['code']}.step")
        header(c,f"{rec['code']} / {rec['name']}",rec['note'],idx,total)
        view(c,s,(42,440,510,285),(0,0,1),(1,0,0),'ÜST / XY')
        view(c,s,(42,112,510,285),(0,-1,0),(1,0,0),'ÖN / XZ')
        view(c,s,(590,112,280,285),(1,0,0),(0,1,0),'SAĞ / YZ')
        c.drawImage(str(ROOT/'images'/f"{rec['code']}.png"),600,415,width=540,height=330,preserveAspectRatio=True,anchor='c')
        y=379;font(c,11,True,ACCENT);c.drawString(900,y,'İMALAT NOTLARI');y-=24
        for t in rec['features']:y=wrapped(c,'- '+t,900,y,245,9.4,13)-9
        y-=8;y=wrapped(c,f"Adet: {rec['qty']} | STL baskı normali: {rec['print_axis']}",900,y,245,9,13)-10
        y=wrapped(c,'Delik ve insert geçmeleri P24 testine göre ayarlanır. Montaj ölçüleri mm. Resmi ölçekle ölçmek yerine rakamları ve STEP geometrisini kullanın.',900,y,245,8.5,12)
        c.showPage()
    c.save()
    with (ROOT/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['Parca','Adet','Aciklama']);w.writerows(BOM)
    import fitz
    doc=fitz.open(out)
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(ROOT/'drawings'/f'sayfa-{i+1:02d}.png')
    print('PDF_READY',len(doc),'pages',flush=True)

if __name__=='__main__':main()
