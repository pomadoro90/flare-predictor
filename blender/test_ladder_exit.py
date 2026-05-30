#!/usr/bin/env blender --background --python
"""Front view of ladder + platform connection."""
import bpy, math, sys, os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def mat(name, rgb, rough=0.45, metal=0.25):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*rgb, 1.0)
    m.roughness = rough
    m.metallic = metal
    return m

MR = mat("Red", (0.82, 0.15, 0.10), metal=0.30)
MW = mat("White", (0.92, 0.91, 0.87))
MS = mat("Steel", (0.55, 0.58, 0.62), metal=0.80, rough=0.30)
MY = mat("Yellow", (0.95, 0.82, 0.05))
MM = mat("Sensor", (0.06, 0.08, 0.16), metal=0.70, rough=0.30)
MN = mat("Concrete", (0.72, 0.68, 0.63), rough=0.88)

from separator_new import create_separator
create_separator(bpy, math, MW, MS, MY, MM, MN, MR)

bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.clear()
ground.data.materials.append(mat("Ground", (0.30, 0.45, 0.18), rough=0.95))

bpy.ops.object.light_add(type='SUN', location=(15, -15, 25))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Camera: front view of ladder area
# Separator center: (-7, -4.5, 1.6), ladder at (-5.875, -3.0)
from mathutils import Vector

bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.lens = 22
cam.location = (-5.9, -7.0, 3.0)
tgt = Vector((-5.9, -3.0, 2.0))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 32
s.view_settings.exposure = 1.2
s.render.resolution_x = 1200
s.render.resolution_y = 900

w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.68, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2

out_path = os.path.join(script_dir, "sep_views", "ladder_exit.png")
os.makedirs(os.path.join(script_dir, "sep_views"), exist_ok=True)
s.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print(f"✅ Rendered: {out_path}")