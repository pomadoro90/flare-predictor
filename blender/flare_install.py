"""
flare_install.py — реалистичная low-poly 3D-модель факельной установки НПЗ.
Основана на референсах реальных установок:
  - Факельный ствол с красно-белыми полосами (авиационная видимость)
  - 3–4 платформы с ограждениями на разных высотах
  - Оттяжки (тросы) для устойчивости
  - Винтовая лестница вокруг ствола
  - Knockout drum (сепаратор): горизонтальный цилиндр с лестницей-клеткой
  - Жёлтые газовые трубы на эстакадах
  - Горелка на вершине с пламенем
Ограничение: ≤25 000 полигонов.
"""

import bpy, math, os
from mathutils import Vector, Euler

# ── ОЧИСТКА ──
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ═══════════════════════════════════════════════
# МАТЕРИАЛЫ (яркие, различные цвета)
# ═══════════════════════════════════════════════
def mat(name, rgb, rough=0.55, metal=0.1):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    m.roughness = rough
    m.metallic = metal
    return m

M_RED    = mat("Red",    (0.82, 0.18, 0.12))
M_WHITE  = mat("White",  (0.92, 0.91, 0.88))
M_STEEL  = mat("Steel",  (0.58, 0.60, 0.64), metal=0.75)
M_YELLOW = mat("Yellow", (0.92, 0.80, 0.08))
M_BURNER = mat("Burner", (0.28, 0.30, 0.33), metal=0.85, rough=0.3)
M_FLAME  = mat("Flame",  (1.0,  0.55, 0.05))
M_CABLE  = mat("Cable",  (0.20, 0.22, 0.25), metal=0.5)
M_CONCR  = mat("Concrete",(0.62, 0.60, 0.56), rough=0.85)
M_GROUND = mat("Ground", (0.35, 0.42, 0.28), rough=0.9)
M_SENSOR = mat("Sensor", (0.10, 0.12, 0.16), metal=0.7)

def set_mat(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

# ═══════════════════════════════════════════════
# ГЕОМЕТРИЧЕСКИЕ ПРИМИТИВЫ
# ═══════════════════════════════════════════════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=M_STEEL, seg=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

def cube(loc, scale, name="Q", m=M_STEEL):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.active_object
    o.name = name; o.scale = scale; set_mat(o, m); return o

def sphere(loc, r, name="S", m=M_SENSOR, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=8, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

def torus(loc, R, r, name="T", m=M_STEEL, seg=20, rseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

# Труба между двумя точками
def pipe(p1, p2, r=0.04, m=M_STEEL, seg=10, name="P"):
    dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    th = math.acos(dz/L) if L > 0 else 0
    ph = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0
    return cyl(mid, r, L, (th, 0, ph), name, m, seg)

# ── ГРУНТ (бетонная площадка + земля) ──
cube((0, -1, 0.03), (14, 10, 0.03), "Pad", M_CONCR)
cube((0, -1, -0.08), (16, 12, 0.08), "Ground", M_GROUND)

# ═══════════════════════════════════════════════
# 1. ФАКЕЛЬНЫЙ СТВОЛ — высокий вертикальный цилиндр
# ═══════════════════════════════════════════════
STACK_H = 36.0        # общая высота ствола (масштаб 1:1 ~36 м)
STACK_R = 1.0         # радиус ствола
FX, FY, FZ = 0.0, -1.0, 0.0   # позиция основания

# 1a. Нижняя секция — красная (0–12 м)
cyl((FX, FY, 6.1), STACK_R, 12.0, name="Stack_Lower", m=M_RED, seg=28)

# 1b. Средняя секция — белая (12–27 м)
cyl((FX, FY, 19.6), STACK_R, 15.0, name="Stack_Mid", m=M_WHITE, seg=28)

# 1c. Верхняя секция — красная (27–36 м)
cyl((FX, FY, 31.6), STACK_R, 9.0, name="Stack_Upper", m=M_RED, seg=28)

# 1d. Основание ствола (фланец/база)
cyl((FX, FY, 0.2), 1.25, 0.4, name="Stack_Base", m=M_STEEL, seg=28)

# ═══════════════════════════════════════════════
# 2. ПЛАТФОРМЫ С ОГРАЖДЕНИЯМИ (3 шт.)
# ═══════════════════════════════════════════════
platforms = [
    (0.0,  -1.0,  3.0),   # нижняя (красная секция, для доступа к датчикам)
    (0.0,  -1.0, 13.5),   # средняя (стык красной и белой)
    (0.0,  -1.0, 28.0),   # верхняя (под горелкой)
]

PLAT_R = 1.9     # радиус платформы
RAIL_H = 0.05    # толщина труб ограждения
POST_R = 0.04    # радиус стоек

for i, (px, py, pz) in enumerate(platforms):
    # Настил платформы (диск)
    cyl((px, py, pz), PLAT_R, 0.12, name=f"Plat{i}_Floor", m=M_STEEL, seg=32)

    # Кольца ограждения (3 уровня)
    for rh in [0.4, 0.9, 1.3]:
        torus((px, py, pz + rh), PLAT_R - 0.15, RAIL_H, name=f"Plat{i}_Rail{rh}", m=M_STEEL, seg=32, rseg=6)

    # Стойки ограждения (через 45°)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx, sy = px + math.cos(ang)*(PLAT_R-0.2), py + math.sin(ang)*(PLAT_R-0.2)
        cyl((sx, sy, pz + 0.75), POST_R, 1.3, name=f"Plat{i}_Post{a}", m=M_STEEL, seg=6)

# ═══════════════════════════════════════════════
# 3. ВИНТОВАЯ ЛЕСТНИЦА вокруг ствола
# ═══════════════════════════════════════════════
STAIR_R = STACK_R + 0.65     # радиус лестницы от центра ствола
STAIR_STEPS = 60              # ступеней
STAIR_START_Z = 0.5
STAIR_END_Z = 35.5
STEP_H = (STAIR_END_Z - STAIR_START_Z) / STAIR_STEPS
STEP_W = 0.55
STEP_D = 0.12
TURNS = 3.5                   # оборотов вокруг ствола
ANG_PER_STEP = (TURNS * 2*math.pi) / STAIR_STEPS

# Перила лестницы (2 непрерывных поручня)
INNER_R = STACK_R + 0.25
OUTER_R = STACK_R + 0.90
RAIL_H_STAIR = 1.05

for i in range(STAIR_STEPS):
    a = i * ANG_PER_STEP
    z = STAIR_START_Z + i * STEP_H
    cx, cy = FX + math.cos(a)*STAIR_R, FY + math.sin(a)*STAIR_R
    # Ступень (горизонтальная пластина)
    step = cube((cx, cy, z + STEP_D/2), (STEP_W/2, 0.08, STEP_D/2), f"Step{i}", M_STEEL)
    step.rotation_euler = (0, 0, a + math.pi/2)

# Стойки перил (каждые 5 ступеней)
for i in range(0, STAIR_STEPS, 5):
    a = i * ANG_PER_STEP
    z = STAIR_START_Z + i * STEP_H
    # Внутренняя стойка
    cx_i, cy_i = FX + math.cos(a)*INNER_R, FY + math.sin(a)*INNER_R
    cyl((cx_i, cy_i, z + RAIL_H_STAIR/2), 0.025, RAIL_H_STAIR, name=f"RailPostIn{i}", m=M_STEEL, seg=6)
    # Внешняя стойка
    cx_o, cy_o = FX + math.cos(a)*OUTER_R, FY + math.sin(a)*OUTER_R
    cyl((cx_o, cy_o, z + RAIL_H_STAIR/2), 0.025, RAIL_H_STAIR, name=f"RailPostOut{i}", m=M_STEEL, seg=6)

# ═══════════════════════════════════════════════
# 4. ОТТЯЖКИ (тросы) — 4 шт. под разными углами
# ═══════════════════════════════════════════════
GUY_HEIGHTS = [12.0, 22.0, 32.0]   # высоты крепления тросов к стволу
GUY_ANCHOR_R = 14.0                 # радиус анкерных точек на земле
GUY_ANGLES = [45, 135, 225, 315]   # направления тросов (в градусах)

for h in GUY_HEIGHTS:
    for ga in GUY_ANGLES:
        ang = math.radians(ga)
        ax, ay = FX + math.cos(ang)*GUY_ANCHOR_R, FY + math.sin(ang)*GUY_ANCHOR_R
        # Анкерный блок
        cube((ax, ay, 0.25), (0.35, 0.35, 0.25), f"Anchor_{h}_{ga}", M_CONCR)
        # Трос
        pipe((FX, FY, h), (ax, ay, 0.5), 0.025, M_CABLE, seg=8, name=f"Guy_{h}_{ga}")

# ═══════════════════════════════════════════════
# 5. ГОРЕЛКА НА ВЕРШИНЕ
# ═══════════════════════════════════════════════
BURNER_Z = 36.3
# Основание горелки
cyl((FX, FY, BURNER_Z), 0.65, 0.5, name="Burner_Base", m=M_BURNER, seg=24)
# Сопло
cyl((FX, FY, BURNER_Z + 0.9), 0.35, 1.2, name="Burner_Nozzle", m=M_BURNER, seg=24)
# Вентиляционные прорези (кольца)
for j, dz in enumerate([0.4, 0.8, 1.2]):
    torus((FX, FY, BURNER_Z + dz), 0.42, 0.03, f"Burner_Ring{j}", M_STEEL, seg=24, rseg=6)

# Пламя (конус)
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.15, radius2=0.55, depth=4.0,
                                 location=(FX, FY, BURNER_Z + 3.5))
flame_obj = bpy.context.active_object; flame_obj.name = "Flame"; set_mat(flame_obj, M_FLAME)

# Дежурные горелки (пилоты) — 4 шт.
for a in [0, 90, 180, 270]:
    ang = math.radians(a)
    px, py = FX + math.cos(ang)*0.25, FY + math.sin(ang)*0.25
    cyl((px, py, BURNER_Z + 1.7), 0.04, 0.6, name=f"Pilot{a}", m=M_BURNER, seg=8)

# ═══════════════════════════════════════════════
# 6. СЕПАРАТОР (KNOCKOUT DRUM) — горизонтальный
# ═══════════════════════════════════════════════
SEP_X, SEP_Y, SEP_Z = -6.0, -3.0, 1.5
SEP_LEN, SEP_R = 7.0, 1.3

# Фундаментные опоры
for sx in [SEP_X - 2.4, SEP_X + 2.4]:
    cube((sx, SEP_Y, 0.25), (0.4, 0.8, 0.25), "SepFoot", M_CONCR)
    cyl((sx, SEP_Y, 0.65), 0.18, 0.6, name="SepSaddle", m=M_STEEL, seg=14)

# Корпус
sb = cyl((SEP_X, SEP_Y, SEP_Z), SEP_R, SEP_LEN, name="Sep_Body", m=M_WHITE, seg=28)
sb.rotation_euler = (0, math.radians(90), 0)

# Торцевые крышки
for dx in [-SEP_LEN/2, SEP_LEN/2]:
    sphere((SEP_X + dx, SEP_Y, SEP_Z), SEP_R, "SepCap", M_STEEL, 16)

# Патрубки сверху
cyl((SEP_X - 1.5, SEP_Y, SEP_Z + SEP_R + 0.2), 0.15, 0.4, name="Sep_Inlet", m=M_STEEL, seg=12)
cyl((SEP_X + 1.5, SEP_Y, SEP_Z + SEP_R + 0.2), 0.12, 0.35, name="Sep_Vent", m=M_STEEL, seg=12)

# Выход конденсата снизу
cyl((SEP_X + 0.5, SEP_Y, SEP_Z - SEP_R - 0.3), 0.10, 0.5, name="Sep_Drain", m=M_STEEL, seg=12)

# Лестница-клетка (сбоку сепаратора)
LADDER_X = SEP_X - SEP_LEN/2 - 0.8
LADDER_Y = SEP_Y - 0.4
for step_i in range(8):
    z = 0.4 + step_i * 0.45
    cube((LADDER_X, LADDER_Y, z), (0.25, 0.02, 0.02), f"SepLad{step_i}", M_STEEL)

# Стойки клетки
for dx_s in [-0.2, 0.2]:
    for dy_s in [-0.13, 0.13]:
        cyl((LADDER_X + dx_s, LADDER_Y + dy_s, 2.2), 0.025, 4.0, name="SepCage", m=M_STEEL, seg=6)

# Датчики на сепараторе
sphere((SEP_X, SEP_Y - 0.7, SEP_Z + SEP_R + 0.5), 0.12, "SepSensor_L", M_SENSOR)
sphere((SEP_X - 2.0, SEP_Y - 0.3, SEP_Z + SEP_R + 0.5), 0.10, "SepSensor_P", M_SENSOR)

# ═══════════════════════════════════════════════
# 7. ДРЕНАЖНАЯ ЁМКОСТЬ — вертикальная
# ═══════════════════════════════════════════════
DRN_X, DRN_Y = -9.0, -3.0
cube((DRN_X, DRN_Y, 0.15), (0.55, 0.55, 0.15), "DrnFoot", M_CONCR)
cyl((DRN_X, DRN_Y, 1.4), 0.4, 2.2, name="Drain_Body", m=M_STEEL, seg=20)
sphere((DRN_X, DRN_Y, 2.6), 0.4, "Drain_Top", M_STEEL, 14)
cyl((DRN_X - 0.45, DRN_Y, 1.8), 0.06, 0.3, name="Drain_In", m=M_YELLOW, seg=10)

# ═══════════════════════════════════════════════
# 8. ТРУБОПРОВОДНАЯ ОБВЯЗКА И ЭСТАКАДЫ
# ═══════════════════════════════════════════════

# Эстакада (pipe rack) — опоры для жёлтых труб
RACK_Y = -4.5
for rx in [-8, -5, -2, 1, 4]:
    cube((rx, RACK_Y, 1.2), (0.12, 0.15, 1.2), "RackLeg", M_STEEL)
if True:
    # Горизонтальные балки эстакады
    for rx1, rx2 in [(-8, 4), (-8, -2), (-2, 4)]:
        mx, my = (rx1+rx2)/2, RACK_Y
        bm = cube((mx, my, 2.4), (abs(rx2-rx1)/2 + 0.1, 0.08, 0.1), "RackBeam", M_STEEL)

# Жёлтые газовые трубы на эстакаде
PIPE_Z = 2.65
pipe((-8, RACK_Y, PIPE_Z), (1, RACK_Y, PIPE_Z), 0.15, M_YELLOW, seg=12, name="GasMain")
pipe((-5, RACK_Y, PIPE_Z + 0.3), (3, RACK_Y, PIPE_Z + 0.3), 0.10, M_YELLOW, seg=10, name="GasSec")

# Труба от сепаратора к стволу
pipe((SEP_X + 2.5, SEP_Y, SEP_Z + SEP_R + 0.3), (SEP_X + 2.5, SEP_Y, 3.0), 0.12, M_YELLOW, seg=10, name="SepToStackV")
pipe((SEP_X + 2.5, SEP_Y, 3.0), (FX + 0.6, FY, 3.0), 0.12, M_YELLOW, seg=10, name="SepToStackH")
pipe((FX + 0.6, FY, 3.0), (FX, FY, 4.5), 0.12, M_YELLOW, seg=10, name="SepToStackRise")

# Труба конденсата: сепаратор → дренаж
pipe((SEP_X + 0.5, SEP_Y, SEP_Z - SEP_R - 0.5), (DRN_X - 0.45, DRN_Y, SEP_Z - SEP_R - 0.5), 0.06, M_STEEL, seg=8, name="Condensate")
pipe((DRN_X - 0.45, DRN_Y, SEP_Z - SEP_R - 0.5), (DRN_X - 0.45, DRN_Y, 1.8), 0.06, M_STEEL, seg=8, name="CondRise")

# Паровая линия
pipe((-11, -6, 5.0), (-4, -5, 5.0), 0.07, M_STEEL, seg=10, name="Steam1")
pipe((-4, -5, 5.0), (FX - 1.0, FY - 1.5, 5.0), 0.07, M_STEEL, seg=10, name="Steam2")
pipe((FX - 1.0, FY - 1.5, 5.0), (FX - 0.6, FY - 0.4, 25.0), 0.05, M_STEEL, seg=8, name="SteamRise")

# ═══════════════════════════════════════════════
# 9. ДАТЧИКИ НА СТВОЛЕ
# ═══════════════════════════════════════════════
sphere((FX + 1.25, FY, 2.0), 0.10, "S_Tflame", M_SENSOR)
sphere((FX - 1.25, FY, 2.0), 0.10, "S_Ppurge", M_SENSOR)
sphere((FX + 1.25, FY, 10.0), 0.08, "S_Qpurge", M_SENSOR)
sphere((FX - 1.25, FY, 20.0), 0.10, "S_Steam", M_SENSOR)

# Индикаторные лампы
sphere((FX + 1.35, FY, 4.5), 0.14, "Ind_Green", M_FLAME)
sphere((FX - 1.35, FY, 4.5), 0.14, "Ind_Red", M_RED)

# ═══════════════════════════════════════════════
# 10. КАМЕРА И РЕНДЕР (WORKBENCH)
# ═══════════════════════════════════════════════
# Широкоугольная камера для обзора ВСЕЙ установки
bpy.ops.object.camera_add(location=(22, -20, 14))
cam = bpy.context.active_object
cam.data.lens = 20
cam.location = Vector((22, -20, 14))
# Смотрим на точку между стволом и сепаратором
target = Vector((-3, -2, 14))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Солнечный свет
bpy.ops.object.light_add(type='SUN', location=(15, -10, 25))
bpy.context.active_object.data.energy = 6.0

# Workbench — материал + студийное освещение
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Яркий фон
w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.82, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 2.0

# Сохранение
blend_path = "/home/pomadoro/projects/flare-predictor/blender/flare_install.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"✅ Модель сохранена: {blend_path}")
print(f"   Компоненты: ствол (красный+белый), 3 платформы, лестница, оттяжки, горелка, сепаратор, дренаж, трубопроводы")
