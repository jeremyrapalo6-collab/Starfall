from pathlib import Path
import sys

import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]; out=root/'assets/fully_assembled_preview.png'
W,H,S=800,1020,2
im=Image.new('RGB',(W*S,H*S),(242,244,248));draw=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype(('C:/Windows/Fonts/arial.ttf' if Path('C:/Windows/Fonts/arial.ttf').exists() else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),n*S)
draw.text((60*S,35*S),'Starfall - Celestial Edition',(27,31,42),font=font(35))
draw.text((60*S,84*S),'Taller bottom for the supplied M3 x 16 screws',(67,75,91),font=font(23))
cam=np.array([1.,-1.3,1.6]);cam/=np.linalg.norm(cam)
right=np.cross([0,0,1],cam);right/=np.linalg.norm(right);up=np.cross(cam,right)
light=np.array([-.2,-.5,1]);light/=np.linalg.norm(light)
colors={'Bottom':(64,63,77),'Top':(59,57,72),'Middle_Purple':(155,65,232),'Purple_Inlays':(187,107,251)}
scene=trimesh.load(root/'CAD/Starfall_Fully_Assembled_Colored.glb',force='scene')
meshes=dict(scene.geometry)
colors={n:tuple(m.visual.vertex_colors[0][:3]) for n,m in meshes.items()}
pixels=np.array(im)
zbuffer=np.full((H*S,W*S),-np.inf,dtype=np.float32)
for idx,exploded in enumerate([False]):
    triangles=[]
    for name,mesh in meshes.items():
        verts=mesh.vertices.copy()
        if exploded:verts[:,2]+=17 if name in ['Top','Purple_Inlays'] else 7 if name=='Middle_Purple' else 0
        for f,n in zip(mesh.faces,mesh.face_normals):
            if n@cam<=0:continue
            t=verts[f];shade=.57+.43*max(0,n@light)
            color=tuple(int(c*shade) for c in colors[name])
            triangles.append((float(t.mean(axis=0)@cam),t,color))
    allv=np.concatenate([t[1] for t in triangles]);px=allv@right;py=allv@up
    scale=min(680/(px.max()-px.min()),680/(py.max()-py.min()))
    cx=(400+idx*800)*S;cy=540*S
    mx=(px.max()+px.min())/2;my=(py.max()+py.min())/2
    for depth,t,color in triangles:
        coords=np.column_stack((cx+(t@right-mx)*scale*S,cy-(t@up-my)*scale*S))
        xmin,ymin=np.maximum(np.floor(coords.min(axis=0)).astype(int),[0,0])
        xmax,ymax=np.minimum(np.ceil(coords.max(axis=0)).astype(int),[W*S-1,H*S-1])
        if xmax<xmin or ymax<ymin:continue
        xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        a,b,c=coords;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        w=1-u-v;z=t@cam;zz=u*z[0]+v*z[1]+w*z[2]
        zb=zbuffer[ymin:ymax+1,xmin:xmax+1]
        mask=(u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)&(zz>zb)
        zb[mask]=zz[mask];pixels[ymin:ymax+1,xmin:xmax+1][mask]=color
im=Image.fromarray(pixels);draw=ImageDraw.Draw(im)
for idx in range(1):draw.text(((60+idx*800)*S,155*S),'ASSEMBLED' if idx==0 else 'EXPLODED',(96,67,140),font=font(18))
draw.text((60*S,919*S),'114.4 x 116 x 22.9 mm  -  PCB layout preserved',(37,42,55),font=font(23))
draw.text((60*S,958*S),'Corrected case with electronics, keycaps and knob.',(89,96,110),font=font(18))
im.resize((W,H),Image.Resampling.LANCZOS).save(out)
print(out)

