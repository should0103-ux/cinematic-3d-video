import bpy, math, os, subprocess
from mathutils import Vector
OUT="/kaggle/working/preview.mp4"; FR="/kaggle/working/frames"; os.makedirs(FR,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=4; s.cycles.use_denoising=False; s.cycles.transparent_max_bounces=8
s.render.resolution_x=270; s.render.resolution_y=480; s.render.resolution_percentage=100
s.render.fps=4; s.frame_end=120; s.render.image_settings.file_format='PNG'
s.world.color=(.012,.018,.04); s.view_settings.view_transform='Standard'; s.camera=None
def mat(n,c,metal=0,rough=.35,alpha=1,trans=0,emission=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,alpha); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 p.inputs['Alpha'].default_value=alpha
 if 'Transmission' in p.inputs: p.inputs['Transmission'].default_value=trans
 if emission and 'Emission Color' in p.inputs: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emission
 return m
navy=mat('Midnight backdrop',(.012,.025,.07),.05,.4)
cyan=mat('Glass edge cyan',(.12,.72,1),.2,.16,1,0,.25)
water=mat('Water translucent blue',(.02,.35,.8),.05,.18,.22,.35)
waterline=mat('Water line glow',(.05,.6,1),.1,.2,1,0,.45)
orange=mat('Straw orange',(1,.28,.035),.05,.24)
ivory=mat('Caption white',(.95,.98,1),0,.25,1,0,.5)
gold=mat('Light ray gold',(1,.72,.12),0,.25,1,0,.35)
def cube(n,loc,dim,ma,bevel=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if bevel:
  m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,d,ma,v=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(ma); return o
cube('Backdrop',(0,0,-.3),(9,9,.5),navy,0)
# Outline glass: thin glowing rims and vertical edges, not an opaque cylinder
for z in (.06,2.28):
 bpy.ops.mesh.primitive_torus_add(major_radius=.76,minor_radius=.035,major_segments=64,minor_segments=12,location=(0,0,z)); bpy.context.object.data.materials.append(cyan)
for x in (-.74,.74):
 for y in (-.62,.62):
  cyl('Glass edge',(x,y,1.17),.025,2.22,cyan,16)
# Water inside is translucent, with a bright waterline
cyl('Water volume',(0,0,.68),.68,1.28,water,64)
cyl('Water surface',(0,0,1.32),.69,.035,waterline,64)
# Straw bends visually at the water boundary: the submerged segment is offset
upper=cyl('Straw above water',(.13,-.04,2.22),.065,1.8,orange,24); upper.rotation_euler[1]=math.radians(-7)
lower=cyl('Straw underwater',(-.13,-.04,.67),.065,1.3,orange,24); lower.rotation_euler[1]=math.radians(-7)
# A few gold ray segments explain the light path
for loc,ang,depth in [((-.42,-.16,.22),-24,.62),((-.08,-.16,.82),18,.62),((.36,-.16,1.48),-12,.62)]:
 ray=cyl('Refraction light ray',loc,.012,depth,gold,12); ray.rotation_euler[1]=math.radians(ang)
# Camera and lights
bpy.ops.object.camera_add(location=(2.5,-6.4,3.45)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=58; s.camera=cam
for loc,power,size in [((3,-4,6),1000,4),((-4,-2,3),700,3),((0,3,4),900,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
# Captions are parented to the camera so they remain in-frame
captions=[(0,3.5,'WHY DOES A STRAW LOOK BROKEN?',.115),(3.5,7,'THE STRAW IS STRAIGHT',.14),(7,12,'LIGHT BENDS AT WATER',.14),(12,17,'THAT IS REFRACTION',.15),(17,22,'YOUR EYES TRACE LIGHT BACK',.12),(22,26,'THE UNDERWATER PART SHIFTS',.11),(26,30,'LIGHT TAKES A TURN!',.17)]
panel=cube('Caption backing',(0,0,0),(2.55,.38,.025),navy,0); panel.parent=cam; panel.location=(0,1.05,-3.2); panel.rotation_euler=(0,0,0)
items=[]
for start,end,body,size in captions:
 cu=bpy.data.curves.new('Caption','FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.extrude=.001
 ob=bpy.data.objects.new(body,cu); s.collection.objects.link(ob); ob.parent=cam; ob.location=(0,1.05,-3.1); ob.rotation_euler=(0,0,0); ob.data.materials.append(ivory); items.append((start,end,ob))
for f in range(1,121):
 t=(f-1)/4
 for start,end,ob in items: ob.hide_render=not(start<=t<end)
 cam.location=(2.5-.35*t/30,-6.4+.55*t/30,3.45); cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
 s.frame_set(f); s.render.filepath=f'{FR}/f_{f:04d}.png'; bpy.ops.render.render(write_still=True)
subprocess.run(['ffmpeg','-y','-framerate','4','-i',f'{FR}/f_%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','27','-preset','ultrafast','/kaggle/working/silent.mp4'],check=True)
narration="Have you ever put a straw in a glass and watched it look broken? The straw is perfectly straight. Light from the underwater part changes direction as it leaves water and enters air. That is called refraction. Your eyes trace the light back in a straight line, so the submerged part seems shifted. The same trick makes a swimming pool look shallower than it really is. So next time your straw looks snapped, do not blame the glass. It is light taking a turn."
subprocess.run(['espeak-ng','-s','145','-w','/kaggle/working/voice.wav',narration],check=True)
subprocess.run(['ffmpeg','-y','-i','/kaggle/working/silent.mp4','-i','/kaggle/working/voice.wav','-filter_complex','[0:v]hqdn3d=2:1:2:1,scale=360:640:flags=lanczos,minterpolate=fps=12:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1[v];[1:a]apad,atrim=0:30[a]','-map','[v]','-map','[a]','-t','30','-c:v','libx264','-crf','22','-preset','medium','-c:a','aac','-b:a','96k','-pix_fmt','yuv420p','-movflags','+faststart',OUT],check=True)
print('PREVIEW_COMPLETE',OUT,os.path.getsize(OUT))
