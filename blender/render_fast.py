#!/usr/bin/env blender --background --python
"""
Fast multi-view renderer for separator — optimized for Telegram.
Outputs: lighter JPEG, 800x600, high contrast, white bg.
Run: blender --background --python render_fast.py
"""
import bpy, math, sys, os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# ─── Clear scene ───
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ─── Materials ───
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
print("Separator created.")

# Ground
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.clear()
ground.data.materials.append(mat("Ground", (0.25, 0.40, 0.15), rough=0.95))

# Sun
bpy.ops.object.light_add(type='SUN', location=(15, -15, 25))
sun = bpy.context.active_object
sun.data.energy = 4.0

# ─── Render settings ───
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 16
s.view_settings.exposure = 1.8
s.view_settings.gamma = 1.0
s.render.resolution_x = 800
s.render.resolution_y = 600
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'JPEG'
s.render.image_settings.quality = 85

# White background
w = bpy.data.worlds['World']
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.95, 0.95, 0.95, 1.0)
bg.inputs['Strength'].default_value = 1.0

from mathutils import Vector

# ─── Camera views ───
views = {
    'front': {
        'loc': (-3.0, -10.0, 4.0),
        'tgt': (-7.0, -4.5, 1.5),
        'lens': 28,
    },
    'front_left': {
        'loc': (-12.0, -9.0, 4.0),
        'tgt': (-7.0, -4.5, 1.5),
        'lens': 28,
    },
    'front_right': {
        'loc': (-2.0, -9.0, 4.0),
        'tgt': (-7.0, -4.5, 1.5),
        'lens': 28,
    },
    'top': {
        'loc': (-7.0, -4.5, 8.0),
        'tgt': (-7.0, -4.5, 0.0),
        'lens': 22,
    },
    'detail_ladder': {
        'loc': (-5.9, -6.0, 3.2),
        'tgt': (-5.9, -3.0, 2.8),
        'lens': 35,
    },
}

out_dir = os.path.join(script_dir, "renders")
os.makedirs(out_dir, exist_ok=True)

for view_name, params in views.items():
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.lens = params['lens']
    cam.location = params['loc']
    tgt = Vector(params['tgt'])
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam

    out_path = os.path.join(out_dir, f"sep_{view_name}.jpg")
    s.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"✅ {view_name}: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)

print(f"\n✅ All renders saved to {out_dir}")