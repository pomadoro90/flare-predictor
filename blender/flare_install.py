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

# ═══════ 2. ПЛАТФОРМЫ ═══════
PR, RH, POST_R = 2.0, 0.05, 0.045
for i, pz in enumerate([4.0, 14.0, 29.5]):
    cyl((FX, FY, pz), PR, 0.15, name="Plat{}_D".format(i), m=MS, seg=36)
    for rh in [0.45, 1.0, 1.4]:
        torus((FX, FY, pz+rh), PR-0.18, RH, name="Plat{}_R{}".format(i, rh), m=MS, seg=36, rseg=6)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx = FX + math.cos(ang) * (PR - 0.22)
        sy = FY + math.sin(ang) * (PR - 0.22)
        cyl((sx, sy, pz+0.85), POST_R, 1.5, name="Plat{}_P{}".format(i, a), m=MS, seg=6)

# ═══════ 3. ЛЕСТНИЦА ═══════
SR, STEPS, TURNS = R + 0.75, 65, 4.0
SZ0, SZ1 = 0.6, 37.5
SH = (SZ1 - SZ0) / STEPS
SA = (TURNS * 2 * math.pi) / STEPS
for i in range(STEPS):
    a = i * SA; z = SZ0 + i * SH
    cx = FX + math.cos(a) * SR; cy = FY + math.sin(a) * SR
    s = cube((cx, cy, z+0.06), (0.7, 0.04, 0.06), name="Step{}".format(i), m=MS)
    s.rotation_euler = (0, 0, a + math.pi/2)
IR, OR = R + 0.30, R + 0.95
for i in range(0, STEPS, 4):
    a = i * SA; z = SZ0 + i * SH
    for rr, side in [(IR, "I"), (OR, "O")]:
        sx = FX + math.cos(a) * rr; sy = FY + math.sin(a) * rr
        cyl((sx, sy, z+0.55), 0.028, 1.1, name="RP{}_{}".format(i, side), m=MS, seg=6)

# ═══════ 4. ОТТЯЖКИ — ПРЯМО НА ЗЕМЛЕ ═══════
# 3 уровня (14, 20, 26м) × 4 направления, радиус 22м
GH = [14.0, 20.0, 26.0]
GA = [45, 135, 225, 315]
GR = 22.0

for h in GH:
    for ga in GA:
        ang = math.radians(ga)
        ax = FX + math.cos(ang) * GR
        ay = FY + math.sin(ang) * GR

        # Бетонный анкер прямо на земле (Z=0)
        cube((ax, ay, 0.22), (0.55, 0.55, 0.22), name="Anc_{}_{}".format(int(h), ga), m=MN)

        # Металлическая петля на вершине анкера
        torus((ax, ay, 0.48), 0.22, 0.045, name="Eye_{}_{}".format(int(h), ga), m=MS, seg=12, rseg=6)

        # Трос от ствола к петле анкера
        pipe((FX, FY, h), (ax, ay, 0.48), r=0.065, m=MC, seg=14,
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
for dx in [-SL/2, SL/2]:
    sphere((SX+dx, SY, SZ), SR, name="Sep_Cap", m=MS, seg=16)
cyl((SX-2.0, SY, SZ+SR+0.3), 0.16, 0.5, name="Sep_In", m=MS, seg=14)
cyl((SX+2.0, SY, SZ+SR+0.3), 0.13, 0.4, name="Sep_Vent", m=MS, seg=14)
cyl((SX+0.8, SY, SZ-SR-0.4), 0.11, 0.6, name="Sep_Drain", m=MS, seg=14)
LX, LY = SX - SL/2 - 0.9, SY - 0.5
for si in range(9):
    cube((LX, LY, 0.5+si*0.50), (0.28, 0.02, 0.02), name="SepL{}".format(si), m=MS)
for dx_s, dy_s in [(-0.22, -0.15), (0.22, -0.15), (-0.22, 0.15), (0.22, 0.15)]:
    cyl((LX+dx_s, LY+dy_s, 2.5), 0.028, 4.5, name="SepCage", m=MS, seg=6)
sphere((SX, SY-0.8, SZ+SR+0.5), 0.14, name="SepS_L", m=MM)
sphere((SX-2.5, SY-0.4, SZ+SR+0.5), 0.12, name="SepS_P", m=MM)

# ═══════ 7. ДРЕНАЖ ═══════
DX, DY = -11.5, -5.0
cube((DX, DY, 0.2), (0.6, 0.6, 0.2), name="Drn_Ft", m=MN)
cyl((DX, DY, 1.6), 0.45, 2.4, name="Drain", m=MS, seg=22)
sphere((DX, DY, 2.9), 0.45, name="Drain_Top", m=MS, seg=16)
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

# ═══════ 9. ДАТЧИКИ ═══════
sphere((FX+1.5, FY, 2.5), 0.12, name="S_Tfl", m=MM)
sphere((FX-1.5, FY, 2.5), 0.12, name="S_Ppg", m=MM)
sphere((FX+1.5, FY, 11.0), 0.10, name="S_Qpg", m=MM)
sphere((FX-1.5, FY, 21.0), 0.12, name="S_Stm", m=MM)
sphere((FX+1.6, FY, 5.5), 0.16, name="Ind_G", m=MF)
sphere((FX-1.6, FY, 5.5), 0.16, name="Ind_R", m=MR)

# ═══════ 10. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(25, -20, 35))
bpy.context.active_object.data.energy = 4.5

# ═══════ 11. КАМЕРА ═══════
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 18
cam.location = Vector((28, -30, 22))
tgt = Vector((-4, -3, 15))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 12. EEVEE + ГОЛУБОЕ НЕБО ═══════
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
