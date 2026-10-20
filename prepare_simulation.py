"""Export CAD visual meshes and two MuJoCo movement demonstrators (SI units).

The servos, friction, inertia and controller are illustrative, not identified
from measurements. This model contains no projectile or target engagement.
"""
from pathlib import Path
import json, math
import numpy as np
import trimesh
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
from geometry import mesh
from validate import read
from model import TILT_Z, tilt_driver

R=Path(__file__).parent; D=R/'simulation'; A=D/'assets'; A.mkdir(parents=True,exist_ok=True)
spec=json.loads((R/'parts.json').read_text()); records={p['code']:p for p in spec}
head={'P03','P04','P05','P06','P07','P08','P19','P22','P25'}
fixed={'P01','P02','P09','P10','P11','P12','P20','E01','E02'}
shapes={}
for p in spec:
    c=p['code']
    if c in ('P24','P26'):continue
    v,f=mesh(read(R/'cad'/f'{c}.step'),.22)
    if c in ('P19','P22'):v[:,2]-=TILT_Z
    if c=='P13':v-=np.array([49.5,0,71])
    shapes[c]=trimesh.Trimesh(v*.001,f,process=True)
v,f=mesh(tilt_driver(),.22);v-=np.array([-72,0,TILT_Z-49.5])
shapes['P13b']=trimesh.Trimesh(v*.001,f,process=True)
for c,m in shapes.items():m.export(A/f'{c}.stl')

def vec(x):return ' '.join(f'{v:.8g}' for v in x)
def rgba(h):return vec([int(h[i:i+2],16)/255 for i in (1,3,5)]+[1])
def inertial(b,mass,diag):SubElement(b,'inertial',pos='0 0 0',mass=str(mass),diaginertia=vec(diag))
def make(variant):
    root=Element('mujoco',model=f'OPTIK-{variant}-movement-prototype')
    SubElement(root,'compiler',angle='radian',meshdir='assets',inertiafromgeom='false')
    SubElement(root,'option',timestep='.002',gravity='0 0 -9.81',integrator='implicitfast')
    visual=SubElement(root,'visual');SubElement(visual,'global',offwidth='960',offheight='720')
    SubElement(visual,'headlight',ambient='.4 .4 .4',diffuse='.6 .6 .6',specular='.1 .1 .1')
    asset=SubElement(root,'asset')
    for c in shapes:SubElement(asset,'mesh',name=c,file=f'{c}.stl')
    world=SubElement(root,'worldbody')
    SubElement(world,'light',pos='.3 -.4 .8',dir='-.3 .4 -.8',diffuse='.8 .8 .8')
    SubElement(world,'geom',name='floor',type='plane',size='1 1 .01',rgba='.89 .91 .92 1',pos='0 0 -.009')
    base=SubElement(world,'body',name='base')
    pan=SubElement(base,'body',name='pan')
    SubElement(pan,'joint',name='pan',type='hinge',axis='0 0 1',limited='true',range=vec([-math.pi/2,math.pi/2]),damping='.07',armature='.005')
    inertial(pan,.85 if variant=='V2' else .65,[.006,.006,.003])
    tilt=SubElement(pan,'body',name='tilt',pos=f'0 0 {TILT_Z*.001}')
    SubElement(tilt,'joint',name='tilt',type='hinge',axis='1 0 0',limited='true',range=vec([-math.pi/2,math.pi/2]),damping='.05',armature='.003')
    inertial(tilt,.21,[.00018,.00024,.0003])
    drive_pan=SubElement(base,'body',name='pan_driver',pos='.0495 0 .071')
    SubElement(drive_pan,'joint',name='pan_driver',axis='0 0 1',damping='.001')
    inertial(drive_pan,.012,[.000004,.000004,.000008])
    drive_tilt=SubElement(pan,'body',name='tilt_driver',pos=f'-.072 0 {(TILT_Z-49.5)*.001}')
    SubElement(drive_tilt,'joint',name='tilt_driver',axis='1 0 0',damping='.001')
    inertial(drive_tilt,.012,[.000008,.000004,.000004])
    for c in shapes:
        if variant=='V1' and c.startswith('E'):continue
        parent=drive_pan if c=='P13' else drive_tilt if c=='P13b' else tilt if c in head else base if c in fixed else pan
        color=records['P13' if c=='P13b' else c]['color']
        SubElement(parent,'geom',name=c,type='mesh',mesh=c,rgba=rgba(color),contype='0',conaffinity='0',group='1')
    # Purchased component envelopes; dimensions, not original manufacturer CAD.
    def box(b,name,pos,size,color):SubElement(b,'geom',name=name,type='box',pos=vec(pos),size=vec(np.array(size)*.5),rgba=color,contype='0',conaffinity='0')
    box(base,'pan_servo',[.05935,0,.0396],[.0407,.0197,.037],'.10 .13 .15 1')
    box(pan,'tilt_servo',[-.1032,.00985,(TILT_Z-49.5)*.001],[.037,.0407,.0197],'.10 .13 .15 1')
    box(tilt,'ESP_reference',[0,.0322,0],[.06274,.0016,.0254],'.10 .35 .23 1')
    box(tilt,'camera_reference',[-.015,-.0132,0],[.0357,.0016,.0239],'.10 .35 .23 1')
    SubElement(tilt,'geom',name='lens_reference',type='cylinder',pos='-.015 -.019 0',size='.005 .005',quat='.70710678 .70710678 0 0',rgba='.07 .10 .12 1',contype='0',conaffinity='0')
    equality=SubElement(root,'equality')
    for name in ('pan','tilt'):SubElement(equality,'joint',joint1=f'{name}_driver',joint2=name,polycoef='0 -1.2 0 0 0',solref='.004 1')
    actuator=SubElement(root,'actuator')
    for name in ('pan','tilt'):SubElement(actuator,'position',name=f'{name}_position',joint=name,kp='8',kv='1.2',ctrllimited='true',ctrlrange=vec([-math.pi/2,math.pi/2]),forcelimited='true',forcerange='-1 1')
    indent(root);ElementTree(root).write(D/f'optik-{variant.lower()}.xml',encoding='utf-8',xml_declaration=True)
for version in ('V1','V2'):make(version)
(D/'README.md').write_text('''# OPTIK MuJoCo hareket gösterimi

`optik-v1.xml` açık test, `optik-v2.xml` kapalı gövde. STL görselleri CAD'den metreye çevrilmiştir. `simulate.py` konum servolarıyla 10 saniyelik iki eksen hareketi çalıştırır ve MP4/CSV üretir.

**Sınır:** MG996R elektriksel modeli, sürekli dönüş hız haritası, sensör gecikmesi, sürtünme, kablo kuvveti ve kütle/ataletler ölçülmedi. Kullanılan konum aktüatörleri gerçek sürekli dönüşlü servonun kontrol modeli değildir. Kütle/atalet sayıları yaklaşık varsayımdır. Görsel meshlerin çarpışması devre dışıdır; mekanik kesişim kontrolü ayrı CAD raporundadır. Bu dosya kalibre edilmiş dijital ikiz veya fiziksel servo başarım kanıtı değildir.

Kaynak: https://mujoco.readthedocs.io/en/3.2.7/python.html
''')
print('MUJOCO_MODELS_READY',len(shapes),flush=True)
