import os, shutil, zipfile, math, json, csv
from pathlib import Path
import cadquery as cq
from cadquery import exporters
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals
from PIL import Image, ImageDraw, ImageFont

BASE_ZIP = Path('/mnt/data/Starfall_Hackpad_Working_Package_v24.zip')
SRC_STEP = Path('/mnt/data/Starfall(1).step')
OLED_FULL = Path('/mnt/data/ER_OLEDM0.91_1x-I2C_FULL_MODULE.step')
OUT_ROOT = Path('/mnt/data/Starfall_Hackpad_Submission_v25')
ZIP_OUT = Path('/mnt/data/Starfall_Hackpad_Working_Package_v25.zip')
TMP = Path('/mnt/data/starfall_v25_tmp')

if OUT_ROOT.exists():
    shutil.rmtree(OUT_ROOT)
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)

# Extract previous package as a starting point
with zipfile.ZipFile(BASE_ZIP, 'r') as zf:
    zf.extractall(TMP)
base_root = TMP / 'Starfall_Hackpad_Submission'
shutil.copytree(base_root, OUT_ROOT)

CAD = OUT_ROOT / 'CAD'
PROD = OUT_ROOT / 'production'
ASSETS = OUT_ROOT / 'assets'
PCB = OUT_ROOT / 'PCB'
FW = OUT_ROOT / 'Firmware'
TOOLS = OUT_ROOT / 'tools'
for d in [CAD, PROD, ASSETS, PCB, FW, TOOLS]:
    d.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Geometry helpers
# -----------------------------
def rounded_box_xy(w, h, z0, t, r):
    wp = cq.Workplane('XY').box(w, h, t, centered=(True, True, False)).translate((0,0,z0))
    if r > 0:
        wp = wp.edges('|Z').fillet(r)
    return wp

def rect_prism(w,h,z0,t,x=0,y=0):
    return cq.Workplane('XY').box(w,h,t,centered=(True,True,False)).translate((x,y,z0))

def cyl(d,z0,h,x=0,y=0):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z0))

def annulus(od, id_, z0, h, x=0,y=0):
    return cq.Workplane('XY').circle(od/2).circle(id_/2).extrude(h).translate((x,y,z0))

def rect_ring(ow, oh, iw, ih, z0, h, x=0,y=0):
    outer = rect_prism(ow,oh,z0,h,x,y)
    inner = rect_prism(iw,ih,z0-0.1,h+0.2,x,y)
    return outer.cut(inner)

# -----------------------------
# Shorten OLED pins in the electronics assembly
# -----------------------------
obj = cq.importers.importStep(str(SRC_STEP))
solids = obj.solids().vals()

def is_long_oled_pin(s):
    bb=s.BoundingBox()
    return (0.60 <= bb.xlen <= 0.68 and 0.60 <= bb.ylen <= 0.68 and bb.zlen > 10
            and -1 < bb.xmin < 1 and 35 < bb.ymin < 45)

kept=[]
removed=[]
for s in solids:
    if is_long_oled_pin(s):
        removed.append(s)
    else:
        kept.append(s)

short_pin_shapes=[]
for s in removed:
    bb=s.BoundingBox()
    cx=(bb.xmin+bb.xmax)/2
    cy=(bb.ymin+bb.ymax)/2
    ztop=bb.zmax
    zbottom=-1.20
    short_pin_shapes.append(
        cq.Workplane('XY').box(bb.xlen, bb.ylen, ztop-zbottom, centered=(True,True,False))
        .translate((cx,cy,zbottom)).val()
    )

all_elec_shapes = kept + short_pin_shapes
elec_compound = cq.Compound.makeCompound(all_elec_shapes)
exporters.export(elec_compound, str(CAD/'Starfall_electronics_short_OLED.step'))

# Standalone OLED step with short pins
try:
    old_oled = cq.importers.importStep(str(OLED_FULL))
    oled_parts=[]
    old_pin_centers=[]
    for s in old_oled.solids().vals():
        bb=s.BoundingBox()
        if 0.60 <= bb.xlen <= 0.68 and 0.60 <= bb.ylen <= 0.68 and bb.zlen > 10:
            old_pin_centers.append(((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,bb.zmax,bb.xlen,bb.ylen))
        else:
            oled_parts.append(s)
    for cx,cy,ztop,xlen,ylen in old_pin_centers:
        zbottom=-1.2
        oled_parts.append(cq.Workplane('XY').box(xlen,ylen,ztop-zbottom, centered=(True,True,False)).translate((cx,cy,zbottom)).val())
    exporters.export(cq.Compound.makeCompound(oled_parts), str(CAD/'ER_OLEDM0.91_1x-I2C_FULL_SHORT_PINS.step'))
except Exception:
    pass

# -----------------------------
# Main case geometry - slightly taller than v24
# -----------------------------
OUT_W = 91.0
OUT_H = 102.5
CORNER_R = 5.0
BOARD_W = 84.89
BOARD_H = 96.94
CLEAR = 0.40
CAV_W = BOARD_W + 2*CLEAR
CAV_H = BOARD_H + 2*CLEAR

BOTTOM_Z0 = -10.6     # taller by +2.6 mm vs previous -8.0
BOTTOM_TOP = 2.0
BOTTOM_H = BOTTOM_TOP - BOTTOM_Z0
PURPLE_Z0 = 2.0
PURPLE_H = 0.9
TOP_Z0 = PURPLE_Z0 + PURPLE_H
TOP_H = 3.0
TOP_Z1 = TOP_Z0 + TOP_H
HARDWARE_Z_SHIFT = -0.70

MOUNT_HOLES = [(-37.805,-42.57),(35.975,-41.16),(30.655,28.20),(-31.375,29.20)]
SWITCH_CENTERS = [
    (-19.05,-23.32),(0.0,-23.32),(19.05,-23.32),
    (-19.05,-4.27),(0.0,-4.27),(19.05,-4.27),
    (-19.05,14.78),(0.0,14.78),(19.05,14.78),
]
OLED_WINDOW_CENTER=(-18.20,40.815)
OLED_WINDOW=(31.2,12.2)
ENC_CENTER=(29.715,40.01)

# Build bottom shell
bottom = rounded_box_xy(OUT_W, OUT_H, BOTTOM_Z0, BOTTOM_H, CORNER_R)
# deeper cavity for more internal clearance
cavity_z = -8.50
cavity_h = BOTTOM_TOP - cavity_z + 0.5
cavity = rect_prism(CAV_W, CAV_H, cavity_z, cavity_h)
bottom = bottom.cut(cavity)

# support bosses and heatset insert pockets
for x,y in MOUNT_HOLES:
    boss = cyl(8.2,-6.05,5.27,x,y)
    bottom = bottom.union(boss)
    pocket = cyl(4.7,-5.08,4.05,x,y)
    bottom = bottom.cut(pocket)

# usb-c opening
usb_x = -0.465
usb = cq.Workplane('XY').box(11.8,6.0,5.6, centered=(True,True,False)).translate((usb_x,-50.2,-5.9))
bottom = bottom.cut(usb)

# side/front chevrons
# Front windows
for pts in [
    [(-39,-5.3),(-31,-5.3),(-36,-1.7)],
    [(-30,-5.3),(-21,-5.3),(-25.5,-2.0)],
    [(21,-5.3),(30,-5.3),(25.5,-2.0)],
    [(31,-5.3),(39,-5.3),(36,-1.7)],
]:
    try:
        win = cq.Workplane('XZ', origin=(0,-53.0,0)).polyline(pts).close().extrude(7.0)
        bottom = bottom.cut(win)
    except Exception:
        pass

# Left and right side diagonal windows for the concept look
# built as slanted parallelogram cutouts in local YZ plane and extruded through X
side_patterns = [
    [(-6.0,-7.0), (0.0,-7.0), (4.5,-2.0), (-1.5,-2.0)],
    [(-1.5,-7.0), (4.5,-7.0), (9.0,-2.0), (3.0,-2.0)],
    [(3.0,-7.0), (9.0,-7.0), (13.5,-2.0), (7.5,-2.0)],
]
for side_sign, x_origin in [(-1, -45.7), (1, 45.7)]:
    for base_y, base_z in [(-35.0,-3.0), (-12.0,-3.0), (12.0,-3.0)]:
        for poly in side_patterns[:2]:
            pts = [(base_y + py, base_z + pz) for py,pz in poly]
            try:
                cut = cq.Workplane('YZ', origin=(x_origin,0,0)).polyline(pts).close().extrude(7.0*side_sign)
                bottom = bottom.cut(cut)
            except Exception:
                pass

# Top plate with stepped MX retention geometry
MX_PLATE_H = 1.30
MX_UPPER_H = TOP_H - MX_PLATE_H
MX_PLATE_OPEN = 14.2
MX_UPPER_OPEN = 16.4
ENC_OPEN = 18.0

top_base = rounded_box_xy(OUT_W,OUT_H,TOP_Z0,MX_PLATE_H,CORNER_R)
for x,y in SWITCH_CENTERS:
    top_base = top_base.cut(rect_prism(MX_PLATE_OPEN,MX_PLATE_OPEN,TOP_Z0-0.2,MX_PLATE_H+0.4,x,y))

top_upper_z = TOP_Z0 + MX_PLATE_H
top_upper = rounded_box_xy(OUT_W,OUT_H,top_upper_z,MX_UPPER_H,CORNER_R)
for x,y in SWITCH_CENTERS:
    top_upper = top_upper.cut(rect_prism(MX_UPPER_OPEN,MX_UPPER_OPEN,top_upper_z-0.2,MX_UPPER_H+0.4,x,y))

top = top_base.union(top_upper)
top = top.cut(rect_prism(OLED_WINDOW[0],OLED_WINDOW[1],TOP_Z0-0.5,TOP_H+1.0,*OLED_WINDOW_CENTER))
top = top.cut(cyl(ENC_OPEN,TOP_Z0-0.5,TOP_H+1.0,*ENC_CENTER))

shifted_elec=[s.translate((0,0,HARDWARE_Z_SHIFT)) for s in all_elec_shapes]
def near_switch(cx,cy):
    return any(abs(cx-sx)<9.0 and abs(cy-sy)<9.0 for sx,sy in SWITCH_CENTERS)
for s in shifted_elec:
    bb=s.BoundingBox()
    if bb.zmax <= TOP_Z0+0.02 or bb.zmin >= TOP_Z1:
        continue
    cx=(bb.xmin+bb.xmax)/2
    cy=(bb.ymin+bb.ymax)/2
    if near_switch(cx,cy) and bb.xlen>10 and bb.ylen>10:
        continue
    if abs(cx-ENC_CENTER[0])<10 and abs(cy-ENC_CENTER[1])<10:
        continue
    if bb.xlen>50 or bb.ylen>50:
        continue
    relief_top=min(bb.zmax+0.25, TOP_Z1-0.80)
    if relief_top > TOP_Z0+0.05:
        rw=max(bb.xlen+0.7,1.2)
        rh=max(bb.ylen+0.7,1.2)
        relief=rect_prism(rw,rh,TOP_Z0-0.15,relief_top-(TOP_Z0-0.15),cx,cy)
        top=top.cut(relief)

# M3 pass-through holes and shallow screw-seat chamfer/counterbore
for x,y in MOUNT_HOLES:
    top=top.cut(cyl(3.4,TOP_Z0-0.5,TOP_H+1.0,x,y))
    # shallow counterbore for screw heads
    top=top.cut(cyl(6.4,TOP_Z1-1.3,1.35,x,y))

# decorative recesses for purple inlays
INLAY_DEPTH=0.55
INLAY_Z=TOP_Z1-INLAY_DEPTH
bezel_recess=rect_ring(34.0,15.0,31.2,12.2,INLAY_Z,INLAY_DEPTH+0.1,*OLED_WINDOW_CENTER)
top=top.cut(bezel_recess)
enc_recess=annulus(21.0,ENC_OPEN,INLAY_Z,INLAY_DEPTH+0.1,*ENC_CENTER)
top=top.cut(enc_recess)
for x,y in SWITCH_CENTERS:
    top=top.cut(rect_ring(17.8,17.8,MX_UPPER_OPEN,MX_UPPER_OPEN,INLAY_Z,INLAY_DEPTH+0.1,x,y))
for x,y in MOUNT_HOLES:
    top=top.cut(annulus(7.2,3.6,INLAY_Z,INLAY_DEPTH+0.1,x,y))

# LTC recess
ltc_shape = None
try:
    ltc_shape = (cq.Workplane('XY')
        .text('LTC', 8.0, INLAY_DEPTH, font='DejaVu Sans', halign='center', valign='center', combine=True)
        .translate((8.5,40.0,INLAY_Z)).val())
    top = top.cut(cq.Workplane(obj=ltc_shape))
except Exception:
    ltc_shape = None

# Purple spacer ring
purple_spacer = rounded_box_xy(OUT_W,OUT_H,PURPLE_Z0,PURPLE_H,CORNER_R)
purple_spacer = purple_spacer.cut(rounded_box_xy(CAV_W+0.5,CAV_H+0.5,PURPLE_Z0-0.2,PURPLE_H+0.4,3.6))
for x,y in MOUNT_HOLES:
    purple_spacer = purple_spacer.cut(cyl(3.4,PURPLE_Z0-0.2,PURPLE_H+0.4,x,y))

# Purple inlays compound
inlay_shapes=[]
inlay_h=0.48
inlay_z=TOP_Z1-inlay_h-0.03
inlay_shapes.append(rect_ring(33.8,14.8,31.4,12.4,inlay_z,inlay_h,*OLED_WINDOW_CENTER).val())
inlay_shapes.append(annulus(20.8,ENC_OPEN+0.2,inlay_z,inlay_h,*ENC_CENTER).val())
for x,y in SWITCH_CENTERS:
    inlay_shapes.append(rect_ring(17.6,17.6,MX_UPPER_OPEN+0.2,MX_UPPER_OPEN+0.2,inlay_z,inlay_h,x,y).val())
for x,y in MOUNT_HOLES:
    inlay_shapes.append(annulus(7.0,3.8,inlay_z,inlay_h,x,y).val())
if ltc_shape is not None:
    try:
        ltc_insert=(cq.Workplane('XY')
            .text('LTC',8.0,inlay_h,font='DejaVu Sans',halign='center',valign='center',combine=True)
            .translate((8.5,40.0,inlay_z)).val())
        inlay_shapes.append(ltc_insert)
    except Exception:
        pass
# front chevron backing panels
for pts in [
    [(-39,-5.3),(-31,-5.3),(-36,-1.7)],
    [(-30,-5.3),(-21,-5.3),(-25.5,-2.0)],
    [(21,-5.3),(30,-5.3),(25.5,-2.0)],
    [(31,-5.3),(39,-5.3),(36,-1.7)],
]:
    try:
        panel=cq.Workplane('XZ', origin=(0,-48.15,0)).polyline(pts).close().extrude(0.55).val()
        inlay_shapes.append(panel)
    except Exception:
        pass
# side diagonal backing strips
for side_sign, x_origin in [(-1, -45.15), (1, 45.15)]:
    for base_y, base_z in [(-35.0,-3.0), (-12.0,-3.0), (12.0,-3.0)]:
        for poly in side_patterns[:2]:
            pts = [(base_y + py, base_z + pz) for py,pz in poly]
            try:
                panel = cq.Workplane('YZ', origin=(x_origin,0,0)).polyline(pts).close().extrude(0.55*side_sign).val()
                inlay_shapes.append(panel)
            except Exception:
                pass

purple_inlays_compound = cq.Compound.makeCompound(inlay_shapes)

# Export production parts
for p in PROD.iterdir():
    if p.is_file():
        p.unlink()
exporters.export(top, str(PROD/'Top.STEP'))
exporters.export(bottom, str(PROD/'Bottom.STEP'))
exporters.export(purple_spacer, str(PROD/'Middle_Purple.STEP'))
exporters.export(purple_inlays_compound, str(PROD/'Purple_Inlays.STEP'))
exporters.export(top, str(PROD/'Top.stl'))
exporters.export(bottom, str(PROD/'Bottom.stl'))
exporters.export(purple_spacer, str(PROD/'Middle_Purple.stl'))
exporters.export(purple_inlays_compound, str(PROD/'Purple_Inlays.stl'))

# Save build script snapshot
build_script_out = CAD / 'build_case.py'
shutil.copy2(__file__, build_script_out)

# -----------------------------
# Assembly visuals: keycaps, knob, screws
# -----------------------------
elec_for_assy = cq.Workplane(obj=elec_compound).translate((0,0,HARDWARE_Z_SHIFT)).val()

keycaps=[]
for x,y in SWITCH_CENTERS:
    cap=(cq.Workplane('XY', origin=(x,y,6.55))
         .rect(17.8,17.8)
         .workplane(offset=11.0).rect(14.6,14.6)
         .loft(combine=True))
    try:
        cap=cap.edges().fillet(0.55)
    except Exception:
        pass
    keycaps.append(cap.val())
keycaps_compound=cq.Compound.makeCompound(keycaps)

# encoder knob with purple base ring
knob = cq.Workplane('XY').circle(8.0).extrude(11.5).translate((ENC_CENTER[0],ENC_CENTER[1],8.8))
knob_top = cq.Workplane('XY').circle(7.6).extrude(0.8).translate((ENC_CENTER[0],ENC_CENTER[1],20.3))
knob = knob.union(knob_top)
knob_ring = annulus(18.6,14.8,TOP_Z1-0.02,1.0,*ENC_CENTER)

# simple screws for assembly visuals
screw_shapes=[]
for x,y in MOUNT_HOLES:
    shaft = cyl(2.9, TOP_Z0-0.4, 12.0, x, y)
    head = cyl(5.6, TOP_Z1-0.9, 1.9, x, y)
    screw_shapes.append(shaft.union(head).val())
screws_compound = cq.Compound.makeCompound(screw_shapes)

# Export assembly STEPs
assy=cq.Assembly(name='Starfall complete Hackpad assembly')
assy.add(bottom.val(), name='Bottom black shell', color=cq.Color(0.04,0.04,0.05))
assy.add(purple_spacer.val(), name='Purple accent spacer', color=cq.Color(0.42,0.08,0.70))
assy.add(top.val(), name='Top black plate', color=cq.Color(0.05,0.05,0.06))
assy.add(purple_inlays_compound, name='Purple decorative inlays', color=cq.Color(0.55,0.12,0.85))
assy.add(elec_for_assy, name='Starfall PCB and electronics - OLED pins shortened', color=cq.Color(0.24,0.33,0.25))
assy.add(keycaps_compound, name='Nine 1u keycap visuals', color=cq.Color(0.025,0.025,0.03))
assy.add(knob.val(), name='Encoder knob visual', color=cq.Color(0.03,0.03,0.035))
assy.add(knob_ring.val(), name='Purple knob ring', color=cq.Color(0.55,0.12,0.85))
assy.add(screws_compound, name='M3 screw visuals', color=cq.Color(0.18,0.18,0.20))
assy.save(str(CAD/'Starfall_assembled.STEP'))

case_assy=cq.Assembly(name='Starfall case assembly')
case_assy.add(bottom.val(), name='Bottom', color=cq.Color(0.04,0.04,0.05))
case_assy.add(purple_spacer.val(), name='Middle purple', color=cq.Color(0.42,0.08,0.70))
case_assy.add(top.val(), name='Top', color=cq.Color(0.05,0.05,0.06))
case_assy.add(purple_inlays_compound, name='Purple inlays', color=cq.Color(0.55,0.12,0.85))
case_assy.save(str(CAD/'Starfall_case_assembly.STEP'))

# -----------------------------
# GLB presentation asset with screen graphics and custom keycap logos
# -----------------------------
def export_stl(shape, path):
    exporters.export(shape, str(path))

def load_colored_mesh(shape, color_rgba, name):
    path = TMP / f'{name}.stl'
    export_stl(shape, path)
    mesh = trimesh.load_mesh(path, force='mesh')
    mesh.visual.vertex_colors = color_rgba
    return mesh

scene = trimesh.Scene()

# Add main parts
scene.add_geometry(load_colored_mesh(bottom, [18,18,22,255], 'glb_bottom'), geom_name='bottom')
scene.add_geometry(load_colored_mesh(purple_spacer, [108,30,180,255], 'glb_mid'), geom_name='purple_spacer')
scene.add_geometry(load_colored_mesh(top, [24,24,28,255], 'glb_top'), geom_name='top')
scene.add_geometry(load_colored_mesh(purple_inlays_compound, [175,90,255,255], 'glb_inlays'), geom_name='inlays')
scene.add_geometry(load_colored_mesh(keycaps_compound, [20,20,24,255], 'glb_keycaps'), geom_name='keycaps')
scene.add_geometry(load_colored_mesh(knob, [22,22,24,255], 'glb_knob'), geom_name='knob')
scene.add_geometry(load_colored_mesh(knob_ring, [170,80,255,255], 'glb_knob_ring'), geom_name='knob_ring')
scene.add_geometry(load_colored_mesh(screws_compound, [55,55,62,255], 'glb_screws'), geom_name='screws')

# Texture helpers
try:
    font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 92)
    font_med = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
except Exception:
    font_bold = ImageFont.load_default()
    font_med = ImageFont.load_default()
    font_small = ImageFont.load_default()

PURPLE = (200, 145, 255, 255)
LIGHT = (240, 225, 255, 255)
BLACK = (12,12,16,255)
TRANSPARENT = (0,0,0,0)

# OLED screen texture
screen_img = Image.new('RGBA', (1024, 384), BLACK)
d = ImageDraw.Draw(screen_img)
# subtle stars
for x,y,r in [(120,85,4),(165,122,3),(210,72,2),(320,115,3),(390,155,4),(550,75,4),(590,120,3),(640,150,2),(715,95,2)]:
    d.ellipse((x-r,y-r,x+r,y+r), fill=LIGHT)
# title and separators
# main title
try:
    d.text((40,28), 'Starfall', font=font_bold, fill=LIGHT)
except Exception:
    d.text((40,28), 'Starfall', fill=LIGHT)
# planet graphic
cx, cy = 185, 200
r=36
d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=PURPLE, width=8)
# ring as tilted ellipse
bbox=(cx-70, cy-30, cx+70, cy+30)
d.arc(bbox, start=200, end=20, fill=PURPLE, width=8)
d.arc((cx-72, cy-32, cx+72, cy+32), start=20, end=200, fill=PURPLE, width=8)
# mountain silhouette
mountain = [(20,318),(90,240),(165,295),(230,225),(310,295),(380,238),(420,280),(420,350),(20,350)]
d.polygon(mountain, fill=(118,55,190,255))
# right side menu
menu_x = 720
d.text((menu_x,72), 'MACRO', font=font_small, fill=LIGHT)
d.text((menu_x,118), 'CREATE', font=font_small, fill=LIGHT)
d.text((menu_x,164), 'PLAY', font=font_small, fill=LIGHT)
d.text((menu_x,210), 'REPEAT', font=font_small, fill=LIGHT)
# little bars
for y in [100, 146, 192, 238]:
    d.rounded_rectangle((675,y,695,y+8), radius=4, fill=PURPLE)
# left lower stars
for x,y,s in [(58,145,9),(95,168,6),(145,135,5),(295,120,5)]:
    d.line((x-s,y,x+s,y), fill=LIGHT, width=3)
    d.line((x,y-s,x,y+s), fill=LIGHT, width=3)
# Save PNG too
screen_png = ASSETS/'oled_screen_graphic.png'
screen_img.save(screen_png)

# Keycap icon textures
icon_names = ['star4','planet','plus','chevrons_up','crosshair','chevrons_down','moon','sparkle_big','sparkles']
icon_files=[]

def draw_diamond_star(draw, cx, cy, size, fill):
    pts=[(cx,cy-size),(cx+size*0.55,cy),(cx,cy+size),(cx-size*0.55,cy)]
    draw.polygon(pts, fill=fill)

def draw_chevrons(draw, up=True, fill=PURPLE):
    basey = 150 if up else 112
    sign = -1 if up else 1
    for off in [0, 28]:
        pts=[(70, basey+off*sign), (128, basey-42*sign+off*sign), (143, basey-26*sign+off*sign), (86, basey+15*sign+off*sign)]
        draw.line(pts, fill=fill, width=12, joint='curve')

for idx,name in enumerate(icon_names):
    img = Image.new('RGBA', (256,256), (20,20,24,255))
    draw = ImageDraw.Draw(img)
    if name=='star4':
        draw_diamond_star(draw,128,128,48,PURPLE)
    elif name=='planet':
        draw.ellipse((90,90,166,166), outline=PURPLE, width=8)
        draw.arc((52,102,204,154), 190, 350, fill=PURPLE, width=8)
        draw.arc((52,102,204,154), 10, 170, fill=PURPLE, width=8)
    elif name=='plus':
        draw.rounded_rectangle((118,62,138,194), radius=6, fill=PURPLE)
        draw.rounded_rectangle((62,118,194,138), radius=6, fill=PURPLE)
    elif name=='chevrons_up':
        draw_chevrons(draw, up=True)
    elif name=='crosshair':
        draw.ellipse((86,86,170,170), outline=PURPLE, width=8)
        draw.line((128,62,128,194), fill=PURPLE, width=10)
        draw.line((62,128,194,128), fill=PURPLE, width=10)
        draw.ellipse((119,119,137,137), fill=PURPLE)
    elif name=='chevrons_down':
        draw_chevrons(draw, up=False)
    elif name=='moon':
        draw.ellipse((76,72,176,172), fill=PURPLE)
        draw.ellipse((112,66,208,164), fill=(20,20,24,255))
    elif name=='sparkle_big':
        draw_diamond_star(draw,128,128,52,PURPLE)
        draw.line((128,58,128,198), fill=PURPLE, width=6)
        draw.line((58,128,198,128), fill=PURPLE, width=6)
    elif name=='sparkles':
        draw_diamond_star(draw,110,112,28,PURPLE)
        draw_diamond_star(draw,154,92,18,PURPLE)
        draw_diamond_star(draw,168,140,14,PURPLE)
        draw_diamond_star(draw,90,156,12,PURPLE)
    file = ASSETS / f'keycap_icon_{idx+1}_{name}.png'
    img.save(file)
    icon_files.append(file)

# Utility: textured rectangle mesh in XY plane centered at x,y,z
from trimesh.visual.texture import unmerge_faces

def textured_plane(width, height, x, y, z, image_path):
    verts = [
        [x - width/2, y - height/2, z],
        [x + width/2, y - height/2, z],
        [x + width/2, y + height/2, z],
        [x - width/2, y + height/2, z],
    ]
    faces = [[0,1,2],[0,2,3]]
    uv = [[0,1],[1,1],[1,0],[0,0]]
    material = PBRMaterial(baseColorTexture=Image.open(image_path), metallicFactor=0.0, roughnessFactor=1.0)
    visual = TextureVisuals(uv=uv, material=material)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, visual=visual, process=False)
    return mesh

# Add OLED screen plane
screen_plane = textured_plane(29.8, 10.8, OLED_WINDOW_CENTER[0], OLED_WINDOW_CENTER[1], TOP_Z1+0.03, screen_png)
scene.add_geometry(screen_plane, geom_name='oled_screen_graphic')

# Add textured keycap tops
for (x,y), icon_file in zip(SWITCH_CENTERS, icon_files):
    plane = textured_plane(14.8, 14.8, x, y, 17.58, icon_file)
    scene.add_geometry(plane, geom_name=f'icon_{icon_file.stem}')

# Add front starfall wordmark as textured plane on front face, optional
front_img = Image.new('RGBA', (1024, 128), TRANSPARENT)
df = ImageDraw.Draw(front_img)
try:
    ff = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 64)
except Exception:
    ff = ImageFont.load_default()
df.text((240,25), 'STARFALL', font=ff, fill=PURPLE)
front_png = ASSETS/'front_starfall_wordmark.png'
front_img.save(front_png)
# simple front plane slightly in front of the case
# build in XZ plane facing -Y by rotating a textured quad from XY
front_w, front_h = 25.0, 3.8
verts = [
    [-front_w/2, 0, -front_h/2], [front_w/2,0,-front_h/2], [front_w/2,0,front_h/2], [-front_w/2,0,front_h/2]
]
faces = [[0,1,2],[0,2,3]]
uv = [[0,1],[1,1],[1,0],[0,0]]
material = PBRMaterial(baseColorTexture=Image.open(front_png), metallicFactor=0.0, roughnessFactor=1.0)
visual = TextureVisuals(uv=uv, material=material)
front_mesh = trimesh.Trimesh(vertices=verts, faces=faces, visual=visual, process=False)
# rotate so normal faces outward at -Y, then translate to front
rot = trimesh.transformations.rotation_matrix(math.radians(90), [1,0,0])
front_mesh.apply_transform(rot)
front_mesh.apply_translation([0, -50.95, -1.0])
scene.add_geometry(front_mesh, geom_name='front_wordmark')

# Save GLB
GLB_PATH = CAD/'Starfall_render_colored.glb'
scene.export(GLB_PATH)

# Copy GLB to assets for convenience too
shutil.copy2(GLB_PATH, ASSETS/'Starfall_render_colored.glb')

# Update mechanical notes and checklist/status
notes = f'''# Starfall mechanical notes (v25)\n\n- Case outer size: {OUT_W:.1f} x {OUT_H:.1f} mm\n- Total case stack height: {BOTTOM_H + PURPLE_H + TOP_H:.1f} mm\n- This version is taller than v24 by 2.6 mm to increase internal clearance.\n- Top plate includes 3.4 mm M3 pass-through holes and 6.4 mm shallow head seats.\n- Bottom includes 4.7 mm heat-set insert pockets for M3 threaded inserts.\n- OLED header pins shortened to ~1.2 mm below the PCB plane.\n- USB-C opening included.\n- Production files are the 4 case parts in /production.\n\nSubmission note: this package still needs your final KiCad project files inside /PCB and your own README before final Hackpad submission.\n'''
(CAD/'MECHANICAL_NOTES.md').write_text(notes, encoding='utf-8')

status = '''STARFALL PACKAGE STATUS (v25)\n\nCompleted by this package:\n- Updated taller case CAD\n- Production STEP/STL files\n- Short-pin OLED STEP\n- Full assembly STEP\n- Colored GLB render with OLED graphics and custom keycap logos\n- Firmware, BOM, checklist, and scripts from the prior package\n\nStill required from you before final submission:\n1. Put your final .kicad_pcb, .kicad_sch, and .kicad_pro files in /PCB\n2. Generate and include production/gerbers.zip from your final KiCad board\n3. Write your own README.md with screenshots and assembly notes\n4. Double-check exact sourced hardware lengths and insert type\n'''
(OUT_ROOT/'SUBMISSION_STATUS.txt').write_text(status, encoding='utf-8')

# Rename top-level checklist slightly? Leave existing.

# Zip final package
if ZIP_OUT.exists():
    ZIP_OUT.unlink()
with zipfile.ZipFile(ZIP_OUT, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for path in OUT_ROOT.rglob('*'):
        zf.write(path, arcname=str(Path('Starfall_Hackpad_Submission_v25') / path.relative_to(OUT_ROOT)))

# Basic output summary json for easier checking
summary = {
    'out_root': str(OUT_ROOT),
    'zip': str(ZIP_OUT),
    'glb': str(GLB_PATH),
    'assembled_step': str(CAD/'Starfall_assembled.STEP'),
    'top_step': str(PROD/'Top.STEP'),
    'bottom_step': str(PROD/'Bottom.STEP'),
    'mid_step': str(PROD/'Middle_Purple.STEP'),
    'inlays_step': str(PROD/'Purple_Inlays.STEP'),
    'oled_step': str(CAD/'ER_OLEDM0.91_1x-I2C_FULL_SHORT_PINS.step'),
}
print(json.dumps(summary, indent=2))
