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

# ═══════ 5. ГОРЕЛКА + ПЛАМЯ + ПАРОВОЙ КОЛЛЕКТОР ═══════
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

# ПАРОВАЯ ТРУБКА: от SteamR (26м) вверх до горелки
STEAM_Z = BZ + 0.5
pipe((FX-0.8, FY-0.5, 26.0), (FX-0.8, FY-0.5, STEAM_Z), r=0.06, m=MS, seg=12, name="SteamRise")

# Кольцевой паровой коллектор вокруг горелки
STEAM_RING_R = 0.62
for ring_h in [STEAM_Z, STEAM_Z+0.6]:
    torus((FX, FY, ring_h), STEAM_RING_R, 0.04, name="SteamRing_{}".format(int(ring_h*10)), m=MS, seg=26, rseg=8)
    # Соединительные трубки от стояка к кольцу
    pipe((FX-0.8, FY-0.5, ring_h), (FX-STEAM_RING_R, FY-0.5, ring_h), r=0.04, m=MS, seg=10, name="SteamBrg_{}".format(int(ring_h*10)))

# Паровые форсунки (сопла) — 8 шт. по окружности, направлены в зону горения
for fi in range(8):
    fa = math.radians(fi * 45)
    fx = FX + math.cos(fa) * STEAM_RING_R
    fy = FY + math.sin(fa) * STEAM_RING_R
    # Короткая трубка-форсунка, направленная внутрь к пламени
    pipe((fx, fy, STEAM_Z+0.3), (FX+math.cos(fa)*0.35, FY+math.sin(fa)*0.35, STEAM_Z+0.3),
         r=0.025, m=MS, seg=8, name="Nozzle{}".format(fi))

# ═══════ 6. ДАТЧИКИ НА СТВОЛЕ ═══════
# Датчик давления: короткий цилиндр на кронштейне
def pressure_sensor(loc, name):
    cube((loc[0], loc[1], loc[2]-0.08), (0.06, 0.06, 0.04), name=name+"_Brkt", m=MS)
    cyl(loc, 0.05, 0.10, name=name+"_Body", m=MY, seg=12)
    cyl((loc[0], loc[1], loc[2]+0.07), 0.03, 0.04, name=name+"_Top", m=MM, seg=10)

# Датчик температуры: длинный цилиндр в гильзе
def temp_sensor(loc, name):
    cube((loc[0], loc[1], loc[2]-0.06), (0.05, 0.05, 0.03), name=name+"_Brkt", m=MS)
    cyl(loc, 0.04, 0.18, name=name+"_Probe", m=MR, seg=10)
    cyl((loc[0], loc[1], loc[2]+0.12), 0.05, 0.05, name=name+"_Head", m=MM, seg=12)

# На нижней красной секции: P_flare, Q_flare
pressure_sensor((FX, FY+1.2, 3.5), "PS_Pflare")
pressure_sensor((FX, FY-1.2, 3.5), "PS_Qflare")
# На белой секции: P_purge, Q_purge
pressure_sensor((FX, FY+1.2, 18.0), "PS_Ppurge")
pressure_sensor((FX, FY-1.2, 18.0), "PS_Qpurge")
# На верхней красной секции: T_flame, Steam_Q
temp_sensor((FX, FY+1.2, 30.0), "TS_Tflame")
pressure_sensor((FX, FY-1.2, 30.0), "PS_SteamQ")

# ═══════ 7. СЕПАРАТОР ═══════
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

# Уровнемер на сепараторе (вертикальная трубка сбоку)
pipe((SX-3.0, SY+1.0, 0.8), (SX-3.0, SY+1.0, SZ+SR+0.2), r=0.03, m=MS, seg=8, name="Sep_LG")
for lz in [1.2, 2.0, 2.8]:
    cyl((SX-3.0, SY+1.0, lz), 0.05, 0.04, name="Sep_LGFlg", m=MM, seg=10)

# Манометр на сепараторе (сверху на корпусе)
cyl((SX-1.0, SY+0.8, SZ+SR+0.5), 0.04, 0.06, name="Sep_PG_Body", m=MY, seg=12)
cyl((SX-1.0, SY+0.8, SZ+SR+0.56), 0.06, 0.02, name="Sep_PG_Face", m=MW, seg=16)

# ═══════ 8. ДРЕНАЖ ═══════
DX, DY = -11.5, -5.0
cube((DX, DY, 0.2), (0.6, 0.6, 0.2), name="Drn_Ft", m=MN)
cyl((DX, DY, 1.6), 0.45, 2.4, name="Drain", m=MS, seg=22)
cyl((DX, DY, 2.9), 0.45, 0.10, name="Drain_Top", m=MS, seg=22)
cyl((DX-0.5, DY, 2.0), 0.07, 0.35, name="Drain_In", m=MY, seg=10)

# Датчик уровня на дренаже
pipe((DX+0.6, DY, 0.5), (DX+0.6, DY, 2.7), r=0.025, m=MS, seg=8, name="Drn_LG")
cyl((DX+0.6, DY, 2.7), 0.04, 0.03, name="Drn_LGHead", m=MM, seg=10)

# ═══════ 9. ТРУБОПРОВОДНАЯ ЭСТАКАДА ═══════
# П-образные рамы на фундаментах, RY=-7.0 — дальше от сепаратора
RY = -7.0
PZ = 2.8
RACK_SPAN = 3.0

# Фундаменты
for rx in range(-12, 4, RACK_SPAN):
    rx = float(rx)
    for sy in [RY-0.4, RY+0.4]:
        cube((rx, sy, 0.15), (0.25, 0.25, 0.15), name="RackFt_{}_{}".format(int(rx), "L" if sy<RY else "R"), m=MN)

# П-образные рамы
for rx in range(-12, 4, RACK_SPAN):
    rx = float(rx)
    for sy in [RY-0.4, RY+0.4]:
        cube((rx, sy, PZ/2), (0.06, 0.06, PZ/2), name="RackCol_{}_{}".format(int(rx), "L" if sy<RY else "R"), m=MS)
    cube((rx, RY, PZ), (0.06, 0.40, 0.05), name="RackBeam_{}".format(int(rx)), m=MS)

# ── Линия СБРОСНОГО газа: сепаратор → эстакада → ствол (z=5.5) ──
for rx in range(-12, 4, RACK_SPAN):
    cube((float(rx), RY, PZ+0.05), (0.03, 0.12, 0.04), name="FlareShoe_{}".format(int(rx)), m=MS)
pipe((-12, RY, PZ+0.12), (3, RY, PZ+0.12), r=0.17, m=MY, seg=14, name="FlareGasLine")
# От сепаратора к началу эстакады
pipe((SX+2.0, SY, SZ+SR+0.4), (SX+2.0, SY, PZ+0.12), r=0.13, m=MY, seg=12, name="Sep2Rack_V")
pipe((SX+2.0, SY, PZ+0.12), (-12, RY, PZ+0.12), r=0.13, m=MY, seg=12, name="Sep2Rack_H")
# От конца эстакады к стволу
pipe((3, RY, PZ+0.12), (FX+0.7, FY, PZ+0.12), r=0.13, m=MY, seg=12, name="Rack2Stack_H")
pipe((FX+0.7, FY, PZ+0.12), (FX, FY, 5.5), r=0.13, m=MY, seg=12, name="Rack2Stack_R")

# ── Линия ПРОДУВОЧНОГО газа: эстакада → ствол (z=8.0) ──
for rx in range(-9, 5, RACK_SPAN):
    cube((float(rx), RY+0.25, PZ+0.08), (0.025, 0.08, 0.03), name="PurgeShoe_{}".format(int(rx)), m=MS)
pipe((-9, RY+0.25, PZ+0.15), (4, RY+0.25, PZ+0.15), r=0.12, m=MY, seg=12, name="PurgeGasLine")
# Отвод к стволу
pipe((3, RY+0.25, PZ+0.15), (FX+0.7, FY, PZ+0.15), r=0.10, m=MY, seg=12, name="Purge2Stack_H")
pipe((FX+0.7, FY, PZ+0.15), (FX, FY, 8.0), r=0.10, m=MY, seg=12, name="Purge2Stack_R")

# ── Конденсат: сепаратор → дренаж ──
pipe((SX+0.8, SY, SZ-SR-0.5), (DX-0.5, DY, SZ-SR-0.5), r=0.07, m=MS, seg=8, name="Cond")
pipe((DX-0.5, DY, SZ-SR-0.5), (DX-0.5, DY, 2.0), r=0.07, m=MS, seg=8, name="CondR")

# ── Паровая линия ──
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
