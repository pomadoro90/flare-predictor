"""Тест: поиск правильной ориентации колена"""
import bpy, math, os
from mathutils import Vector, Matrix

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Колено: порты в (−R,0,0) и (0,0,+R)
import bmesh
R_elbow, r_elbow = 0.3, 0.2
mesh = bpy.data.meshes.new('elbow90')
elbow = bpy.data.objects.new('elbow90', mesh)
bpy.context.collection.objects.link(elbow)

bm = bmesh.new()
rings = []
for i in range(11):
    u = (i/10)*math.pi/2
    ring = []
    for j in range(8):
        v = (j/8)*2*math.pi
        x = -(R_elbow+r_elbow*math.cos(v))*math.cos(u)
        y = r_elbow*math.sin(v)
        z = (R_elbow+r_elbow*math.cos(v))*math.sin(u)
        ring.append(bm.verts.new((x,y,z)))
    rings.append(ring)
bm.verts.ensure_lookup_table()
for i in range(10):
    for j in range(8):
        jn = (j+1)%8
        bm.faces.new((rings[i][j],rings[i][jn],rings[i+1][jn],rings[i+1][j]))
bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Трубы
def tube(p1,p2,r,name):
    d=Vector(p2)-Vector(p1); L=d.length
    mid=(Vector(p1)+Vector(p2))/2
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=L,location=mid)
    o=bpy.context.active_object; o.name=name
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return o

pipe_r=0.13
R=pipe_r*1.5
loc=Vector((4,0,0))
tube((1,0,0),(loc.x-R,0,0),pipe_r,"PipeIn")
tube((loc.x,0,R),(loc.x,0,5),pipe_r,"PipeOut")
tube((loc.x+R,0,0),(7,0,0),pipe_r,"PipeCont")

# Позиционируем
v_in=Vector((1,0,0)); v_out=Vector((0,0,1))
scale=pipe_r/r_elbow
elbow.scale=(scale,scale,scale)
mx=v_in; mz=v_out
my=mz.cross(mx)
if my.length<1e-6: my=Vector((0,1,0))
my.normalize()
mx=my.cross(mz)
elbow.matrix_world=Matrix.Translation(loc)@Matrix((mx,my,mz)).to_4x4()

# Проверка
Rs=R_elbow*scale
c_in=elbow.matrix_world@Vector((-Rs,0,0))
c_out=elbow.matrix_world@Vector((0,0,Rs))
n_in=elbow.matrix_world.to_3x3()@Vector((-1,0,0))
n_out=elbow.matrix_world.to_3x3()@Vector((0,0,-1))
e_in=Vector((loc.x-R,0,0)); e_out=Vector((loc.x,0,R))
ok=(c_in-e_in).length<0.005 and (n_in+v_in).length<0.005 and (c_out-e_out).length<0.005 and (n_out+v_out).length<0.005
print(f'IN pos=({c_in.x:.3f},{c_in.y:.3f},{c_in.z:.3f}) exp=({e_in.x:.3f},{e_in.y:.3f},{e_in.z:.3f})')
print(f'OUT pos=({c_out.x:.3f},{c_out.y:.3f},{c_out.z:.3f}) exp=({e_out.x:.3f},{e_out.y:.3f},{e_out.z:.3f})')
print(f'{"CORRECT" if ok else "WRONG"}')
if ok:
    ad=os.path.join(os.path.expanduser('~'),'projects','flare-predictor','assets')
    os.makedirs(ad,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ad,'elbow.blend'))
    print(f'Saved {ad}/elbow.blend')
    s=bpy.context.scene; s.render.engine='BLENDER_EEVEE'
    w=bpy.data.worlds.new('W'); s.world=w; w.use_nodes=True
    w.node_tree.nodes['Background'].inputs[0].default_value=(0.05,0.05,0.05,1)
    bpy.ops.object.light_add(type='SUN',location=(10,5,10))
    bpy.context.active_object.data.energy=3
    cam=bpy.data.cameras.new('Cam'); co=bpy.data.objects.new('Cam',cam)
    bpy.context.collection.objects.link(co)
    co.location=(6,-4,3); co.data.lens=35
    co.rotation_euler=(Vector((4,0,2))-co.location).to_track_quat('-Z','Y').to_euler()
    s.camera=co; s.render.filepath='/tmp/elbow_test.png'
    bpy.ops.render.render(write_still=True)
    print('RENDERED /tmp/elbow_test.png')
