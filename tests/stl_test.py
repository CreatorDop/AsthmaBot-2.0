from pathlib import Path
import struct,collections
R=Path(__file__).resolve().parents[1]
for p in sorted((R/'cad').glob('AB20_*.stl')):
 b=p.read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n,p.name
 edges=collections.Counter();volume=0
 for i in range(n):
  v=struct.unpack_from('<12fH',b,84+50*i);a,bv,c=[tuple(round(x,5) for x in v[k:k+3]) for k in [3,6,9]]
  if len({a,bv,c})<3:continue
  for x,y in [(a,bv),(bv,c),(c,a)]:edges[tuple(sorted([x,y]))]+=1
  volume+=(a[0]*(bv[1]*c[2]-bv[2]*c[1])+a[1]*(bv[2]*c[0]-bv[0]*c[2])+a[2]*(bv[0]*c[1]-bv[1]*c[0]))/6
 assert all(v==2 for v in edges.values()),(p.name,'open/nonmanifold edges')
 assert volume>0,(p.name,'orientation/volume')
 print('PASS watertight manifold STL:',p.name,'triangles',n)
