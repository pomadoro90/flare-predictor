#!/usr/bin/env blender --background --python
"""
Standalone test for separator_new.py
Creates materials and calls create_separator().
Run: blender --background --python separator_test.py
"""

import bpy, math, sys, os

# Add parent dir to path if needed
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# ─── Clear scene ───
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ─── Create materials (matching flare_install.py) ───
def mat(name, rgb, rough=0.45, metal=0.25):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*rgb, 1.0)
    m.roughness = rough
    m.metallic = metal
    return m

MR = mat(name="Red",       rgb=(0.82, 0.15, 0.10), metal=0.30)
MW = mat(name="White",     rgb=(0.92, 0.91, 0.87))
MS = mat(name="Steel",     rgb=(0.55, 0.58, 0.62), metal=0.80, rough=0.30)
MY = mat(name="Yellow",    rgb=(0.95, 0.82, 0.05))
MM = mat(name="Sensor",    rgb=(0.06, 0.08, 0.16), metal=0.70, rough=0.30)
MN = mat(name="Concrete",  rgb=(0.72, 0.68, 0.63), rough=0.88)

print("Materials created.")

# ─── Import and call create_separator ───
from separator_new import create_separator
create_separator(bpy, math, MW, MS, MY, MM, MN, MR)

print("Separator created successfully!")

# ─── Add basic scene elements for viewing ───
# Ground plane
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
m_ground = mat(name="Ground", rgb=(0.30, 0.45, 0.18), rough=0.95)
ground.data.materials.clear()
ground.data.materials.append(m_ground)

# Sun light
bpy.ops.object.light_add(type='SUN', location=(15, -15, 25))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Camera
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 18
cam.location = (10, -12, 8)
# Look at separator center
from mathutils import Vector
tgt = Vector((-7.0, -4.5, 1.6))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Render settings
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 32
s.view_settings.exposure = 1.2
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# World - blue sky
w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.68, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2

# ─── Save .blend file ───
blend_path = os.path.join(script_dir, "separator_test.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# ─── Render test image ───
render_path = os.path.join(script_dir, "separator_test.png")
s.render.filepath = render_path
bpy.ops.render.render(write_still=True)

print("✅ Test complete! Blend: {} | Render: {}".format(blend_path, render_path))
