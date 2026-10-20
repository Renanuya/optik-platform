"""CAD interference checks. Not a structural, hardware, or laser classification test."""
from pathlib import Path
import itertools,json,math
from geometry import *
from model import tilt_driver,TILT_Z,UPPER_LIFT
from OCP.STEPControl import STEPControl_Reader

R=Path(__file__).parent

def read(path):
    r=STEPControl_Reader();r.ReadFile(str(path));r.TransferRoots();return r.OneShape()

def overlap(a,b,tol=1e-5):
    aa=bounds(a); bb=bounds(b)
    return all(min(aa[i+3],bb[i+3])-max(aa[i],bb[i])>tol for i in range(3))

def main():
    entries=json.loads((R/'parts.json').read_text()); p={e['code']:read(R/'cad'/f"{e['code']}.step") for e in entries}
    p.pop('P24',None);p.pop('P26',None) # Optional manufacturing / cable fixtures.
    for c in ('P03','P04','P05','P06','P07','P08','P25'):p[c]=translate(p[c],(0,0,TILT_Z))
    p['P13b']=tilt_driver()
    results=[]
    for a,b in itertools.combinations(p,2):
        if not overlap(p[a],p[b]):continue
        v=intersection_volume(p[a],p[b])
        if v>.015:
            print('INTERFERENCE',a,b,round(v,5),flush=True);results.append(dict(a=a,b=b,volume_mm3=v))
    print('STATIC_DONE',len(results),flush=True)
    # Independent purchased-part envelopes catch mounting and rotating-spacer clashes.
    hardware={
      'pan-servo-body':box(40.7,19.7,37,(59.35,0,39.6)),
      'pan-servo-ears':box(54,19.7,2.5,(59.35,0,49.15)),
      'tilt-servo-body':box(37,40.7,19.7,(-103.2,9.85,155.5+UPPER_LIFT)),
      'tilt-servo-ears':box(2.5,54,19.7,(-93.65,9.85,155.5+UPPER_LIFT)),
      'camera-pcb':box(35.7,1.6,23.9,(-15,-13.2,TILT_Z)),
      'light-module':cyl(4,21,(32,0,TILT_Z),axis=(0,1,0)),
      'pan-encoder-pcb':box(25.4,17.78,1.6,(0,0,11.3)),
      'tilt-encoder-pcb':box(1.6,25.4,17.78,(80.8,0,TILT_Z)),
      'esp-reference-pcb':box(62.74,1.6,25.4,(0,32.2,TILT_Z)),
    }
    for label,x,length in [('left-outer',-66.5,3),('left-inner',-56,4),('right-inner',56,4),('right-outer',66,2)]:
      hardware[label+'-spacer']=cut(cyl(6,length,(x,0,TILT_Z),axis=(1,0,0)),cyl(4.1,length+2,(x,0,TILT_Z),axis=(1,0,0)))
    hw=[]
    for name,shape in hardware.items():
      for code,part in p.items():
        if overlap(shape,part):
          v=intersection_volume(shape,part)
          if v>.015:hw.append(dict(hardware=name,part=code,volume_mm3=v));print('HARDWARE',name,code,round(v,5),flush=True)
    print('HARDWARE_DONE',len(hw),flush=True)
    gears=[]
    for angle in (0,15,30,45,60,75,90):
        a=rotate(p['P13'],(0,0,1),-1.2*angle,(49.5,0,0));b=rotate(p['P14'],(0,0,1),angle)
        v=intersection_volume(a,b);gears.append(dict(output_angle_deg=angle,intersection_mm3=v))
        print('GEAR',angle,round(v,7),flush=True)
    # Only optical moving housing versus both stationary yoke arms.
    sweep=[]
    for angle in (-90,-60,-30,0,30,60,90):
        for code in ('P03','P04','P05','P06','P07','P08','P25','P19','P22'):
          moved=rotate(p[code],(1,0,0),angle,(0,0,TILT_Z))
          for arm in ('P17','P18','E03','E04','E05','E06'):
            if overlap(moved,p[arm]):
              v=intersection_volume(moved,p[arm])
              if v>.015:sweep.append(dict(angle=angle,a=code,b=arm,volume_mm3=v));print('SWEEP',angle,code,arm,round(v,5),flush=True)
    yaw=[]
    for angle in (-90,-60,-30,0,30,60,90):
        moved=rotate(p['P15'],(0,0,1),angle)
        v=intersection_volume(moved,p['P20'])
        yaw.append(dict(angle=angle,intersection_mm3=v))
        print('YAW_STOP',angle,round(v,7),flush=True)
    report=dict(static_interferences=results,hardware_envelope_interferences=hw,gear_samples=gears,optical_head_sweep_interferences=sweep,yaw_stop_samples=yaw,
      checked_tilt_angles=[-90,-60,-30,0,30,60,90],
      note='Geometric sampling only. No cable sweep, bearing fits, strength, laser classification or hardware testing.')
    (R/'checks'/'assembly-checks.json').write_text(json.dumps(report,indent=2))
    print('CHECKS_DONE',flush=True)
    if results or hw or sweep or any(g['intersection_mm3']>.015 for g in gears+yaw):
      raise SystemExit('CAD interferences require correction before release')

if __name__=='__main__':main()
