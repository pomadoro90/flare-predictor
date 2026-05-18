"""
conveyor_v3.py — Ленточный конвейер по ГОСТ 20-85 (учебная схема).
Вид сбоку. Красная рама. Голубое небо (Workbench — только так видно цвета).
Основные узлы: рама, приводной барабан с мотор-редуктором,
натяжной барабан с винтовым устройством, желобчатые роликоопоры,
холостые роликоопоры, лента, загрузочный лоток.
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

MR = mat("Red",     (0.78, 0.16, 0.16), metal=0.12)   # рама #C62828
MS = mat("Steel",   (0.55, 0.58, 0.62), metal=0.80)   # ролики/валы
MB = mat("Belt",    (0.16, 0.18, 0.21), rough=0.92, metal=0.0)  # лента чёрная
MD = mat("Drum",    (0.40, 0.42, 0.45), metal=0.85, rough=0.22) # барабан
MG = mat("Ground",  (0.24, 0.37, 0.15), rough=0.95)   # земля
MW = mat("White",   (0.88, 0.87, 0.82), rough=0.5, metal=0.1)
MY = mat("Motor",   (0.25, 0.28, 0.32), metal=0.8, rough=0.35)  # мотор
MZ = mat("Hopper",  (0.70, 0.73, 0.76), metal=0.6, rough=0.4)   # бункер

def sm(obj, m):
    obj.data.materials.clear(); obj.data.materials.append(m)

# ═══════ ПРИМИТИВЫ ═══════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; sm(o, m); return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; sm(o, m); return o

def pipe(p1, p2, r=0.025, m=MS, seg=12, name="P"):
    dx,dy,dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(mid, r, L, rot=(0,0,0), name=name, m=m, seg=seg)
    c.rotation_euler = Vector((dx,dy,dz)).to_track_quat('Z','Y').to_euler()
    return c

# ═══════ ПАРАМЕТРЫ КОНВЕЙЕРА ═══════
# X — вдоль конвейера, Y — ширина, Z — высота
LEN = 8.0          # расстояние между осями барабанов
HEAD_X = LEN/2     # приводной (правый)
TAIL_X = -LEN/2    # натяжной (левый)
DRUM_R = 0.32      # радиус барабанов
DRUM_W = 0.60      # ширина барабанов (вдоль Y)
DRUM_Z = 1.05      # высота центров барабанов
BELT_W = 0.50      # ширина ленты
BELT_TH = 0.03     # толщина ленты
TOP_Z = DRUM_Z + DRUM_R           # верх барабана ~1.37
BOT_Z = DRUM_Z - DRUM_R           # низ барабана ~0.73
BELT_TOP_Z = TOP_Z - BELT_TH/2    # центр верхней ленты ~1.355
BELT_BOT_Z = BOT_Z + BELT_TH/2    # центр нижней ленты ~0.745

# ═══════ 1. ЗЕМЛЯ ═══════
cube((0, 0, -0.02), (9, 3, 0.02), name="Ground", m=MG)

# ═══════ 2. РАМА (красные швеллеры) ═══════
RY = BELT_W/2 + 0.08  # швеллеры по бокам ленты
FRAME_Z = BOT_Z - 0.05

for sy in [-RY, RY]:
    # Продольные швеллеры (красные)
    cube((0, sy, FRAME_Z - 0.10), (LEN/2 + 1.0, 0.05, 0.09), name="Rail_{}".format("L" if sy<0 else "R"), m=MR)
    # Стойки к земле
    for fx in [TAIL_X+0.5, TAIL_X+2.5, 0, HEAD_X-2.5, HEAD_X-0.5]:
        cube((fx, sy, FRAME_Z/2 - 0.18), (0.04, 0.04, FRAME_Z/2 + 0.08), name="Leg_{}_{}".format(int(fx), "L" if sy<0 else "R"), m=MR)

# Поперечины рамы
for fx in [TAIL_X+1.5, 0, HEAD_X-1.5]:
    pipe((fx, -RY, FRAME_Z-0.05), (fx, RY, FRAME_Z-0.05), r=0.03, m=MR, seg=8, name="Cross_{}".format(int(fx)))

# Диагональные раскосы (жёсткость)
for i, (x1, x2) in enumerate([(TAIL_X+0.5, TAIL_X+2.5), (TAIL_X+2.5, 0), (0, HEAD_X-2.5), (HEAD_X-2.5, HEAD_X-0.5)]):
    for sy in [-RY, RY]:
        pipe((x1, sy, FRAME_Z-0.25), (x2, sy, FRAME_Z-0.05), r=0.022, m=MR, seg=8, name="Brace_{}_{}".format(i, "L" if sy<0 else "R"))

# ═══════ 3. БАРАБАНЫ ═══════
for dx, tag in [(HEAD_X, "Head"), (TAIL_X, "Tail")]:
    # Барабан
    cyl((dx, 0, DRUM_Z), DRUM_R, DRUM_W, name="Drum_{}".format(tag), m=MD, seg=36)
    # Вал
    cyl((dx, 0, DRUM_Z), 0.07, DRUM_W+0.30, name="Shaft_{}".format(tag), m=MS, seg=20)
    # Футеровка (тёмный слой поверх барабана) — только для приводного
    if tag == "Head":
        cyl((dx, 0, DRUM_Z), DRUM_R+0.008, DRUM_W-0.02, name="Lining_{}".format(tag), m=MB, seg=36)
    # Ступицы
    for sy in [-DRUM_W/2, DRUM_W/2]:
        cyl((dx, sy, DRUM_Z), 0.12, 0.06, name="Hub_{}_{}".format(tag, "L" if sy<0 else "R"), m=MS, seg=20)

# ═══════ 4. МОТОР-РЕДУКТОР (на приводном конце) ═══════
MOTOR_X = HEAD_X + 0.70
MOTOR_Z = DRUM_Z
MOTOR_Y = DRUM_W/2 + 0.25

# Редуктор
cube((HEAD_X+0.25, MOTOR_Y, DRUM_Z), (0.30, 0.20, 0.18), name="Gearbox", m=MS)
# Электродвигатель (цилиндр)
cyl((MOTOR_X, MOTOR_Y, MOTOR_Z), 0.18, 0.55, rot=(math.radians(90),0,0), name="Motor", m=MY, seg=20)
# Кожух муфты
cyl((HEAD_X+0.08, MOTOR_Y, DRUM_Z), 0.16, 0.15, name="Coupling", m=MR, seg=20)
# Рама двигателя (красная опора)
cube((MOTOR_X-0.05, MOTOR_Y, FRAME_Z-0.05), (0.45, 0.08, 0.28), name="MotorBase", m=MR)
# Опора под раму двигателя
for sy_sign in [-1, 1]:
    cube((MOTOR_X-0.05, MOTOR_Y+sy_sign*0.18, FRAME_Z-0.50), (0.04, 0.04, 0.40), name="MotLeg_{}".format("L" if sy_sign<0 else "R"), m=MR)

# ═══════ 5. ЛЕНТА ═══════
# Верхняя рабочая ветвь
cube((0, 0, BELT_TOP_Z), (LEN/2, BELT_W/2, BELT_TH/2), name="Belt_Top", m=MB)
# Нижняя холостая ветвь
cube((0, 0, BELT_BOT_Z), (LEN/2, BELT_W/2, BELT_TH/2), name="Belt_Bot", m=MB)
# Огибание барабанов (полуцилиндры)
for dx, tag in [(HEAD_X, "H"), (TAIL_X, "T")]:
    cyl((dx, 0, DRUM_Z), DRUM_R+BELT_TH/2, BELT_W, name="Wrap_{}".format(tag), m=MB, seg=36)

# ═══════ 6. РОЛИКООПОРЫ ВЕРХНЕЙ ВЕТВИ (желобчатые 3-роликовые, угол 30°) ═══════
R_R = 0.06   # радиус ролика
R_L = 0.18   # длина одного ролика
ANG = 30     # угол наклона боковых роликов
R_Z = BELT_TOP_Z - BELT_TH/2 - R_R  # центр роликов под лентой

for i, rx in enumerate([TAIL_X+1.2, TAIL_X+3.2, HEAD_X-3.2, HEAD_X-1.2]):
    # Кронштейн на раме (стальной)
    cube((rx, 0, R_Z-0.08), (0.35, BELT_W/2+0.06, 0.05), name="Brk_U{}".format(i), m=MS)

    # Центральный ролик (горизонтальный, ось Y)
    cyl((rx, 0, R_Z), R_R, R_L, rot=(math.radians(90),0,0), name="RC{}".format(i), m=MS, seg=16)

    # Боковые ролики под углом
    for side, sg in [("L", -1), ("R", 1)]:
        a = math.radians(ANG)
        ro_y = sg * (R_L/2 + 0.01)
        ro_z = R_Z + math.sin(a) * R_L/2 * 0.85
        cyl((rx, ro_y, ro_z), R_R, R_L, rot=(math.radians(90), -a*sg, 0), name="RS{}_{}".format(side,i), m=MS, seg=16)

# ═══════ 7. РОЛИКООПОРЫ НИЖНЕЙ ВЕТВИ (прямые 1-роликовые) ═══════
RET_Z = BELT_BOT_Z + BELT_TH/2 + R_R

for i, rx in enumerate([TAIL_X+2.2, 0, HEAD_X-2.2]):
    cube((rx, 0, RET_Z-0.06), (0.14, BELT_W/2+0.04, 0.03), name="Brk_D{}".format(i), m=MS)
    cyl((rx, 0, RET_Z), R_R, BELT_W, rot=(math.radians(90),0,0), name="RR{}".format(i), m=MS, seg=16)

# ═══════ 8. НАТЯЖНОЕ УСТРОЙСТВО (винтовое, на хвосте) ═══════
# Направляющие ползуна
for sy in [-RY, RY]:
    cube((TAIL_X, sy, FRAME_Z-0.05), (0.50, 0.06, 0.10), name="Guide_{}".format("L" if sy<0 else "R"), m=MR)
    # Ползун
    cube((TAIL_X, sy, DRUM_Z), (0.09, 0.07, 0.12), name="Slider_{}".format("L" if sy<0 else "R"), m=MW)

# Винты
SCR_START = TAIL_X-0.90
for sy in [-RY, RY]:
    pipe((SCR_START, sy, DRUM_Z), (TAIL_X-0.12, sy, DRUM_Z), r=0.025, m=MS, seg=14, name="Screw_{}".format("L" if sy<0 else "R"))
    # Гайка
    cube((TAIL_X-0.32, sy, DRUM_Z), (0.025, 0.04, 0.035), name="Nut_{}".format("L" if sy<0 else "R"), m=MS)
    # Маховичок
    bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.014, location=(SCR_START, sy, DRUM_Z), major_segments=16, minor_segments=8)
    sm(bpy.context.active_object, MR); bpy.context.active_object.name = "Wheel_{}".format("L" if sy<0 else "R")

# Торцевая пластина рамы под винты
for sy in [-RY, RY]:
    cube((TAIL_X-0.68, sy, FRAME_Z-0.05), (0.04, 0.06, 0.30), name="EndPlate_{}".format("L" if sy<0 else "R"), m=MR)

# ═══════ 9. ЗАГРУЗОЧНЫЙ ЛОТОК (бункер над лентой, слева) ═══════
HOP_X = TAIL_X + 1.8
HOP_Z = BELT_TOP_Z + 0.35

# Воронка (расширяется кверху)
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.45, radius2=0.18, depth=0.55, location=(HOP_X, 0, HOP_Z+0.50))
sm(bpy.context.active_object, MZ); bpy.context.active_object.name = "Hopper_Cone"
# Загрузочная горловина (цилиндр сверху)
cyl((HOP_X, 0, HOP_Z+0.80), 0.20, 0.15, name="Hopper_Neck", m=MZ, seg=20)
# Борта (боковые щитки вдоль ленты от бункера)
cube((HOP_X+0.15, BELT_W/2+0.06, BELT_TOP_Z+0.05), (0.30, 0.015, 0.12), name="Skirt_L", m=MS)
cube((HOP_X+0.15, -BELT_W/2-0.06, BELT_TOP_Z+0.05), (0.30, 0.015, 0.12), name="Skirt_R", m=MS)

# ═══════ 10. РАЗГРУЗКА (лоток под приводным барабаном) ═══════
# Наклонная плоскость от барабана вниз
CHUTE_X = HEAD_X + 0.25
cube((CHUTE_X, 0, DRUM_Z-0.35), (0.35, BELT_W/2, 0.03), name="Chute", m=MZ)
# Боковины
for sy in [-BELT_W/2-0.03, BELT_W/2+0.03]:
    cube((CHUTE_X, sy, DRUM_Z-0.25), (0.35, 0.015, 0.16), name="Chute_Side_{}".format("L" if sy<0 else "R"), m=MS)

# ═══════ 11. ОЧИСТНОЙ СКРЕБОК (под холостой ветвью) ═══════
SCRAPE_X = HEAD_X - 0.60
SCRAPE_Z = BELT_BOT_Z - BELT_TH/2 - 0.04
cube((SCRAPE_X, 0, FRAME_Z-0.05), (0.04, BELT_W/2+0.02, 0.18), name="Scraper_Mount", m=MR)
cube((SCRAPE_X, 0, SCRAPE_Z), (BELT_W/2-0.02, 0.012, 0.02), name="Scraper_Blade", m=MS)

# ═══════ 12. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(20, -15, 30))
bpy.context.active_object.data.energy = 4.5
bpy.ops.object.light_add(type='SUN', location=(-15, 8, 20))
bpy.context.active_object.data.energy = 2.0

# ═══════ 13. КАМЕРА (почти сбоку, чуть 3/4) ═══════
bpy.ops.object.camera_add()
cam = bpy.context.active_object; cam.name = "Camera"; cam.data.lens = 24
cam.location = Vector((1.5, -8.5, 3.0))
tgt = Vector((0, -0.1, 1.3))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 14. РЕНДЕР ═══════
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'STUDIO'
s.display.shading.color_type = 'MATERIAL'
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# Голубое небо
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.48, 0.70, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.3

# ── СОХРАНЕНИЕ + РЕНДЕР ──
out = "/home/pomadoro/projects/flare-predictor/conveyor/"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "conveyor.blend"))
s.render.filepath = os.path.join(out, "conveyor_003.png")
bpy.ops.render.render(write_still=True)
print("✅ conveyor_v3 done")
