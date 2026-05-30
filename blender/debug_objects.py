#!/usr/bin/env blender --background --python
"""Debug: list all objects in scene after creating separator."""
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

# List ladder-related objects
ladder_objs = [obj for obj in bpy.data.objects if 'Ladder' in obj.name or 'ladder' in obj.name.lower() or 'Cage' in obj.name or 'Exit' in obj.name or 'Hole' in obj.name]
print(f"\n=== LADDER & HOLE OBJECTS ({len(ladder_objs)}) ===")
for obj in sorted(ladder_objs, key=lambda o: o.name):
    loc = obj.location
    dims = obj.dimensions
    print(f"  {obj.name:35s} loc=({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}) size=({dims.x:.3f}, {dims.y:.3f}, {dims.z:.3f})")

# Count total
all_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
print(f"\nTotal mesh objects: {len(all_objs)}")
total_polys = sum(len(obj.data.polygons) for obj in all_objs)
print(f"Total polygons: {total_polys}")