"""
render_views.py v5 — 4 цветных ракурса (EEVEE, GPU-friendly).
"""
import bpy, math, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/blender/renders/"
os.makedirs(out, exist_ok=True)

bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.eevee.taa_render_samples = 32
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.view_settings.exposure = 1.5
bpy.context.scene.view_settings.gamma = 1.2

TX, TY, TZ = -3.5, -2.5, 15
cam = bpy.context.scene.camera
cam.data.lens = 22

views = [
    ((24, -22, 16),  (TX, TY, TZ), "v5_front_right"),
    ((-22, -20, 12), (TX, TY, TZ), "v5_front_left"),
    ((0, -28, 18),   (TX, TY, TZ), "v5_front_low"),
    ((-4, 14, 30),   (TX, TY, TZ), "v5_top"),
]

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 views rendered")
