"""OPTIK R0.1: camera + Class 1 light demonstrator. No projectile hardware.

Run in the task venv. Manufacturer dimensions and design assumptions are
recorded separately in the engineering notes; this is a prototype, not a
physically qualified assembly.
"""
from pathlib import Path
import json, math, sys
from geometry import *
from render import render

ROOT=Path(__file__).parent
for d in ('cad','stl','images','drawings','checks'): (ROOT/d).mkdir(exist_ok=True)
parts={}; spec=[]; assembly=[]

def add(code,name,shape,note,color='#307f8a',qty=1,print_axis='Z',features=()):
    print('BUILD',code,name,flush=True)
    s=shape
    bbox=bounds(s); dx,dy,dz=[bbox[i+3]-bbox[i] for i in range(3)]
    stem=ROOT/'cad'/code
    out=save(s,stem)
    printable=out.copy()
    import trimesh
    if print_axis in ('X','Y','-Z'):
        axis={'X':(0,1,0),'Y':(1,0,0),'-Z':(1,0,0)}[print_axis]
        angle=180 if print_axis=='-Z' else 90
        printable.apply_transform(trimesh.transformations.rotation_matrix(math.radians(angle),axis))
    pb=printable.bounds; printable.apply_translation((-(pb[0,0]+pb[1,0])/2,-(pb[0,1]+pb[1,1])/2,-pb[0,2]))
    printable.export(ROOT/'stl'/f'{code}.stl')
    (ROOT/'cad'/f'{code}.stl').unlink()
    render([(s,color)],ROOT/'images'/f'{code}.png',f'{code}  /  {name}',note)
    parts[code]=s
    spec.append(dict(code=code,name=name,qty=qty,note=note,color=color,bbox=list(bbox),size=[dx,dy,dz],
      volume_mm3=volume(s),watertight=out.is_watertight,cad_valid=True,print_axis=print_axis,print_size=list(printable.extents),features=features))
    (ROOT/'parts.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
    return s

def base():
    # Base outer 190 x 150; removable lid datum Z=30. Wall 3, floor 6.
    s=rounded_rect(190,150,30,12,(10,0,15))
    s=cut(s,rounded_rect(184,144,30,9,(10,0,21)))
    for x in (-73,93):
      for y in (-63,63):
        s=fuse(s,cyl(6,24,(x,y,18)))
        s=holes(s,[(x,y,27.5)],4.4,5)
    # Four bench mounting positions and pedestal attachment pattern.
    s=holes(s,[(x,y,3) for x in (-63,83) for y in (-53,53)],4.5,20)
    s=holes(s,[(x,y,3) for x in (-22,22) for y in (-22,22)],4.5,20)
    s=holes(s,[(59.35+x,y,3) for x in (-26.5,26.5) for y in (-12,12)],3.5,20)
    for x in (-34,82):
      for y in (-32,32):
        s=fuse(s,cyl(4.5,24,(x,y,18)))
        s=holes(s,[(x,y,27.5)],4.4,5)
    # Rear cable cutout; lower corners stay above the floor.
    s=cut(s,rounded_rect(18,16,14,3,(55,72,16)))
    # Small cable-tie holes; board retention doesn't assume an unknown devkit PCB.
    s=holes(s,[(x,y,3) for x in (-40,0,40) for y in (-40,-30)],3,20)
    return s

def lid():
    s=rounded_rect(190,150,3,12,(10,0,31.5))
    s=holes(s,[(x,y,31.5) for x in (-73,93) for y in (-63,63)],3.4,20)
    s=holes(s,[(0,0,31.5)],36.8,20)
    s=cut(s,rounded_rect(62,32,20,3,(59.35,0,31.5)))
    # Electronics cooling: five rounded slots, remote from all fasteners.
    s=cut(s,*[slot(34,3,20,(x,-46,31.5),along='y') for x in (-40,-30,-20,-10,0)])
    # Guard columns fasten through the cover into captured nuts / insert bosses.
    s=holes(s,[(x,y,31.5) for x in (-34,82) for y in (-32,32)],3.4,20)
    return s

def head_body():
    # Local frame: optical direction -Y; tilt axis X through (0,0,0).
    s=rounded_rect(96,36,46,5,(0,0,0))
    # rounded_rect rounds in XY. Rear is completely open for service.
    s=cut(s,box(90,38,40,(0,4,0)))
    for x in (-42.5,42.5):
      for z in (-17.5,17.5):
        s=fuse(s,box(7,33,7,(x,1.5,z)))
        s=holes(s,[(x,15.5,z)],4.4,5,axis=(0,1,0))
    # Circular trunnions carry only this small optical housing.
    s=fuse(s,*[cyl(11,12,(x,0,0),axis=(1,0,0)) for x in (-48,48)])
    s=holes(s,[(0,0,0)],8.5,140,axis=(1,0,0))
    s=cut(s,hex_prism(13.3,6,(-44,0,0),axis=(1,0,0)))
    s=cut(s,box(37,12,25,(-15,-18,0)))
    s=holes(s,[(26,-18,0)],11,12,axis=(0,1,0))
    s=holes(s,[(x,-16.5,z) for x in (-35.5,5.5) for z in (-14.5,14.5)],2.9,12,axis=(0,1,0))
    # Class 1 module clamp: posts rise from the bottom; M2.5 inserts face +Z.
    for x in (19.5,32.5):
        s=fuse(s,box(5,20,14,(x,0,-13)))
        s=holes(s,[(x,0,-8.5)],3.6,5)
    # Right joint uses a D8 shoulder screw with M6 thread, not M8 threading.
    s=cut(s,hex_prism(10.3,6,(44,0,0),axis=(1,0,0)))
    # Optical-head hard-stop lug; no payload attachment interface.
    s=fuse(s,box(7.4,8,5,(51.7,12,0)),cyl(2.5,7.4,(51.7,14,0),axis=(1,0,0)))
    return s

def camera_cassette():
    s=box(47,3,35,(-15,-13.5,0))
    s=cut(s,box(36.1,2.2,24.3,(-15,-12.9,0)),box(32,8,20,(-15,-13.5,0)))
    s=holes(s,[(x,-13.5,z) for x in (-35.5,5.5) for z in (-14.5,14.5)],2.9,12,axis=(0,1,0))
    return s

def camera_backframe():
    s=cut(box(47,1.5,35,(-15,-11.25,0)),box(32,8,20,(-15,-11.25,0)))
    return holes(s,[(x,-11.25,z) for x in (-35.5,5.5) for z in (-14.5,14.5)],2.9,10,axis=(0,1,0))

def rear_cover():
    s=rounded_rect(96,3,46,1.0,(0,19.5,0))
    s=holes(s,[(x,19.5,z) for x in (-42.5,42.5) for z in (-17.5,17.5)],3.4,20,axis=(0,1,0))
    s=cut(s,box(14,20,7,(0,19.5,-19.5)))
    # Backplate vents don't intersect the mounting seats.
    for x in (-24,-12,0,12,24): s=cut(s,box(3,20,16,(x,19.5,4)))
    return s

def laser_clamp(upper=False):
    if upper:
        s=box(18,16,6,(26,0,3.2))
        s=cut(s,cyl(4.15,24,(26,0,0),axis=(0,1,0)))
        return holes(s,[(x,0,3.2) for x in (19.5,32.5)],2.9,20)
    s=box(18,16,6,(26,0,-3))
    s=cut(s,cyl(4.15,24,(26,0,0),axis=(0,1,0)))
    return holes(s,[(x,0,-3) for x in (19.5,32.5)],2.9,20)

def pedestal():
    s=fuse(rounded_rect(58,58,6,5,(0,0,9)),box(40,32,18,(0,0,21)),cyl(18,17,(0,0,38.5)))
    s=cut(s,box(30,24,23,(0,0,17.5)),box(30,30,10,(0,-20,11)),cyl(9,24,(0,0,37)))
    s=cut(s,cyl(11.075,7,(0,0,43.5)),box(24,20,8,(0,18,36)))
    s=holes(s,[(x,y,9) for x in (-22,22) for y in (-22,22)],4.5,20)
    s=holes(s,[(x,-26,9) for x in (-18,18)],2.2,6,axis=(0,1,0))
    for a in (0,120,240):
        p=(14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a)),44.5)
        s=holes(s,[p],4.4,5)
    return s

def bearing_cap():
    s=cut(cyl(18,12,(0,0,53)),cyl(9,20,(0,0,53)),cyl(11.075,7,(0,0,55.5)))
    return holes(s,[(14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a)),53) for a in (0,120,240)],3.4,30)

def encoder_drawer():
    s=rounded_rect(28,22,3,2,(0,0,7.5))
    s=fuse(s,box(28,18,3,(0,-20,7.5)),box(44,3,8,(0,-30.5,10)))
    for x in (-10.16,10.16):
      for y in (-6.35,6.35):
        s=fuse(s,cyl(2.7,1.5,(x,y,9.75)))
        s=holes(s,[(x,y,9)],3.6,3)
    # Drawer fastening to two M2.5 self-tapped holes in the front flange.
    s=holes(s,[(x,-30.5,9) for x in (-18,18)],2.9,10,axis=(0,1,0))
    return s

def servo_pedestal():
    center=59.35
    lower=cut(rounded_rect(62,32,5,3,(center,0,8.5)),box(44,20,12,(center,0,8.5)))
    top=cut(rounded_rect(62,32,5,3,(center,0,45.4)),box(41.3,20.3,12,(center,0,45.4)))
    legs=[box(6,6,31.9,(center+x,y,26.95)) for x in (-26.5,26.5) for y in (-12,12)]
    s=fuse(lower,top,*legs)
    s=cut(s,*[slot(7,4.3,12,(center+x,y,45.4)) for x in (-24.5,24.5) for y in (-5,5)])
    s=holes(s,[(center+x,y,8.5) for x in (-26.5,26.5) for y in (-12,12)],4.4,5)
    return s

def drive_gear():
    s=gear(30)
    s=holes(s,[(0,0,4)],7,20)
    for a in (0,90,180,270):
        q=slot(6,2.9,20,(8,0,4)); s=cut(s,rotate(q,(0,0,1),a))
    return translate(s,(49.5,0,67))

def pan_gear():
    s=gear(36,phase=5)
    s=holes(s,[(0,0,4)],8.5,20)
    s=holes(s,[(14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a)),4) for a in (0,120,240)],3.4,20)
    return translate(s,(0,0,67))

def rotor():
    s=fuse(cyl(18,19,(0,0,84.5)),cyl(46,6,(0,0,97)),cyl(3,6,(38,0,91)))
    s=holes(s,[(0,0,85)],8.1,60)
    s=cut(s,box(.8,19,14,(0,9.5,87)))
    s=holes(s,[(0,12,85)],3.4,60,axis=(1,0,0))
    s=cut(s,hex_prism(5.8,3,(-13.5,12,85),axis=(1,0,0)))
    for a in (0,120,240):
        p=(14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a)),77.5)
        s=holes(s,[p],4.4,5)
    for x in (-26,26):
      for y in (-26,26):
        s=holes(s,[(x,y,97)],3.4,20)
        s=cut(s,hex_prism(5.8,2.7,(x,y,95.35)))
    return s

def bridge():
    s=rounded_rect(168,90,6,6,(0,0,103))
    s=holes(s,[(0,0,103)],10.5,20)
    s=holes(s,[(x,y,103) for x in (-26,26) for y in (-26,26)],3.4,20)
    return holes(s,[(x,y,103) for x in (-74,74) for y in (-30,30)],4.5,20)

def arm(left=True):
    x=-65 if left else 59
    if left: outline=[(-42,112),(42,112),(42,174),(19,222),(-19,222),(-42,174)]
    else: outline=[(-20,112),(20,112),(18,222),(-18,222)]
    s=prism([(x,y,z) for y,z in outline],(6,0,0))
    side=-1 if left else 1
    s=fuse(s,rounded_rect(32,90,6,4,(side*68,0,109)),cyl(17,11,(side*61.5,0,205),axis=(1,0,0)))
    s=holes(s,[(side*74,y,109) for y in (-30,30)],4.5,20)
    s=holes(s,[(side*62,0,205)],8.5,40,axis=(1,0,0))
    s=cut(s,cyl(11.075,9,(side*62.5,0,205),axis=(1,0,0)))
    if left:
        frame=cut(box(6,84,44,(-92,0,155.5)),box(12,41.3,20.3,(-92,9.85,155.5)))
        # Mounting slots are deliberately wider than a nominal clone hole pattern.
        frame=cut(frame,*[slot(7,4.3,16,(-92,y,155.5+z),axis=(1,0,0),along='y') for y in (-14.65,34.35) for z in (-5,5)])
        s=fuse(s,frame,*[box(24,6,27,(-77,y,155.5)) for y in (-36,36)])
    else:
        for y in (-10.16,10.16):
          for z in (-6.35,6.35):
            s=fuse(s,cyl(3,13,(73.5,y,205+z),axis=(1,0,0)))
            s=holes(s,[(78.5,y,205+z)],3.6,3,axis=(1,0,0))
        offset=90+math.degrees(2*math.asin(5/28))
        for a in (-offset,offset):
            s=fuse(s,cyl(2.5,1.2,(55.4,14*math.cos(math.radians(a)),205+14*math.sin(math.radians(a))),axis=(1,0,0)))
    return s

def tilt_output():
    s=gear(36,phase=5)
    s=holes(s,[(0,0,4)],8.5,20)
    s=cut(s,hex_prism(13.3,5.4,(0,0,2.7)))
    return translate(rotate(s,(0,1,0),90),(-76,0,205))

def tilt_driver():
    s=translate(drive_gear(),(-49.5,0,-67))
    return translate(rotate(s,(0,1,0),90),(-76,0,155.5))

def guard():
    roof=rounded_rect(128,76,3,6,(24,0,79.5))
    wall=cut(rounded_rect(128,76,14,6,(24,0,71)),rounded_rect(122,70,20,3,(24,0,71)))
    legs=[cyl(3.5,45,(x,y,55.5)) for x in (-34,82) for y in (-32,32)]
    s=fuse(roof,wall,*legs)
    s=holes(s,[(0,0,79)],38,20)
    s=holes(s,[(49.5,0,79)],9,20)
    s=holes(s,[(x,y,55.5) for x in (-34,82) for y in (-32,32)],3.4,70)
    offset=90+math.degrees(2*math.asin(6/76))
    for a in (-offset,offset):
        s=fuse(s,cyl(3,12.7,(38*math.cos(math.radians(a)),38*math.sin(math.radians(a)),87.35)))
    return s

def pan_magnet_cup():
    s=cyl(6,10,(0,0,20.4))
    s=cut(s,cyl(3.05,2.6,(0,0,16.7)),cyl(4.1,4,(0,0,23.4)))
    return s

def tilt_magnet_cup():
    s=cyl(8,9.7,(71.85,0,205),axis=(1,0,0))
    s=cut(s,cyl(6.6,5.6,(69.8,0,205),axis=(1,0,0)),cyl(3.05,2.6,(75.4,0,205),axis=(1,0,0)))
    return s

def encoder_cover():
    s=box(3,34,27,(83.1,0,205))
    return holes(s,[(83.1,y,205+z) for y in (-10.16,10.16) for z in (-6.35,6.35)],2.9,20,axis=(1,0,0))

if __name__=='__main__':
    add('P01','Elektronik taban',base(),'190 x 150 x 30 mm / 3 mm duvar / 6 mm taban',
      features=['Dis olcu 190 x 150 x 30','R12 dis kose','4x M3 insert yuvasi D4.4 x 5','4x tezgah deligi D4.5 / 146 x 106 aralik'])
    if '--first' in sys.argv: sys.exit(0)
    add('P02','Servis kapagi',lid(),'190 x 150 x 3 mm / sokulebilir / kablo ve havalandirma acikliklari',
      color='#374e58',features=['4x D3.4 / 166 x 126 aralik','D32.6 merkez acikligi','62 x 32 servo servis acikligi'])
    add('P03','Optik baslik govdesi',head_body(),'OV5640 + D8 mm Class 1 isik modulu / yalniz optik yuk',
      features=['96 x 36 x 46 ana govde','D8.5 iki yan mil deligi','M8 somun cebi AF13.3','4x M3 insert D4.4 x 5', '37 x 25 kamera penceresi'])
    add('P04','Kamera kaseti',camera_cassette(),'Waveshare OV5640 Board A / 36.1 x 24.3 mm PCB oturma cebi',
      print_axis='Y',features=['PCB nominali 35.7 x 23.9','32 x 20 optik aciklik','4x D2.9 / 41 x 29 aralik'])
    add('P05','Kamera baski cercevesi',camera_backframe(),'1.5 mm baski cercevesi / 0.5 mm ince kopuk ara katman',
      color='#374e58',print_axis='Y',features=['47 x 35 x 1.5','4x D2.9','Konektor acikligi fiziksel PCB ile dogrulanacak'])
    add('P06','Baslik arka kapagi',rear_cover(),'Kablo cikisi + sogutma / 4 adet M3 vida',
      color='#374e58',print_axis='Y',features=['4x D3.4 / 85 x 35 aralik','14 x 7 kablo cikisi'])
    add('P07','Isik alt yatagi',laser_clamp(False),'Picotronic D8 x 21 mm govde / D8.30 yatak',
      features=['18 x 16 x 6','D8.30 yari kanal','2x D2.9 / 13 aralik'])
    add('P08','Isik ust kelepcesi',laser_clamp(True),'Iki M2.5 ile kapatma / optik govdeye baskiyi sinirla',
      color='#374e58',features=['18 x 16 x 6','D8.30 yari kanal','0.2 mm kelepce araligi'])
    add('P09','Pan rulman kulesi',pedestal(),'608 yatak / enkoder erisimi / 4 adet M4 taban baglantisi',
      features=['58 x 58 taban','4x D4.5 / 44 x 44 aralik','Alt 608 cebi D22.15 x 7 / Z40-47','3x M3 insert / PCD29'])
    add('P10','Ust rulman kartusu',bearing_cap(),'Ikinci 608 rulman / iki yatak arasinda 12 mm merkez mesafesi',
      color='#374e58',features=['D36 x 12','608 cebi D22.15 x 7','3x D3.4 / PCD29'])
    add('P11','Pan enkoder cekmecesi',encoder_drawer(),'Adafruit AS5600 #6357 / uretici PCB deliklerine gore',
      features=['PCB 25.4 x 17.78','4x M2.5 insert / 20.32 x 12.70 aralik','PCB alt duzlemi Z10.5'])
    add('P12','Pan servo sehpası',servo_pedestal(),'MG996R govde oturma acikligi / uzun montaj delikleri',
      features=['Gövde penceresi 41.3 x 20.3','Kulak yuzeyi Z47.9','Nominal kulak vida araligi 49 x 10, slot ile ayar','Alt 4x insert D4.4 x 5'])
    add('P13','Servo tahrik dislisi',drive_gear(),'30 dis / modul 1.5 / 20 derece / stok servo hornuna vidalanir',
      color='#db9e52',qty=2,features=['m1.5 / z30 / basinc acisi 20','Dis genisligi 8','Stok horn: 4 radyal slot 6 x 2.9','0.18 mm dis kalinligi azaltma'])
    add('P14','Pan cikis dislisi',pan_gear(),'36 dis / 49.5 mm eksen araligi / cikis hiz orani 5:6',
      color='#db9e52',features=['m1.5 / z36 / basinc acisi 20','3x D3.4 / PCD29','D8.5 merkez deligi'])
    add('P15','Pan doner tasiyici',rotor(),'D8 mil sikma gobegi / kamera koprusu / mekanik hareket durdurucu',
      features=['D92 x 6 ust flans','D8.10 mil cebi','M3 capraz sikma civatasi','4x M3 / 52 x 52 aralik','3x insert / PCD29'])
    add('P16','Optik platform koprusu',bridge(),'168 x 90 x 6 mm / iki dikme / yalniz kamera ve isik basligi',
      features=['4x D3.4 / 52 x 52 aralik','Dikme delikleri D4.5 / 148 x 60 aralik'])
    add('P17','Sol hareket dikmesi',arm(True),'Tilt servosu + 608 yatagi / yan yuzeyi baski tablasina',
      print_axis='X',features=['Tilt ekseni Z205','Motor ekseni Z155.5','49.5 mm disli eksen araligi','608 cebi D22.15 x 9','Slotlu servo montaji'])
    add('P18','Sag sensor dikmesi',arm(False),'608 yatak / AS5600 sabit montaji / +-90 derece durdurucular',
      print_axis='X',features=['Tilt ekseni Z205','608 cebi D22.15 x 9','AS5600: 20.32 x 12.70 aralik','PCB alt duzlemi X80'])
    add('P19','Tilt cikis dislisi',tilt_output(),'36 dis / M8 baslik yakalama / standart 8 mm omuzlu baglanti',
      color='#db9e52',print_axis='X',features=['m1.5 / z36 / dis genisligi 8','M8 alti kose baslik cebi AF13.3 x 5.4'])
    add('P20','Pan aktarim muhafazasi',guard(),'Dislileri orter / iki mekanik durdurucu / kapak asagi basilir',
      color='#374e58',print_axis='-Z',features=['128 x 76 dis cevre','4x D3.4 uzun baglanti','D38 doner gobek boslugu','+-90 derece mekanik sinir'])
    add('P21','Pan miknatis adaptoru',pan_magnet_cup(),'Cap boyunca kutuplanmis D6 x 2.5 miknatis / mile yapistirma',
      features=['D12 x 10','Miknatis cebi D6.10 x 2.6','Mil cebi D8.2 x 4'])
    add('P22','Tilt miknatis adaptoru',tilt_magnet_cup(),'D8 omuz civatasi basligina gecme / D6 x 2.5 capsal miknatis',
      print_axis='X',features=['D16 x 9.7','Baslik cebi D13.2 x 5.6','Miknatis cebi D6.10 x 2.6'])
    add('P23','Enkoder dis kapagi',encoder_cover(),'AS5600 PCB arka yuzu / 4 adet M2.5 baglanti',
      color='#374e58',print_axis='X',features=['34 x 27 x 3','4x D2.9 / 20.32 x 12.70 aralik'])

    # Neutral assembly transforms. Part CAD stays editable in these datums.
    for rec in spec:
        code=rec['code']; s=parts[code]
        if code in ('P03','P04','P05','P06','P07','P08'): s=translate(s,(0,0,205))
        assembly.append((s,rec['color'],code))
    assembly.append((tilt_driver(),'#db9e52','P13b'))
    # Purchased item envelopes: body dimensions are indicative; mounting awaits fit check.
    purchased=[]
    pan_servo=fuse(box(40.7,19.7,37,(59.35,0,39.6)),box(54,19.7,2.5,(59.35,0,49.15)),cyl(3,5.7,(49.5,0,61.15)))
    purchased.append((pan_servo,'#29353b','MG996R-pan'))
    tilt_servo=translate(rotate(translate(pan_servo,(-49.5,0,-21.1)),(1,1,1),120),(-121.7,0,155.5))
    purchased.append((tilt_servo,'#29353b','MG996R-tilt'))
    for z in (43.5,55.5): purchased.append((cut(cyl(11,7,(0,0,z)),cyl(4,10,(0,0,z))),'#a7b3b7','608-pan'))
    for x in (-61.5,61.5): purchased.append((cut(cyl(11,7,(x,0,205),axis=(1,0,0)),cyl(4,10,(x,0,205),axis=(1,0,0))),'#a7b3b7','608-tilt'))
    purchased.append((cyl(4,86,(0,0,64.4)),'#a7b3b7','Pan-shaft-D8'))
    purchased.append((box(35.7,1.6,23.9,(-15,-13.2,205)),'#287341','OV5640-PCB'))
    purchased.append((cyl(5,10,(-15,-19,205),axis=(0,1,0)),'#182a34','Lens-envelope'))
    purchased.append((cyl(4,21,(26,0,205),axis=(0,1,0)),'#9b5551','Class1-module'))
    purchased.append((box(25.4,17.78,1.6,(0,0,11.3)),'#287341','AS5600-pan-PCB'))
    purchased.append((box(1.6,25.4,17.78,(80.8,0,205)),'#287341','AS5600-tilt-PCB'))
    allitems=[(s,c) for s,c,_ in assembly+purchased]
    render(allitems,ROOT/'images'/'montaj.png','OPTIK  /  Kamera ve isik platformu','R0.1 / 2 eksen / D8 miller / 608 yataklar / AS5600 geri bildirim',elev=21,azim=-62)
    # OpenCascade compound STEP retains the actual assembly positions.
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    compound=TopoDS_Compound(); builder=BRep_Builder(); builder.MakeCompound(compound)
    for shape,_,_ in assembly+purchased: builder.Add(compound,shape)
    sw=STEPControl_Writer(); sw.Transfer(compound,STEPControl_AsIs); sw.Write(str(ROOT/'cad'/'OPTIK-montaj.step'))
    print('ASSEMBLY_READY',flush=True)
