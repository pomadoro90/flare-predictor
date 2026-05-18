"""
conveyor_v2.py — Ленточный конвейер (исправленный).
- Лента: тёмно-серая, толстая (4 см), хорошо видна
- Рама: красная #C62828
- Роликоопоры: стальные, ПОД лентой
- Натяжной механизм: винты + ползуны слева
- Камера: вид почти сбоку с лёгким 3/4
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

MR = mat(name="Red",    rgb=(0.78, 0.16, 0.16), metal=0.12)   # конструктив
MS = mat(name="Steel",  rgb=(0.55, 0.58, 0.62), metal=0.80)   # ролики/валы
MB = mat(name="Belt",   rgb=(0.18, 0.20, 0.22), rough=0.90, metal=0.0)  # лента
MD = mat(name="Drum",   rgb=(0.38, 0.40, 0.43), metal=0.85, rough=0.22) # барабаны
MG = mat(name="Ground", rgb=(0.24, 0.37, 0.15), rough=0.95, metal=0.0)
MW = mat(name="White",  rgb=(0.88, 0.87, 0.82), rough=0.50, metal=0.1)

def sm(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

# ═══════ ПРИМИТИВЫ ═══════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=20):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m); return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; sm(obj=o, m=m); return o

def pipe(p1, p2, r=0.025, m=MS, seg=12, name="P"):
    dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(loc=mid, r=r, d=L, rot=(0,0,0), name=name, m=m, seg=seg)
    c.rotation_euler = Vector((dx,dy,dz)).to_track_quat('Z','Y').to_euler()
    return c

def torus(loc, R, r, name="T", m=MS, seg=16, rseg=6):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=R, minor_radius=r, location=loc,
        major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m); return o

# ═══════ ПАРАМЕТРЫ ═══════
BELT_W   = 0.45   # ширина ленты (Y)
BELT_H   = 0.04   # толщина ленты (Z)
DIST     = 5.5    # расстояние между осями барабанов (X)
TAIL_X   = -DIST/2
HEAD_X   = DIST/2
DRUM_R   = 0.28   # радиус обоих барабанов
DRUM_W   = 0.55   # ширина барабана
DRUM_Z   = 0.95   # высота центров барабанов
TOP_Z    = DRUM_Z + DRUM_R          # верхняя точка барабана ~1.23
BOT_Z    = DRUM_Z - DRUM_R          # нижняя точка барабана ~0.67
BELT_TOP_Z = TOP_Z - BELT_H/2      # центр верхней ленты ~1.21
BELT_BOT_Z = BOT_Z + BELT_H/2      # центр нижней ленты ~0.69

# ═══════ 1. ЗЕМЛЯ ═══════
cube((0, 0, -0.02), (7, 3, 0.02), name="Ground", m=MG)

# ═══════ 2. РАМА (красные швеллеры) ═══════
RY = BELT_W/2 + 0.06  # положение швеллеров по Y
RZ_MID = (BOT_Z + (BOT_Z - 0.30)) / 2  # центр рамы по вертикали

for sy in [-RY, RY]:
    # Продольные балки (красные)
    cube((0, sy, BELT_BOT_Z - 0.25),
         (DIST/2 + 0.8, 0.045, 0.07),
         name="Rail_{}".format("L" if sy<0 else "R"), m=MR)
    # Стойки
    for fx in [TAIL_X+0.3, TAIL_X+2.0, HEAD_X-2.0, HEAD_X-0.3]:
        cube((fx, sy, BELT_BOT_Z - 0.35),
             (0.04, 0.04, 0.25),
             name="Post_{}_{}".format("L" if sy<0 else "R", int(fx)), m=MR)

# Поперечины между швеллерами (снизу)
for fx in [TAIL_X+1.15, 0, HEAD_X-1.15]:
    pipe((fx, -RY, BELT_BOT_Z - 0.35), (fx, RY, BELT_BOT_Z - 0.35),
         r=0.025, m=MR, seg=8, name="Cross_{}".format(int(fx)))

# ═══════ 3. БАРАБАНЫ ═══════
for dx, tag in [(HEAD_X, "Head"), (TAIL_X, "Tail")]:
    cyl((dx, 0, DRUM_Z), DRUM_R, DRUM_W, name="Drum_{}".format(tag), m=MD, seg=32)
    # Вал
    cyl((dx, 0, DRUM_Z), 0.06, DRUM_W+0.25, name="Shaft_{}".format(tag), m=MS, seg=16)
    # Ступицы
    for sy in [-DRUM_W/2, DRUM_W/2]:
        cyl((dx, sy, DRUM_Z), 0.11, 0.05, name="Hub_{}_{}".format(tag, "L" if sy<0 else "R"), m=MS, seg=16)

# Муфта на приводном валу (спереди)
cyl((HEAD_X, DRUM_W/2+0.10, DRUM_Z), 0.13, 0.08, name="Coupling", m=MR, seg=20)

# ═══════ 4. ЛЕНТА (тёмно-серая, толстая) ═══════
# Верхняя (рабочая)
cube((0, 0, BELT_TOP_Z), (DIST/2, BELT_W/2, BELT_H/2), name="Belt_Top", m=MB)
# Нижняя (холостая)
cube((0, 0, BELT_BOT_Z), (DIST/2, BELT_W/2, BELT_H/2), name="Belt_Bot", m=MB)

# Огибание барабанов
for dx, tag in [(HEAD_X, "H"), (TAIL_X, "T")]:
    # полуцилиндр ленты снаружи барабана
    cyl((dx, 0, DRUM_Z), DRUM_R+BELT_H/2, DRUM_W, name="Wrap_{}".format(tag), m=MB, seg=32)

# ═══════ 5. ВЕРХНИЕ РОЛИКООПОРЫ (желобчатые, 3 ролика) ═══════
R_R = 0.05      # радиус ролика
R_L = 0.17      # длина ролика
ANG = 25        # наклон боковых роликов
R_Z = BELT_TOP_Z - BELT_H/2 - R_R  # центр роликов = низ ленты - радиус ролика

for i, rx in enumerate([TAIL_X+1.15, TAIL_X+2.65, 0, HEAD_X-2.65, HEAD_X-1.15]):
    # Кронштейн под роликами (стальной)
    cube((rx, 0, R_Z - 0.07), (0.30, BELT_W/2+0.04, 0.04), name="Bkt_U_{}".format(i), m=MS)

    # Центральный ролик (горизонтальный)
    cyl((rx, 0, R_Z), R_R, R_L,
        rot=(math.radians(90), 0, 0),
        name="RC_{}".format(i), m=MS, seg=14)

    # Боковые ролики
    for side, sg in [("L", 1), ("R", -1)]:
        half_len = R_L/2
        ang_rad = math.radians(ANG)
        ro_y = sg * (R_L/2 - 0.005)
        ro_z = R_Z + math.sin(ang_rad) * half_len * 0.85
        cyl((rx, ro_y, ro_z), R_R, R_L,
            rot=(math.radians(90), -ang_rad*sg, 0),
            name="RS_{}_{}".format(side, i), m=MS, seg=14)

# ═══════ 6. НИЖНИЕ РОЛИКООПОРЫ (прямые, 1 ролик) ═══════
RET_Z = BELT_BOT_Z + BELT_H/2 + R_R  # центр ролика

for i, rx in enumerate([TAIL_X+1.9, 0, HEAD_X-1.9]):
    cube((rx, 0, RET_Z - 0.06), (0.14, BELT_W/2+0.03, 0.03), name="Bkt_D_{}".format(i), m=MS)
    cyl((rx, 0, RET_Z), R_R, BELT_W,
        rot=(math.radians(90), 0, 0),
        name="RR_{}".format(i), m=MS, seg=14)

# ═══════ 7. НАТЯЖНОЙ МЕХАНИЗМ (слева) ═══════
# Торцевые пластины рамы
for sy in [-RY, RY]:
    cube((TAIL_X - 0.65, sy, BELT_BOT_Z - 0.35),
         (0.04, 0.05, 0.40),
         name="EndPlate_{}".format("L" if sy<0 else "R"), m=MR)

# Направляющие ползуна (красные)
for sy in [-RY, RY]:
    cube((TAIL_X, sy, BELT_BOT_Z - 0.08),
         (0.45, 0.06, 0.08),
         name="Guide_{}".format("L" if sy<0 else "R"), m=MR)

# Ползуны (белые — подшипниковые корпуса)
for sy in [-DRUM_W/2 - 0.03, DRUM_W/2 + 0.03]:
    cube((TAIL_X, sy, DRUM_Z),
         (0.08, 0.07, 0.11),
         name="Slider_{}".format("L" if sy<0 else "R"), m=MW)

# Винтовые шпильки (по бокам рамы)
SCR_START = TAIL_X - 0.80
for sy in [-RY, RY]:
    pipe((SCR_START, sy, DRUM_Z), (TAIL_X-0.15, sy, DRUM_Z),
         r=0.022, m=MS, seg=12,
         name="Screw_{}".format("L" if sy<0 else "R"))
    # Гайка на винте
    cube((TAIL_X-0.30, sy, DRUM_Z),
         (0.025, 0.035, 0.03),
         name="Nut_{}".format("L" if sy<0 else "R"), m=MS)
    # Маховичок на конце винта
    torus((SCR_START, sy, DRUM_Z), 0.07, 0.012,
          name="Wheel_{}".format("L" if sy<0 else "R"), m=MR, seg=12, rseg=6)

# ═══════ 8. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(15, -12, 22))
bpy.context.active_object.data.energy = 3.5
bpy.ops.object.light_add(type='SUN', location=(-10, 5, 18))
bpy.context.active_object.data.energy = 1.5

# ═══════ 9. КАМЕРА (сбоку с лёгким 3/4) ═══════
bpy.ops.object.camera_add()
cam = bpy.context.active_object; cam.name = "Camera"; cam.data.lens = 22
cam.location = Vector((0.5, -6.5, 2.2))
tgt = Vector((0, -0.2, 1.1))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 10. РЕНДЕР ═══════
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'STUDIO'
s.display.shading.color_type = 'MATERIAL'
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# Голубое небо
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.50, 0.72, 0.92, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

# ── СОХРАНЕНИЕ ──
out = "/home/pomadoro/projects/flare-predictor/conveyor/"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "conveyor.blend"))
s.render.filepath = os.path.join(out, "conveyor_002.png")
bpy.ops.render.render(write_still=True)
print("✅ conveyor_v2 done")
