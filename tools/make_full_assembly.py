from pathlib import Path
import sys
p=Path(__file__).resolve().parent/'generate_final_case.py'
ns={'__file__':str(p)}
exec(p.read_text().split('bottom,spacer=build_bottom(),build_spacer()')[0],ns)
cq=ns['cq'];trimesh=ns['trimesh'];r=p.parents[1];out=r/'CAD'
parts=[]
for n,c in [('Bottom',(15,15,22,255)),('Middle_Purple',(183,67,255,255)),('Top',(28,24,34,255)),('Purple_Inlays',(183,67,255,255))]:
 parts.append((cq.importers.importStep(str(r/'production'/f'{n}.STEP')).val(),n,c))
e=cq.importers.importStep(str(out/'Starfall_fit_reference_1p6mm.STEP')).val()
glass=[];other=[]
for q in e.Solids():
 b=q.BoundingBox()
 if b.ymin>35 and b.xmax<0 and b.xlen>20 and b.zmax>2:
  glass.append(q)
 else:other.append(q)
parts.append((cq.Compound.makeCompound(other),'Electronics',(44,106,74,255)))
parts.append((cq.Compound.makeCompound(glass),'Actual_OLED_Glass',(5,6,12,255)))
caps,pcb,bezel,screen,txt,knob,kring,screws=ns['render_parts']()
knob=ns['cyl'](15.8,8.0,13.3,*ns['ENC_CENTER']).union(ns['cyl'](15.0,21.3,.9,*ns['ENC_CENTER']))
txt=ns['text_solid']('STARFALL',2.4,.10,-16.49,39.46,3.78)
for s,n,c in [(caps,'Keycaps',(20,20,28,255)),(knob,'Encoder_Knob',(20,20,28,255)),(screws,'M3_Screws',(175,175,190,255)),(txt,'OLED_STARFALL',(230,150,255,255))]:
 parts.append((s.val() if isinstance(s,cq.Workplane) else s,n,c))
# Illustrative keycap legends, matching the reference theme.
icons=[]
for i,(x,y) in enumerate(ns['SWITCH_CENTERS']):
 z=16.56
 if i in (1,6):shape=ns['star'](2.8,z,.12,x,y)
 elif i==0:shape=ns['crescent'](2.6,2.35,1.1,z,.12,x,y)
 elif i==7:shape=ns['planet'](3.4,4.0,1.6,3.5,1.1,25,z,.12,x,y)
 elif i==2:shape=ns['star'](2.0,z,.12,x,y).union(ns['star'](.9,z,.12,x+3,y+2.5))
 else:shape=ns['text_solid']({3:'^',4:'+',5:'v',8:'+'}[i],6,.12,x,y,z)
 icons.extend(shape.solids().vals())
parts.append((cq.Compound.makeCompound(icons),'Illustrative_Keycap_Legends',(183,90,240,255)))
a=cq.Assembly(name='Starfall Fully Assembled');scene=trimesh.Scene()
for s,n,c in parts:
 a.add(s,name=n,color=cq.Color(*[v/255 for v in c[:3]]))
 scene.add_geometry(ns['mesh'](s,n,c,None),geom_name=n)
a.save(str(out/'Starfall_Fully_Assembled.STEP'))
scene.export(out/'Starfall_Fully_Assembled_Colored.glb')
check=cq.importers.importStep(str(out/'Starfall_Fully_Assembled.STEP')).val()
assert check.isValid()
assert len(check.Solids())==sum(len(s.Solids()) for s,n,c in parts)
print('Valid STEP:',len(check.Solids()),'solids; GLB:',len(scene.geometry),'groups')

