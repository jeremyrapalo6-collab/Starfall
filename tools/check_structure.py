from pathlib import Path
import sys,json

import cadquery as cq
from mechanical_fit import intersection
r=Path(__file__).resolve().parents[1];parts={n:cq.importers.importStep(str(r/'production'/f'{n}.STEP')).val() for n in ['Top','Bottom','Middle_Purple']}
result={}
for a,b in [('Top','Bottom'),('Top','Middle_Purple'),('Bottom','Middle_Purple')]:
 v=intersection(parts[a],parts[b]);result[a+' / '+b]=v;assert v<1e-5,(a,b,v)
(r/'production/STRUCTURAL_COLLISIONS.json').write_text(json.dumps(result,indent=2))
print(result)

