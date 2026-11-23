"""Blender: справжня анімація CAD-вузлів, 240 кадрів / 24 fps."""
import bpy,struct,math,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];OUT=R/'qa/video_frames';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
mats={k:material(k,c) for k,c in {'cyan':(.03,.66,.7),'white':(.86,.92,.96),'purple':(.42,.22,.85),'yellow':(1,.68,.08),'green':(.05,.45,.32),'red':(.9,.24,.24),'dark':(.03,.07,.14),'metal':(.55,.63,.7)}.items()}
def stl(name,loc,col):
 b=(R/'cad'/f'{name}.stl').read_bytes();vs=[];faces=[]
 for i in range(struct.unpack_from('<I',b,80)[0]):
  v=struct.unpack_from('<12fH',b,84+i*50);j=len(vs);vs.extend([v[3:6],v[6:9],v[9:12]]);faces.append((j,j+1,j+2))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.location=loc;o.data.materials.append(mats[col]);return o
objects={};m=json.loads((R/'cad/manifest.json').read_text())
keep=['base','lid','carrier','peak_inlet','peak_outlet','diaphragm','mouthpiece','channel_clamp']
for p in m:
 if not any(k in p['part'] for k in keep) or 'nasal' in p['part']:continue
 col='cyan' if 'base' in p['part'] or 'peak' in p['part'] else 'yellow' if 'diaphragm' in p['part'] else 'white' if 'lid' in p['part'] or 'mouth' in p['part'] else 'purple'
 objects[p['part']]=stl(p['part'],p['xyz'],col)
def cube(name,loc,size,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[col]);objects[name]=o;return o
cube('OLED',(31.75,27.85,34.4),(27.5,27.7,11.2),'dark')
cube('ESP32',(32.13,23.97,11),(48.26,27.94,8),'green')
cube('SDP810',(97.5,57,18.525),(29,18,27.05),'white')
cube('Power',(88.5,16.5,12),(37,17,14),'green')
cube('Charger',(89,36.75,7),(28,17.5,4),'green')
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=9.25,depth=65.3,location=(40.65,61,14.5),rotation=(0,math.pi/2,0));bat=bpy.context.object;bat.name='Battery';bat.data.materials.append(mats['red']);objects['Battery']=bat
# Для відео внутрішні електронні вузли — габаритні блоки, не vendor CAD.
starts={k:o.location.copy() for k,o in objects.items()}
offsets={'AB20_02_lid':(0,0,115),'OLED':(-30,-5,77),'ESP32':(-40,0,42),'Battery':(-10,55,32),'SDP810':(15,50,55),'Power':(5,-30,24),'Charger':(25,0,28),'AB20_04_peak_inlet':(40,0,0),'AB20_05_peak_outlet':(40,0,85),'AB20_06_diaphragm_D32':(40,0,44),'AB20_08_mouthpiece':(40,0,-15),'AB20_09_channel_clamp':(22,0,0),'AB20_03_module_carrier':(10,0,0)}
for name,o in objects.items():
 end=starts[name]+Vector(offsets.get(name,(0,0,0)))
 for frame,pos in [(1,starts[name]),(36,starts[name]),(146,end),(194,end),(240,starts[name])]:o.location=pos;o.keyframe_insert(data_path='location',frame=frame)
 if o.animation_data:
  for fc in o.animation_data.action.fcurves:
   for kf in fc.keyframe_points:kf.interpolation='BEZIER'
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.4;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_specular_highlight=True;scene.display.render_aa='8';scene.render.film_transparent=True
scene.render.resolution_x=960;scene.render.resolution_y=660;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.fps=24;scene.frame_start=1;scene.frame_end=240
bpy.ops.object.camera_add(location=(320,-430,320));cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=390;cam.rotation_euler=(Vector((104,45,82))-cam.location).to_track_quat('-Z','Y').to_euler()
labels=[('AB20_02_lid',(62,40,1.25)),('OLED',(0,0,0)),('ESP32',(0,0,0)),('Battery',(0,0,0)),('SDP810',(0,0,0)),('AB20_05_peak_outlet',(0,0,20)),('AB20_06_diaphragm_D32',(0,0,0)),('AB20_01_base',(62,0,15))]
coords={}
for frame in range(1,241,2):
 scene.frame_set(frame);coords[str(frame)]=[]
 for name,local in labels:
  v=world_to_camera_view(scene,cam,objects[name].matrix_world@Vector(local));coords[str(frame)].append([v.x*960,(1-v.y)*660])
 if '--save-only' not in sys.argv:
  scene.render.filepath=str(OUT/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
if '--save-only' not in sys.argv:(R/'qa/video_labels.json').write_text(json.dumps(coords))
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'cad/AsthmaBot2_exploded_animation.blend'))
