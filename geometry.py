"""Small OpenCascade CAD toolkit. All modelling coordinates are millimetres."""
import math
import numpy as np
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Ax1, gp_Trsf, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

def box(x,y,z,c=(0,0,0)):
    return BRepPrimAPI_MakeBox(gp_Pnt(c[0]-x/2,c[1]-y/2,c[2]-z/2),x,y,z).Shape()

def cyl(r,h,c=(0,0,0),axis=(0,0,1)):
    start=tuple(c[i]-axis[i]*h/2 for i in range(3))
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*start),gp_Dir(*axis)),r,h).Shape()

def fuse(*shapes):
    s=shapes[0]
    for q in shapes[1:]:
        op=BRepAlgoAPI_Fuse(s,q); op.Build(); s=op.Shape()
    return s

def cut(s,*tools):
    for q in tools:
        op=BRepAlgoAPI_Cut(s,q); op.Build(); s=op.Shape()
    return s

def rounded_rect(l,w,h,r,c=(0,0,0)):
    x,y,z=c
    return fuse(box(l-2*r,w,h,c),box(l,w-2*r,h,c),
      *[cyl(r,h,(x+dx*(l/2-r),y+dy*(w/2-r),z)) for dx in (-1,1) for dy in (-1,1)])

def prism(points, vector):
    wire=BRepBuilderAPI_MakePolygon()
    for p in points: wire.Add(gp_Pnt(*p))
    wire.Close()
    face=BRepBuilderAPI_MakeFace(wire.Wire()).Face()
    return BRepPrimAPI_MakePrism(face,gp_Vec(*vector)).Shape()

def hex_prism(flat,h,c,axis=(0,0,1)):
    r=flat/math.sqrt(3)
    p=[(r*math.cos(a),r*math.sin(a)) for a in np.linspace(0,2*math.pi,6,endpoint=False)]
    if axis==(0,0,1):
        return prism([(c[0]+x,c[1]+y,c[2]-h/2) for x,y in p],(0,0,h))
    return prism([(c[0]-h/2,c[1]+x,c[2]+y) for x,y in p],(h,0,0))

def rotate(s,axis,angle,origin=(0,0,0)):
    t=gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(*origin),gp_Dir(*axis)),math.radians(angle))
    return BRepBuilderAPI_Transform(s,t,True).Shape()

def translate(s,xyz):
    t=gp_Trsf(); t.SetTranslation(gp_Vec(*xyz))
    return BRepBuilderAPI_Transform(s,t,True).Shape()

def holes(s,points,d,depth=100,axis=(0,0,1)):
    return cut(s,*[cyl(d/2,depth,p,axis) for p in points])

def slot(length,width,depth,c,axis=(0,0,1),along='x'):
    a=length-width
    if axis==(0,0,1):
        if along=='x': return fuse(box(a,width,depth,c),cyl(width/2,depth,(c[0]-a/2,c[1],c[2])),cyl(width/2,depth,(c[0]+a/2,c[1],c[2])))
        return fuse(box(width,a,depth,c),cyl(width/2,depth,(c[0],c[1]-a/2,c[2])),cyl(width/2,depth,(c[0],c[1]+a/2,c[2])))
    return translate(rotate(slot(length,width,depth,(0,0,0)),(0,1,0),90),c)

def gear(z,m=1.5,h=8,phase=0,backlash=.18):
    rp=m*z/2; rb=rp*math.cos(math.radians(20)); ra=rp+m; rf=rp-1.25*m
    inv=lambda a: math.tan(a)-a
    half=math.pi/(2*z)-backlash/(2*rp)
    beta=lambda r: half+inv(math.radians(20))-inv(math.acos(min(1,rb/r)))
    b0=beta(rb); ba=beta(ra); pts=[]
    for i in range(z):
        mid=2*math.pi*i/z+math.radians(phase)
        pairs=[(rf,-b0),(rb,-b0)]
        pairs += [(r,-beta(r)) for r in np.linspace(rb,ra,10)[1:]]
        pairs += [(ra,a) for a in np.linspace(-ba,ba,5)[1:]]
        pairs += [(r,beta(r)) for r in np.linspace(ra,rb,10)[1:]]
        pairs += [(rf,b0)]
        pairs += [(rf,a) for a in np.linspace(b0,2*math.pi/z-b0,7)[1:-1]]
        pts += [(r*math.cos(mid+a),r*math.sin(mid+a),0) for r,a in pairs]
    return prism(pts,(0,0,h))

def bounds(s):
    b=Bnd_Box(); BRepBndLib.AddOptimal_s(s,b)
    return b.Get()

def volume(s):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g)
    return g.Mass()

def intersection_volume(a,b):
    op=BRepAlgoAPI_Common(a,b); op.Build()
    return volume(op.Shape())

def mesh(s,tolerance=.13):
    BRepMesh_IncrementalMesh(s,tolerance,False,.20,True)
    verts=[]; faces=[]; ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face_s(ex.Current()); loc=TopLoc_Location()
        tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            n=len(verts); tr=loc.Transformation()
            for j in range(1,tri.NbNodes()+1):
                p=tri.Node(j).Transformed(tr); verts.append((p.X(),p.Y(),p.Z()))
            for j in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(j).Get()
                faces.append((n+a-1,n+c-1,n+b-1) if f.Orientation()==TopAbs_REVERSED else (n+a-1,n+b-1,n+c-1))
        ex.Next()
    return np.array(verts),np.array(faces)

def save(s,stem):
    assert BRepCheck_Analyzer(s).IsValid(),str(stem)+' invalid CAD topology'
    writer=STEPControl_Writer(); writer.Transfer(s,STEPControl_AsIs); writer.Write(str(stem)+'.step')
    import trimesh
    v,f=mesh(s,.09)
    out=trimesh.Trimesh(v,f,process=True)
    out.export(str(stem)+'.stl')
    assert out.is_watertight,str(stem)+' open STL mesh'
    return out
