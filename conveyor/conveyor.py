"""
conveyor.py — Ленточный конвейер для лабораторной работы.
Два барабана, желобчатые роликоопоры, винтовой натяжной механизм.
Вид сбоку с лёгким смещением для видимости трёхроликовых опор.
Красная гамма #C62828.
"""
import bpy
import math
from mathutils import Vector

# ═══════════════════════════════════════════════════════════════════
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

MR = mat(name="Red",    rgb=(0.78, 0.16, 0.16), metal=0.15)   # #C62828
MS = mat(name="Steel",  rgb=(0.52, 0.55, 0.60), metal=0.85)
MB = mat(name="Belt",   rgb=(0.12, 0.13, 0.16), rough=0.85, metal=0.0)
MD = mat(name="Drum",   rgb=(0.35, 0.37, 0.40), metal=0.9, rough=0.25)
MG = mat(name="Ground", rgb=(0.22, 0.35, 0.13), rough=0.95, metal=0.0)
MW = mat(name="White",  rgb=(0.90, 0.89, 0.85), rough=0.5, metal=0.1)
MY = mat(name="Yellow", rgb=(0.92, 0.78, 0.04), metal=0.2)

def sm(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

# ═══════ ПРИМИТИВЫ ═══════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=20):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=seg, radius=r, depth=d,
        location=loc, rotation=rot
    )
    o = bpy.context.active_object
    o.name = name
    sm(obj=o, m=m)
    return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    sm(obj=o, m=m)
    return o

def pipe(p1, p2, r=0.025, m=MS, seg=10, name="P"):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 0.001:
        return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(loc=mid, r=r, d=L, rot=(0,0,0), name=name, m=m, seg=seg)
    direction = Vector((dx, dy, dz))
    c.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return c

def torus(loc, R, r, name="T", m=MS, seg=18, rseg=6):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=R, minor_radius=r, location=loc,
        major_segments=seg, minor_segments=rseg
    )
    o = bpy.context.active_object
    o.name = name
    sm(obj=o, m=m)
    return o

# ═══════ ПАРАМЕТРЫ КОНВЕЙЕРА ═══════
# Координаты: ось X — длина конвейера, ось Y — ширина, ось Z — высота
BELT_W = 0.40     # ширина ленты (вдоль Y)
BELT_H = 0.012    # толщина ленты
CONV_LEN = 6.0    # расстояние между осями барабанов
TAIL_X = -3.0     # ось натяжного барабана
HEAD_X = 3.0      # ось приводного барабана
DRUM_R_HEAD = 0.30
DRUM_R_TAIL = 0.25
DRUM_W = 0.52      # ширина барабана (чуть шире ленты)
DRUM_Z_HEAD = 0.90 # центр приводного барабана по высоте
DRUM_Z_TAIL = 0.85 # центр натяжного барабана

# Уровни ленты
BELT_TOP = DRUM_Z_HEAD + DRUM_R_HEAD    # ~1.20 — верхняя ветвь
BELT_BOT = DRUM_Z_HEAD - DRUM_R_HEAD    # ~0.60 — нижняя ветвь

# ═══════ 1. ЗЕМЛЯ ═══════
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, -0.3, -0.05))
sm(obj=bpy.context.active_object, m=MG)
bpy.context.active_object.name = "Ground"

# ═══════ 2. ОПОРНАЯ РАМА (два швеллера) ═══════
FRAME_Z_BOT = BELT_BOT - 0.35  # нижний пояс рамы ~0.25
FRAME_Z_TOP = BELT_BOT - 0.12  # верхний пояс рамы ~0.48
FRAME_Y = BELT_W / 2 + 0.08    # швеллера по бокам от ленты

for sy in [-FRAME_Y, FRAME_Y]:
    # Нижний пояс
    cube(loc=(0, sy, FRAME_Z_BOT), scale=(CONV_LEN/2 + 0.6, 0.04, 0.06),
         name="FrameBot_{}".format("L" if sy<0 else "R"), m=MS)
    # Верхний пояс
    cube(loc=(0, sy, FRAME_Z_TOP), scale=(CONV_LEN/2 + 0.6, 0.04, 0.05),
         name="FrameTop_{}".format("L" if sy<0 else "R"), m=MS)
    # Стойки рамы (вертикальные соединители)
    for fx in [-2.5, -1.0, 0.5, 2.0]:
        cube(loc=(fx, sy, (FRAME_Z_BOT+FRAME_Z_TOP)/2),
             scale=(0.04, 0.04, (FRAME_Z_TOP - FRAME_Z_BOT)/2),
             name="FP_{}_{}".format(fx, "L" if sy<0 else "R"), m=MS)

# ═══════ 3. ОПОРНЫЕ НОГИ ═══════
for fx in [-2.5, -1.0, 0.5, 2.0]:
    for sy in [-FRAME_Y, FRAME_Y]:
        cube(loc=(fx, sy, FRAME_Z_BOT/2),
             scale=(0.05, 0.05, FRAME_Z_BOT/2),
             name="Leg_{}_{}".format(fx, "L" if sy<0 else "R"), m=MS)

# ═══════ 4. БАРАБАНЫ ═══════
# Приводной барабан (правый, больше)
cyl(loc=(HEAD_X, 0, DRUM_Z_HEAD), r=DRUM_R_HEAD, d=DRUM_W,
    name="Drum_Head", m=MD, seg=32)
# Ступицы приводного барабана
for sy in [-DRUM_W/2, DRUM_W/2]:
    cyl(loc=(HEAD_X, sy, DRUM_Z_HEAD), r=0.12, d=0.06,
        name="Hub_H_{}".format("L" if sy<0 else "R"), m=MS, seg=16)
# Вал приводного барабана
cyl(loc=(HEAD_X, 0, DRUM_Z_HEAD), r=0.06, d=DRUM_W+0.3,
    name="Shaft_Head", m=MS, seg=16)
# Муфта/шкив на приводном валу (спереди)
cyl(loc=(HEAD_X, DRUM_W/2+0.12, DRUM_Z_HEAD), r=0.14, d=0.10,
    name="Coupling", m=MR, seg=20)

# Натяжной барабан (левый, меньше)
cyl(loc=(TAIL_X, 0, DRUM_Z_TAIL), r=DRUM_R_TAIL, d=DRUM_W,
    name="Drum_Tail", m=MD, seg=32)
# Ступицы натяжного барабана
for sy in [-DRUM_W/2, DRUM_W/2]:
    cyl(loc=(TAIL_X, sy, DRUM_Z_TAIL), r=0.10, d=0.05,
        name="Hub_T_{}".format("L" if sy<0 else "R"), m=MS, seg=16)
# Вал натяжного барабана
cyl(loc=(TAIL_X, 0, DRUM_Z_TAIL), r=0.055, d=DRUM_W+0.25,
    name="Shaft_Tail", m=MS, seg=16)

# ═══════ 5. ЛЕНТА ═══════
# Верхняя ветвь (рабочая, несёт груз)
cube(loc=((HEAD_X+TAIL_X)/2, 0, BELT_TOP - BELT_H/2),
     scale=(CONV_LEN/2, BELT_W/2, BELT_H/2),
     name="Belt_Top", m=MB)
# Нижняя ветвь (холостая)
cube(loc=((HEAD_X+TAIL_X)/2, 0, BELT_BOT + BELT_H/2),
     scale=(CONV_LEN/2, BELT_W/2, BELT_H/2),
     name="Belt_Bot", m=MB)
# Огибание барабанов (полуцилиндры)
for dx, dz, r, tag in [
    (HEAD_X, DRUM_Z_HEAD, DRUM_R_HEAD, "Head"),
    (TAIL_X, DRUM_Z_TAIL, DRUM_R_TAIL, "Tail")
]:
    pipe(p1=(dx, 0, dz), p2=(dx, 0, dz), r=r+BELT_H/2, m=MB, seg=24,
         name="Belt_Wrap_{}".format(tag))

# ═══════ 6. РОЛИКООПОРЫ ВЕРХНЕЙ ВЕТВИ (желобчатые, трёхроликовые) ═══════
ROLLER_R = 0.045     # радиус ролика
ROLLER_L = 0.16      # длина одного ролика
SIDE_ANGLE = 25      # угол наклона боковых роликов (градусы)
ROLLER_Z = BELT_TOP - ROLLER_R  # высота центра роликов под лентой

# Опоры через ~1.2м
for i, rx in enumerate([-2.4, -1.2, 0.0, 1.2, 2.4]):
    # Кронштейн (красный)
    cube(loc=(rx, 0, ROLLER_Z - 0.10),
         scale=(0.30, BELT_W/2 + 0.06, 0.06),
         name="RoSup_U_{}".format(i), m=MR)

    # Центральный ролик (горизонтальный, ось вдоль Y)
    cyl(loc=(rx, 0, ROLLER_Z), r=ROLLER_R, d=ROLLER_L,
        rot=(math.radians(90), 0, 0),
        name="Roller_C_{}".format(i), m=MS, seg=12)

    # Боковые ролики под углом
    for side, sy_sign in [("L", -1), ("R", 1)]:
        ro_y = sy_sign * (ROLLER_L/2 + 0.01)
        ro_z = ROLLER_Z + math.sin(math.radians(SIDE_ANGLE)) * ROLLER_L/2
        # Смещаем по Y и Z для наклона
        cyl(loc=(rx, ro_y, ro_z), r=ROLLER_R, d=ROLLER_L,
            rot=(math.radians(90), math.radians(SIDE_ANGLE * sy_sign), 0),
            name="Roller_{}_{}".format(side, i), m=MS, seg=12)

# ═══════ 7. РОЛИКООПОРЫ НИЖНЕЙ ВЕТВИ (прямые, однороликовые) ═══════
RET_Z = BELT_BOT + ROLLER_R  # высота центров роликов под нижней лентой

for i, rx in enumerate([-1.8, 0.0, 1.8]):
    # Кронштейн
    cube(loc=(rx, 0, RET_Z - 0.08),
         scale=(0.16, BELT_W/2 + 0.04, 0.04),
         name="RoSup_D_{}".format(i), m=MS)
    # Ролик
    cyl(loc=(rx, 0, RET_Z), r=ROLLER_R, d=BELT_W,
        rot=(math.radians(90), 0, 0),
        name="Ret_Roller_{}".format(i), m=MS, seg=12)

# ═══════ 8. НАТЯЖНОЙ МЕХАНИЗМ (винтовой, на хвостовом барабане) ═══════
# Ползун — корпус подшипника натяжного барабана
for sy in [-FRAME_Y, FRAME_Y]:
    # Направляющая ползуна (красный швеллер)
    cube(loc=(TAIL_X, sy, FRAME_Z_TOP),
         scale=(0.35, 0.05, 0.07),
         name="Guide_{}".format("L" if sy<0 else "R"), m=MR)
    # Ползун (подвижная платформа подшипника)
    cube(loc=(TAIL_X, sy, DRUM_Z_TAIL),
         scale=(0.08, 0.06, 0.10),
         name="Slider_{}".format("L" if sy<0 else "R"), m=MW)

# Винтовые тяги (2 шт., по бокам)
TENSION_START_X = TAIL_X - 0.70  # начало резьбовой части
for sy in [-FRAME_Y, FRAME_Y]:
    # Торцевая пластина рамы
    cube(loc=(TAIL_X - 0.55, sy, (FRAME_Z_BOT+FRAME_Z_TOP)/2),
         scale=(0.04, 0.04, (FRAME_Z_TOP-FRAME_Z_BOT)/2 + 0.02),
         name="EndPlate_{}".format("L" if sy<0 else "R"), m=MS)
    # Резьбовая шпилька
    pipe(p1=(TENSION_START_X, sy, DRUM_Z_TAIL),
         p2=(TAIL_X - 0.12, sy, DRUM_Z_TAIL),
         r=0.020, m=MS, seg=12,
         name="Screw_{}".format("L" if sy<0 else "R"))
    # Гайка (кубик на резьбе)
    cube(loc=(TAIL_X - 0.25, sy, DRUM_Z_TAIL),
         scale=(0.03, 0.035, 0.03),
         name="Nut_{}".format("L" if sy<0 else "R"), m=MS)
    # Маховик / рукоятка (кольцо на конце винта)
    torus(loc=(TENSION_START_X, sy, DRUM_Z_TAIL),
          R=0.06, r=0.01,
          name="Handwheel_{}".format("L" if sy<0 else "R"), m=MR, seg=12, rseg=6)

# Подшипниковые узлы на ползуне (спереди и сзади вала)
for sy in [-DRUM_W/2 - 0.05, DRUM_W/2 + 0.05]:
    cube(loc=(TAIL_X, sy, DRUM_Z_TAIL),
         scale=(0.06, 0.06, 0.07),
         name="Bearing_T_{}".format("L" if sy<0 else "R"), m=MW)

# ═══════ 9. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(20, -15, 25))
bpy.context.active_object.data.energy = 3.5

# ═══════ 10. КАМЕРА (слегка со смещением для видимости трёхроликовых опор) ═══════
bpy.ops.object.camera_add(location=(2, -5, 2.5))
cam = bpy.context.active_object
cam.data.lens = 20
cam.name = "Camera"

# Наводимся на центр конвейера + чуть вглубь чтобы видеть боковые ролики
tgt = Vector((0, -0.3, 1.0))
cam.location = Vector((0.5, -5.5, 2.8))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 11. РЕНДЕР ═══════
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.light = 'STUDIO'
bpy.context.scene.display.shading.color_type = 'MATERIAL'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Голубое небо (для контраста тёмных деталей)
w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.50, 0.72, 0.92, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

# ── СОХРАНЕНИЕ + РЕНДЕР ──
out_dir = "/home/pomadoro/projects/flare-predictor/conveyor/"
import os
os.makedirs(out_dir, exist_ok=True)

blend_path = os.path.join(out_dir, "conveyor.blend")
render_path = os.path.join(out_dir, "conveyor_001.png")

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
bpy.context.scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)

print("✅ Конвейер сохранён + рендер: {}".format(blend_path))
