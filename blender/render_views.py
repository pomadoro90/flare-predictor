"""
render_views.py v7 — 4 ракурса (Workbench, Studio light, Material color).
Запуск: blender --background flare_install.blend --python render_views.py
"""
import bpy, math, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/blender/renders/"
os.makedirs(out, exist_ok=True)

bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

TX, TY, TZ = -4, -3, 15
cam = bpy.context.scene.camera
cam.data.lens = 18

views = [
    ((30, -28, 20),  (TX, TY, TZ), "v7_front_right"),
    ((-28, -26, 16), (TX, TY, TZ), "v7_front_left"),
    ((0, -32, 22),   (TX, TY, TZ), "v7_front_low"),
    ((-5, 16, 34),   (TX, TY, TZ), "v7_top"),
]

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 views rendered")
