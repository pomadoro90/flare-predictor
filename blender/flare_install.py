"""
flare_install.py — low-poly 3D-модель факельной установки НПЗ
Рендер: BLENDER_WORKBENCH (Studio lighting, Material color).
"""

import bpy, math, os
from mathutils import Vector

# ── Очистка ──
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ── МАТЕРИАЛЫ ──
def make_mat(name, rgb, emit=0.0, rough=0.6, metal=0.1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*rgb, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Emission Strength'].default_value = emit
    bsdf.inputs['Emission Color'].default_value = (*rgb, 1)
    return mat

# Яркие/контрастные цвета для различимости
mat_steel  = make_mat("Steel",      (0.55, 0.58, 0.62))
mat_pipe   = make_mat("Pipe",       (0.50, 0.53, 0.57))
mat_insul  = make_mat("Insulation", (0.90, 0.85, 0.75))
mat_concr  = make_mat("Concrete",   (0.65, 0.63, 0.58))
mat_sensor = make_mat("Sensor",     (0.12, 0.15, 0.22))
mat_burner = make_mat("Burner",     (0.35, 0.38, 0.42))
mat_flame  = make_mat("FlameRing",  (0.90, 0.45, 0.10))
mat_green  = make_mat("Green",      (0.10, 0.85, 0.25))
mat_yellow = make_mat("Yellow",     (0.95, 0.75, 0.10))
mat_red    = make_mat("Red",        (0.90, 0.15, 0.10))
mat_ground = make_mat("Ground",     (0.42, 0.45, 0.38))

def apply_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def cyl(loc, r, d, rot=(0,0,0), name="C", mat=mat_steel, seg=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; apply_mat(o, mat); return o

def cube(loc, scale, name="C", mat=mat_steel):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.active_object
    o.name = name; o.scale = scale; apply_mat(o, mat); return o

def sphere(loc, r, name="S", mat=mat_sensor, seg=16, ring=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; apply_mat(o, mat); return o

def pipe(p1, p2, r=0.03, mat=mat_pipe, seg=12, name="P"):
    dx,dy,dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    th = math.acos(dz/L) if L>0 else 0
    ph = math.atan2(dy,dx) if (dx or dy) else 0
    return cyl(mid, r, L, (th, 0, ph), name, mat, seg)

# ═══════════════════════════════════════════════
# ГРУНТ
# ═══════════════════════════════════════════════
cube((0,0,-0.15), (10,8,0.15), "Ground", mat_ground)

# ═══════════════════════════════════════════════
# 1. ФАКЕЛЬНАЯ ТРУБА (центр)
# ═══════════════════════════════════════════════
FX, FY, H = 0.0, 0.0, 12.0

cube((FX, FY, 0.15), (1.2, 1.2, 0.15), "Flare_Fnd", mat_concr)
cyl((FX, FY, H/2+0.3), 0.25, H, name="Flare_Stack", mat=mat_steel, seg=24)
cyl((FX, FY, H-1.0), 0.35, 2.5, name="Flare_Insul", mat=mat_insul, seg=20)

# Опоры
for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
    cx, cy = FX+math.cos(ang)*0.6, FY+math.sin(ang)*0.6
    cyl((cx, cy, 1.5), 0.06, 3.0, name="Leg", mat=mat_steel, seg=8)
    pipe((cx, cy, 2.8), (FX, FY, 0.8), 0.04, name="Diag")

# Горелка на вершине
BZ = H + 0.3
cyl((FX, FY, BZ), 0.28, 0.15, name="Burner_Flange", mat=mat_burner, seg=24)
cyl((FX, FY, BZ+0.2), 0.22, 0.1, name="Burner_Plate", mat=mat_flame, seg=24)
for a in [0, math.pi/2, math.pi, 3*math.pi/2]:
    cyl((FX+math.cos(a)*0.18, FY+math.sin(a)*0.18, BZ+0.3), 0.03, 0.25, name="Pilot", mat=mat_burner, seg=8)

# Паровой ввод
pipe((FX-1.5, FY-0.4, H-2.0), (FX, FY-0.4, H-1.2), 0.04, name="Steam_P")
sv = cyl((FX, FY-0.4, H-1.0), 0.05, 1.2, name="Steam_In", mat=mat_pipe, seg=12)
sv.rotation_euler = (math.radians(20), 0, 0)

# Датчики
sphere((FX+0.3, FY, 0.8), 0.08, "S_Tflame")
cube((FX+0.3, FY, 0.72), (0.04, 0.04, 0.05), "S_Tf_body", mat_red)
sphere((FX-0.35, FY, 1.0), 0.07, "S_Ppurge")
sphere((FX-1.2, FY-0.4, H-2.2), 0.06, "S_Steam")
sphere((FX+0.45, FY, 2.0), 0.1, "Ind_Otriv", mat_green)

# ═══════════════════════════════════════════════
# 2. СЕПАРАТОР — горизонтальный цилиндр слева
# ═══════════════════════════════════════════════
SX, SY, SZ = -2.5, 0.0, 0.0
for sx in [SX-1.0, SX+1.0]:
    cube((sx, SY, 0.15), (0.2, 0.5, 0.15), "SF", mat_concr)
    cyl((sx, SY, 0.45), 0.12, 0.6, name="SS", mat=mat_steel, seg=12)

sb = cyl((SX, SY, 0.9), 0.4, 2.2, name="Sep_Body", mat=mat_steel, seg=24)
sb.rotation_euler = (0, math.radians(90), 0)
for dx in [-1.1, 1.1]:
    sphere((SX+dx, SY, 0.9), 0.4, "Sep_Cap", mat_steel, 16)

cyl((SX-0.5, SY, 1.4), 0.08, 0.4, name="Sep_In", mat=mat_pipe, seg=12)
cyl((SX+0.6, SY, 0.4), 0.07, 0.5, name="Sep_Out", mat=mat_pipe, seg=12)
sphere((SX, SY+0.5, 0.9), 0.07, "S_Level")
sphere((SX-0.8, SY, 1.5), 0.07, "S_Pflare")

# ═══════════════════════════════════════════════
# 3. ДРЕНАЖНАЯ ЁМКОСТЬ
# ═══════════════════════════════════════════════
DX, DY = -3.5, 1.5
cube((DX, DY, 0.1), (0.4, 0.4, 0.1), "DF", mat_concr)
cyl((DX, DY, 0.9), 0.2, 1.4, name="Drain", mat=mat_steel, seg=16)
sphere((DX, DY, 1.65), 0.2, "Drain_Top", mat_steel, 12)
cyl((DX-0.25, DY, 1.2), 0.04, 0.4, name="Drain_In", mat=mat_pipe, seg=8)

# ═══════════════════════════════════════════════
# 4. ТРУБОПРОВОДЫ
# ═══════════════════════════════════════════════
pipe((-5, 0, 1.4), (SX-0.5, SY, 1.4), 0.06, name="P_FlareGas")
pipe((SX+1.1, SY, 0.9), (SX+1.1, SY, 1.2), 0.05, name="P_Rise1")
pipe((SX+1.1, SY, 1.2), (FX, FY+0.3, 1.2), 0.05, name="P_Horiz")
pipe((FX, FY+0.3, 1.2), (FX, FY, 1.8), 0.05, name="P_Rise2")
pipe((-2, -0.6, 1.0), (FX, FY-0.35, 1.0), 0.05, name="P_Purge")
pipe((SX+0.6, SY, 0.4), (DX+0.25, DY, 0.4), 0.04, name="P_CondH")
pipe((DX+0.25, DY, 0.4), (DX+0.25, DY, 1.2), 0.04, name="P_CondR")
pipe((-4, -1, 2), (-4, -0.5, 2), 0.04, name="P_SteamS")
pipe((-4, -0.5, 2), (FX-1.5, FY-0.4, 2), 0.04, name="P_SteamH")
pipe((FX-1.5, FY-0.4, 2), (FX-1.5, FY-0.4, H-2), 0.04, name="P_SteamR")

# ═══════════════════════════════════════════════
# 5. КАМЕРА И РЕНДЕР (WORKBENCH)
# ═══════════════════════════════════════════════
bpy.ops.object.camera_add(location=(12, -8, 8))
cam = bpy.context.active_object
cam.data.lens = 28
cam.location = Vector((12, -8, 8))
target = Vector((FX-1, FY, H/2))  # смотрим на центр установки
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Workbench — гарантированная видимость
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Сохраняем
blend_path = "/home/pomadoro/projects/flare-predictor/blender/flare_install.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"✅ Модель сохранена: {blend_path}")
