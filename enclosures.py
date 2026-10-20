"""R0.2 removable cosmetic shells for the optical platform, in assembly datums."""
import math
import geometry as G
from model import FLANGE_LIFT,UPPER_LIFT

def common(a,b):
    op=G.BRepAlgoAPI_Common(a,b);op.Build();return op.Shape()

def base_shell(front=True):
    outer=G.loft_solid([
      G.rounded_wire(205,165,16,-3,10,0),G.rounded_wire(205,165,16,32,10,0),
      G.rounded_wire(160,130,14,80,16,0),G.rounded_wire(128,130,23,93+FLANGE_LIFT,0,0)])
    inner=G.loft_solid([
      G.rounded_wire(199,159,13,0,10,0),G.rounded_wire(199,159,13,32,10,0),
      G.rounded_wire(154,124,11,80,16,0),G.rounded_wire(122,124,20,90+FLANGE_LIFT,0,0)])
    s=G.cut(outer,inner,G.cyl(62,22,(0,0,93+FLANGE_LIFT)))
    # USB bulkhead #4218, and an independent power-wire grommet passage.
    s=G.holes(s,[(55,81,17)],22.2,25,axis=(0,1,0))
    s=G.holes(s,[(-55,81,17)],10,25,axis=(0,1,0))
    s=G.holes(s,[(x,y,-1.5) for x in (-63,83) for y in (-53,53)],2.4,20)
    # Clearance for the existing under-base nuts / screw heads.
    s=G.holes(s,[(x,y,-1.5) for x in (-22,22) for y in (-22,22)],5.2,12)
    s=G.holes(s,[(59.35+x,y,-1.5) for x in (-26.5,26.5) for y in (-12,12)],5.2,12)
    for x in range(-30,31,10):s=G.cut(s,G.box(3,20,12,(x,-81,15)))
    s=common(s,G.box(500,250,500,(0,-125 if front else 125,100)))
    # Four lap keys at the floor align the two cosmetic halves.
    for x in (-60,-20,20,60):
        if front:s=G.cut(s,G.box(14.4,8.4,1.6,(x,-2,-.8)))
        else:s=G.fuse(s,G.box(14,8,1.4,(x,-2,-.7)))
    return s

def left_shell(outer_cap=False):
    # Rounded corners: bottom R4, top R22. Internal space clears servo cabling.
    s=G.rounded_yz(100,139,79.4,(4,22,22,4),(-94.3,0,169.5))
    cavity=G.rounded_yz(94,133,73.4,(1,19,19,1),(-94.3,0,169.5))
    s=G.cut(s,cavity)
    s=G.holes(s,[(-55,0,205)],36.4,15,axis=(1,0,0))
    s=G.cut(s,G.box(40,94,14,(-65,0,106)))
    for y in (-42,42):
      for z in (119,220):
        s=G.fuse(s,G.cyl(6,40,(-114,y,z),axis=(1,0,0)))
        s=G.holes(s,[(-115,y,z)],2.4,50,axis=(1,0,0))
        s=G.holes(s,[(-97.5,y,z)],3.1,5,axis=(1,0,0))
        s=G.holes(s,[(-132.4,y,z)],4.5,3.2,axis=(1,0,0))
    for y,z in [(-20,120),(20,120),(-20,217),(20,217)]:
        s=G.fuse(s,G.cyl(4,1.4,(-58.3,y,z),axis=(1,0,0)))
        s=G.holes(s,[(-56.5,y,z)],2.4,12,axis=(1,0,0))
    # A protected wiring exit on the lower rear wall.
    s=G.cut(s,G.box(12,14,8,(-73,48,124)))
    s=common(s,G.box(200,500,500,(-200 if outer_cap else 0,0,180)))
    return G.translate(s,(0,0,UPPER_LIFT))

def right_shell(outer_cap=False):
    s=G.rounded_yz(58,128,36.4,(4,17,17,4),(72.8,0,168))
    cavity=G.rounded_yz(52,122,30.4,(1,14,14,1),(72.8,0,168))
    s=G.cut(s,cavity)
    s=G.holes(s,[(55,0,205)],36.4,15,axis=(1,0,0))
    s=G.cut(s,G.box(36,94,12,(67,0,107)))
    for y in (-24,24):
      for z in (122,220):
        s=G.fuse(s,G.cyl(4,23,(79.5,y,z),axis=(1,0,0)))
        s=G.holes(s,[(80,y,z)],2.4,35,axis=(1,0,0))
        s=G.holes(s,[(71.5,y,z)],3.1,5,axis=(1,0,0))
    for y,z in [(-21.5,120),(21.5,120),(-16,220),(16,220)]:
        s=G.fuse(s,G.cyl(4,1.4,(58.3,y,z),axis=(1,0,0)))
        s=G.holes(s,[(56.5,y,z)],2.4,12,axis=(1,0,0))
    s=G.cut(s,G.box(12,12,9,(72,28,180)))
    if outer_cap:s=common(s,G.box(200,500,500,(174,0,180)))
    else:s=common(s,G.box(200,500,500,(-26,0,180)))
    return G.translate(s,(0,0,UPPER_LIFT))

def cable_clip():
    s=G.rounded_rect(16,12,6,2,(0,0,3))
    s=G.cut(s,G.box(10,16,4,(0,0,4)))
    # Open-sided cable guide; M2 mounting hole in the retained base.
    return G.holes(s,[(0,0,1)],2.4,10)
