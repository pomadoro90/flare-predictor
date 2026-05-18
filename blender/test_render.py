"""
test_render.py — минимальный тест рендера.
"""
import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Красный куб
mat = bpy.data.materials.new("Red")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.9, 0.15, 0.15, 1)
mat.node_tree.nodes["Principled BSDF"].inputs['Emission Color'].default_value = (0.8, 0.05, 0.05, 1)
mat.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 0.4

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.context.active_object.data.materials.append(mat)

# Синяя сфера справа
mat_b = bpy.data.materials.new("Blue")
mat_b.use_nodes = True
mat_b.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.25, 0.9, 1)
mat_b.node_tree.nodes["Principled BSDF"].inputs['Emission Color'].default_value = (0.1, 0.2, 0.8, 1)
mat_b.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 0.4

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(2, 0, 1))
bpy.context.active_object.data.materials.append(mat_b)

# Грунт
mat_g = bpy.data.materials.new("Ground")
mat_g.use_nodes = True
mat_g.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.55, 0.58, 0.50, 1)
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_g)

# Свет x3
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.active_object.data.energy = 5.0
bpy.ops.object.light_add(type='AREA', location=(-3, 2, 4))
bpy.context.active_object.data.energy = 300
bpy.ops.object.light_add(type='AREA', location=(0, -2, 2))
bpy.context.active_object.data.energy = 200

# Камера
bpy.ops.object.camera_add(location=(5, -5, 4))
cam = bpy.context.active_object
cam.location = Vector((5, -5, 4))
dir_vec = Vector((0, 0, 1)) - cam.location
cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Фон
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.6, 0.7, 0.85, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.5

# Workbench
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600

bpy.context.scene.render.filepath = '/home/pomadoro/projects/flare-predictor/blender/test_render.png'
bpy.ops.render.render(write_still=True)
print("✅ Test render done")
