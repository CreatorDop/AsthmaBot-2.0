import bpy,struct,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];(R/'assets').mkdir(exist_ok=True)
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
import json
manifest=json.loads((R/'cad/manifest.json').read_text());objects={}
for item in manifest:
 name=item['part'];color='cyan' if 'base' in name or 'peak' in name else 'white' if 'lid' in name or 'mouth' in name else 'yellow' if 'diaphragm' in name or 'button' in name else 'purple'
 objects[name]=stl(name,item['xyz'],color)
screen=cube('OLED envelope',(31.75,27.85,39),(27.5,27.7,1),'navy')
for i in range(6):cube('illustrative display bar',(23+i*3,25+2*math.sin(i),39.6),(1.5,1,.2),'mint')
for x,y in [(55,35),(55,47)]:stl('AB20_12_button',(x,y,39),'yellow')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.world.color=(.7,.7,.7)
for name,loc,power,size in [('key',(60,-100,260),2500000,220),('fill',(230,180,170),1500000,180)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((100,30,10))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(320,-330,290));camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=320
camera.rotation_euler=(Vector((125,40,30))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=-3;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
def render(name):scene.render.filepath=str(R/'assets'/name);bpy.ops.render.render(write_still=True)
render('assembly.png')
objects['AB20_02_lid'].location.z=85
screen.location.z=84
for name in ['AB20_04_peak_inlet','AB20_05_peak_outlet','AB20_06_diaphragm_D32','AB20_07_airflow_basic','AB20_08_mouthpiece','AB20_09_channel_clamp','AB20_10_nasal_pod','AB20_11_nasal_lid']:objects[name].hide_render=True
for name,loc,size,col in [('ESP32 envelope',(32.13,21.97,12),(48.26,27.94,8),'mint'),('SDP810 envelope',(97.5,57,18.525),(29,18,27.05),'white'),('boost envelope',(88.5,16.5,12),(37,17,14),'purple'),('charger envelope',(89,36.75,7),(28,17.5,4),'mint')]:cube(name,loc,size,col)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=9.25,depth=65.3,location=(40.65,61,14.5),rotation=(0,math.pi/2,0));bpy.context.object.data.materials.append(mats['coral'])
camera.location=(250,-260,240);camera.data.ortho_scale=205;camera.rotation_euler=(Vector((65,40,38))-camera.location).to_track_quat('-Z','Y').to_euler();render('exploded.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'cad/AsthmaBot2_visual.blend'))
