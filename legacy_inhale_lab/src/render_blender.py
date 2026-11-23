import bpy,struct,math
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/scratch/cab8eaba5635/inhale_lab')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,hex):
 m=bpy.data.materials.new(name);m.diffuse_color=tuple(int(hex[i:i+2],16)/255 for i in (0,2,4))+(1,);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.35
 return m
mats={k:mat(k,c) for k,c in [('cyan','00B5BA'),('mint','17CDB4'),('white','F2F6FA'),('navy','142443'),('purple','7757FF'),('yellow','FFD549'),('coral','FF6258'),('hose','A6BBC5')]}
def stl(name,loc,col):
 b=(R/'cad'/f'{name}.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];vs=[];faces=[]
 for i in range(n):
  v=struct.unpack_from('<12fH',b,84+i*50);j=len(vs);vs.extend([v[3:6],v[6:9],v[9:12]]);faces.append((j,j+1,j+2))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.location=loc;o.data.materials.append(mats[col]);return o
def cube(name,loc,size,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[col]);return o
def tube(name,pts,r=1.4):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mats['hose']);return o
base=stl('IL01_console_base',(0,0,0),'cyan');lid=stl('IL02_console_lid',(0,0,41),'white')
left=stl('IL03_flow_left',(170,50,6),'cyan');right=stl('IL04_flow_right',(170,50,6),'mint');plate=stl('IL05_orifice_D12',(170,50,6),'yellow');trigger=stl('IL06_trigger_shell',(75,-65,0),'purple')
screen=cube('display placeholder',(70,59,43.7),(49,37,1),'navy')
bars=[cube('display plot',(53+i*5,58+5*math.sin(i*.5),44.3),(3,1.7,.3),'mint') for i in range(8)]
btn=[]
for x,col in [(35,'yellow'),(70,'purple'),(105,'coral')]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=3.7,depth=4,location=(x,20,45));o=bpy.context.object;o.data.materials.append(mats[col]);btn.append(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=5.8,depth=6,location=(97.5,-47.5,21));tb=bpy.context.object;tb.data.materials.append(mats['yellow'])
hoses=[tube('P plus',[(140,35,20),(152,22,35),(175,32,72),(188,50,54)]),tube('P minus',[(140,50,20),(158,77,48),(205,83,79),(224,50,54)]),tube('button cable',[(140,75,20),(154,-15,5),(119,-57,6),(117,-47,10)],1)]
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.world.color=(.7,.7,.7)
for name,loc,power,size in [('key',(60,-100,260),2500000,220),('fill',(230,180,170),1500000,180)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((100,30,10))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(320,-330,290));camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=340
camera.rotation_euler=(Vector((110,22,25))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=-3;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
def render(name):scene.render.filepath=str(R/'assets'/name);bpy.ops.render.render(write_still=True)
render('assembly.png')
for o in [left,right,plate,trigger,tb,*hoses]:o.hide_render=True
lid.location.z=92;screen.location.z+=51
for o in bars+btn:o.location.z+=51
camera.location=(260,-290,270);camera.data.ortho_scale=240;camera.rotation_euler=(Vector((70,50,45))-camera.location).to_track_quat('-Z','Y').to_euler();render('exploded.png')
for o in [base,lid,screen,*bars,*btn]:o.hide_render=True
for o in [left,right,plate]:o.hide_render=False;o.location=(0,0,0)
right.location.x=30;plate.location.x=15
camera.location=(160,-180,130);camera.data.ortho_scale=145;camera.rotation_euler=(Vector((50,0,20))-camera.location).to_track_quat('-Z','Y').to_euler();render('cassette.png')
