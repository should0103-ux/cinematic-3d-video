import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

# Clean scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "CYCLES"
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 180
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 64

def mat(name, color, metallic=0.0, rough=0.4, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = rough
    if "Transmission" in bs.inputs: bs.inputs["Transmission"].default_value = transmission
    return m

cyan = mat("Deep teal laboratory", (0.012, 0.12, 0.16), rough=0.32)
steel = mat("Brushed stainless steel", (0.24, 0.32, 0.34), metallic=0.78, rough=0.24)
glass = mat("Petri dish glass", (0.55, 0.82, 0.88), metallic=0.12, rough=0.12, transmission=0.82)
yogurt = mat("Thick creamy yogurt", (0.88, 0.82, 0.68), rough=0.23)
dark = mat("Ant dark exoskeleton", (0.035, 0.018, 0.012), metallic=0.18, rough=0.25)

# Studio floor and backdrop
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-0.08))
floor = bpy.context.object
floor.name = "Seamless teal studio floor"
floor.data.materials.append(cyan)

# Work surface
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
bench = bpy.context.object
bench.name = "Lab worktop"
bench.dimensions = (3.2, 2.2, 0.16)
bench.data.materials.append(steel)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bev = bench.modifiers.new("Soft machined edges", "BEVEL"); bev.width=0.06; bev.segments=4
bench.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")

# Petri dish: glass rim and yogurt surface
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.72, depth=0.075, location=(0,-0.12,0.045))
dish = bpy.context.object; dish.name="Clear glass petri dish"; dish.data.materials.append(glass)
bev=dish.modifiers.new("Rounded glass edge","BEVEL"); bev.width=0.025; bev.segments=4
dish.modifiers.new("Dish normals","WEIGHTED_NORMAL")
bpy.ops.mesh.primitive_torus_add(major_radius=0.68, minor_radius=0.035, major_segments=96, minor_segments=16, location=(0,-0.12,0.095))
rim=bpy.context.object; rim.name="Petri dish raised rim"; rim.data.materials.append(glass)
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.625, depth=0.045, location=(0,-0.12,0.105))
cream=bpy.context.object; cream.name="Fresh thick yogurt"; cream.data.materials.append(yogurt)
bev=cream.modifiers.new("Soft yogurt edge","BEVEL"); bev.width=0.04; bev.segments=5
cream.modifiers.new("Cream normals","WEIGHTED_NORMAL")

# Tiny yogurt swirls
for i in range(5):
    x=-0.34+i*0.16
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(x,-0.16+0.10*math.sin(i),0.139))
    blob=bpy.context.object; blob.name="Yogurt surface texture"; blob.scale=(0.16,0.10,0.018); blob.data.materials.append(yogurt)

# Import the CC0 ant asset, normalize its size and arrange several instances.
ant_path=os.path.join(ASSETS,"ant.glb")
if not os.path.exists(ant_path): raise RuntimeError("Missing assets/ant.glb")
def import_ant(location, scale_factor=1.0):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=ant_path)
    imported=[o for o in bpy.data.objects if o not in before]
    meshes=[o for o in imported if o.type=="MESH"]
    if not meshes: raise RuntimeError("Ant GLB imported without mesh objects")
    # Group imported objects under one animated root while preserving local transforms.
    root=bpy.data.objects.new("Animated ant root",None); scene.collection.objects.link(root)
    for o in imported:
        o.parent=root
    bpy.context.view_layer.update()
    dims=[o.dimensions for o in meshes]
    maxdim=max(max(d.x,d.y,d.z) for d in dims)
    factor=(0.18/maxdim)*scale_factor if maxdim else 1
    root.location=location
    root.scale=(factor,factor,factor)
    return root

ants=[]
for i,loc in enumerate([(-0.34,-0.20,0.17),(0.08,-0.28,0.17),(0.36,0.02,0.17)]):
    try: ants.append(import_ant(loc, 1.0 if i==0 else 0.82))
    except Exception as e: print("ANT_INSTANCE_WARNING",e)

# Import the CC0 static researcher model as a background hero subject.
researcher_path=os.path.join(ASSETS,"professional-lab-researcher.glb")
if not os.path.exists(researcher_path): raise RuntimeError("Missing researcher GLB")
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=researcher_path)
researcher_objects=[o for o in bpy.data.objects if o not in before]
researcher_meshes=[o for o in researcher_objects if o.type=="MESH"]
if not researcher_meshes: raise RuntimeError("Researcher GLB imported without mesh objects")
researcher_root=bpy.data.objects.new("Researcher character (static CC0 model)",None); scene.collection.objects.link(researcher_root)
for o in researcher_objects: o.parent=researcher_root
bpy.context.view_layer.update()
maxdim=max(max(o.dimensions.x,o.dimensions.y,o.dimensions.z) for o in researcher_meshes)
scale=1.72/maxdim if maxdim else 1
researcher_root.scale=(scale,scale,scale)
researcher_root.location=(0.12,0.78,0.0)
researcher_root.rotation_euler[2]=math.radians(180)

# Background lab equipment silhouettes
for x in [-1.05,1.05]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.12, depth=0.52, location=(x,0.78,0.26))
    vial=bpy.context.object; vial.name="Out-of-focus lab glassware"; vial.data.materials.append(glass)

# Lighting: large soft key, cyan rim and warm detail light
world=bpy.data.worlds.new("Cinematic cyan world") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.018,0.055,0.07,1)
world.node_tree.nodes["Background"].inputs[1].default_value=0.32
def area(name, loc, power, color, size, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=power; l.data.color=color; l.data.shape="DISK"; l.data.size=size
    l.rotation_euler=(Vector(target)-l.location).to_track_quat("-Z","Y").to_euler()
area("Large soft key", (1.8,-2.2,3.1), 850, (0.72,0.88,1.0), 2.8, (0,0,0))
area("Cool cyan rim", (-2.0,0.8,2.2), 1100, (0.12,0.72,1.0), 2.0, (0,0,0.4))
area("Warm yogurt kicker", (0.2,-1.0,1.6), 320, (1.0,0.72,0.43), 1.1, (0,-0.1,0.1))

# Portrait macro camera
bpy.ops.object.camera_add(location=(2.05,-3.65,2.25))
cam=bpy.context.object; cam.name="Cinematic macro camera"
cam.rotation_euler=(Vector((0,-0.05,0.34))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=58; cam.data.dof.use_dof=True; cam.data.dof.focus_object=cream; cam.data.dof.aperture_fstop=3.2
scene.camera=cam
cam.keyframe_insert(data_path="location",frame=1)
cam.location=(1.55,-3.0,1.78); cam.keyframe_insert(data_path="location",frame=180)
for a in ants:
    start=a.location.copy()
    a.location=start; a.keyframe_insert(data_path="location",frame=1)
    a.location.x += 0.13; a.location.y += 0.08
    a.keyframe_insert(data_path="location",frame=180)

# Smooth camera/ant movement
for obj in [cam]+ants:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation="BEZIER"

scene.frame_set(1)
scene.render.filepath=os.path.join(OUT,"researcher_ants_yogurt_preview.png")
bpy.ops.render.render(write_still=True)
print("PREVIEW_RENDERED",scene.render.filepath)

# Short 6-second MP4 proof-of-scene; this is a quality/asset validation pass, not the final 33s film.
scene.render.image_settings.file_format="FFMPEG"
scene.render.ffmpeg.format="MPEG4"
scene.render.ffmpeg.codec="H264"
scene.render.ffmpeg.constant_rate_factor="MEDIUM"
scene.render.ffmpeg.ffmpeg_preset="GOOD"
scene.render.filepath=os.path.join(OUT,"researcher_ants_yogurt_preview.mp4")
bpy.ops.render.render(animation=True)
print("PREVIEW_VIDEO_RENDERED",scene.render.filepath)
