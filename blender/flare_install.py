"""
ФАКЕЛЬНАЯ УСТАНОВКА НПЗ — low-poly модель для курсовой работы.
Версия: v29 | Полигонов: ~25K | Blender 5.1.1 | Рендер: EEVEE/Workbench

═══════════════════════════════════════════════════════════
                    АННОТАЦИЯ ОБЪЕКТОВ
═══════════════════════════════════════════════════════════

СЕКЦИИ КОДА (по номерам ═══):
  0. ЗЕМЛЯ + ПЛОЩАДКА — Ground (зелёный plane 60×60), Pad (бетон 48×36×0.12)
  1. СТВОЛ — три секции: красная 0-12м (Ø2.2), белая 12-28м (Ø2.2), красная 28-38м (Ø2.2)
  2. ПЛАТФОРМЫ — 3 шт. на стыках 12/28м + верхняя 37м, R=2.0, перила h=1.3
  3. ЛЕСТНИЦА — Н-образная (2 рейки + перекладины), 3 секции со сдвигом 90°, защитная клетка
  4. ОТТЯЖКИ — 12 тросов (3 яруса × 4 направления), анкеры 1.4×1.4×0.8м на расстоянии 20м
  5. ГОРЕЛКА — Burner_B + сопло + пламя (конус 7м) + дежурные горелки (3) + паровой коллектор + газовый коллектор
  6. ДАТЧИКИ НА СТВОЛЕ — P_flare, Q_flare, P_purge, Q_purge (давление), T_flame (темп.), Steam_Q
  7. СЕПАРАТОР — горизонтальный 7.5×Ø2.8м, опоры, уровнемер, манометр, лестница-клетка
  8. ДРЕНАЖ — вертикальная ёмкость Ø0.9×2.4м, уровнемер
  9. ТРУБОПРОВОДНАЯ ЭСТАКАДА — П-образные рамы на фундаментах, линии: сброс, продувка, конденсат, пар
 9a. ДАТЧИК РАСХОДА НА ПРОДУВОЧНОЙ ЛИНИИ — корпус + измерительный элемент (X=-3, Y=RY+0.3)
 9b. ДАТЧИКИ НА ОПОРЫ ЭСТАКАДЫ — 3 вибродатчика на левых стойках рам X∈{-12,-6,0}
 9c. ФУНДАМЕНТНАЯ ПЛИТА СЕПАРАТОРА — бетонная плита 8.5×3.4×0.12 под сепаратором
 10. СВЕТ — Sun (25,-20,35), energy=4.5
 11. КАМЕРА — lens=18, позиция (28,-30,22), цель (-4,-3,15)
 12. РЕНДЕР — EEVEE, 1920×1080, голубое небо, exposure=1.2

МАТЕРИАЛЫ (префиксы):
  MR — Red (#C62828) ствол, опоры эстакады
  MW — White ствол, сепаратор, анкерные блоки
  MS — Steel ролики, валы, лестница, клетка, перила
  MY — Yellow трубы, датчики давления
  MB — Burner тёмный металл горелок
  MF — Flame оранжевое пламя
  MC — Cable чёрные тросы оттяжек
  MN — Concrete фундаменты, бетонная площадка
  MG — Ground зелёная земля
  MM — Sensor тёмные головки датчиков

ПРОСТРАНСТВЕННАЯ СХЕМА (вид сверху, ось X→, Y↑):
                    N (Y+)
            anc(20,19)  anc(20,19)
             /              \
            /                \
    W --sep(-7,-4.5)====эстакада(Y=-7)====[СТВОЛ(0,-1)]--  E (X+)
            \                /
             \              /
            anc(-20,-21) anc(-20,-21)
                    S (Y-)

  Ствол:    X=0, Y=-1, H=38м
  Сепаратор: X=-7, Y=-4.5, 7.5×Ø2.8
  Дренаж:   X=-11.5, Y=-5, Ø0.9×2.4
  Эстакада: Y=-7, X∈[-12;3], трубы на z≈2.9
  Анкеры:   R=20м от ствола, высоты крепления 10/20/34м

ЗАПУСК:
  blender --background --python flare_install.py
  blender --background flare_install.blend --python render_views.py
  bash render_all.sh
"""
import bpy, math, os
from mathutils import Vector, Matrix

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
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def torus(loc, R, r, name="T", m=MS, seg=20, rseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def pipe(p1, p2, r=0.04, m=MS, seg=12, name="P"):
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]; dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(mid, r, L, rot=(0,0,0), name=name, m=m, seg=seg)
    direction = Vector((dx, dy, dz))
    c.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return c

def joint(loc, pipe_r, v_in, v_out, name="J", m=MS):
    """DEBUG: два цилиндра-порта в позициях стыков. Потом заменим на elbow."""
    R = pipe_r * 1.5
    # Входной порт: loc - R·v_in, смотрит по v_in
    c_in = loc - R * v_in
    p_in = cyl(c_in, pipe_r, 0.06, name=name + "_IN", m=m, seg=16)
    p_in.rotation_euler = v_in.to_track_quat('Z', 'Y').to_euler()
    # Выходной порт: loc + R·v_out, смотрит по v_out
    c_out = loc + R * v_out
    p_out = cyl(c_out, pipe_r, 0.06, name=name + "_OUT", m=m, seg=16)
    p_out.rotation_euler = v_out.to_track_quat('Z', 'Y').to_euler()
    return p_in

def elbow(loc, v_in, v_out, pipe_r, name="Elbow", m=MS, seg=24):
    """Четверть тора (90° изгиб). Вход по v_in, выход по v_out."""
    import bmesh
    loc_v = Vector(loc)
    v_in = Vector(v_in).normalized()
    v_out = Vector(v_out).normalized()

    Re = pipe_r * 1.5      # радиус изгиба по центральной линии
    rt = pipe_r             # радиус трубы

    # --- локальная геометрия четверти тора ---
    # Дуга: старт (0,0,-Re) касат. +Z → конец (Re,0,0) касат. +X
    # Параметризация: x=Re*(1-cos u), z=Re*sin u - Re, u∈[0,π/2]
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    rings = []
    for i in range(seg + 1):
        u = (i / seg) * math.pi / 2
        cx = Re * (1 - math.cos(u))
        cz = Re * math.sin(u) - Re
        tx = math.sin(u)
        tz = math.cos(u)
        ring = []
        for j in range(seg):
            v = (j / seg) * 2 * math.pi
            x = cx + rt * math.cos(v) * tz
            y = rt * math.sin(v)
            z = cz - rt * math.cos(v) * tx
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((rings[i][j], rings[i][jn], rings[i+1][jn], rings[i+1][j]))
    bm.to_mesh(mesh)
    bm.free()
    # Сглаживание: выставляем use_smooth на всех гранях напрямую
    for p in mesh.polygons:
        p.use_smooth = True

    # --- матрица: локальная +Z→v_in, локальная +X→v_out ---
    mz = v_in
    mx = v_out
    my = mz.cross(mx)
    if my.length < 1e-6:
        my = Vector((0, 1, 0))
    my.normalize()
    mz = mx.cross(my)
    mz.normalize()
    M = Matrix((mx, my, mz)).to_4x4()
    obj.matrix_world = Matrix.Translation(loc_v) @ M

    # --- порты в мировых координатах ---
    port_in  = loc_v + M @ Vector((0, 0, -Re))
    port_out = loc_v + M @ Vector((Re, 0, 0))

    sm(obj=obj, m=m)

    return obj, tuple(port_in), tuple(port_out)

def route(points, r, m=MS, seg=12, name="R", joint_m=None):
    """Прокладывает трубу по ломаной с elbow-коленами в вершинах поворота."""
    if joint_m is None:
        joint_m = m
    n = len(points)
    if n < 2:
        return
    current_start = Vector(points[0])
    seg_idx = 0
    for pivot_idx in range(1, n - 1):
        p_prev  = Vector(points[pivot_idx - 1])
        p_pivot = Vector(points[pivot_idx])
        p_next  = Vector(points[pivot_idx + 1])
        v_in  = (p_pivot - p_prev).normalized()
        v_out = (p_next - p_pivot).normalized()
        if abs(v_in.dot(v_out)) > 0.999:
            continue  # прямой участок — без колена
        # колено в точке поворота
        _, port_in, port_out = elbow(
            p_pivot, v_in, v_out, r, seg=24,
            name="{}_E{}".format(name, pivot_idx), m=joint_m)
        # труба от предыдущего старта до входного порта колена
        if (current_start - Vector(port_in)).length > 0.001:
            pipe(tuple(current_start), port_in, r=r, m=m, seg=seg,
                 name="{}_{}".format(name, seg_idx))
            seg_idx += 1
        current_start = Vector(port_out)
    # последний прямой сегмент
    if (current_start - Vector(points[-1])).length > 0.001:
        pipe(tuple(current_start), points[-1], r=r, m=m, seg=seg,
             name="{}_{}".format(name, seg_idx))

# ═══════ ЗЕМЛЯ + ПЛОЩАДКА ═══════
# Земля ниже, площадка толще и выше — чтобы не было наложения
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, -2, -0.03))
sm(obj=bpy.context.active_object, m=MG)
bpy.context.active_object.name = "Ground"
cube((0, -2, 0.06), (24, 18, 0.06), name="Pad", m=MN)

# ═══════ 1. СТВОЛ ═══════
H, R, FX, FY = 38.0, 1.1, 0.0, -1.0
cyl((FX, FY, 6.1),  R, 12.0, name="Stack_L", m=MR, seg=30)
cyl((FX, FY, 20.1), R, 16.0, name="Stack_M", m=MW, seg=30)
cyl((FX, FY, 33.1), R, 10.0, name="Stack_U", m=MR, seg=30)
cyl((FX, FY, 0.25), 1.35, 0.5, name="Stack_Base", m=MS, seg=30)

# ═══════ 2. ПЛАТФОРМЫ — только на стыках секций + верхняя ═══════
PR, RH, POST_R = 2.0, 0.05, 0.045
LR = R + 0.25           # радиус лестницы (нужен для отверстий в платформах)
# Платформы: стык красный-белый (12м), стык белый-красный (28м), верхняя (37м)
for pz, pname in [(12.0, "Joint_LM"), (28.0, "Joint_MU"), (37.0, "Top")]:
    cyl((FX, FY, pz), PR, 0.12, name="{}_D".format(pname), m=MS, seg=48)
    for rh in [0.40, 0.90, 1.30]:
        torus((FX, FY, pz+rh), PR-0.18, RH, name="{}_R{}".format(pname, rh), m=MS, seg=48, rseg=12)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx = FX + math.cos(ang) * (PR - 0.22)
        sy = FY + math.sin(ang) * (PR - 0.22)
        # Стойка: от чуть ниже нижнего поручня (pz+0.30) до верхнего (pz+1.30)
        cyl((sx, sy, pz+0.30), POST_R, 1.0, name="{}_P{}".format(pname, a), m=MS, seg=6)

# ── Отверстия (круглые люки) в платформах над лестницей ──
HATCH_R = 0.35  # радиус круглого люка (достаточно для прохода человека)
for pz, pname, az_deg in [(12.0, "Joint_LM", 0), (28.0, "Joint_MU", 90), (37.0, "Top", 0)]:
    az = math.radians(az_deg)
    hx = FX + math.cos(az) * LR
    hy = FY + math.sin(az) * LR
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=HATCH_R, depth=0.20,
        location=(hx, hy, pz))
    cutter = bpy.context.active_object; cutter.name = "{}_Hole".format(pname)
    disc = bpy.data.objects["{}_D".format(pname)]
    bpy.context.view_layer.objects.active = disc
    mod = disc.modifiers.new(name="Hole", type='BOOLEAN')
    mod.object = cutter; mod.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

# ═══════ 3. ЛЕСТНИЦА: Н-образная, только на красных секциях, у ствола ═══════
LR = R + 0.25          # радиус — прямо у ствола
RAIL_R = 0.025         # радиус реек
STEP_W = 0.45          # ширина лестницы
CAGE_R = LR + 0.28     # радиус клетки
CAGE_BAR_R = 0.014     # тонкие прутья

# Три секции лестницы: нижняя красная, белая, верхняя красная
LADDER_SECTIONS = [
    (0.6, 12.0, 0),      # нижняя красная
    (12.0, 28.0, 90),    # белая ← возвращаю!
    (28.0, 37.5, 0),     # верхняя красная
]

for sec_idx, (z0, z1, az_deg) in enumerate(LADDER_SECTIONS):
    az = math.radians(az_deg)
    ox = FX + math.cos(az) * LR
    oy = FY + math.sin(az) * LR
    px = -math.sin(az)
    py = math.cos(az)

    # Координаты реек
    lx = ox - px * STEP_W/2
    ly = oy - py * STEP_W/2
    rx = ox + px * STEP_W/2
    ry = oy + py * STEP_W/2

    # Рейки — СТАЛЬНЫЕ серые
    pipe((lx, ly, z0), (lx, ly, z1), r=RAIL_R, m=MS, seg=12,
         name="Rail_L_{}".format(sec_idx))
    pipe((rx, ry, z0), (rx, ry, z1), r=RAIL_R, m=MS, seg=12,
         name="Rail_R_{}".format(sec_idx))

    # Ступени: одна перекладина на шаг
    STEP_H = 0.30
    n_steps = int((z1 - z0) / STEP_H)
    sh = (z1 - z0) / n_steps
    for si in range(n_steps):
        z = z0 + si * sh + sh/2
        pipe((lx, ly, z), (rx, ry, z), r=RAIL_R*0.7, m=MS, seg=6,
             name="Rung_{}_{}".format(sec_idx, si))

    # Защитная клетка
    cage_n = 8
    for ci in range(cage_n):
        ca = math.radians(ci * 360 / cage_n)
        cx = ox + math.cos(ca) * (CAGE_R - LR)
        cy = oy + math.sin(ca) * (CAGE_R - LR)
        pipe((cx, cy, z0), (cx, cy, z1), r=CAGE_BAR_R, m=MS, seg=6,
             name="CageV_{}_{}".format(sec_idx, ci))

    # Кольца клетки + радиальные распорки к стволу
    n_rings = int((z1 - z0) / 1.5) + 1
    for ri in range(n_rings):
        ring_z = z0 + ri * 1.5
        if ring_z > z1: ring_z = z1
        torus((ox, oy, ring_z), CAGE_R - LR, CAGE_BAR_R,
              name="CageR_{}_{}".format(sec_idx, int(ring_z)), m=MS, seg=36, rseg=12)
        # Боковые распорки от кольца клетки к стволу (левая + правая)
        for ra in [90, 270]:
            rang = math.radians(az_deg + ra)
            csx = ox + math.cos(rang) * (CAGE_R - LR)
            csy = oy + math.sin(rang) * (CAGE_R - LR)
            pipe((csx, csy, ring_z), (FX+math.cos(rang)*LR*0.6, FY+math.sin(rang)*LR*0.6, ring_z),
                 r=CAGE_BAR_R*0.8, m=MS, seg=6,
                 name="Brkt_{}_{}_{}".format(sec_idx, int(ring_z), ra))
    # Гарантируем кольцо на самом верху (z1) — если ещё не создано
    if z0 + (n_rings - 1) * 1.5 < z1 - 0.01:
        torus((ox, oy, z1), CAGE_R - LR, CAGE_BAR_R,
              name="CageR_{}_{}".format(sec_idx, int(z1)), m=MS, seg=36, rseg=12)
        for ra in [90, 270]:
            rang = math.radians(az_deg + ra)
            csx = ox + math.cos(rang) * (CAGE_R - LR)
            csy = oy + math.sin(rang) * (CAGE_R - LR)
            pipe((csx, csy, z1), (FX+math.cos(rang)*LR*0.6, FY+math.sin(rang)*LR*0.6, z1),
                 r=CAGE_BAR_R*0.8, m=MS, seg=6,
                 name="Brkt_{}_{}_top".format(sec_idx, int(z1), ra))

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

# ═══════ 5. ГОРЕЛКА + ДЕЖУРНЫЕ ГОРЕЛКИ + ПАР + ГАЗОВЫЙ КОЛЛЕКТОР ═══════
BZ = H + 0.3
cyl((FX, FY, BZ), 0.80, 1.0, name="Burner_B", m=MB, seg=26)
cyl((FX, FY, BZ+1.3), 0.45, 2.2, name="Burner_N", m=MB, seg=26)
for j, dz in enumerate([0.5, 1.0, 1.5, 2.0]):
    torus((FX, FY, BZ+0.4+dz*0.8), 0.50, 0.04, name="Bur_R{}".format(j), m=MS, seg=36, rseg=12)
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.10, radius2=0.80, depth=7.0, location=(FX, FY, BZ+6.5))
sm(obj=bpy.context.active_object, m=MF)
bpy.context.active_object.name = "Flame"
bpy.ops.object.shade_smooth()
for a in [0, 90, 180, 270]:
    ang = math.radians(a)
    px = FX + math.cos(ang) * 0.35; py = FY + math.sin(ang) * 0.35
    cyl((px, py, BZ+2.5), 0.05, 1.0, name="Pilot{}".format(a), m=MB, seg=8)

# ДЕЖУРНЫЕ ГОРЕЛКИ — 3 шт. вокруг сопла, постоянное пламя
for da in [60, 180, 300]:
    dang = math.radians(da)
    dpx = FX + math.cos(dang) * 0.60
    dpy = FY + math.sin(dang) * 0.60
    # Корпус дежурной горелки
    cyl((dpx, dpy, BZ+2.0), 0.06, 0.35, name="Stand_Flame_{}".format(da), m=MB, seg=12)
    # Маленький язычок пламени (медный оттенок)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.03, radius2=0.10, depth=1.2,
                                     location=(dpx, dpy, BZ+2.8))
    so = bpy.context.active_object; so.name = "Pilot_Flame_{}".format(da)
    sm(obj=so, m=mat("PilotFlame", (0.95, 0.65, 0.20)))
    bpy.ops.object.shade_smooth()

# Дежурные горелки: газ подаётся изнутри ствола через маленькие патрубки
# (основной сбросной газ идёт внутри ствола — подводится от сепаратора через эстакаду)

# ПАР: внешний стояк вдоль ствола, посекционная окраска как у ствола, крепления-хомуты
# Стояк сзади-слева (азимут ~220°), от уровня эстакады до парового кольца
STEAM_Z = BZ + 0.5          # высота парового кольца
STEAM_R = R + 0.35          # отступ от центра ствола
STEAM_AZ = math.radians(210)  # азимут стояка (сзади-слева)
STEAM_PIPE_R = 0.12
SX0 = FX + math.cos(STEAM_AZ) * STEAM_R
SY0 = FY + math.sin(STEAM_AZ) * STEAM_R
SS_Z = 2.7  # уровень эстакады (SHOE_Z, секция 9) — начало стояка

# Стояк: только от эстакады вверх (нижний конец на эстакаде, не на земле)
pipe((SX0, SY0, SS_Z),  (SX0, SY0, 12.0), r=STEAM_PIPE_R, m=MR, seg=16, name="SteamRise_L")
pipe((SX0, SY0, 12.0), (SX0, SY0, 28.0), r=STEAM_PIPE_R, m=MW, seg=16, name="SteamRise_M")
pipe((SX0, SY0, 28.0), (SX0, SY0, STEAM_Z), r=STEAM_PIPE_R, m=MR, seg=16, name="SteamRise_U")
# Горизонтальная подводка: от стояка (SS_Z) → к эстакаде по Y
pipe((SX0, SY0, SS_Z), (SX0, -7.0, SS_Z), r=STEAM_PIPE_R*0.7, m=MS, seg=12, name="SteamFeed")

# Крепления-хомуты каждые 2 метра (torus вокруг стояка + стержень к стволу)
CLAMP_R = STEAM_PIPE_R * 1.5
# Начинаем от SS_Z + 0.5 (чуть выше joint-а), чтобы не накладываться на стык
for cz in [z/10.0 for z in range(int(SS_Z*10+5), int(STEAM_Z*10), 20)]:  # каждые 2.0м
    # Хомут — torus вокруг стояка
    torus((SX0, SY0, cz), CLAMP_R, 0.012, name="SCL_T_{}".format(int(cz*10)), m=MS, seg=24, rseg=12)
    # Стержень от хомута к стволу
    pipe((SX0+math.cos(STEAM_AZ)*CLAMP_R, SY0+math.sin(STEAM_AZ)*CLAMP_R, cz),
         (FX+math.cos(STEAM_AZ)*R, FY+math.sin(STEAM_AZ)*R, cz),
         r=0.012, m=MS, seg=6, name="SCL_B_{}".format(int(cz*10)))

# Кольцевой паровой коллектор вокруг горелки
STEAM_RING_R = 0.62
for ring_h in [STEAM_Z, STEAM_Z+0.6]:
    torus((FX, FY, ring_h), STEAM_RING_R, 0.04, name="SteamRing_{}".format(int(ring_h*10)), m=MS, seg=48, rseg=12)
    # Соединительная трубка от стояка к кольцу
    pipe((SX0, SY0, ring_h), (FX-STEAM_RING_R*math.cos(STEAM_AZ+math.pi), FY-STEAM_RING_R*math.sin(STEAM_AZ+math.pi), ring_h),
         r=0.04, m=MS, seg=10, name="SteamBrg_{}".format(int(ring_h*10)))

# Паровые форсунки (сопла) — 8 шт. по окружности, направлены в зону горения
for fi in range(8):
    fa = math.radians(fi * 45)
    fx = FX + math.cos(fa) * STEAM_RING_R
    fy = FY + math.sin(fa) * STEAM_RING_R
    # Короткая трубка-форсунка, направленная внутрь к пламени
    pipe((fx, fy, STEAM_Z+0.3), (FX+math.cos(fa)*0.35, FY+math.sin(fa)*0.35, STEAM_Z+0.3),
         r=0.025, m=MS, seg=8, name="Nozzle{}".format(fi))

# ═══════ 6. ДАТЧИКИ НА СТВОЛЕ ═══════
# Датчик давления: корпус на кронштейне + стержень к стволу
def pressure_sensor(loc, name):
    # Направление к стволу: от датчика к поверхности (центр ствола (FX,FY), радиус R)
    dx, dy = loc[0] - FX, loc[1] - FY
    dist = math.sqrt(dx*dx + dy*dy)
    ux, uy = dx/dist, dy/dist  # единичный вектор от ствола к датчику
    stem_r = 0.015
    cube((loc[0], loc[1], loc[2]-0.08), (0.06, 0.06, 0.04), name=name+"_Brkt", m=MS)
    # Стержень от кронштейна к поверхности ствола
    pipe((FX + ux*R, FY + uy*R, loc[2]-0.08), (loc[0]-ux*0.06, loc[1]-uy*0.06, loc[2]-0.08),
         r=stem_r, m=MS, seg=8, name=name+"_Stem")
    cyl(loc, 0.05, 0.10, name=name+"_Body", m=MY, seg=12)
    cyl((loc[0], loc[1], loc[2]+0.07), 0.03, 0.04, name=name+"_Top", m=MM, seg=10)

# Датчик температуры: длинный зонд в гильзе + стержень к стволу
def temp_sensor(loc, name):
    dx, dy = loc[0] - FX, loc[1] - FY
    dist = math.sqrt(dx*dx + dy*dy)
    ux, uy = dx/dist, dy/dist
    stem_r = 0.015
    cube((loc[0], loc[1], loc[2]-0.06), (0.05, 0.05, 0.03), name=name+"_Brkt", m=MS)
    # Стержень от кронштейна к поверхности ствола
    pipe((FX + ux*R, FY + uy*R, loc[2]-0.06), (loc[0]-ux*0.05, loc[1]-uy*0.05, loc[2]-0.06),
         r=stem_r, m=MS, seg=8, name=name+"_Stem")
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
# Подробная модель: эллиптические днища, седловидные опоры, площадка с ограждениями,
# лестница с клеткой, патрубки с фланцами, люк, уровнемер, манометр, предупреждающие полосы
# Координаты (используются также в секциях 9, 9a, 9c):
SX, SY, SZ, SL, SR = -7.0, -4.5, 1.6, 7.5, 1.4
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from separator_new import create_separator
create_separator(bpy, math, MW, MS, MY, MM, MN, MR)

# ═══════ 8. ДРЕНАЖ ═══════
DX, DY = -11.5, -5.0
cube((DX, DY, 0.2), (0.6, 0.6, 0.2), name="Drn_Ft", m=MN)
cyl((DX, DY, 1.6), 0.45, 2.4, name="Drain", m=MS, seg=22)
cyl((DX, DY, 2.9), 0.45, 0.10, name="Drain_Top", m=MS, seg=22)
cyl((DX-0.5, DY, 2.0), 0.07, 0.35, name="Drain_In", m=MY, seg=10)

# Датчик уровня на дренаже
pipe((DX+0.6, DY, 0.5), (DX+0.6, DY, 2.7), r=0.025, m=MS, seg=8, name="Drn_LG")
cyl((DX+0.6, DY, 2.7), 0.04, 0.03, name="Drn_LGHead", m=MM, seg=10)

# ═══════ 9. ТРУБОПРОВОДНАЯ ЭСТАКАДА (УСИЛЕННАЯ) ═══════
RY = -7.0
RACK_SPAN = 3     # int — для range()
BEAM_Z = 2.6        # верх балки (centre + half scale)
COL_W = 0.12         # толщина стоек УВЕЛИЧЕНА
SHOE_Z = BEAM_Z + 0.08
FLARE_Z = SHOE_Z + 0.17 + 0.03
PURGE_Z = SHOE_Z + 0.12 + 0.03

# Фундаменты (крупные, заметные)
for rx in range(-12, 4, RACK_SPAN):
    rx = float(rx)
    for sy in [RY-0.5, RY+0.5]:
        cube((rx, sy, 0.20), (0.30, 0.30, 0.20), name="RackFt_{}_{}".format(int(rx), "L" if sy<RY else "R"), m=MN)

# П-образные рамы — КРАСНЫЕ стойки, СЕРЫЕ балки
for rx in range(-12, 4, RACK_SPAN):
    rx = float(rx)
    for sy in [RY-0.5, RY+0.5]:
        # Стойка — толстая и красная
        cube((rx, sy, BEAM_Z/2), (COL_W/2, COL_W/2, BEAM_Z/2), name="RackCol_{}_{}".format(int(rx), "L" if sy<RY else "R"), m=MR)
    # Ригель — широкая балка
    cube((rx, RY, BEAM_Z), (COL_W/2, 0.50, 0.06), name="RackBeam_{}".format(int(rx)), m=MS)

# Седельные опоры (заметные блоки)
for rx in range(-12, 4, RACK_SPAN):
    cube((float(rx), RY, SHOE_Z-0.02), (0.04, 0.18, 0.06), name="FlareShoe_{}".format(int(rx)), m=MW)

# СБРОСНОЙ ГАЗ (FlareGas): сепаратор → эстакада → ствол (горизонтально, прямой угол)
# От сепаратора горизонтально до эстакады, спуск у эстакады, дальше горизонтально до ствола
route([
    (SX+2.0, SY, SZ+SR+0.4),       # 0: выход из сепаратора (верхний патрубок, z≈3.4)
    (SX+2.0, RY,  SZ+SR+0.4),       # 1: горизонтально к эстакаде (на том же уровне)
    (SX+2.0, RY,  FLARE_Z),         # 2: вертикально вниз на уровень эстакады
    (FX,     RY,  FLARE_Z),         # 3: горизонтально до X=ствола
    (FX,     FY,  FLARE_Z),         # 4: к стволу по Y
], r=0.13, m=MY, seg=14, name="FlareGas")

# ПРОДУВОЧНЫЙ ГАЗ (Purge): подаётся через внутренний стояк, отдельная наружная труба не нужна

# КОНДЕНСАТ: сбрасывается внутри сепаратора, отдельная труба не нужна
# (жидкость отводится через дренажный патрубок Sep_Drain на корпусе)

# ПАР (Steam): магистраль скрыта внутри ствола, снаружи только паровое кольцо + форсунки
# Внешняя паровая труба не нужна — пар подаётся по внутреннему стояку
# (см. секцию 5 — SteamRing + Nozzles)

# Опорная стойка под паровую подводку SteamFeed
cube((SX0, -7.0, SS_Z/2), (0.06, 0.06, SS_Z/2), name="SteamFeed_Support", m=MR)

# (датчик расхода убран вместе с продувочной линией)

# ═══════ 9b. ДАТЧИКИ НА ОПОРЫ ЭСТАКАДЫ ═══════
# Вибродатчики состояния на стойках П-образных рам (по 1 на раму, левая стойка)
for vs_x in [-12.0, -6.0, 0.0]:
    vs_y = RY - 0.5  # левая стойка
    vs_z = 1.2       # высота от земли
    cube((vs_x+0.10, vs_y, vs_z), (0.015, 0.03, 0.03), name="VibS_Brkt_{}".format(int(vs_x)), m=MS)
    cyl((vs_x+0.10, vs_y, vs_z+0.03), 0.025, 0.05, name="VibS_Body_{}".format(int(vs_x)), m=MR, seg=8)
    cyl((vs_x+0.10, vs_y, vs_z+0.07), 0.018, 0.025, name="VibS_Head_{}".format(int(vs_x)), m=MM, seg=8)

# ═══════ 9c. ФУНДАМЕНТНАЯ ПЛИТА ПОД СЕПАРАТОР ═══════
# Бетонная плита под всем сепаратором, выступает за габариты
cube((SX, SY, 0.07), (SL/2+0.8, SR+0.6, 0.06), name="Sep_Foundation", m=MN)

# ═══════ 10. СВЕТ ═══════
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
print("✅ v14 сохранена + рендер: {}".format(render_path))
