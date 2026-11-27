import bpy, math, os, subprocess
from mathutils import Vector
OUT="/kaggle/working/preview.mp4"; FR="/kaggle/working/frames"; os.makedirs(FR,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=360; s.render.resolution_y=640; s.render.resolution_percentage=100; s.render.fps=12; s.frame_end=360; s.world.color=(.012,.018,.04); s.view_settings.view_transform='Standard'
def material(n,c,metal=0,rough=.35):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
blue=material('Deep blue',(.015,.04,.12)); aqua=material('Water',(.025,.3,.65),.1,.2); orange=material('Straw orange',(1,.22,.025),.05,.25); ivory=material('Caption white',(.95,.98,1)); gold=material('Light ray',(1,.7,.08))
def cube(n,loc,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma); return o
def cyl(n,loc,r,d,ma,v=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(ma); return o
cube('Backdrop',(0,0,-.25),(9,9,.5),blue)
glass=cyl('Glass beaker',(0,0,1.15),.8,2.3,aqua,64); glass.modifiers.new('Rounded rim','BEVEL').width=.04
cyl('Water',(0,0,.62),.7,1.35,aqua,64)
a=cyl('Straw above water',(.16,-.05,2.35),.07,1.85,orange,24); a.rotation_euler[1]=math.radians(-7)
b=cyl('Straw underwater',(-.08,-.05,.24),.07,.95,orange,24); b.rotation_euler[1]=math.radians(-7)
bpy.ops.mesh.primitive_torus_add(major_radius=.78,minor_radius=.045,major_segments=64,minor_segments=12,location=(0,0,2.28)); bpy.context.object.data.materials.append(ivory)
# ray rods, visual explanation
for loc in [(-.45,-.18,.15),(.05,-.18,.8),(.55,-.18,1.45)]:
 r=cyl('Refraction ray',loc,.018,.9,gold,12); r.rotation_euler[1]=math.radians(28)
bpy.ops.object.camera_add(location=(3.8,-9,4.0)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=52; s.camera=cam
for loc,power,size in [((3,-4,6),900,5),((-4,-2,3),650,4),((0,3,4),850,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
captions=[(0,3.5,'WHY DOES A STRAW LOOK BROKEN?',.25),(3.5,7,'THE STRAW IS STRAIGHT',.32),(7,12,'LIGHT BENDS AT THE WATER LINE',.24),(12,17,'THIS IS CALLED REFRACTION',.29),(17,22,'YOUR EYES TRACE LIGHT BACK',.26),(22,26,'THE UNDERWATER PART LOOKS SHIFTED',.22),(26,30,'LIGHT TAKES A TURN!',.36)]
items=[]
for start,end,body,size in captions:
 c=bpy.data.curves.new('Caption','FONT'); c.body=body; c.size=size; c.align_x='CENTER'; c.extrude=.001
 o=bpy.data.objects.new(body,c); s.collection.objects.link(o); o.location=(0,-1.55,4.35); o.rotation_euler=(math.radians(90),0,0); o.data.materials.append(ivory); items.append((start,end,o))
for f in range(1,361):
 t=(f-1)/12
 for start,end,o in items: o.hide_render=not(start<=t<end)
 cam.location=(3.8-.5*t/30,-9+.8*t/30,4.0); cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
 s.frame_set(f); s.render.filepath=f'{FR}/f_{f:04d}.png'; bpy.ops.render.render(write_still=True)
subprocess.run('ffmpeg -y -framerate 12 -i /kaggle/working/frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 27 -preset ultrafast /kaggle/working/silent.mp4',shell=True,check=True)
narration="Have you ever put a straw in a glass and watched it look broken? The straw is perfectly straight. Light from the underwater part changes direction as it leaves water and enters air. That is called refraction. Your eyes trace the light back in a straight line, so the submerged part seems shifted. The same trick makes a swimming pool look shallower than it really is. So next time your straw looks snapped, do not blame the glass. It is light taking a turn."
subprocess.run(['espeak-ng','-s','145','-w','/kaggle/working/voice.wav',narration],check=True)
subprocess.run('ffmpeg -y -i /kaggle/working/silent.mp4 -i /kaggle/working/voice.wav -filter_complex "[1:a]apad,atrim=0:30[a]" -map 0:v -map "[a]" -t 30 -c:v copy -c:a aac -b:a 96k -shortest '+OUT,shell=True,check=True)
print('RENDER_COMPLETE',OUT,os.path.getsize(OUT))
