from pathlib import Path
import math,json
import cadquery as cq
import trimesh,numpy as np
from mechanical_fit import intersection
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'production/knob';OUT.mkdir(exist_ok=True)
CX,CY,Z=29.715,40.01,9.0

def d_bore(gap,z,height):
 r=3+gap
 return cq.Workplane('XY').circle(r).extrude(height).translate((0,0,z)).intersect(cq.Workplane('XY').box(20,20,height+2,centered=(True,False,False)).translate((0,-17.6+gap,z-1)))

def star(size,z,height):
 pts=[(0,size),(.65,.65),(size,0),(.65,-.65),(0,-size),(-.65,-.65),(-size,0),(-.65,.65)]
 return cq.Workplane('XY').polyline(pts).close().extrude(height).translate((0,0,z))

body=cq.Workplane('XY').circle(8).extrude(14.2).edges('>Z').fillet(.65)
for i in range(28):
 a=2*math.pi*i/28
 body=body.cut(cq.Workplane('XY').circle(.42).extrude(12.8).translate((8*math.cos(a),8*math.sin(a),.3)))
body=body.cut(d_bore(.10,-.1,12.5))
body=body.cut(cq.Workplane('XY').circle(4.5).extrude(3.9).translate((0,0,-.1)))
# Lead-in bevel makes the D-shaped opening easier to locate.
body=body.cut(cq.Workplane('XY').circle(4.9).workplane(offset=.4).circle(4.5).loft())
accent=star(4.4,13.66,.44)
# Pocket clearance built by offsetting the star contour, not by scaling its tips.
f=max(accent.val().Faces(),key=lambda f:f.Center().z)
w=f.outerWire().offset2D(.15)[0]
if cq.Face.makeFromWires(w).Area()<f.Area():w=f.outerWire().offset2D(-.15)[0]
pocket=cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,.8)).translate((0,0,13.6-f.Center().z))
body=body.cut(pocket)
assert body.val().isValid() and len(body.val().Solids())==1
assert intersection(body.val(),accent.val())<1e-6
parts={'Knob_Black':body.val(),'Knob_Star_Purple':accent.val().translate((0,0,-13.66))}
for name,s in parts.items():
 for ext in ['STEP','stl']:cq.exporters.export(s,str(OUT/(name+'.'+ext)))
 q=cq.importers.importStep(str(OUT/(name+'.STEP'))).val();assert q.isValid()
 assert trimesh.load_mesh(OUT/(name+'.stl')).is_watertight
for gap in [.05,.10,.15]:
 c=cq.Workplane('XY').circle(5).extrude(4).cut(d_bore(gap,-.1,4.2))
 name='Dshaft_sample_'+str(round(6+2*gap,2)).replace('.','p')+'mm'
 for ext in ['STEP','stl']:cq.exporters.export(c,str(OUT/(name+'.'+ext)))
# Check the entire rotation envelope, including an extra 1.1 mm downward allowance.
e=cq.importers.importStep(str(ROOT/'CAD/Starfall_fit_reference_1p6mm.STEP')).val().Solids()
shaft=e[14]
hits=[]
placed=body.val().translate((CX,CY,Z))
for i,s in enumerate(e):
 if intersection(placed,s)>1e-5:hits.append(['rest',i])
env=cq.Workplane('XY').circle(8).extrude(14.2).cut(cq.Workplane('XY').circle(4.5).extrude(3.8)).cut(cq.Workplane('XY').circle(3.1).extrude(12.4)).val()
for dz in [0,-1.1]:
 p=env.translate((CX,CY,Z+dz))
 for i,s in enumerate(e):
  if i==14:continue
  if intersection(p,s)>1e-5:hits.append(['rotation/down',dz,i])
 for n in ['Top','Bottom','Middle_Purple','Purple_Inlays']:
  s=cq.importers.importStep(str(ROOT/'production'/(n+'.STEP'))).val()
  if intersection(p,s)>1e-5:hits.append(['case',dz,n])
 for x,y in [(-37.805,-42.57),(35.975,-41.16),(30.655,28.20),(-31.375,29.20)]:
  h=cq.Workplane('XY').circle(2.75).extrude(3).translate((x,y,4.65)).val()
  if intersection(p,h)>1e-5:hits.append(['screw',dz,x,y])
assert not hits,hits
result={'status':'CAD_CHECKS_PASSED_PHYSICAL_SHAFT_FIT_PENDING','diameter_mm':16,'height_mm':14.2,'nominal_shaft_mm':6,'bore_diameter_mm':6.2,'bore_flat_y_mm':2.5,'shaft_flat_y_mm':2.4,'bore_depth_mm':12.4,'collar_relief_diameter_mm':9,'collar_relief_depth_mm':3.8,'downward_envelope_checked_mm':1.1,'collisions':hits}
(OUT/'VALIDATION.json').write_text(json.dumps(result,indent=2))
a=cq.Assembly(name='Starfall printable knob');a.add(body.val(),name='Black_fluted_knob',color=cq.Color(.06,.05,.08));a.add(accent.val(),name='Purple_star',color=cq.Color(.7,.25,1));a.save(str(OUT/'Knob_Assembled.STEP'))
scene=trimesh.Scene()
for shape,name,color in [(body.val(),'Black_fluted_knob',[24,20,31,255]),(accent.val(),'Purple_star',[183,67,255,255])]:
 v,f=shape.tessellate(.03,.08);m=trimesh.Trimesh(vertices=[p.toTuple() for p in v],faces=f,process=False);m.visual.vertex_colors=np.tile(color,(len(m.vertices),1));scene.add_geometry(m,geom_name=name)
scene.export(OUT/'Knob_Assembled.glb')
(OUT/'README.md').write_text('''# Starfall star knob

Print Knob_Black.stl in black and Knob_Star_Purple.stl in purple. The purple star is flat on the bed; glue into the top recess sparingly. It sits 0.10 mm below the knob top. Do not print Knob_Assembled.STEP as an extra part.

Print the 6.2 mm Dshaft sample first. It is the SAME bore as the knob. The 6.1 and 6.3 mm samples offer tighter/looser comparisons. Samples are labelled by filename; keep them separate. If 6.2 does not grip comfortably, adjust the knob bore using the selected sample before printing. Do not force a tight fit or glue the knob to the encoder. This is a friction-fit design; real shaft/printer tolerances must be tested.

Knob: 16 mm diameter, 14.2 mm high, 28 grip flutes, 6.2 mm D bore with flat at +2.5 mm, 12.4 mm deep; 9 mm collar relief 3.8 mm deep. Print the black body with its closed star face on the bed and its bore facing upward; inspect/clean any bridging at the bore transition. Ask the printer to preserve the small top pocket and account for first-layer expansion. No extra screw or insert is needed.

The full rotation envelope clears the modeled case/electronics/screw heads, including 1.1 mm downward travel allowance. Actual push travel and shaft retention remain physical checks. The original EC11 model is the dimensional reference, not a measurement of the delivered part.
''')
print(result)
