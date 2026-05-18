"""
render_views.py v8 — 4 ракурса (Workbench, Studio light, голубое небо).
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

# Голубое небо
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.65, 0.85, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

TX, TY, TZ = -4, -3, 15
cam = bpy.context.scene.camera
cam.data.lens = 18

views = [
    ((30, -28, 20),  (TX, TY, TZ), "v8_front_right"),   # право-перед
    ((-28, -26, 16), (TX, TY, TZ), "v8_front_left"),    # лево-перед
    ((0, -35, 28),   (TX, TY, TZ), "v8_front_wide"),    # фронт широкий — должны быть видны боковые оттяжки
    ((-4, 20, 28),   (TX, TY, TZ), "v8_top_west"),      # верх-запад — все 4 направления
]

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 views rendered")
