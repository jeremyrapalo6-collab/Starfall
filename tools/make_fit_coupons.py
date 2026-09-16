"""Small samples for confirming the real printer and supplied hardware."""
from pathlib import Path
import cadquery as cq
from cadquery import exporters
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production/fit_coupons'
OUT.mkdir(exist_ok=True)
plate=cq.Workplane('XY').box(70,24,3,centered=(True,True,False))
for index,(x,opening) in enumerate([(-23,14.2),(0,14.4),(23,14.6)],1):
    through=cq.Workplane('XY').box(opening,opening,3.4,centered=(True,True,False)).translate((x,0,-.2))
    upper=cq.Workplane('XY').box(16.4,16.4,2,centered=(True,True,False)).translate((x,0,1.3))
    relief=(cq.Workplane('XY',origin=(x,0,.95)).rect(opening,opening).workplane(offset=.35).rect(14.9,14.9).loft())
    plate=plate.cut(through).cut(upper).cut(relief)
    for mark in range(index):
        plate=plate.cut(cq.Workplane('XY').box(.6,2,1).translate((x+(mark-(index-1)/2)*1.5,-11,2.8)))
base=cq.Workplane('XY').box(36,14,2.1,centered=(True,True,False)).translate((0,0,-16.3))
for x,d in [(-12,4.6),(0,4.7),(12,4.8)]:
    post=cq.Workplane('XY').circle(4.1).extrude(14.3).translate((x,0,-14.3))
    base=base.union(post)
    base=base.cut(cq.Workplane('XY').circle(2.9).extrude(7.1).translate((x,0,-6.9)))
    base=base.cut(cq.Workplane('XY').circle(d/2).extrude(4.2).translate((x,0,-11.0)))
    base=base.cut(cq.Workplane('XY').circle(1.7).extrude(1).translate((x,0,-11.4)))
for name,part in [('Switch_retention_14p2_14p4_14p6',plate),('Insert_well_4p6_4p7_4p8',base)]:
    assert len(part.solids().vals())==1 and part.val().isValid()
    for ext in ['STEP','stl']:exporters.export(part,str(OUT/(name+'.'+ext)))
print('Fit coupons generated')
