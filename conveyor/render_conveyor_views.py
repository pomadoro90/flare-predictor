"""
render_conveyor_views.py — 4 ракурса ленточного конвейера.
"""
import bpy, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/conveyor/renders/"
os.makedirs(out, exist_ok=True)

s = bpy.context.scene
cam = bpy.context.scene.camera
cam.data.lens = 26

tgt = Vector((0, -0.1, 1.3))

views = [
    ((1.5, -8.5, 3.0),  tgt, "c3_side_right"),
    ((-1.5, -8.5, 3.0), tgt, "c3_side_left"),
    ((0, -9.5, 8.0),    tgt, "c3_top_front"),
    ((9.0, -3.0, 2.5),  tgt, "c3_end_drive"),
]

for vloc, tloc, name in views:
    cam.location = Vector(vloc)
    cam.rotation_euler = (Vector(tloc) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = os.path.join(out, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"✅ {name}")

print("✅ All 4 conveyor views rendered")
