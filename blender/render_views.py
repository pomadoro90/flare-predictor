"""
render_views.py — рендер 4 ракурсов (Workbench, Studio light, Material colors).
Запуск: blender --background flare_install.blend --python render_views.py
"""
import bpy, math, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/blender/renders/"
os.makedirs(out, exist_ok=True)

# Workbench
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

views = [
    ((12, -8, 8),   (-1, 0, 6),   "front_right"),
    ((-12, -6, 6),  (-1, 0, 6),   "front_left"),
    ((0, -12, 10),  (-1, 0, 5),   "front_low"),
    ((-1, 4, 15),   (-1, 0, 6),   "top"),
]

cam = bpy.context.scene.camera
for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(out, f"view_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 views rendered")
