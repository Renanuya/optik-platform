"""OPTIK R0.2: camera + Class 1 light demonstrator. No projectile hardware.

Run in the task venv. Manufacturer dimensions and design assumptions are
recorded separately in the engineering notes; this is a prototype, not a
physically qualified assembly.
"""
from pathlib import Path
import json, math, sys
from geometry import *
from render import render

# R0.2: M2 assembly, protected wiring gap and removable outer shells.
FLANGE_LIFT=20
UPPER_LIFT=22
TILT_Z=205+UPPER_LIFT
MOUNT_DIAMETER_MAP={3.4:2.4,3.5:2.4,4.4:3.1,4.5:2.4,3.6:3.1,2.9:2.4,2.6:2.2,2.2:1.7}
_raw_holes=holes
_raw_slot=slot
_raw_hex=hex_prism
def holes(s,points,d,depth=100,axis=(0,0,1)):
    return _raw_holes(s,points,MOUNT_DIAMETER_MAP.get(d,d),depth,axis)
def slot(length,width,depth,c,axis=(0,0,1),along='x'):
    return _raw_slot(length,{4.3:2.5,2.9:2.4}.get(width,width),depth,c,axis,along)
def hex_prism(flat,h,c,axis=(0,0,1)):
    return _raw_hex(4.2 if flat==5.8 else flat,h,c,axis)

ROOT=Path(__file__).parent
for d in ('cad','stl','images','drawings','checks'): (ROOT/d).mkdir(exist_ok=True)
parts={}; spec=[]; assembly=[]

def add(code,name,shape,note,color='#307f8a',qty=1,print_axis='Z',features=()):
    print('BUILD',code,name,flush=True)
    s=shape
    lift=UPPER_LIFT if code in ('P17','P18','P19','P22','P23') else (FLANGE_LIFT if code=='P16' else 0)
    if lift:s=translate(s,(0,0,lift))
    def label(t):
        for a,b in [('M2.5','M2'),('M3','M2'),('M4','M2'),('D4.4','D3.1'),('D4.5','D2.4'),('D3.4','D2.4'),('D3.6','D3.1'),('D2.9','D2.4')]:t=t.replace(a,b)
        if code in ('P17','P18'):t=t.replace('Z205',f'Z{TILT_Z}').replace('Z155.5',f'Z{155.5+UPPER_LIFT}')
        return t
    note=label(note);features=[label(t) for t in features]
    bbox=bounds(s); dx,dy,dz=[bbox[i+3]-bbox[i] for i in range(3)]
    stem=ROOT/'cad'/code
    out=save(s,stem)
    printable=out.copy()
    import trimesh
    if print_axis in ('X','Y','-X','-Y','-Z'):
        axis={'X':(0,1,0),'-X':(0,1,0),'Y':(1,0,0),'-Y':(1,0,0),'-Z':(1,0,0)}[print_axis]
        angle=180 if print_axis=='-Z' else (-90 if print_axis.startswith('-') else 90)
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
    s=_raw_holes(s,[(55,74,17)],24,20,axis=(0,1,0))
    s=_raw_holes(s,[(-55,74,17)],10,20,axis=(0,1,0))
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
    s=holes(s,[(32,-18,0)],11,12,axis=(0,1,0))
    s=holes(s,[(x,-16.5,z) for x in (-35.5,5.5) for z in (-14.5,14.5)],2.9,12,axis=(0,1,0))
    # Class 1 module clamp: posts rise from the bottom; M2.5 inserts face +Z.
    for x in (25.5,38.5):
        s=fuse(s,box(5,20,14,(x,0,-13)))
        s=holes(s,[(x,0,-8.5)],3.6,5)
    # Right joint uses a D8 shoulder screw with M6 thread, not M8 threading.
    s=cut(s,hex_prism(10.3,6,(44,0,0),axis=(1,0,0)))
    s=holes(s,[(0,12,-23)],8,10)
    # Optical-head hard-stop lug; no payload attachment interface.
    s=fuse(s,box(7.4,5.5,4.4,(51.7,10.75,0)),cyl(2.5,7.4,(51.7,14,0),axis=(1,0,0)))
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
    # Electronics backpack: short DVP wiring stays near the camera.
    s=cut(rounded_rect(96,30,46,4,(0,33,0)),box(90,33,40,(0,28.5,0)))
    for x in (-42.5,42.5):
      for z in (-17.5,17.5):s=fuse(s,box(7,30,7,(x,33,z)))
    s=holes(s,[(x,33,z) for x in (-42.5,42.5) for z in (-17.5,17.5)],3.4,40,axis=(0,1,0))
    for x in (-24,-12,0,12,24): s=cut(s,box(3,10,14,(x,47,4)))
    for x in (-37,37):
        s=fuse(s,cyl(4,9,(x,40.5,0),axis=(0,1,0)))
        s=holes(s,[(x,38.5,0)],4.4,5,axis=(0,1,0))
    return s

def laser_clamp(upper=False):
    if upper:
        s=box(18,16,6,(32,0,3.2))
        s=cut(s,cyl(4.15,24,(32,0,0),axis=(0,1,0)))
        return holes(s,[(x,0,3.2) for x in (25.5,38.5)],2.9,20)
    s=box(18,16,6,(32,0,-3))
    s=cut(s,cyl(4.15,24,(32,0,0),axis=(0,1,0)))
    return holes(s,[(x,0,-3) for x in (25.5,38.5)],2.9,20)

def pedestal():
    s=fuse(rounded_rect(56,56,6,5,(0,0,9)),box(40,32,18,(0,0,21)),cyl(18,17,(0,0,38.5)))
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
    s=fuse(cyl(18,19+FLANGE_LIFT,(0,0,84.5+FLANGE_LIFT/2)),cyl(60,6,(0,0,97+FLANGE_LIFT)),cyl(3,6,(52,0,91+FLANGE_LIFT)))
    s=fuse(s,box(10,10,12,(-14,12,88)),box(10,10,12,(14,12,88)))
    s=holes(s,[(0,0,95)],8.1,100)
    s=cut(s,box(.8,19,14+FLANGE_LIFT,(0,9.5,87+FLANGE_LIFT/2)))
    for z in (85.5,90.5):
      s=holes(s,[(0,12,z)],3.4,60,axis=(1,0,0))
      s=cut(s,hex_prism(5.8,2.2,(-17.9,12,z),axis=(1,0,0)))
    for a in (0,120,240):
        p=(14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a)),77.5)
        s=holes(s,[p],4.4,5)
    for x in (-26,26):
      for y in (-26,26):
        s=holes(s,[(x,y,97+FLANGE_LIFT)],3.4,20)
        s=cut(s,hex_prism(5.8,2.2,(x,y,95.1+FLANGE_LIFT)))
    s=cut(s,rounded_rect(16,10,12,2,(0,25,97+FLANGE_LIFT)))
    return s

def bridge():
    s=rounded_rect(168,90,8,6,(0,0,104))
    s=holes(s,[(0,0,104)],10.5,20)
    s=holes(s,[(x,y,104) for x in (-26,26) for y in (-26,26)],3.4,20)
    s=holes(s,[(x,y,104) for x in (-74,74) for y in (-30,30)],4.5,20)
    s=cut(s,rounded_rect(16,10,20,2,(0,25,104)))
    s=cut(s,box(118,12,4.6,(0,14,102.2)),box(12,23,4.6,(0,19.5,102.2)),box(12,26,4.6,(-59,21,102.2)),box(12,16,4.6,(59,13,102.2)))
    s=_raw_holes(s,[(-59,28,104),(59,12,104)],8.5,20)
    return s

def arm(left=True):
    x=-65 if left else 59
    if left: outline=[(-45,112),(45,112),(45,174),(24,222),(-24,222),(-45,174)]
    else: outline=[(-25,112),(25,112),(25,180),(22,214),(20,225),(-20,225),(-22,214),(-25,180)]
    s=prism([(x,y,z) for y,z in outline],(6,0,0))
    side=-1 if left else 1
    s=fuse(s,rounded_rect(32,90,6,4,(side*68,0,109)),cyl(17,11,(side*61.5,0,205),axis=(1,0,0)))
    s=holes(s,[(side*74,y,109) for y in (-30,30)],4.5,20)
    # Relief around the rotating inner-race spacers; plastic must not rub OD12 spacers.
    s=holes(s,[(side*62,0,205)],12.4,40,axis=(1,0,0))
    s=cut(s,cyl(11.075,9,(side*62.5,0,205),axis=(1,0,0)))
    # Enclosure attachment inserts and wiring channels.
    mounts=[(-20,120),(20,120),(-20,217),(20,217)] if left else [(-21.5,120),(21.5,120),(-16,220),(16,220)]
    for y,z in mounts:s=holes(s,[(side*61.5,y,z)],4.4,5,axis=(1,0,0))
    yy=28 if left else 12;top=175 if left else 185
    s=cut(s,box(2.2,8,top-110,(side*60,yy,(110+top)/2)))
    s=holes(s,[(side*59,yy,109)],8,12)
    s=holes(s,[(side*62,yy,top-3)],6,30,axis=(1,0,0))
    if left:
        frame=cut(box(6,90,44,(-98,0,155.5)),box(12,41.3,20.3,(-98,9.85,155.5)))
        # Mounting slots are deliberately wider than a nominal clone hole pattern.
        frame=cut(frame,*[slot(7,4.3,16,(-98,y,155.5+z),axis=(1,0,0),along='y') for y in (-14.65,34.35) for z in (-5,5)])
        s=fuse(s,frame,*[box(30,6,27,(-80,y,155.5)) for y in (-41,41)])
    else:
        for y in (-10.16,10.16):
          for z in (-6.35,6.35):
            s=fuse(s,cyl(3,13,(73.5,y,205+z),axis=(1,0,0)))
            s=holes(s,[(76.5,y,205+z)],2.6,7,axis=(1,0,0))
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
    return translate(rotate(s,(0,1,0),90),(-76,0,155.5+UPPER_LIFT))

def guard():
    roof=rounded_rect(128,76,3,6,(24,0,79.5))
    wall=cut(rounded_rect(128,76,14,6,(24,0,71)),rounded_rect(122,70,20,3,(24,0,71)))
    legs=[cyl(3.5,45,(x,y,55.5)) for x in (-34,82) for y in (-32,32)]
    s=fuse(roof,wall,*legs)
    s=holes(s,[(0,0,79)],38,20)
    s=holes(s,[(49.5,0,79)],9,20)
    s=holes(s,[(x,y,55.5) for x in (-34,82) for y in (-32,32)],3.4,70)
    offset=90+math.degrees(2*math.asin(8/104))
    for a in (-offset,offset):
        px,py=52*math.cos(math.radians(a)),52*math.sin(math.radians(a))
        s=fuse(s,rounded_rect(24,34,3,6,(px,math.copysign(45,py),79.5)),box(6,28,12,(px,math.copysign(45,py),72)),cyl(5,12.7+FLANGE_LIFT,(px,py,87.35+FLANGE_LIFT/2)))
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

def fit_coupon():
    s=rounded_rect(120,62,8,4,(0,0,4))
    for x,d in zip((-42,-14,14,42),(21.95,22.05,22.15,22.25)):
        s=holes(s,[(x,12,4)],d,20)
    for x,d in zip((-48,-32,-16,0),(7.95,8.05,8.15,8.30)):
        s=holes(s,[(x,-17,4)],d,20)
    for x,d in zip((20,32,44),(2.8,3.0,3.1)):s=_raw_holes(s,[(x,-17,4)],d,20)
    for x,d in zip((20,32,44),(1.9,2.1,2.4)):s=_raw_holes(s,[(x,-5,4)],d,20)
    return s

def esp_carrier():
    s=cut(box(68,3,34,(0,34.5,0)),box(58,12,24,(0,34.5,0)))
    s=fuse(s,*[cyl(4,3,(x,34.5,0),axis=(0,1,0)) for x in (-37,37)])
    s=_raw_holes(s,[(x,34.5,0) for x in (-37,37)],2.4,12,axis=(0,1,0))
    s=cut(s,*[box(8,12,2,(x,34.5,z)) for x in (-20,20) for z in (-15,15)])
    return s

if __name__=='__main__':
    add('P01','Elektronik taban',base(),'190 x 150 x 30 mm / 3 mm duvar / 6 mm taban',
      features=['Dis olcu 190 x 150 x 30','R12 dis kose','8x M3 insert yuvasi D4.4 x 5','4x tezgah deligi D4.5 / 146 x 106 aralik','Kule: 4x D4.5 / 44 x 44 aralik'])
    if '--first' in sys.argv: sys.exit(0)
    add('P02','Servis kapagi',lid(),'190 x 150 x 3 mm / sokulebilir / kablo ve havalandirma acikliklari',
      color='#374e58',features=['4x D3.4 / 166 x 126 aralik','D36.8 merkez acikligi','62 x 32 servo servis acikligi'])
    add('P03','Optik baslik govdesi',head_body(),'OV5640 + D8 mm Class 1 isik modulu / yalniz optik yuk',print_axis='Y',
      features=['96 x 36 x 46 ana govde','D8.5 iki yan mil deligi','Sol AF13.3 / sag AF10.3 somun cebi','4x M3 insert D4.4 x 5', '37 x 25 kamera penceresi'])
    add('P04','Kamera kaseti',camera_cassette(),'Waveshare OV5640 Board A / 36.1 x 24.3 mm PCB oturma cebi',
      print_axis='Y',features=['PCB nominali 35.7 x 23.9','32 x 20 optik aciklik','4x D2.9 / 41 x 29 aralik'])
    add('P05','Kamera baski cercevesi',camera_backframe(),'1.5 mm baski cercevesi / 0.5 mm ince kopuk ara katman',
      color='#374e58',print_axis='Y',features=['47 x 35 x 1.5','4x D2.9','Konektor acikligi fiziksel PCB ile dogrulanacak'])
    add('P06','Elektronik sirt kapagi',rear_cover(),'Kisa kamera baglantisi / ESP kaseti / 4 adet M2 vida',
      color='#374e58',print_axis='Y',features=['96 x 30 x 46 / on yuz Y18','4x D2.4 / 85 x 35 aralik','ESP tasiyici baglantisi: 2x M2','Kontrol karti modeli dogrulanacak'])
    add('P07','Isik alt yatagi',laser_clamp(False),'Picotronic D8 x 21 mm govde / D8.30 yatak',
      features=['18 x 16 x 6','D8.30 yari kanal','2x D2.9 / 13 aralik'])
    add('P08','Isik ust kelepcesi',laser_clamp(True),'Iki M2.5 ile kapatma / optik govdeye baskiyi sinirla',
      color='#374e58',features=['18 x 16 x 6','D8.30 yari kanal','0.2 mm kelepce araligi'])
    add('P09','Pan rulman kulesi',pedestal(),'608 yatak / enkoder erisimi / 4 adet M4 taban baglantisi',
      features=['56 x 56 taban','4x D4.5 / 44 x 44 aralik','Alt 608 cebi D22.15 x 7 / Z40-47','3x M3 insert / PCD29'])
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
    add('P15','Pan doner tasiyici',rotor(),'D8 mil sikma gobegi / korumali kablo halkasi / 20 mm ek aciklik',print_axis='-Z',
      features=['D120 x 6 ust flans','D8.10 mil cebi','2x M2 capraz sikma civatasi','4x M2 / 52 x 52 aralik','3x insert / PCD29','16 x 10 kablo gecisi / R25'])
    add('P16','Optik platform koprusu',bridge(),'168 x 90 x 8 mm / altta 12 mm kablo kanallari',
      features=['4x D2.4 / 52 x 52 aralik','Dikme delikleri D2.4 / 148 x 60 aralik','Kanal derinligi 4.5 mm','Kablo cikislari D8.5'])
    add('P17','Sol hareket dikmesi',arm(True),'Tilt servosu + 608 yatagi / yan yuzeyi baski tablasina',
      print_axis='X',features=['Tilt ekseni Z205','Motor ekseni Z155.5','49.5 mm disli eksen araligi','608 cebi D22.15 x 9','D12.4 ara burc rahatlatmasi','Slotlu servo montaji'])
    add('P18','Sag sensor dikmesi',arm(False),'608 yatak / AS5600 sabit montaji / +-90 derece durdurucular',
      print_axis='X',features=['Tilt ekseni Z205','608 cebi D22.15 x 9','D12.4 ara burc rahatlatmasi','AS5600: 20.32 x 12.70 aralik','PCB alt duzlemi X80'])
    add('P19','Tilt cikis dislisi',tilt_output(),'36 dis / M8 x 35 DIN931 baslik cebi',
      color='#db9e52',print_axis='X',features=['m1.5 / z36 / dis genisligi 8','M8 alti kose baslik cebi AF13.3 x 5.4'])
    add('P20','Pan aktarim muhafazasi',guard(),'Dislileri orter / iki mekanik durdurucu / kapak asagi basilir',
      color='#374e58',print_axis='-Z',features=['Genisletilmis pan durdurucu kollari','4x D3.4 uzun baglanti','D38 doner gobek boslugu','+-90 derece mekanik sinir'])
    add('P21','Pan miknatis adaptoru',pan_magnet_cup(),'Cap boyunca kutuplanmis D6 x 2.5 miknatis / mile yapistirma',
      features=['D12 x 10','Miknatis cebi D6.10 x 2.6','Mil cebi D8.2 x 4'])
    add('P22','Tilt miknatis adaptoru',tilt_magnet_cup(),'D8 omuz civatasi basligina gecme / D6 x 2.5 capsal miknatis',
      print_axis='X',features=['D16 x 9.7','Baslik cebi D13.2 x 5.6','Miknatis cebi D6.10 x 2.6'])
    add('P23','Enkoder dis kapagi',encoder_cover(),'AS5600 PCB arka yuzu / 4 adet M2.5 baglanti',
      color='#374e58',print_axis='X',features=['34 x 27 x 3','4x D2.9 / 20.32 x 12.70 aralik'])
    add('P24','Gecme deneme kuponu',fit_coupon(),'Ilk baski / rulman, mil, optik modul ve insert toleransi',
      color='#db9e52',features=['Ust sira, soldan: D21.95 / 22.05 / 22.15 / 22.25',
      'Alt sol: D7.95 / 8.05 / 8.15 / 8.30','Alt sag: D2.8 / 3.0 / 3.1',
      'Orta sag: D1.9 / 2.1 / 2.4','Tum delikler gecis deligi, kupon kalinligi 8'])
    add('P25','ESP elektronik kaseti',esp_carrier(),'62.74 x 25.40 mm DevKitC-1 referansi / ayarlanabilir baglama',
      print_axis='Y',features=['Uretici karti kimligi dogrulanmadi','2x D2.4 / 74 mm aralik','4 baglama yuvasi 8 x 2','PCB arka yuz Y33'])
    import enclosures as E
    add('P26','Kablo kilavuz klipsi',E.cable_clip(),'Genel M2 kablo rehberi / prototipte uygun konuma takilir',qty=6,
      features=['16 x 12 x 6','10 x 4 acik kanal','M2 baglanti; montaj modelinde gosterilmez'])
    for code,name,fn,axis in [
      ('E01','V2 taban on kabuk',lambda:E.base_shell(True),'Z'),
      ('E02','V2 taban arka kabuk',lambda:E.base_shell(False),'Z'),
      ('E03','V2 sol sabit cerceve',lambda:E.left_shell(False),'X'),
      ('E04','V2 sol servis kapagi',lambda:E.left_shell(True),'-X'),
      ('E05','V2 sag sabit cerceve',lambda:E.right_shell(False),'-X'),
      ('E06','V2 sag servis kapagi',lambda:E.right_shell(True),'X')]:
        add(code,name,fn(),'Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj',color='#dce1df',print_axis=axis,
          features=['Nominal 3 mm duvar','Yalniz V2 kapali surumde kullanilir','M2 vida ve insert baglantisi','Destek ve gecme onizlemesi gerekli'])

    # Neutral assembly transforms. Part CAD stays editable in these datums.
    for rec in spec:
        code=rec['code']; s=parts[code]
        if code in ('P24','P26') or code.startswith('E'):continue
        if code in ('P03','P04','P05','P06','P07','P08','P25'): s=translate(s,(0,0,TILT_Z))
        assembly.append((s,rec['color'],code))
    assembly.append((tilt_driver(),'#db9e52','P13b'))
    # Purchased item envelopes: body dimensions are indicative; mounting awaits fit check.
    purchased=[]
    pan_servo=fuse(box(40.7,19.7,37,(59.35,0,39.6)),box(54,19.7,2.5,(59.35,0,49.15)),cyl(3,5.7,(49.5,0,61.15)))
    purchased.append((pan_servo,'#29353b','MG996R-pan'))
    tilt_servo=translate(rotate(translate(pan_servo,(-49.5,0,-21.1)),(1,1,1),120),(-121.7,0,155.5))
    tilt_servo=translate(tilt_servo,(0,0,UPPER_LIFT))
    purchased.append((tilt_servo,'#29353b','MG996R-tilt'))
    for z in (43.5,55.5): purchased.append((cut(cyl(11,7,(0,0,z)),cyl(4,10,(0,0,z))),'#a7b3b7','608-pan'))
    for x in (-61.5,61.5): purchased.append((cut(cyl(11,7,(x,0,TILT_Z),axis=(1,0,0)),cyl(4,10,(x,0,TILT_Z),axis=(1,0,0))),'#a7b3b7','608-tilt'))
    purchased.append((cyl(4,106,(0,0,74.4)),'#a7b3b7','Pan-shaft-D8'))
    purchased.append((box(35.7,1.6,23.9,(-15,-13.2,TILT_Z)),'#287341','OV5640-PCB'))
    purchased.append((cyl(5,10,(-15,-19,TILT_Z),axis=(0,1,0)),'#182a34','Lens-envelope'))
    purchased.append((cyl(4,21,(32,0,TILT_Z),axis=(0,1,0)),'#9b5551','Class1-module'))
    purchased.append((box(25.4,17.78,1.6,(0,0,11.3)),'#287341','AS5600-pan-PCB'))
    purchased.append((box(1.6,25.4,17.78,(80.8,0,TILT_Z)),'#287341','AS5600-tilt-PCB'))
    # Reference devkit, not a claim that the unidentified user PCB is identical.
    esp=box(62.74,1.6,25.4,(0,32.2,TILT_Z))
    purchased.append((esp,'#244d42','ESP32-S3-reference-PCB'))
    purchased.append((box(25.5,3.1,18,(-13,29.85,TILT_Z)),'#a7b3b7','WROOM-reference-envelope'))
    for z in (-11.43,11.43):
        purchased.append((box(55.88,7,2.54,(0,27.9,TILT_Z+z)),'#273136','ESP-header-reference'))
        for k in range(22):purchased.append((box(.64,10,.64,(-26.67+2.54*k,26.4,TILT_Z+z)),'#c39d53','ESP-pin-reference'))
    for z in (-5,5):purchased.append((box(8.6,3.2,7.4,(29.5,29.8,TILT_Z+z)),'#a7b3b7','ESP-USB-reference'))
    usb=fuse(cyl(10.75,22,(55,71.5,17),axis=(0,1,0)),cyl(14.75,3,(55,84,17),axis=(0,1,0)))
    usb=cut(usb,translate(rotate(rounded_rect(9,3.5,10,1.5),(1,0,0),90),(55,86,17)))
    purchased.append((usb,'#26363a','USB-C-4218-envelope'))
    grommet=cut(fuse(cyl(4.9,3,(-55,81,17),axis=(0,1,0)),cyl(6,2,(-55,83.5,17),axis=(0,1,0))),cyl(2,12,(-55,82,17),axis=(0,1,0)))
    purchased.append((grommet,'#26363a','Power-grommet-envelope'))
    # Optical tilt joint fasteners; simplified envelopes, no thread modelling.
    left_shaft=fuse(cyl(4,35,(-53.1,0,205),axis=(1,0,0)),hex_prism(13,5.3,(-73.25,0,205),axis=(1,0,0)))
    right_shaft=fuse(cyl(4,16,(59,0,205),axis=(1,0,0)),cyl(3,11,(45.5,0,205),axis=(1,0,0)),cyl(6.5,5.5,(69.75,0,205),axis=(1,0,0)))
    purchased.append((translate(left_shaft,(0,0,UPPER_LIFT)),'#a7b3b7','M8x35-DIN931'))
    purchased.append((translate(right_shaft,(0,0,UPPER_LIFT)),'#a7b3b7','D8-L16-M6-shoulder'))
    allitems=[(s,c) for s,c,_ in assembly+purchased]
    render(allitems,ROOT/'images'/'montaj.png','OPTIK V1  /  Acik test ve servis','R0.2 / M2 baglantilar / kablo kanallari / AS5600 geri bildirim',elev=21,azim=-62)
    closed_items=allitems+[(parts[c],'#dce1df') for c in ('E01','E02','E03','E04','E05','E06')]
    render(closed_items,ROOT/'images'/'montaj-v2.png','OPTIK V2  /  Kapali govde','R0.2 / sokulebilir kapaklar / USB programlama / gizli aktarim',elev=21,azim=-62)
    render(closed_items,ROOT/'images'/'montaj-v2-arka.png','OPTIK V2  /  Arka servis erisimi','USB-C panel konnektoru + guc gecisi / referans mekanik model',elev=22,azim=58)
    render([(s,c) for s,c,code in assembly+purchased if code!='P06'],ROOT/'images'/'elektronik-yerlesim.png','OPTIK  /  Elektronik servis gorunumu','ESP karti referans geometridir; kullanicinin PCB modeli henuz dogrulanmadi',elev=22,azim=58)
    # OpenCascade compound STEP retains the actual assembly positions.
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    compound=TopoDS_Compound(); builder=BRep_Builder(); builder.MakeCompound(compound)
    for shape,_,_ in assembly+purchased: builder.Add(compound,shape)
    import zipfile
    sw=STEPControl_Writer(); sw.Transfer(compound,STEPControl_AsIs); sw.Write(str(ROOT/'cad'/'OPTIK-montaj.step'))
    with zipfile.ZipFile(ROOT/'cad'/'OPTIK-V1-montaj.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(ROOT/'cad'/'OPTIK-montaj.step','OPTIK-V1-montaj.step')
    (ROOT/'cad'/'OPTIK-montaj.step').unlink()
    for code in ('E01','E02','E03','E04','E05','E06'):builder.Add(compound,parts[code])
    sw=STEPControl_Writer(); sw.Transfer(compound,STEPControl_AsIs); sw.Write(str(ROOT/'cad'/'OPTIK-V2-montaj.step'))
    with zipfile.ZipFile(ROOT/'cad'/'OPTIK-V2-montaj.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(ROOT/'cad'/'OPTIK-V2-montaj.step','OPTIK-V2-montaj.step')
    (ROOT/'cad'/'OPTIK-V2-montaj.step').unlink()
    print('ASSEMBLY_READY',flush=True)
