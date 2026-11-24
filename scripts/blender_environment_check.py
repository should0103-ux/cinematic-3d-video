import bpy
import sys
print("BLENDER_ENVIRONMENT_OK")
print("Blender version:", bpy.app.version_string)
print("Render engines available:", sorted({item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}))
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.fps=30
scene.frame_start=1
scene.frame_end=993
print("Configured vertical target: 720x1280, 30fps, 33.1s")
