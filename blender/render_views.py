"""
render_views.py v9 — 5 ракурсов факельной установки + вид сзади.
"""
import bpy, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/blender/renders/"
os.makedirs(out, exist_ok=True)

s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'STUDIO'
s.display.shading.color_type = 'MATERIAL'
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# Голубое небо
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.65, 0.85, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

TX, TY, TZ = -4, -3, 15
cam = bpy.context.scene.camera
cam.data.lens = 18

views = [
    ((30, -28, 20),   (TX, TY, TZ), "v9_front_right"),   # право-перед
    ((-30, -28, 20),  (TX, TY, TZ), "v9_front_left"),    # лево-перед
    ((0, -35, 24),    (TX, TY, TZ), "v9_front_wide"),    # фронт широкий
    ((-4, 22, 24),    (TX, TY, TZ), "v9_top_west"),      # верх-запад
    ((0, 30, 18),     (TX, TY, TZ), "v9_rear"),          # СЗАДИ — видно задние тросы
]

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 5 views rendered")
