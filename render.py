"""Orthographic, depth-buffered CAD previews; no generative images."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from geometry import mesh
from matplotlib.colors import to_rgb

def render(items,path,title,subtitle='',elev=27,azim=-62):
    W,H=1600,1040
    screen=np.tile(np.array([241,243,243],dtype=np.uint8),(H,W,1)); depth=np.full((H,W),-np.inf)
    az,el=np.radians([azim,elev]); eye=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    right=np.cross([0,0,1],eye); right/=np.linalg.norm(right)
    up=np.cross(eye,right); basis=np.array([right,up,eye]); data=[]
    for s,col in items:
        v,f=mesh(s,.16); p=v@basis.T; data.append((v,p,f,np.array(to_rgb(col))))
    p=np.vstack([d[1] for d in data]); lo=p.min(axis=0); hi=p.max(axis=0); center=(hi+lo)/2
    scale=min(1260/max(hi[0]-lo[0],1),650/max(hi[1]-lo[1],1))
    light=np.array([-.35,-.6,.85]); light/=np.linalg.norm(light)
    for v,p,faces,color in data:
      uv=np.column_stack(((p[:,0]-center[0])*scale+W/2,-(p[:,1]-center[1])*scale+H*.55,p[:,2]))
      for ids in faces:
        tri=uv[ids]; n=np.cross(v[ids[1]]-v[ids[0]],v[ids[2]]-v[ids[0]])
        norm=np.linalg.norm(n)
        if norm<1e-10: continue
        n/=norm
        if n@eye < -1e-6: continue
        xmin=max(0,int(np.floor(tri[:,0].min()))); xmax=min(W-1,int(np.ceil(tri[:,0].max())))
        ymin=max(0,int(np.floor(tri[:,1].min()))); ymax=min(H-1,int(np.ceil(tri[:,1].max())))
        if xmin>xmax or ymin>ymax: continue
        x,y=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        a,b,c=tri; den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10: continue
        w1=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        w2=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        w3=1-w1-w2; z=w1*a[2]+w2*b[2]+w3*c[2]
        old=depth[ymin:ymax+1,xmin:xmax+1]
        keep=(w1>=-1e-7)&(w2>=-1e-7)&(w3>=-1e-7)&(z>=old-1e-7)
        shade=.56+.38*max(0,float(n@light))
        screen[ymin:ymax+1,xmin:xmax+1][keep]=np.clip(color*shade*255,0,255).astype('uint8'); old[keep]=z[keep]
    img=Image.fromarray(screen); d=ImageDraw.Draw(img)
    fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'; boldpath='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
    d.text((70,38),title,font=ImageFont.truetype(boldpath,44),fill='#172c35')
    d.text((72,102),subtitle,font=ImageFont.truetype(fontpath,21),fill='#52656b')
    d.text((72,H-58),'OPTIK / R0.1   |   GERCEK CAD GEOMETRISI   |   PROTOTIP - MONTAJ DOGRULAMASI GEREKIR',font=ImageFont.truetype(fontpath,17),fill='#52656b')
    img.save(path)
