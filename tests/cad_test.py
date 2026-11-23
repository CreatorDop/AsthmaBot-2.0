from pathlib import Path
import cadquery as cq,ezdxf,json
R=Path(__file__).resolve().parents[1];data=json.loads((R/'cad/manifest.json').read_text())
for row in data:
 n=row['part'];obj=cq.importers.importStep(str(R/'cad'/f'{n}.step')).val();assert obj.isValid(),n;assert obj.Volume()>0,n
 b=obj.BoundingBox();assert all(abs(a-v)<.02 for a,v in zip(row['bounds_mm'],[b.xlen,b.ylen,b.zlen])),n
 doc=ezdxf.readfile(R/'cad'/f'{n}.dxf');assert doc.units==4;assert not doc.audit().has_errors,n;assert len(doc.modelspace().query('DIMENSION'))>=1,n
 print('PASS STEP/STL source + DXF:',n)
base=cq.importers.importStep(str(R/'cad/AB20_01_base.step')).val()
# Ключові реальні габарити в корпусі: відсутність об'ємного перетину.
for name,w,d,h,x,y,z in [('ESP',48.26,27.94,18,8,10,7),('SDP',29,18,27.05,83,48,5),('OLED',27.5,27.7,11.2,18,14,28.8),('BOOST',37,17,14,70,8,5),('CHARGER',28,17.5,4,75,28,5)]:
 envelope=cq.Workplane('XY').box(w,d,h,centered=(False,False,False)).translate((x,y,z)).val();v=base.intersect(envelope).Volume();assert v<.01,(name,v);print('PASS body clearance:',name)
print('CAD checks passed. Print tolerances, assembly fasteners, tubes and actual SKUs NOT physically verified.')
