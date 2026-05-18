"""
render_check.py — рендер с уровня земли для проверки оттяжек.
"""
import bpy, os
from mathutils import Vector

out = "/home/pomadoro/projects/flare-predictor/blender/renders/"
os.makedirs(out, exist_ok=True)

cam = bpy.context.scene.camera
cam.data.lens = 24
cam.location = Vector((-8, -3, 0.3))  # камера почти на земле слева от ствола
tgt = Vector((-4, -3, 15))  # смотрим вверх на ствол
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()

bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = os.path.join(out, "v8_ground_check.png")
bpy.ops.render.render(write_still=True)
print("✅ v8_ground_check.png")
