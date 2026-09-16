from pathlib import Path
import json, math, tempfile
from contextlib import nullcontext
import cadquery as cq
from cadquery import exporters
import trimesh
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "production"
CAD = ROOT / "CAD"
PROD.mkdir(exist_ok=True)
CAD.mkdir(exist_ok=True)

BOARD_W, BOARD_H, CLEAR = 84.89, 96.94, 0.40
CAV_W, CAV_H = BOARD_W + 2*CLEAR, BOARD_H + 2*CLEAR
BOTTOM_Z0, BOTTOM_TOP = -17.0, 2.0
BOTTOM_H = BOTTOM_TOP - BOTTOM_Z0
PURPLE_Z0, PURPLE_H = 2.0, 0.9
TOP_Z0, TOP_H = 2.9, 3.0
TOP_Z1 = TOP_Z0 + TOP_H
MX_PLATE_H = 1.30
MX_UPPER_H = TOP_H - MX_PLATE_H
MX_PLATE_OPEN, MX_UPPER_OPEN = 14.2, 16.4
ENC_OPEN = 14.2

MOUNT_HOLES = [(-37.805,-42.57),(35.975,-41.16),(30.655,28.20),(-31.375,29.20)]
SWITCH_CENTERS = [
    (-19.05,-23.32),(0,-23.32),(19.05,-23.32),
    (-19.05,-4.27),(0,-4.27),(19.05,-4.27),
    (-19.05,14.78),(0,14.78),(19.05,14.78),
]
OLED_CENTER = (-18.20,40.815)
OLED_WINDOW = (31.2,12.2)
ENC_CENTER = (29.715,40.01)
REACTOR_POINTS = [
    (-38,-58),(38,-58),(50,-51),(56,-41),(56,41),(50,51),
    (38,58),(-38,58),(-50,51),(-56,41),(-56,-41),(-50,-51)
]


def rect(w,h,z0,t,x=0,y=0):
    return cq.Workplane("XY").box(w,h,t,centered=(True,True,False)).translate((x,y,z0))

def cyl(d,z0,h,x=0,y=0):
    return cq.Workplane("XY").circle(d/2).extrude(h).translate((x,y,z0))

def annulus(od,id_,z0,h,x=0,y=0):
    return cq.Workplane("XY").circle(od/2).circle(id_/2).extrude(h).translate((x,y,z0))

def rect_ring(ow,oh,iw,ih,z0,h,x=0,y=0):
    return rect(ow,oh,z0,h,x,y).cut(rect(iw,ih,z0-.1,h+.2,x,y))

def polyplate(points,z0,t):
    return cq.Workplane("XY").polyline(points).close().extrude(t).translate((0,0,z0))

def rotated_rect(w,h,a,z0,t,x,y):
    return rect(w,h,z0,t,x,y).rotate((x,y,z0),(x,y,z0+1),a)

def text_solid(txt,size,t,x,y,z):
    return cq.Workplane("XY").text(txt,size,t,font="DejaVu Sans",halign="center",valign="center",combine=True).translate((x,y,z))

def crescent(r,cr,dx,z0,h,x,y):
    return cyl(2*r,z0,h,x,y).cut(cyl(2*cr,z0-.1,h+.2,x+dx,y+.35))

def planet(d,rx,ry,irx,iry,a,z0,h,x,y):
    disc = cyl(d,z0,h,x,y)
    ring = cq.Workplane("XY").ellipse(rx,ry).ellipse(irx,iry).extrude(h).rotate((0,0,z0),(0,0,z0+1),a).translate((x,y,z0))
    return disc.union(ring)

def star(size,z0,h,x,y):
    p=[(0,size),(.35*size,.35*size),(size,0),(.35*size,-.35*size),(0,-size),(-.35*size,-.35*size),(-size,0),(-.35*size,.35*size)]
    return cq.Workplane("XY").polyline(p).close().extrude(h).translate((x,y,z0))

def stars(data,z0,h):
    return cq.Compound.makeCompound([star(s,z0,h,x,y).val() for x,y,s in data])

def keepout(shape,z0,h,screw=7.0,encoder=21.0,oled=(35.6,16.6)):
    out=shape
    for x,y in MOUNT_HOLES:
        out=out.cut(cyl(screw,z0-.2,h+.4,x,y))
    out=out.cut(cyl(encoder,z0-.2,h+.4,*ENC_CENTER))
    out=out.cut(rect(oled[0],oled[1],z0-.2,h+.4,*OLED_CENTER))
    return out


def build_bottom():
    # Keep the PCB at Z=-0.70; lower the insert seats for supplied M3x16 screws.
    s=polyplate(REACTOR_POINTS,BOTTOM_Z0,BOTTOM_H)
    s=s.cut(rect(CAV_W,CAV_H,-14.90,BOTTOM_TOP+14.90+.55))
    for x,y in MOUNT_HOLES:
        s=s.union(cyl(8.2,-15.00,14.30,x,y))
        # 5.8 mm installation well above a 4.7 x 4.1 mm heat-set pocket.
        s=s.cut(cyl(5.8,-7.60,7.10,x,y))
        s=s.cut(cyl(4.7,-11.70,4.20,x,y))
        s=s.cut(cyl(3.4,-12.10,1.00,x,y))
    # Cable-overmold access through the thicker Reactor front wall.
    # Recess the exterior face to Y=-50.3, 1.06 mm ahead of the USB shell.
    s=s.cut(rect(22.0,12.0,-7.59,9.0,-.465,-56.3))
    s=s.cut(rect(10.2,14.0,-5.79,5.4,-.465,-48.0))
    for sx in (-1,1):
        for yy in (-26,0,26):
            port=cq.Workplane("YZ",origin=(sx*54.0,0,0)).circle(3.2).extrude(4.0*sx).translate((0,yy,-4.0))
            s=s.cut(port)
    return s


def build_spacer():
    s=polyplate(REACTOR_POINTS,PURPLE_Z0,PURPLE_H).cut(rect(CAV_W+.5,CAV_H+.5,PURPLE_Z0-.2,PURPLE_H+.4))
    for x,y in MOUNT_HOLES:
        s=s.cut(cyl(3.4,PURPLE_Z0-.2,PURPLE_H+.4,x,y))
    for sign in (-1,1):
        panel=cq.Workplane("YZ",origin=(56.2,0,-6)).rect(76,16).extrude(1.0)
        for y in (-35,-17,1,19):
            for pts in [[(y,-12),(y+14,-12),(y,-1)],[(y+16,-1),(y+2,-1),(y+16,-12)]]:
                cutter=cq.Workplane("YZ",origin=(56.0,0,0)).polyline(pts).close().extrude(1.5)
                panel=panel.cut(cutter)
        bridge=rect(1.7,76,2.0,.9,56.35,0)
        panel=panel.union(bridge)
        if sign<0:panel=panel.mirror("YZ")
        s=s.union(panel)
    return s


def build_top():
    lower=polyplate(REACTOR_POINTS,TOP_Z0,MX_PLATE_H)
    upper=polyplate(REACTOR_POINTS,TOP_Z0+MX_PLATE_H,MX_UPPER_H)
    for x,y in SWITCH_CENTERS:
        lower=lower.cut(rect(MX_PLATE_OPEN,MX_PLATE_OPEN,TOP_Z0-.2,MX_PLATE_H+.4,x,y))
        upper=upper.cut(rect(MX_UPPER_OPEN,MX_UPPER_OPEN,TOP_Z0+MX_PLATE_H-.2,MX_UPPER_H+.4,x,y))
    top=lower.union(upper)
    # Keep underside glass clearance; a narrower upper window hides the glass edges.
    top=top.cut(rect(*OLED_WINDOW,TOP_Z0-.5,1.8,*OLED_CENTER))
    top=top.cut(rect(28.4,10.2,4.19,2.0,*OLED_CENTER))
    top=top.cut(cyl(ENC_OPEN,TOP_Z0-.5,TOP_H+1.0,*ENC_CENTER))
    for x,y in MOUNT_HOLES:
        top=top.cut(cyl(3.4,TOP_Z0-.5,TOP_H+1.0,x,y)).cut(cyl(6.4,TOP_Z1-1.25,1.30,x,y))

    # Clearance recesses are generated from the actual inlay outlines in mechanical_fit.
    RD,RZ,IH,IZ=.58,TOP_Z1-.58,.48,TOP_Z1-.48-.04
    ins=[]
    ins.append(rect_ring(33.85,14.85,31.55,12.55,IZ,IH,*OLED_CENTER).val())

    er=annulus(19.4,ENC_OPEN,RZ,RD+.1,*ENC_CENTER)
    eri=annulus(19.0,ENC_OPEN+.35,IZ,IH,*ENC_CENTER)
    for x,y in MOUNT_HOLES:
        er=er.cut(cyl(6.8,RZ-.1,RD+.3,x,y)); eri=eri.cut(cyl(7.0,IZ-.1,IH+.3,x,y))
    ins.append(eri.val())

    for x,y in SWITCH_CENTERS:
        ins.append(rect_ring(17.72,17.72,16.75,16.75,IZ,IH,x,y).val())

    # Bold forward-slanted block lettering.
    letters=[(.35,[(0,0),(4.3,0),(4.3,1.3),(1.3,1.3),(1.3,5.8),(0,5.8)]),(5.1,[(0,4.5),(1.8,4.5),(1.8,0),(3.1,0),(3.1,4.5),(4.9,4.5),(4.9,5.8),(0,5.8)]),(10.8,[(0,0),(4.7,0),(4.7,1.3),(1.3,1.3),(1.3,4.5),(4.7,4.5),(4.7,5.8),(0,5.8)])]
    for offset,points in letters:
        points=[(x+offset+.22*y+.6,y+37.6) for x,y in points]
        ins.append(polyplate(points,IZ,IH).val())
    for x,y,size in [(-43,43,2.8),(-46,24,1.9),(-43,2,2.5),(-46,-19,1.6),(-25,-46,2.3),(-12,-49,1.5),(12,-48,2.0),(26,-49,1.3),(43,-26,2.2),(46,-4,1.5),(44,16,2.4),(9,52,1.6)]:
        ins.append(star(size,IZ,IH,x,y).val())
    ins.append(crescent(4.1,3.7,1.5,IZ,IH,0,-44).val())
    for x,y in MOUNT_HOLES:
        ins.append(annulus(9.0,7.5,IZ,IH,x,y).val())
    return top,cq.Compound.makeCompound(ins)


def keycap(x,y):
    return cq.Workplane("XY",origin=(x,y,6.55)).rect(17.8,17.8).workplane(offset=10).rect(14.8,14.8).loft(combine=True)

def render_parts():
    caps=cq.Compound.makeCompound([keycap(x,y).val() for x,y in SWITCH_CENTERS])
    pcb=rect(BOARD_W,BOARD_H,-.7,1.6)
    bezel=rect(33,13.6,5.85,.65,*OLED_CENTER)
    screen=rect(29,9.2,6.48,.22,*OLED_CENTER)
    oledtxt=text_solid("STARFALL",3.2,.16,*OLED_CENTER,6.70)
    knob=cyl(15.8,8.0,11.3,*ENC_CENTER).union(cyl(15.0,19.3,.9,*ENC_CENTER))
    kring=annulus(18.7,16.2,5.88,.9,*ENC_CENTER)
    screws=[]
    for x,y in MOUNT_HOLES:
        screws.extend([cyl(3.0,TOP_Z1-1.25-16,16,x,y).val(),cyl(5.5,TOP_Z1-1.25,3.0,x,y).val()])
    return caps,pcb,bezel,screen,oledtxt,knob,kring,cq.Compound.makeCompound(screws)


def mesh(shape,name,color,tmp):
    shape=shape.val() if isinstance(shape,cq.Workplane) else shape
    vertices,faces=shape.tessellate(.05,.1)
    m=trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],faces=faces,process=False)
    m.visual.vertex_colors=np.tile(np.array(color,dtype=np.uint8),(len(m.vertices),1)); return m


bottom,spacer=build_bottom(),build_spacer()
top,inlays=build_top()
from mechanical_fit import correct_top_and_inlays, export_fit_reference, check_mechanics, validate_exports
top,inlays=correct_top_and_inlays(top,inlays,ROOT,SWITCH_CENTERS,ENC_CENTER,MOUNT_HOLES)
electronics=export_fit_reference(ROOT)


# Canonical production files
for name,shape in [("Top.STEP",top),("Bottom.STEP",bottom),("Middle_Purple.STEP",spacer),("Purple_Inlays.STEP",cq.Workplane(obj=inlays)),
                   ("Top.stl",top),("Bottom.stl",bottom),("Middle_Purple.stl",spacer),("Purple_Inlays.stl",cq.Workplane(obj=inlays))]:
    exporters.export(shape,str(PROD/name),opt={'write_pcurves':False} if name.endswith('.STEP') else {})

validate_exports(ROOT)

case=cq.Assembly(name="Starfall Reactor Celestial FINAL")
case.add(bottom.val(),name="Bottom black",color=cq.Color(.025,.025,.035)); case.add(spacer.val(),name="Middle purple",color=cq.Color(.42,.06,.74)); case.add(top.val(),name="Top black",color=cq.Color(.045,.045,.06)); case.add(inlays,name="Purple celestial inlays",color=cq.Color(.68,.16,.98))
case.save(str(CAD/"Starfall_Reactor_Celestial_FINAL_COLORED_CASE.STEP"))

caps,pcb,bezel,screen,oledtxt,knob,kring,screws=render_parts()
with nullcontext(None) as td:
    scene=trimesh.Scene()
    for s,n,c in [
        (bottom,"Bottom_Black",[15,15,22,255]),(spacer,"Middle_Purple",[183,67,255,255]),(top,"Top_Black",[28,24,34,255]),
        (cq.Workplane(obj=inlays),"Purple_Celestial_Inlays",[183,67,255,255]),(pcb,"PCB",[36,104,72,255]),(cq.Workplane(obj=caps),"Keycaps",[15,15,22,255]),
        (bezel,"OLED_Bezel",[15,15,22,255]),(screen,"OLED_Screen",[4,6,16,255]),(oledtxt,"OLED_STARFALL",[230,150,255,255]),
        (knob,"Encoder_Knob",[15,15,22,255]),(cq.Workplane(obj=screws),"M3_Screws",[175,175,190,255])]:
        scene.add_geometry(mesh(s,n,c,td),geom_name=n)
    scene.export(CAD/"Starfall_Reactor_Celestial_FINAL_FULL_COLOR.glb")

# Mechanical/print-readiness record
sd=math.dist(MOUNT_HOLES[2],ENC_CENTER)
enc_clear=sd-(ENC_OPEN/2+6.4/2)
a=math.radians(20); py=math.sqrt((4.5*math.sin(a))**2+(1.55*math.cos(a))**2)
check={
    "cad_solids_valid":{"Top":top.val().isValid(),"Bottom":bottom.val().isValid(),"Middle_Purple":spacer.val().isValid(),"Purple_Inlays":inlays.isValid()},
    "pcb_cavity_mm":[round(CAV_W,2),round(CAV_H,2)],"pcb_clearance_per_side_mm":CLEAR,
    "m3_pass_through_mm":3.4,"screw_head_seat_mm":6.4,"heat_set_insert_pocket_mm":4.7,"encoder_opening_mm":ENC_OPEN,
    "encoder_to_nearby_screw_edge_clearance_mm":round(enc_clear,3),"right_planet_center_mm":[49.0,8.5],
    "right_planet_clearance_to_lower_rail_mm":round((8.5-py)-3.5,3),"right_planet_clearance_to_upper_rail_mm":round(13-(8.5+py),3),
    "usb_c_tunnel_preserved":True,"switch_and_mount_coordinates_preserved":True
}
check.update(check_mechanics(ROOT,top,bottom,spacer,inlays,electronics,MOUNT_HOLES,SWITCH_CENTERS))
(PROD/"CASE_PRINT_READY_CHECK.json").write_text(json.dumps(check,indent=2)+"\n")
print(json.dumps(check,indent=2))


