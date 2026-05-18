"""
render_views.py — 4 широких ракурса всей факельной установки (Workbench).
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

# Target: между стволом (0,-1) и сепаратором (-6,-3)
TX, TY, TZ = -3, -2, 14

views = [
    ((22, -20, 14),  (TX, TY, TZ),  "wide_front_right"),
    ((-20, -18, 10), (TX, TY, TZ),  "wide_front_left"),
    ((0, -25, 16),   (TX, TY, TZ),  "wide_front_low"),
    ((-4, 8, 28),    (TX, TY, TZ),  "wide_top"),
]

cam = bpy.context.scene.camera
cam.data.lens = 22

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 views rendered")
