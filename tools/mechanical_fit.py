"""Mechanical corrections and measured checks for the Reactor Celestial case.

The PCB XY layout is unchanged. Z=-0.70 is its underside datum.
Physical switch/insert/cable fit still depends on the supplied parts and printer.
"""
import json
from pathlib import Path
import cadquery as cq
from cadquery import exporters
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def box(w,h,z,t,x=0,y=0):
    return cq.Workplane('XY').box(w,h,t,centered=(True,True,False)).translate((x,y,z))

def cyl(d,z,h,x=0,y=0):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z))

def rounded_rect(w,h,z,t,r,x,y):
    return box(w,h,z,t,x,y).edges('|Z').fillet(r)

def electronics_shapes(root):
    shapes=cq.importers.importStep(str(root/'CAD/Starfall_electronics_short_OLED.step')).solids().vals()
    result=[]
    for s in shapes:
        b=s.BoundingBox()
        if b.xlen>80 and b.ylen>90:
            s=s.translate((0,0,-.70))
            f=max(s.Faces(),key=lambda f:f.Center().z)
            extra=cq.Solid.extrudeLinear(f.outerWire(),f.innerWires(),cq.Vector(0,0,1.60-b.zlen))
            s=s.fuse(extra).clean()
        else:
            # Top-side parts follow the actual 1.60 mm PCB; bottom-side parts do not.
            s=s.translate((0,0,-.61 if b.zmax>0 else -.70))
        result.append(s)
    return result

def offset_wire(w,amount):
    before=abs(cq.Face.makeFromWires(w).Area())
    ws=w.offset2D(amount)
    after=sum(abs(cq.Face.makeFromWires(v).Area()) for v in ws)
    if ws and (after-before)*amount<0:
        ws=w.offset2D(-amount)
    return ws

def expanded_pocket(s,gap=.18):
    f=max(s.Faces(),key=lambda v:v.Center().z)
    z=f.Center().z
    outer=offset_wire(f.outerWire(),gap)
    if not outer: raise ValueError('Could not expand decorative pocket')
    solids=[cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,.70)).translate((0,0,5.32-z)) for w in outer]
    pocket=solids[0].fuse(*solids[1:]) if len(solids)>1 else solids[0]
    for iw in f.innerWires():
        for hole in offset_wire(iw,-gap):
            cut=cq.Solid.extrudeLinear(hole,[],cq.Vector(0,0,.90)).translate((0,0,5.22-z))
            pocket=pocket.cut(cut)
    return pocket

def correct_top_and_inlays(top,inlays,root,switches,encoder,mounts):
    def require_solid(stage):
        n=len(top.val().Solids())
        if n!=1 or not top.val().isValid(): raise ValueError(f'Top invalid after {stage}: {n} solids')
    require_solid('initial construction')
    # Keep a 14.2 mm locating aperture, relieving only the upper lip transition.
    for x,y in switches:
        chamfer=(cq.Workplane('XY',origin=(x,y,3.85)).rect(14.2,14.2)
                 .workplane(offset=.35).rect(14.9,14.9).loft(combine=True))
        top=top.cut(chamfer)
    require_solid('switch transition relief')
    # A round shaft hole alone does not clear the rectangular encoder body.
    top=top.cut(rounded_rect(13.0,12.6,2.7,3.5,.45,*encoder))
    require_solid('encoder relief')
    for s in electronics_shapes(root):
        b=s.BoundingBox();cx=(b.xmin+b.xmax)/2;cy=(b.ymin+b.ymax)/2
        if b.zmax+.40<=2.9 or b.zmin>=5.9 or b.xlen>50 or b.ylen>50: continue
        if any(abs(cx-x)<9 and abs(cy-y)<9 for x,y in switches) and b.xlen>10 and b.ylen>10: continue
        if abs(cx-encoder[0])<10 and abs(cy-encoder[1])<10: continue
        roof=min(b.zmax+.40,5.1)
        top=top.cut(box(max(b.xlen+.8,1.2),max(b.ylen+.8,1.2),2.75,roof-2.75,cx,cy))
    require_solid('electronics relief')
    trimmed=[]
    for s in inlays.Solids():
        for x,y in switches:
            if not s.Solids(): break
            cut=box(16.75,16.75,5.1,1,x,y).val()
            if overlaps(s,cut): s=s.cut(cut)
        if not s.Solids(): continue
        s=s.cut(rounded_rect(13.4,13.0,5.1,1,.45,*encoder).val())
        trimmed.extend(v for v in s.Solids() if v.Volume()>1e-5)
    fused=trimmed[0].fuse(*trimmed[1:]).clean()
    # Generate clearance pockets from the real insert contours, including inner holes.
    # This fixes crescent/planet/LTC contour differences without losing the artwork.
    for i,s in enumerate(fused.Solids()):
        pocket=expanded_pocket(s)
        if not pocket.Solids() or not pocket.isValid():raise ValueError(f'Invalid decorative cutter {i}')
        top=top.cut(pocket)
        require_solid('decorative pocket '+str(i))
    # Capture the PCB with 0.25 mm nominal vertical allowance, rather than 2 mm of play.
    for x,y in mounts:
        collar=cq.Workplane('XY').circle(3.2).circle(1.7).extrude(1.85).translate((x,y,1.15))
        top=top.union(collar)
    require_solid('PCB retaining collars')
    # Offset-curve STEP translation in OCCT 7.8 can reopen as loose shells.
    # Convert the final solid to supported NURBS surfaces before exporting/testing it.
    top=cq.Workplane(obj=cq.Shape.cast(BRepBuilderAPI_NurbsConvert(top.val().wrapped,True).Shape()))
    require_solid('STEP-compatible surface conversion')
    return top,cq.Compound.makeCompound(fused.Solids())

def export_fit_reference(root):
    shapes=electronics_shapes(root)
    exporters.export(cq.Compound.makeCompound(shapes),str(root/'CAD/Starfall_fit_reference_1p6mm.STEP'))
    return shapes

def overlaps(a,b):
    x=a.BoundingBox();y=b.BoundingBox()
    return all(getattr(x,k+'min')<getattr(y,k+'max')-1e-7 and getattr(y,k+'min')<getattr(x,k+'max')-1e-7 for k in 'xyz')

def intersection(a,b):
    if not overlaps(a,b):return 0.0
    op=BRepAlgoAPI_Common(a.wrapped,b.wrapped)
    if not op.IsDone():raise ValueError('Boolean collision check did not complete')
    props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props)
    return props.Mass()

def distance(a,b):
    return BRepExtrema_DistShapeShape(a.wrapped,b.wrapped).Value()

def validate_exports(root):
    import trimesh
    result={}
    for name in ['Top','Bottom','Middle_Purple','Purple_Inlays']:
        shape=cq.importers.importStep(str(root/'production'/(name+'.STEP'))).val()
        solids=shape.Solids()
        assert solids and shape.isValid(),f'{name}: invalid STEP round trip'
        if name!='Purple_Inlays':assert len(solids)==1,f'{name}: disconnected structural STEP'
        mesh=trimesh.load_mesh(root/'production'/(name+'.stl'))
        assert mesh.is_watertight,f'{name}: non-watertight STL'
        error=abs(mesh.volume-shape.Volume())/shape.Volume()
        assert error<.002,f'{name}: STEP/STL volume mismatch'
        result[name]={'step_solid_count':len(solids),'step_valid':True,'stl_watertight':True,
                      'step_volume_mm3':shape.Volume(),'relative_stl_volume_error':error,
                      'stl_bounds_mm':mesh.bounds.tolist()}
    (root/'production/EXPORT_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def check_mechanics(root,top,bottom,spacer,inlays,electronics,mounts,switches):
    parts={'Top':top.val(),'Bottom':bottom.val(),'Middle_Purple':spacer.val()}
    assert all(len(p.Solids())==1 for p in parts.values()),'Each structural part must be one connected solid'
    assert all(s.isValid() for s in parts.values())
    hits=[];switch_clear=[]
    for i,e in enumerate(electronics):
        for name,p in parts.items():
            v=intersection(e,p)
            if v>1e-5:hits.append([i,name,v])
        b=e.BoundingBox()
        if 15<b.xlen<16 and 16<b.ylen<17:switch_clear.append(distance(e,parts['Top']))
        if i%40==0:print('Verified electronics',i,flush=True)
    decorations=inlays.Solids();deco_hits=[]
    for i,a in enumerate(decorations):
        if i%10==0:print('Verified inlays',i,flush=True)
        assert a.isValid()
        for name,p in parts.items():
            v=intersection(a,p)
            if v>1e-5:deco_hits.append([i,name,v])
        for j,b in enumerate(decorations[:i]):
            v=intersection(a,b)
            if v>1e-5:deco_hits.append([i,j,v])
        for j,e in enumerate(electronics):
            v=intersection(a,e)
            if v>1e-5:deco_hits.append([i,'electronics_'+str(j),v])
    screws=[]
    for x,y in mounts:
        shaft=cyl(3.0,-11.35,16,x,y).val();head=cyl(5.5,4.65,3.0,x,y).val()
        for label,s in [('shaft',shaft),('head',head)]:
            for name,p in parts.items():
                v=intersection(s,p)
                if v>1e-5:screws.append([x,y,label,name,v])
            for i,e in enumerate(electronics):
                v=intersection(s,e)
                if v>1e-5:screws.append([x,y,label,'electronics_'+str(i),v])
            for i,p in enumerate(decorations):
                v=intersection(s,p)
                if v>1e-5:screws.append([x,y,label,'inlay_'+str(i),v])
    result={'status':'CAD_CHECKS_PASSED_PHYSICAL_FIT_PENDING' if not(hits or deco_hits or screws) else 'FAILED',
      'case_outer_mm':[112,116,22.9],'pcb_thickness_mm':1.6,'electronics_solids_tested':len(electronics),
      'bottom_connected_solids':len(parts['Bottom'].Solids()),'decorative_solids':len(decorations),
      'electronics_collisions':hits,'inlay_collisions':deco_hits,'fastener_collisions':screws,
      'minimum_switch_plate_clearance_mm':min(switch_clear),'pcb_upper_retaining_allowance_mm':.25,
      'screw_spec':'M3 x 16; head envelope diameter 5.5, height 3.0',
      'insert_installation_top_z_mm':-7.6,'insert_pocket_diameter_mm':4.7,'insert_installation_well_diameter_mm':5.8,
      'insert_installation_depth_below_support_mm':6.9,'screw_thread_engagement_mm':3.75,
      'screw_tip_relief_clearance_mm':.75,'usb_access_mm':[18,8],
      'physical_checks_required':['Actual switch snap retention and keycap travel','Insert heat-setting coupon and iron-tip access','Actual USB cable overmold','Actual knob skirt and screw head dimensions','Printer tolerance and thin decorative features']}
    assert len(switch_clear)==9,'Expected nine switch bodies in fit reference'
    (root/'production/MECHANICAL_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    if hits or deco_hits or screws:raise ValueError('Mechanical collisions: see MECHANICAL_VALIDATION.json')
    # Separate, flattened accent layout for single-colour printing.
    arranged=[];x=y=row_h=0.0
    for s in sorted(decorations,key=lambda s:-s.BoundingBox().ylen):
        b=s.BoundingBox()
        if x+b.xlen>180:x=0;y+=row_h+4;row_h=0
        arranged.append(s.translate((x-b.xmin,y-b.ymin,-b.zmin)))
        x+=b.xlen+4;row_h=max(row_h,b.ylen)
    for ext in ['STEP','stl']:exporters.export(cq.Compound.makeCompound(arranged),str(root/'production'/('Purple_Inlays_Print_Layout.'+ext)))
    assy=cq.Assembly(name='Starfall mechanically checked assembly')
    for name,p in parts.items():assy.add(p,name=name)
    assy.add(inlays,name='Purple inlays');assy.add(cq.Compound.makeCompound(electronics),name='Actual electronics with 1.6mm PCB')
    assy.save(str(root/'CAD/Starfall_Mechanical_Assembly.STEP'))
    for filename,count in [('Starfall_Mechanical_Assembly.STEP',3+len(decorations)+len(electronics)),
                           ('Starfall_Reactor_Celestial_FINAL_COLORED_CASE.STEP',3+len(decorations))]:
        loaded=cq.importers.importStep(str(root/'CAD'/filename)).val()
        assert loaded.isValid() and len(loaded.Solids())==count,f'Invalid assembly STEP: {filename}'
    return result
