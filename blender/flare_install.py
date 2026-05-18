"""
flare_install.py v8 — Факельная установка с ЗАЗЕМЛЁННЫМИ оттяжками.
- Фон: голубое небо для видимости тёмных тросов
- Оттяжки: 3 уровня × 4 направления, анкеры ПРЯМО НА ЗЕМЛЕ
- Рендер: EEVEE с низкой экспозицией для правильных цветов
- Камера: вид 3/4 спереди-справа
"""
import bpy, math, os
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ═══════ МАТЕРИАЛЫ ═══════
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
MB = mat(name="Burner",    rgb=(0.28, 0.30, 0.35), metal=0.90, rough=0.20)
MF = mat(name="Flame",     rgb=(1.00, 0.55, 0.05))
MC = mat(name="Cable",     rgb=(0.06, 0.08, 0.12), metal=0.65, rough=0.35)  # почти чёрный трос
MN = mat(name="Concrete",  rgb=(0.72, 0.68, 0.63), rough=0.88)  # светлый бетон анкеров
MG = mat(name="Ground",    rgb=(0.30, 0.45, 0.18), rough=0.95)  # зелёная земля
MM = mat(name="Sensor",    rgb=(0.06, 0.08, 0.16), metal=0.70, rough=0.30)

def sm(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

# ═══════ ПРИМИТИВЫ ═══════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m); return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; sm(obj=o, m=m); return o

def sphere(loc, r, name="S", m=MM, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=8, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m); return o

def torus(loc, R, r, name="T", m=MS, seg=20, rseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m); return o

def pipe(p1, p2, r=0.04, m=MS, seg=12, name="P"):
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]; dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(mid, r, L, rot=(0,0,0), name=name, m=m, seg=seg)
    direction = Vector((dx, dy, dz))
    c.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return c

# ═══════ ЗЕМЛЯ + ПЛОЩАДКА ═══════
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, -2, -0.01))
sm(obj=bpy.context.active_object, m=MG)
bpy.context.active_object.name = "Ground"
cube((0, -2, 0.02), (24, 18, 0.02), name="Pad", m=MN)

# ═══════ 1. СТВОЛ ═══════
H, R, FX, FY = 38.0, 1.1, 0.0, -1.0
cyl((FX, FY, 6.1),  R, 12.0, name="Stack_L", m=MR, seg=30)
cyl((FX, FY, 20.1), R, 16.0, name="Stack_M", m=MW, seg=30)
cyl((FX, FY, 33.1), R, 10.0, name="Stack_U", m=MR, seg=30)
cyl((FX, FY, 0.25), 1.35, 0.5, name="Stack_Base", m=MS, seg=30)

# ═══════ 2. ПЛАТФОРМЫ — только на стыках секций + верхняя ═══════
PR, RH, POST_R = 2.0, 0.05, 0.045
# Платформы: стык красный-белый (12м), стык белый-красный (28м), верхняя (37м)
for pz, pname in [(12.0, "Joint_LM"), (28.0, "Joint_MU"), (37.0, "Top")]:
    cyl((FX, FY, pz), PR, 0.12, name="{}_D".format(pname), m=MS, seg=36)
    for rh in [0.40, 0.90, 1.30]:
        torus((FX, FY, pz+rh), PR-0.18, RH, name="{}_R{}".format(pname, rh), m=MS, seg=36, rseg=6)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx = FX + math.cos(ang) * (PR - 0.22)
        sy = FY + math.sin(ang) * (PR - 0.22)
        cyl((sx, sy, pz+0.75), POST_R, 1.3, name="{}_P{}".format(pname, a), m=MS, seg=6)

# ═══════ 3. ЛЕСТНИЦА: H-ступени + клетка + площадки на стыках + сдвиг 90° ═══════
LR = R + 0.65          # радиус лестницы от оси ствола
STEP_H = 0.35          # шаг ступени по высоте
RAIL_R = 0.025         # радиус рейки ступени
STEP_W = 0.50          # ширина ступени (расстояние между рейками)
CAGE_R = LR + 0.30     # радиус защитной клетки
CAGE_BAR_R = 0.015     # радиус прутьев клетки

# Секции лестницы: (z_start, z_end, azimuth_deg)
LADDER_SECTIONS = [
    (0.6, 12.0, 0),     # по нижней красной секции, азимут 0°
    (12.0, 28.0, 90),   # по белой секции, азимут 90°
    (28.0, 37.5, 180),  # по верхней красной, азимут 180°
]

for sec_idx, (z0, z1, az_deg) in enumerate(LADDER_SECTIONS):
    az = math.radians(az_deg)
    n_steps = int((z1 - z0) / STEP_H)
    actual_sh = (z1 - z0) / n_steps

    # Направляющий вектор от оси ствола наружу для этого азимута
    ox = FX + math.cos(az) * LR
    oy = FY + math.sin(az) * LR
    # Перпендикуляр (для ориентации перекладин)
    px = -math.sin(az)
    py = math.cos(az)

    for si in range(n_steps):
        z = z0 + si * actual_sh + actual_sh / 2
        # Левая рейка (внутренняя, ближе к стволу)
        lx = ox - px * STEP_W/2
        ly = oy - py * STEP_W/2
        cyl((lx, ly, z), RAIL_R, actual_sh, name="LR_{}_{}".format(sec_idx, si), m=MS, seg=8)

        # Правая рейка (внешняя)
        rx = ox + px * STEP_W/2
        ry = oy + py * STEP_W/2
        cyl((rx, ry, z), RAIL_R, actual_sh, name="RR_{}_{}".format(sec_idx, si), m=MS, seg=8)

        # Горизонтальная перекладина (H-образная ступень)
        pipe((lx, ly, z + actual_sh*0.35), (rx, ry, z + actual_sh*0.35),
             r=RAIL_R*0.8, m=MS, seg=6, name="HC_{}_{}".format(sec_idx, si))
        pipe((lx, ly, z - actual_sh*0.35), (rx, ry, z - actual_sh*0.35),
             r=RAIL_R*0.8, m=MS, seg=6, name="HB_{}_{}".format(sec_idx, si))

    # Защитная клетка вокруг секции
    cage_n = 8  # число вертикальных прутьев
    for ci in range(cage_n):
        ca = math.radians(ci * 360 / cage_n)
        cx = ox + math.cos(ca) * (CAGE_R - LR)
        cy = oy + math.sin(ca) * (CAGE_R - LR)
        pipe((cx, cy, z0), (cx, cy, z1), r=CAGE_BAR_R, m=MS, seg=6,
             name="CageV_{}_{}".format(sec_idx, ci))

    # Кольца клетки через каждые 2м
    for ring_z in [z0 + k*2.0 for k in range(int((z1-z0)/2.0) + 1)]:
        if ring_z > z1: ring_z = z1
        # Смещённый центр кольца
        torus((ox, oy, ring_z), CAGE_R - LR, CAGE_BAR_R,
              name="CageR_{}_{}".format(sec_idx, int(ring_z)), m=MS, seg=20, rseg=6)

# ═══════ 4. ОТТЯЖКИ — НА КРАСНЫХ СЕКЦИЯХ, АНКЕРЫ 1.4×1.4×0.8м ═══════
GH = [10.0, 20.0, 34.0]
GA = [45, 135, 225, 315]
GR = 20.0
for h in GH:
    r = 0.09 if h == 20.0 else 0.08
    for ga in GA:
        ang = math.radians(ga)
        ax = FX + math.cos(ang) * GR
        ay = FY + math.sin(ang) * GR
        # Анкерный блок: центр z=0.40, scale=0.70 → верх z=0.80
        cube((ax, ay, 0.40), (0.70, 0.70, 0.40), 
             name="Anc_{}_{}".format(int(h), ga), m=MN)
        # Трос от ствола к вершине анкера
        pipe((FX, FY, h), (ax, ay, 0.80), r=r, m=MC, seg=14,
             name="Guy_{}_{}".format(int(h), ga))

# ═══════ 5. ГОРЕЛКА + ПЛАМЯ ═══════
BZ = H + 0.3
cyl((FX, FY, BZ), 0.80, 1.0, name="Burner_B", m=MB, seg=26)
cyl((FX, FY, BZ+1.3), 0.45, 2.2, name="Burner_N", m=MB, seg=26)
for j, dz in enumerate([0.5, 1.0, 1.5, 2.0]):
    torus((FX, FY, BZ+0.4+dz*0.8), 0.50, 0.04, name="Bur_R{}".format(j), m=MS, seg=26, rseg=6)
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.10, radius2=0.80, depth=7.0, location=(FX, FY, BZ+6.5))
sm(obj=bpy.context.active_object, m=MF)
bpy.context.active_object.name = "Flame"
for a in [0, 90, 180, 270]:
    ang = math.radians(a)
    px = FX + math.cos(ang) * 0.35; py = FY + math.sin(ang) * 0.35
    cyl((px, py, BZ+2.5), 0.05, 1.0, name="Pilot{}".format(a), m=MB, seg=8)

# ═══════ 6. СЕПАРАТОР ═══════
SX, SY, SZ, SL, SR = -7.0, -4.5, 1.6, 7.5, 1.4
for sx in [SX-2.5, SX+2.5]:
    cube((sx, SY, 0.3), (0.45, 0.9, 0.3), name="Sep_Ft", m=MN)
    cyl((sx, SY, 0.75), 0.20, 0.7, name="Sep_Saddle", m=MS, seg=14)
sb = cyl((SX, SY, SZ), SR, SL, name="Sep_Body", m=MW, seg=30)
sb.rotation_euler = (0, math.radians(90), 0)
# ── заглушки-диски вместо сфер ──
for dx in [-SL/2, SL/2]:
    cyl((SX+dx, SY, SZ), SR, 0.10, rot=(0, math.radians(90), 0), name="Sep_Cap", m=MS, seg=30)
cyl((SX-2.0, SY, SZ+SR+0.3), 0.16, 0.5, name="Sep_In", m=MS, seg=14)
cyl((SX+2.0, SY, SZ+SR+0.3), 0.13, 0.4, name="Sep_Vent", m=MS, seg=14)
cyl((SX+0.8, SY, SZ-SR-0.4), 0.11, 0.6, name="Sep_Drain", m=MS, seg=14)
LX, LY = SX - SL/2 - 0.9, SY - 0.5
for si in range(9):
    cube((LX, LY, 0.5+si*0.50), (0.28, 0.02, 0.02), name="SepL{}".format(si), m=MS)
for dx_s, dy_s in [(-0.22, -0.15), (0.22, -0.15), (-0.22, 0.15), (0.22, 0.15)]:
    cyl((LX+dx_s, LY+dy_s, 2.5), 0.028, 4.5, name="SepCage", m=MS, seg=6)

# ── без сфер на сепараторе ──

# ═══════ 7. ДРЕНАЖ ═══════
DX, DY = -11.5, -5.0
cube((DX, DY, 0.2), (0.6, 0.6, 0.2), name="Drn_Ft", m=MN)
cyl((DX, DY, 1.6), 0.45, 2.4, name="Drain", m=MS, seg=22)
cyl((DX, DY, 2.9), 0.45, 0.10, name="Drain_Top", m=MS, seg=22)
cyl((DX-0.5, DY, 2.0), 0.07, 0.35, name="Drain_In", m=MY, seg=10)

# ═══════ 8. ТРУБОПРОВОДЫ ═══════
RY, PZ = -6.0, 2.8
for rx in [-11, -8, -5, -2, 1]:
    cyl((rx, RY, 1.3), 0.06, 2.6, name="RackLeg", m=MS, seg=10)
pipe((-12, RY, PZ), (3, RY, PZ), r=0.17, m=MY, seg=14, name="GasMain")
pipe((-9, RY, PZ+0.35), (4, RY, PZ+0.35), r=0.12, m=MY, seg=12, name="GasSec")
pipe((SX+2.0, SY, SZ+SR+0.4), (SX+2.0, SY, 3.5), r=0.13, m=MY, seg=12, name="S2S_V")
pipe((SX+2.0, SY, 3.5), (FX+0.7, FY, 3.5), r=0.13, m=MY, seg=12, name="S2S_H")
pipe((FX+0.7, FY, 3.5), (FX, FY, 5.5), r=0.13, m=MY, seg=12, name="S2S_R")
pipe((SX+0.8, SY, SZ-SR-0.5), (DX-0.5, DY, SZ-SR-0.5), r=0.07, m=MS, seg=8, name="Cond")
pipe((DX-0.5, DY, SZ-SR-0.5), (DX-0.5, DY, 2.0), r=0.07, m=MS, seg=8, name="CondR")
pipe((-13, -8, 5.5), (-6, -7, 5.5), r=0.08, m=MS, seg=10, name="Steam1")
pipe((-6, -7, 5.5), (FX-1.2, FY-2.0, 5.5), r=0.08, m=MS, seg=10, name="Steam2")
pipe((FX-1.2, FY-2.0, 5.5), (FX-0.8, FY-0.5, 26.0), r=0.06, m=MS, seg=8, name="SteamR")

# ═══════ 9. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(25, -20, 35))
bpy.context.active_object.data.energy = 4.5

# ═══════ 10. КАМЕРА ═══════
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 18
cam.location = Vector((28, -30, 22))
tgt = Vector((-4, -3, 15))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 11. EEVEE + ГОЛУБОЕ НЕБО ═══════
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 32
s.view_settings.exposure = 1.2
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# Голубое небо
w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.68, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2

# ── СОХРАНЕНИЕ + РЕНДЕР ──
blend_path = "/home/pomadoro/projects/flare-predictor/blender/flare_install.blend"
render_path = "/home/pomadoro/projects/flare-predictor/blender/0001.png"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
s.render.filepath = render_path
bpy.ops.render.render(write_still=True)
print("✅ v8 сохранена + рендер: {}".format(blend_path))
