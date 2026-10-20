"""Local release preparation. Does not contact GitHub or send messages."""
from pathlib import Path
import json,csv,math
import trimesh
from geometry import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from validate import read
from model import MOUNT_DIAMETER_MAP, FLANGE_LIFT, UPPER_LIFT, TILT_Z

R=Path(__file__).parent
spec=json.loads((R/'parts.json').read_text());checks=[]
for rec in spec:
    mesh=trimesh.load_mesh(R/'stl'/f"{rec['code']}.stl")
    s=read(R/'cad'/f"{rec['code']}.step");ex=TopExp_Explorer(s,TopAbs_SOLID);n=0
    while ex.More():n+=1;ex.Next()
    item=dict(code=rec['code'],step_valid=BRepCheck_Analyzer(s).IsValid(),solids=n,
      watertight=bool(mesh.is_watertight),positive_volume=bool(mesh.volume>0),
      build_size_mm=mesh.extents.tolist(),fits_256_cube=bool(all(mesh.extents<=256)),
      minimum_z_mm=float(mesh.bounds[0,2]))
    assert item['step_valid'] and n==1 and item['watertight'] and item['positive_volume'] and item['fits_256_cube'],item
    assert abs(item['minimum_z_mm'])<1e-5,item
    checks.append(item)
(R/'checks'/'part-checks.json').write_text(json.dumps(checks,indent=2))

# Coordinate table is in each part's STEP frame, not the rotated STL print frame.
rows=[]
def hole(code,role,diam,xyz,axis='Z',depth='THRU'):
    xyz=list(xyz)
    if code in ('P17','P18','P19','P22','P23'):xyz[2]+=UPPER_LIFT
    if code=='P16':xyz[2]+=FLANGE_LIFT+1
    if code=='P15' and role=='Kopru baglantisi':xyz[2]+=FLANGE_LIFT
    for a,b in [('M2.5','M2'),('M3','M2'),('M4','M2')]:role=role.replace(a,b)
    rows.append([code,role,MOUNT_DIAMETER_MAP.get(diam,diam),*xyz,axis,depth])
for x in (-73,93):
 for y in (-63,63):
  hole('P01','M3 kapak inserti',4.4,(x,y,27.5),depth=5)
  hole('P02','Kapak baglantisi',3.4,(x,y,31.5))
for x in (-34,82):
 for y in (-32,32):
  hole('P01','M3 muhafaza inserti',4.4,(x,y,27.5),depth=5)
  hole('P02','Muhafaza gecisi',3.4,(x,y,31.5))
  hole('P20','Uzun muhafaza vidasi',3.4,(x,y,57))
for x in (-22,22):
 for y in (-22,22):
  hole('P01','Kule tabani',4.5,(x,y,3));hole('P09','Kule ayagi',4.5,(x,y,9))
for x in (-63,83):
 for y in (-53,53):hole('P01','Tezgah montaji',4.5,(x,y,3))
for x in (32.85,85.85):
 for y in (-12,12):
  hole('P01','Servo sehpa gecisi',3.5,(x,y,3));hole('P12','Servo sehpa inserti',4.4,(x,y,8.5),depth=5)
for code,yy in [('P03',-16.5),('P04',-13.5),('P05',-11.25)]:
 for x in (-35.5,5.5):
  for z in (-14.5,14.5):hole(code,'Kamera kaseti',2.9,(x,yy,z),'Y')
for x in (-42.5,42.5):
 for z in (-17.5,17.5):
  hole('P03','Arka kapak M3 insert',4.4,(x,15.5,z),'Y',5)
  hole('P06','Arka kapak gecisi',3.4,(x,19.5,z),'Y')
for x in (25.5,38.5):
 hole('P03','Isik M2.5 insert',3.6,(x,0,-8.5),'Z',5)
 for code,z in [('P07',-3),('P08',3.2)]:hole(code,'Isik kelepce gecisi',2.9,(x,0,z))
for code,z in [('P09',43.5),('P10',55.5)]:hole(code,'608 yatak cebi',22.15,(0,0,z),'Z',7)
for a in (0,120,240):
 x,y=14.5*math.cos(math.radians(a)),14.5*math.sin(math.radians(a))
 for code,d,z,depth in [('P09',4.4,44.5,5),('P10',3.4,53,'THRU'),('P14',3.4,71,'THRU'),('P15',4.4,77.5,5)]:
  hole(code,'PCD29 baglanti',d,(x,y,z),'Z',depth)
for x in (-10.16,10.16):
 for y in (-6.35,6.35):hole('P11','AS5600 inserti',3.6,(x,y,9),'Z',3)
for x in (-26,26):
 for y in (-26,26):
  hole('P15','Kopru baglantisi',3.4,(x,y,97));hole('P16','Kopru baglantisi',3.4,(x,y,103))
for x in (-74,74):
 for y in (-30,30):
  hole('P16','Dikme ayagi',4.5,(x,y,103));hole('P17' if x<0 else 'P18','Dikme ayagi',4.5,(x,y,109))
for code,xx in [('P17',-62.5),('P18',62.5)]:
 hole(code,'608 yatak cebi',22.15,(xx,0,205),'X',9)
 hole(code,'Donen ara burc rahatlatmasi',12.4,(xx,0,205),'X')
for y in (-10.16,10.16):
 for z in (-6.35,6.35):
  hole('P18','AS5600 inserti',3.6,(78.5,y,205+z),'X',3)
  hole('P23','AS5600 kapak gecisi',2.9,(83.1,y,205+z),'X')
hole('P02','Sabit kule acikligi',36.8,(0,0,31.5))
hole('P03','Tilt mil gecisi',8.5,(0,0,0),'X')
hole('P03','Isik on aciklik',11,(32,-18,0),'Y')
hole('P13','Horn vida erisimi',7,(49.5,0,71))
hole('P14','Mil gecisi',8.5,(0,0,71))
hole('P15','Sikmali mil yuvasi',8.1,(0,0,85))
hole('P15','Capraz sikma',3.4,(0,12,85.5),'X')
hole('P19','Tilt mil gecisi',8.5,(-72,0,205),'X')
hole('P20','Doner gobek acikligi',38,(0,0,79.5))
hole('P21','Miknatis',6.1,(0,0,16.7),'Z',2.6)
hole('P21','Mil yapistirma',8.2,(0,0,23.4),'Z',4)
hole('P22','Civata basligi',13.2,(69.8,0,205),'X',5.6)
hole('P22','Miknatis',6.1,(75.4,0,205),'X',2.6)
# R0.2 service and enclosure mounting datums. All native part coordinates.
for code,diam,y in [('P01',24,74),('E02',22.2,81)]:hole(code,'USB panel acikligi',diam,(55,y,17),'Y')
for code,y in [('P01',74),('E02',81)]:hole(code,'Guc gecisi',10,(-55,y,17),'Y')
for x in (-37,37):
 hole('P25','ESP tasiyici gecisi',2.4,(x,34.5,0),'Y')
 hole('P06','ESP tasiyici inserti',3.1,(x,38.5,0),'Y',5)
for code in ('E01','E02'):
 for x in (-63,83):hole(code,'V2 taban montaji',2.4,(x,-53 if code=='E01' else 53,-1.5))
for code in ('E03','E04'):
 for y in (-42,42):
  for z in (141,242):hole(code,'Sol servis kapak gecisi',2.4,(-115 if code=='E04' else -97.5,y,z),'X')
for code in ('E05','E06'):
 for y in (-24,24):
  for z in (144,242):hole(code,'Sag servis kapak gecisi',2.4,(80 if code=='E06' else 71.5,y,z),'X')
with (R/'drawings'/'delik-koordinatlari.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Parca','Aciklama','Cap_mm','Merkez_X_mm','Merkez_Y_mm','Merkez_Z_mm','Eksen','Derinlik_mm']);w.writerows(rows)
frames=dict(units='mm; joint angles rad',pan=dict(parent='base',origin=[0,0,120],axis=[0,0,1],limits=[-math.pi/2,math.pi/2]),
 tilt=dict(parent='pan',origin_in_pan=[0,0,TILT_Z-120],global_neutral_origin=[0,0,TILT_Z],axis=[1,0,0],limits=[-math.pi/2,math.pi/2]),
 camera_cad_frame=dict(origin_in_head=[-15,-19,0],nominal_view_direction=[0,-1,0]),
 light_aperture=dict(origin_in_head=[32,-10.5,0],direction=[0,-1,0]),
 note='CAD datums only. Pan datum at global Z120; tilt global Z227. Simulation XML uses base origin at Z0, with the same axis lines. Not a calibrated dynamic twin.')
(R/'joint-frames.json').write_text(json.dumps(frames,indent=2))

text=(R/'README.template.md').read_text().replace('{{PART_COUNT}}',str(len(spec))).replace('{{PAGE_COUNT}}',str(len(spec)+6))
text+='\n## Parça galerisi\n\nHer görsel gerçek CAD geometrisinden üretilmiştir. P13 iki, P26 altı adet; P24 test kuponu, P26 isteğe bağlıdır. E parçaları yalnız V2 içindir.\n\n'
for i,d in enumerate(spec,7):
 text+=f"### {d['code']} - {d['name']}\n\n{d['note']}\n\n![{d['name']}](images/{d['code']}.png)\n\n[STEP](cad/{d['code']}.step) · [STL](stl/{d['code']}.stl) · [Ölçülü çizim](drawings/sayfa-{i:02d}.png)\n\n"
(R/'README.md').write_text(text)
print('RELEASE_CHECKS',len(checks),'parts;',len(rows),'hole-coordinate rows')
