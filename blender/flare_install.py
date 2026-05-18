"""
flare_install.py v4 — ЦВЕТНАЯ low-poly модель факельной установки НПЗ.
Cycles + эмиссионные материалы + яркое небо + зелёная земля.
Все аргументы — keyword, никаких позиционных f-строк.
"""

import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ════════════════════ МАТЕРИАЛЫ ════════════════════
def mkmat(name, base_rgb, emit_rgb=None, emit_str=0.35, rough=0.55, metal=0.1):
    if emit_rgb is None: emit_rgb = base_rgb
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*base_rgb, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*emit_rgb, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emit_str
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return mat

MR = mkmat("Red",       (0.85, 0.15, 0.10), emit_str=0.40)
MW = mkmat("White",     (0.92, 0.91, 0.87), emit_str=0.30)
MS = mkmat("Steel",     (0.62, 0.64, 0.68), metal=0.70, rough=0.30)
MY = mkmat("Yellow",    (0.95, 0.82, 0.05), emit_str=0.45)
MB = mkmat("Burner",    (0.30, 0.32, 0.36), metal=0.80, rough=0.25, emit_str=0.20)
MF = mkmat("Flame",     (1.00, 0.42, 0.02), (1.0, 0.55, 0.05), emit_str=3.5)
MC = mkmat("Cable",     (0.15, 0.17, 0.20), metal=0.60, rough=0.40, emit_str=0.10)
MN = mkmat("Concrete",  (0.65, 0.63, 0.58), rough=0.80, emit_str=0.10)
MG = mkmat("Ground",    (0.28, 0.48, 0.18), emit_str=0.12)
MM = mkmat("Sensor",    (0.08, 0.10, 0.18), metal=0.65, rough=0.30, emit_str=0.20)

def set_mat(obj, m):
    obj.data.materials.clear(); obj.data.materials.append(m)

# ════════════════════ ПРИМИТИВЫ ════════════════════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.active_object
    o.name = name; o.scale = scale; set_mat(o, m); return o

def sphere(loc, r, name="S", m=MM, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=8, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

def torus(loc, R, r, name="T", m=MS, seg=20, rseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; set_mat(o, m); return o

def pipe(p1, p2, r=0.04, m=MS, seg=10, name="P"):
    dx,dy,dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    th = math.acos(dz/L) if L>0 else 0
    ph = math.atan2(dy,dx) if (dx!=0 or dy!=0) else 0
    return cyl(mid, r, L, rot=(th,0,ph), name=name, m=m, seg=seg)

# ── ЗЕМЛЯ ──
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,-2,-0.05))
set_mat(bpy.context.active_object, MG); bpy.context.active_object.name = "Ground"
cube((0,-2,0.03), (17,12,0.03), name="Pad", m=MN)

# ════════════════════ 1. СТВОЛ ════════════════════
H, R, FX, FY = 38.0, 1.1, 0.0, -1.0
cyl((FX,FY,6.1),  R, 12.0, name="Stack_Lower", m=MR, seg=30)
cyl((FX,FY,20.1), R, 16.0, name="Stack_Mid",   m=MW, seg=30)
cyl((FX,FY,33.1), R, 10.0, name="Stack_Upper", m=MR, seg=30)
cyl((FX,FY,0.25), 1.35, 0.5, name="Stack_Base", m=MS, seg=30)

# ════════════════════ 2. ПЛАТФОРМЫ ════════════════════
PR, RH, POST_R = 2.0, 0.05, 0.04
for i, pz in enumerate([4.0, 14.0, 29.5]):
    cyl((FX,FY,pz), PR, 0.15, name="Plat"+str(i)+"_Deck", m=MS, seg=36)
    for rh in [0.45, 1.0, 1.4]:
        torus((FX,FY,pz+rh), PR-0.18, RH, name="Plat"+str(i)+"_R"+str(rh), m=MS, seg=36, rseg=6)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx, sy = FX+math.cos(ang)*(PR-0.22), FY+math.sin(ang)*(PR-0.22)
        cyl((sx,sy,pz+0.85), POST_R, 1.5, name="Plat"+str(i)+"_P"+str(a), m=MS, seg=6)

# ════════════════════ 3. ВИНТОВАЯ ЛЕСТНИЦА ════════════════════
SR, STEPS, TURNS = R+0.70, 65, 4.0
SZ0, SZ1 = 0.6, 37.5
SH = (SZ1-SZ0)/STEPS
SA = (TURNS*2*math.pi)/STEPS
for i in range(STEPS):
    a = i*SA; z = SZ0+i*SH
    cx, cy = FX+math.cos(a)*SR, FY+math.sin(a)*SR
    s = cube((cx,cy,z+0.06), (0.65,0.04,0.06), name="Step"+str(i), m=MS)
    s.rotation_euler = (0,0,a+math.pi/2)
IR, OR = R+0.28, R+0.93
for i in range(0, STEPS, 4):
    a = i*SA; z = SZ0+i*SH
    for rr,side in [(IR,"I"),(OR,"O")]:
        sx, sy = FX+math.cos(a)*rr, FY+math.sin(a)*rr
        cyl((sx,sy,z+0.55), 0.025, 1.1, name="RP"+str(i)+"_"+side, m=MS, seg=6)

# ════════════════════ 4. ОТТЯЖКИ (тросы к земле) ════════════════════
# 3 высоты крепления к стволу × 4 направления = 12 тросов
# Трос идёт от точки (FX,FY,height) до анкера (ax,ay,0.4) на земле
GH = [12.0, 23.0, 33.0]
GA = [45, 135, 225, 315]
GR = 15.0  # расстояние анкеров от ствола

for h in GH:
    for ga in GA:
        ang = math.radians(ga)
        ax, ay = FX+math.cos(ang)*GR, FY+math.sin(ang)*GR
        # Бетонный анкерный блок на земле (z=0.2)
        cube((ax,ay,0.2), (0.4,0.4,0.2), name="Anc_"+str(int(h))+"_"+str(ga), m=MN)
        # Трос: от ствола на высоте h → к верху анкера (z=0.4)
        pipe((FX,FY,h), (ax,ay,0.5), r=0.025, m=MC, seg=8, name="Guy_"+str(int(h))+"_"+str(ga))

# ════════════════════ 5. ГОРЕЛКА + ПЛАМЯ ════════════════════
BZ = H+0.3
cyl((FX,FY,BZ), 0.80, 1.0, name="Burner_Base", m=MB, seg=26)
cyl((FX,FY,BZ+1.3), 0.45, 2.2, name="Burner_Nozzle", m=MB, seg=26)
for j, dz in enumerate([0.5, 1.0, 1.5, 2.0]):
    torus((FX,FY,BZ+0.4+dz*0.8), 0.50, 0.04, name="Bur_R"+str(j), m=MS, seg=26, rseg=6)
# Пламя — крупнее
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.10, radius2=0.80, depth=7.0,
                                 location=(FX,FY,BZ+6.5))
set_mat(bpy.context.active_object, MF); bpy.context.active_object.name = "Flame"
# Пилоты — крупнее
for a in [0,90,180,270]:
    ang = math.radians(a)
    px, py = FX+math.cos(ang)*0.35, FY+math.sin(ang)*0.35
    cyl((px,py,BZ+2.5), 0.05, 1.0, name="Pilot"+str(a), m=MB, seg=8)

# ════════════════════ 6. СЕПАРАТОР ════════════════════
SX, SY, SZ, SLEN, SRAD = -6.5, -4.0, 1.6, 7.5, 1.4
for sx in [SX-2.5, SX+2.5]:
    cube((sx,SY,0.3), (0.45,0.9,0.3), name="Sep_Ft", m=MN)
    cyl((sx,SY,0.75), 0.20, 0.7, name="Sep_Saddle", m=MS, seg=14)
sb = cyl((SX,SY,SZ), SRAD, SLEN, name="Sep_Body", m=MW, seg=30)
sb.rotation_euler = (0, math.radians(90), 0)
for dx in [-SLEN/2, SLEN/2]:
    sphere((SX+dx,SY,SZ), SRAD, name="Sep_Cap", m=MS, seg=16)
cyl((SX-2.0,SY,SZ+SRAD+0.3), 0.16, 0.5, name="Sep_In", m=MS, seg=14)
cyl((SX+2.0,SY,SZ+SRAD+0.3), 0.13, 0.4, name="Sep_Vent", m=MS, seg=14)
cyl((SX+0.8,SY,SZ-SRAD-0.4), 0.11, 0.6, name="Sep_Drain", m=MS, seg=14)
# Лестница-клетка
LX, LY = SX-SLEN/2-0.9, SY-0.5
for si in range(9):
    cube((LX,LY,0.5+si*0.50), (0.28,0.02,0.02), name="SepL"+str(si), m=MS)
for dx_s, dy_s in [(-0.22,-0.15),(0.22,-0.15),(-0.22,0.15),(0.22,0.15)]:
    cyl((LX+dx_s,LY+dy_s,2.5), 0.028, 4.5, name="SepCage", m=MS, seg=6)
sphere((SX,SY-0.8,SZ+SRAD+0.5), 0.14, name="SepS_L", m=MM)
sphere((SX-2.5,SY-0.4,SZ+SRAD+0.5), 0.12, name="SepS_P", m=MM)
sphere((SX-0.5,SY-1.3,SZ+SRAD+0.5), 0.10, name="SepS_T", m=MR)

# ════════════════════ 7. ДРЕНАЖНАЯ ЁМКОСТЬ ════════════════════
DX, DY = -10.5, -4.5
cube((DX,DY,0.2), (0.6,0.6,0.2), name="Drn_Ft", m=MN)
cyl((DX,DY,1.6), 0.45, 2.4, name="Drain", m=MS, seg=22)
sphere((DX,DY,2.9), 0.45, name="Drain_Top", m=MS, seg=16)
cyl((DX-0.5,DY,2.0), 0.07, 0.35, name="Drain_In", m=MY, seg=10)

# ════════════════════ 8. ТРУБОПРОВОДЫ ════════════════════
RY, PZ = -5.5, 2.8
for rx in [-10,-7,-4,-1,2]:
    cyl((rx,RY,1.3), 0.06, 2.6, name="RackLeg", m=MS, seg=10)
pipe((-11,RY,PZ),      (3,RY,PZ),       r=0.17, m=MY, seg=14, name="GasMain")
pipe((-8,RY,PZ+0.35),  (4,RY,PZ+0.35),  r=0.12, m=MY, seg=12, name="GasSec")
pipe((SX+2.0,SY,SZ+SRAD+0.4), (SX+2.0,SY,3.5),    r=0.13, m=MY, seg=12, name="S2S_V")
pipe((SX+2.0,SY,3.5),         (FX+0.7,FY,3.5),     r=0.13, m=MY, seg=12, name="S2S_H")
pipe((FX+0.7,FY,3.5),         (FX,FY,5.5),          r=0.13, m=MY, seg=12, name="S2S_R")
pipe((SX+0.8,SY,SZ-SRAD-0.5), (DX-0.5,DY,SZ-SRAD-0.5), r=0.07, m=MS, seg=8, name="Cond")
pipe((DX-0.5,DY,SZ-SRAD-0.5), (DX-0.5,DY,2.0),          r=0.07, m=MS, seg=8, name="CondR")
pipe((-12,-7,5.5),      (-5,-6,5.5),                r=0.08, m=MS, seg=10, name="Steam1")
pipe((-5,-6,5.5),       (FX-1.2,FY-1.8,5.5),        r=0.08, m=MS, seg=10, name="Steam2")
pipe((FX-1.2,FY-1.8,5.5),(FX-0.8,FY-0.5,26.0),      r=0.06, m=MS, seg=8, name="SteamR")

# ════════════════════ 9. ДАТЧИКИ ════════════════════
sphere((FX+1.4,FY,2.5), 0.12, name="S_Tfl", m=MM)
sphere((FX-1.4,FY,2.5), 0.12, name="S_Ppg", m=MM)
sphere((FX+1.4,FY,11.0), 0.10, name="S_Qpg", m=MM)
sphere((FX-1.4,FY,21.0), 0.12, name="S_Stm", m=MM)
sphere((FX+1.5,FY,5.5), 0.16, name="Ind_G", m=MF)
sphere((FX-1.5,FY,5.5), 0.16, name="Ind_R", m=MR)

# ════════════════════ 10. СВЕТ ════════════════════
bpy.ops.object.light_add(type='SUN', location=(20,-15,30))
bpy.context.active_object.data.energy = 8.0
bpy.context.active_object.data.angle = math.radians(3)
bpy.ops.object.light_add(type='AREA', location=(-15,5,10))
bpy.context.active_object.data.energy = 600; bpy.context.active_object.data.size = 15
bpy.ops.object.light_add(type='AREA', location=(5,15,8))
bpy.context.active_object.data.energy = 400; bpy.context.active_object.data.size = 12

# ════════════════════ 11. КАМЕРА ════════════════════
bpy.ops.object.camera_add(location=(24,-22,16))
cam = bpy.context.active_object; cam.data.lens = 18
cam.location = Vector((24,-22,16))
tgt = Vector((-3.5,-2.5,15))
cam.rotation_euler = (tgt-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera = cam

# ════════════════════ 12. МИР (голубое небо) ════════════════════
w = bpy.data.worlds['World']; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.35,0.60,0.95,1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 2.5

# ════════════════════ 13. EEVEE ════════════════════
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.eevee.taa_render_samples = 16
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.view_settings.exposure = 3.0
bpy.context.scene.view_settings.gamma = 1.5

# ── Сохранить ──
blend_path = "/home/pomadoro/projects/flare-predictor/blender/flare_install.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# ── Рендер прямо здесь ──
bpy.context.scene.render.filepath = "/home/pomadoro/projects/flare-predictor/blender/0001.png"
bpy.ops.render.render(write_still=True)
print(f"✅ v5 EEVEE рендер сохранён")
