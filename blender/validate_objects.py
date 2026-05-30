import bpy
bpy.ops.wm.open_mainfile(filepath="/home/pomadoro/projects/flare-predictor/blender/separator_test.blend")
objects = bpy.data.objects
grating = [o for o in objects if "Grating" in o.name]
brackets = [o for o in objects if "Bracket" in o.name]
floor = [o for o in objects if "Floor" in o.name]
print("Grating bars:", len(grating))
for g in sorted(g.name for g in grating)[:5]:
    print("  ", g)
print("  ...")
print("Bracket parts:", len(brackets))
for b in sorted(b.name for b in brackets):
    print("  ", b)
print("Floor:", [f.name for f in floor])
print("\nTotal objects:", len(objects))
