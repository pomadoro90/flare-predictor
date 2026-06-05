"""
Detailed horizontal separator (knockout drum) for flare-predictor project.
Blender 4.0.2 compatible, low-poly (~2000-3000 faces).
Coordinate system matches flare_install.py: SX=-7.0, SY=-4.5, SZ=2.8, SL=7.5, SR=1.4.

Function: create_separator(bpy, math, MW, MS, MY, MM, MN, MR)
"""

import math


def create_separator(bpy, math_mod, MW, MS, MY, MM, MN, MR):
    """
    Creates a complete horizontal separator vessel with all fittings.
    
    Parameters:
        bpy: Blender Python API module
        math_mod: Python math module (may be different from built-in in bpy context)
        MW: white/light grey material for body
        MS: steel material for structure
        MY: yellow material for indicators
        MM: dark material for sensors/gauges
        MN: concrete material for bases
        MR: red material for warnings
    """
    # Use the passed math module (or fallback to built-in)
    if math_mod is None:
        math_mod = math
    
    from mathutils import Vector

    # ─── Constants ────────────────────────────────────────────
    SX, SY, SZ, SL, SR = -10.0, -4.5, 2.8, 7.5, 1.4
    GROUND_Z = 0.0

    # ─── Helper functions ─────────────────────────────────────
    def assign_mat(obj, mat):
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    def make_circle_disk(loc, radius, normal_axis='Y', name="Disk",
                         material=MS, segs=48):
        """Create a flat circle mesh facing along the specified axis."""
        # Create in XY plane (normal +Z), then rotate to desired axis
        bpy.ops.mesh.primitive_circle_add(
            vertices=segs, radius=radius, fill_type='NGON',
            location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_flat()
        if normal_axis == 'Y':
            obj.rotation_euler = (math_mod.radians(-90), 0, 0)
        elif normal_axis == 'X':
            obj.rotation_euler = (0, math_mod.radians(90), 0)
        elif normal_axis == 'neg_X':
            obj.rotation_euler = (0, math_mod.radians(-90), 0)
        # else Z: no rotation needed
        obj.location = loc
        return obj

    def make_cylinder(loc, radius, depth, rot=(0, 0, 0), name="Cyl",
                      material=MS, segs=20):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=segs, radius=radius, depth=depth,
            location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_box(loc, scale, name="Box", material=MS):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_torus(loc, major_r, minor_r, name="Torus",
                   material=MS, m_segs=20, r_segs=8):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=major_r, minor_radius=minor_r,
            location=loc, major_segments=m_segs, minor_segments=r_segs)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_uvsphere(loc, radius, name="Sphere", material=MS, segs=16):
        rings = max(8, segs // 2)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius, location=loc,
            segments=segs, ring_count=rings)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_pipe(p1, p2, radius=0.04, material=MS, segs=8, name="Pipe"):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        length = math_mod.sqrt(dx*dx + dy*dy + dz*dz)
        if length < 0.001:
            return None
        mid = ((p1[0] + p2[0]) / 2,
               (p1[1] + p2[1]) / 2,
               (p1[2] + p2[2]) / 2)
        obj = make_cylinder(mid, radius, length, name=name,
                            material=material, segs=segs)
        direction = Vector((dx, dy, dz))
        obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        return obj

    def make_disc_flange(end_pos, direction_vec, radius, name_prefix,
                         flange_scale=1.5, material=MS):
        """Create a blind flange assembly: bored flange, cap, nuts, studs."""
        flange_disc_radius = radius * 1.75
        flange_body_radius = radius * 1.9
        bore_radius = radius * 1.05
        bolt_circle_radius = flange_disc_radius * 0.82
        bolt_radius = 0.012
        nut_radius = bolt_radius * 1.8
        nut_depth = bolt_radius * 1.5
        stud_radius = bolt_radius * 0.6
        stud_protrusion = bolt_radius * 0.8
        n_bolts = max(8, int(flange_disc_radius / (bolt_radius * 2.5)))
        bottom_flange_thickness = 0.04
        blind_cap_thickness = 0.05
        bore_depth = bottom_flange_thickness
        raised_face_radius = radius * 1.1
        raised_face_thickness = 0.006
        bolt_hole_depth = bottom_flange_thickness + blind_cap_thickness + 0.004

        direction = Vector(direction_vec).normalized()
        rotation = direction.to_track_quat('Z', 'Y').to_euler()

        def point_along(dist, offset=None):
            base = Vector(end_pos) + direction * dist
            if offset is not None:
                base += offset
            return (base.x, base.y, base.z)

        bottom_flange_dist = bottom_flange_thickness / 2
        blind_cap_dist = bottom_flange_thickness + blind_cap_thickness / 2
        cap_top_dist = bottom_flange_thickness + blind_cap_thickness
        bore_dist = bottom_flange_thickness - bore_depth / 2

        # --- Bottom flange disc: flat shading for crisp 90° edges ---
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48, radius=flange_body_radius,
            depth=bottom_flange_thickness,
            location=point_along(bottom_flange_dist))
        bottom_flange = bpy.context.active_object
        bottom_flange.name = name_prefix + "_BottomFlange"
        bottom_flange.rotation_euler = rotation
        assign_mat(bottom_flange, material)
        # Flat shading = no smooth vertex normals = sharp 90° edges
        bpy.ops.object.shade_flat()

        bore = make_cylinder(
            point_along(bore_dist), bore_radius, bore_depth,
            name=name_prefix + "_BottomFlangeBore", material=MM, segs=24)
        bore.rotation_euler = rotation

        # --- Blind cap disc: flat shading for crisp 90° edges ---
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48, radius=flange_body_radius,
            depth=blind_cap_thickness,
            location=point_along(blind_cap_dist))
        blind_cap = bpy.context.active_object
        blind_cap.name = name_prefix + "_BlindCap"
        blind_cap.rotation_euler = rotation
        assign_mat(blind_cap, material)
        bpy.ops.object.shade_flat()

        raised_face = make_torus(
            point_along(cap_top_dist + raised_face_thickness / 2),
            raised_face_radius, raised_face_thickness,
            name=name_prefix + "_RaisedFaceRing", material=material,
            m_segs=32, r_segs=8)
        raised_face.rotation_euler = rotation

        reference = Vector((0, 0, 1))
        if abs(direction.dot(reference)) > 0.95:
            reference = Vector((0, 1, 0))
        local_x = direction.cross(reference).normalized()
        local_y = direction.cross(local_x).normalized()

        for i in range(n_bolts):
            angle = i * 2 * math_mod.pi / n_bolts
            offset = (local_x * (math_mod.cos(angle) * bolt_circle_radius) +
                      local_y * (math_mod.sin(angle) * bolt_circle_radius))

            hole = make_cylinder(
                point_along(bolt_hole_depth / 2 - 0.002, offset),
                bolt_radius * 0.9, bolt_hole_depth,
                name=name_prefix + "_BoltHole_" + str(i),
                material=MM, segs=12)
            hole.rotation_euler = rotation

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6, radius=nut_radius, depth=nut_depth,
                location=point_along(cap_top_dist + nut_depth / 2, offset),
                rotation=rotation)
            nut = bpy.context.active_object
            nut.name = name_prefix + "_FlangeNut_" + str(i)
            assign_mat(nut, material)
            nut.rotation_euler = rotation
            bpy.ops.object.shade_flat()

            stud_dist = cap_top_dist + nut_depth + stud_protrusion / 2
            stud = make_cylinder(
                point_along(stud_dist, offset), stud_radius,
                stud_protrusion,
                name=name_prefix + "_Stud_" + str(i),
                material=material, segs=12)
            stud.rotation_euler = rotation
            make_uvsphere(
                point_along(cap_top_dist + nut_depth + stud_protrusion, offset),
                stud_radius,
                name=name_prefix + "_StudTop_" + str(i),
                material=material, segs=12)

    def make_nozzle(pos, radius, length, direction_vec, name_prefix,
                    flange_scale=1.5, flange_r=0.04, material=MS):
        """Create a nozzle cylinder + flat bolted flange pointing in direction_vec."""
        dz = direction_vec
        end_pos = (pos[0] + dz[0] * length,
                   pos[1] + dz[1] * length,
                   pos[2] + dz[2] * length)
        mid_pos = ((pos[0] + end_pos[0]) / 2,
                   (pos[1] + end_pos[1]) / 2,
                   (pos[2] + end_pos[2]) / 2)
        # Cylinder
        cyl_obj = make_cylinder(mid_pos, radius, length,
                                name=name_prefix + "_Nozzle",
                                material=material, segs=12)
        direction = Vector(dz)
        cyl_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        make_disc_flange(end_pos, dz, radius, name_prefix,
                         flange_scale=flange_scale, material=material)
        return cyl_obj

    def make_polyline(points, radius=0.02, material=MS, segs=8,
                      name="Polyline"):
        if len(points) < 2:
            return None
        pipe_objects = []
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            length = (dx*dx + dy*dy + dz*dz) ** 0.5
            if length < 0.001:
                continue
            mid = ((p1[0] + p2[0]) / 2,
                   (p1[1] + p2[1]) / 2,
                   (p1[2] + p2[2]) / 2)
            obj = make_cylinder(
                mid, radius, length,
                name=name + "_seg_" + str(i),
                material=material, segs=segs)
            direction = Vector((dx, dy, dz))
            obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
            pipe_objects.append(obj)
        if not pipe_objects:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = pipe_objects[0]
        for obj in pipe_objects:
            obj.select_set(True)
        bpy.ops.object.join()
        joined = bpy.context.active_object
        joined.name = name
        joined.data.name = name + "_data"
        # Merge overlapping vertices at segment junctions and recalculate normals
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        bpy.ops.object.select_all(action='DESELECT')
        return joined

    def make_curve_tube(points, radius=0.02, material=MS,
                        name="CurveTube"):
        if len(points) < 2:
            return None
        curve = bpy.data.curves.new(name + "_data", type='CURVE')
        curve.dimensions = '3D'
        curve.fill_mode = 'FULL'
        curve.bevel_depth = radius
        curve.bevel_resolution = 8
        curve.resolution_u = 64

        spline = curve.splines.new(type='POLY')
        spline.points.add(len(points) - 1)
        for point, coord in zip(spline.points, points):
            point.co = (coord[0], coord[1], coord[2], 1.0)

        obj = bpy.data.objects.new(name, curve)
        bpy.context.collection.objects.link(obj)
        assign_mat(obj, material)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)
        return obj

    # ═══════════════════════════════════════════════════════════
    # 1. MAIN BODY
    # ═══════════════════════════════════════════════════════════
    # Horizontal cylinder (rotated to X-axis)
    body = make_cylinder((SX, SY, SZ), SR, SL,
                         rot=(0, math_mod.radians(90), 0),
                         name="Sep_Body", material=MW, segs=30)

    # Elliptical heads at both ends (elongated UV hemispheres)
    head_scale_x = 0.6  # elliptical head depth ~0.6 * SR
    vessel_parts = [body]
    for side_label, x_offset in [("L", -SL / 2), ("R", SL / 2)]:
        head = make_uvsphere(
            (SX + x_offset, SY, SZ), SR,
            name="Sep_Head_Temp_" + side_label,
            material=MW, segs=20)
        head.scale = (head_scale_x, 1.0, 1.0)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = head
        head.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        threshold = 0.01 * SR
        for vertex in head.data.vertices:
            if side_label == "L":
                vertex.select = vertex.co.x > threshold
            else:
                vertex.select = vertex.co.x < -threshold

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        vessel_parts.append(head)

    bpy.ops.object.select_all(action='DESELECT')
    for part in vessel_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    vessel = bpy.context.active_object
    vessel.name = "Sep_Body"
    vessel.data.name = "Sep_Body_Mesh"
    assign_mat(vessel, MW)
    bpy.ops.object.shade_smooth()

    # ═══════════════════════════════════════════════════════════
    # 2. MASSIVE STEEL BEAM SUPPORTS
    # ═══════════════════════════════════════════════════════════
    sx_positions = [SX - SL * 0.3, SX + SL * 0.3]
    support_y_l = SY - SR * 0.65
    support_y_r = SY + SR * 0.65
    support_top_z = SZ - SR - 0.05

    for i, sx in enumerate(sx_positions):
        make_box(
            (sx, support_y_l, SZ / 2),
            (0.15 / 2, 0.15 / 2, SZ / 2),
            name="Sep_Support_Column_L_" + str(i), material=MS)
        make_box(
            (sx, support_y_r, SZ / 2),
            (0.15 / 2, 0.15 / 2, SZ / 2),
            name="Sep_Support_Column_R_" + str(i), material=MS)

        make_pipe(
            (sx, support_y_l, support_top_z),
            (sx, support_y_r, support_top_z),
            radius=0.04, material=MS, segs=8,
            name="Sep_Support_CrossBeam_" + str(i))

        make_pipe(
            (sx, support_y_l, 0.1),
            (sx, support_y_r, SZ - SR - 0.1),
            radius=0.025, material=MS, segs=8,
            name="Sep_Support_Diag_L_" + str(i))
        make_pipe(
            (sx, support_y_r, 0.1),
            (sx, support_y_l, SZ - SR - 0.1),
            radius=0.025, material=MS, segs=8,
            name="Sep_Support_Diag_R_" + str(i))

        make_box(
            (sx, support_y_l, GROUND_Z + 0.04),
            (0.25, 0.25, 0.04),
            name="Sep_Support_Base_L_" + str(i), material=MN)
        make_box(
            (sx, support_y_r, GROUND_Z + 0.04),
            (0.25, 0.25, 0.04),
            name="Sep_Support_Base_R_" + str(i), material=MN)

        cradle = make_cylinder(
            (sx, SY, SZ), SR + 0.03, 0.45,
            rot=(0, math_mod.radians(90), 0),
            name="Sep_Support_Cradle_" + str(i),
            material=MS, segs=24)
        cradle.scale = (1.0, 1.0, 0.85)

        make_pipe(
            (sx, support_y_l, GROUND_Z + 0.08),
            (sx, support_y_r, GROUND_Z + 0.08),
            radius=0.04, material=MS, segs=8,
            name="Sep_Support_BaseBeam_" + str(i))

    make_pipe(
        (sx_positions[0], support_y_l, GROUND_Z + 0.08),
        (sx_positions[1], support_y_l, GROUND_Z + 0.08),
        radius=0.04, material=MS, segs=8,
        name="Sep_Support_LongBeam_L")
    make_pipe(
        (sx_positions[0], support_y_r, GROUND_Z + 0.08),
        (sx_positions[1], support_y_r, GROUND_Z + 0.08),
        radius=0.04, material=MS, segs=8,
        name="Sep_Support_LongBeam_R")

    # ═══════════════════════════════════════════════════════════
    # 3. NOZZLES AND FITTINGS
    # ═══════════════════════════════════════════════════════════

    # ── Inlet nozzle (large, top-left, slightly angled) ──
    inlet_x = SX - SL * 0.25
    inlet_z = SZ + SR
    make_nozzle(
        (inlet_x, SY, inlet_z), 0.18, 0.55, (0, 0, 1),
        "Sep_Inlet", flange_scale=1.6, flange_r=0.045,
        material=MS)

    # ── Vent nozzle (medium, top-right, pointing up) ──
    vent_x = SX + SL * 0.28
    vent_z = SZ + SR
    make_nozzle(
        (vent_x, SY, vent_z), 0.14, 0.50, (0, 0, 1),
        "Sep_Vent", flange_scale=1.5, flange_r=0.04,
        material=MS)

    # ── Drain nozzle (small, bottom-center, pointing down) ──
    drain_x = SX
    drain_z = SZ - SR
    make_nozzle(
        (drain_x, SY, drain_z), 0.10, 0.55, (0, 0, -1),
        "Sep_Drain", flange_scale=1.5, flange_r=0.035,
        material=MS)

    # ── Drain/valve nozzle on left head bottom ──
    # Small nozzle port on the lower portion of the left elliptical head,
    # pointing outward at an angle (left and slightly down)
    head_center_x = SX - SL / 2
    head_a = head_scale_x * SR
    head_b = SR
    head_drain_angle = math_mod.radians(240)
    head_drain_x = head_center_x + head_a * math_mod.cos(head_drain_angle)
    head_drain_z = SZ + head_b * math_mod.sin(head_drain_angle)
    make_nozzle(
        (head_drain_x, SY, head_drain_z), 0.08, 0.35, (-0.5, 0, -0.866),
        "Sep_HeadDrain", flange_scale=1.4, flange_r=0.03,
        material=MS)

    # ── (Manhole removed from left head per reference — no manhole on left end cap) ──

    # ── Pressure gauge assembly: nozzle, valve, detailed dial ──
    pg_x = SX - SL * 0.15
    pg_y = SY + SR * 0.3     # slight Y-offset
    pg_z = SZ + SR + 1.0

    # Flange anchor: all above-flange elements positioned relative to flange_top
    flange_z = pg_z - 0.08
    flange_top = flange_z + 0.10    # flange body 0.04 + cap 0.05 + raised face 0.006 + margin

    # Vertical connecting pipe from separator shell to flange base
    make_pipe(
        (pg_x, pg_y, SZ + SR), (pg_x, pg_y, flange_z),
        radius=0.025, material=MS, segs=8,
        name="Sep_PG_ConnPipe")

    # Flange at junction
    make_disc_flange(
        (pg_x, pg_y, flange_z), (0, 0, 1), 0.045,
        name_prefix="Sep_PG_Base", flange_scale=1.5, material=MS)

    # Riser pipe: visible section from flange top to gauge (same dia as ConnPipe)
    riser_top = flange_top + 0.12
    make_pipe(
        (pg_x, pg_y, flange_top), (pg_x, pg_y, riser_top),
        radius=0.025, material=MS, segs=8,
        name="Sep_PG_RiserPipe")

    # Hex nut connector below pressure gauge dial
    nut = make_cylinder(
        (pg_x, pg_y, riser_top + 0.02), 0.025, 0.035,
        name="Sep_PG_NutConnector", material=MM, segs=6)
    bpy.context.view_layer.objects.active = nut
    nut.select_set(True)
    bpy.ops.object.shade_flat()

    make_pipe(
        (pg_x, pg_y, riser_top), (pg_x, pg_y, riser_top + 0.04),
        radius=0.015, material=MS, segs=8,
        name="Sep_PG_StemPipe")

    # Pressure gauge case, bezel, face, scale, and needle
    dial_z = riser_top + 0.06
    make_cylinder(
        (pg_x, pg_y, dial_z), 0.125, 0.06,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_DialCase", material=MM, segs=48)
    bezel = make_cylinder(
        (pg_x - 0.032, pg_y, dial_z), 0.128, 0.006,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_FrontBezel", material=MM, segs=48)
    dial_face = make_circle_disk(
        (pg_x - 0.036, pg_y, dial_z), 0.118,
        normal_axis='neg_X', name="Sep_PG_DialFace", material=MW, segs=48)
    dial_face.data.materials[0].diffuse_color = (1.0, 1.0, 1.0, 1.0)

    dial_cx = pg_x
    dial_cz = dial_z
    tick_x = dial_cx - 0.037
    label_x = dial_cx - 0.038
    needle_x = dial_cx - 0.039
    pivot_x = dial_cx - 0.040
    arc_start = -45
    arc_end = 225

    def dial_rotation(angle):
        return (angle - math_mod.radians(90), 0, 0)

    for i in range(10):
        angle = math_mod.radians(arc_start + i * (arc_end - arc_start) / 9)
        tick_r = 0.10
        ty = pg_y + tick_r * math_mod.cos(angle)
        tz = dial_cz + tick_r * math_mod.sin(angle)
        tick = make_box(
            (tick_x, ty, tz), (0.001, 0.001, 0.015),
            name="Sep_PG_TickM_{}".format(i), material=MM)
        tick.rotation_euler = dial_rotation(angle)

    for i in range(40):
        angle = math_mod.radians(arc_start + i * (arc_end - arc_start) / 39)
        tick_r = 0.105
        ty = pg_y + tick_r * math_mod.cos(angle)
        tz = dial_cz + tick_r * math_mod.sin(angle)
        tick = make_box(
            (tick_x, ty, tz), (0.0005, 0.001, 0.008),
            name="Sep_PG_TickS_{}".format(i), material=MM)
        tick.rotation_euler = dial_rotation(angle)

    text_values = [("0", -45), ("20", 9), ("40", 63), ("60", 117), ("80", 171), ("100", 225)]
    for txt_str, angle_deg in text_values:
        angle = math_mod.radians(angle_deg)
        lr = 0.07
        ly = pg_y + lr * math_mod.cos(angle)
        lz = dial_cz + lr * math_mod.sin(angle)
        bpy.ops.object.text_add(location=(label_x, ly, lz))
        txt_obj = bpy.context.active_object
        txt_obj.name = "Sep_PG_Text_" + txt_str
        txt_obj.data.body = txt_str
        txt_obj.data.size = 0.012
        txt_obj.data.align_x = 'CENTER'
        txt_obj.data.align_y = 'CENTER'
        txt_obj.rotation_euler = (0, math_mod.radians(-90), 0)
        assign_mat(txt_obj, MM)

    needle_angle = math_mod.radians(-45)
    needle = make_box(
        (needle_x, pg_y, dial_cz), (0.003, 0.001, 0.06),
        name="Sep_PG_Needle", material=MM)
    needle.rotation_euler = dial_rotation(needle_angle)
    make_cylinder(
        (pivot_x, pg_y, dial_cz), 0.008, 0.003,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_PivotDot", material=MM, segs=16)

    # Face elements face -X directly (no rotation needed)

    # ── Pipe stubs connecting to FlareGas route ──
    # Small horizontal pipe from top of separator toward the gas pipe route
    stub_x = SX + SL * 0.3
    stub_z = SZ + SR + 0.35
    make_cylinder(
        (stub_x, SY + 0.3, stub_z), 0.06, 0.6,
        rot=(0, 0, math_mod.radians(90)),  # along Y
        name="Sep_GasStub", material=MY, segs=10)
    # Flange on stub
    make_disc_flange(
        (stub_x, SY + 0.6, stub_z), (0, 1, 0), 0.06,
        name_prefix="Sep_GasStub", flange_scale=1.5, material=MY)

    # ═══════════════════════════════════════════════════════════
    # 4. SERVICE PLATFORM ON TOP
    # ═══════════════════════════════════════════════════════════
    plat_len = SL * 0.65         # ~65% of cylinder length
    plat_w = SR * 2.4            # extends beyond diameter
    plat_z = SZ + SR             # on top of cylinder
    plat_thick = 0.06
    rail_h = 0.90                # railing height

    # Platform boundaries (computed first — ladder position depends on them)
    p_x_min = SX - plat_len / 2
    p_x_max = SX + plat_len / 2
    p_y_min = SY - plat_w / 2
    p_y_max = SY + plat_w / 2

    # Ladder coordinates (aligned with front edge of platform grating)
    lad_x = SX + SL * 0.15              # ladder X center (stringers along X)
    lad_y = p_y_max                     # ladder Y = front edge of platform (was SY + SR + 0.10)
    lad_z_top = plat_z                  # top of ladder = platform level (flush with grating)
    lad_z_bot = GROUND_Z + 0.4          # above ground

    # No hole in the platform — grating is continuous under the ladder.
    # The cage sits above the platform surface and does NOT cut through it.

    bar_r = 0.02      # pipe radius for grating
    bar_spacing = 0.18 # gap between bars

    # ── Longitudinal bars along Y axis (running front-to-back) ──
    # All bars are full-length — no hole around ladder.
    bar_idx = 0
    n_bars_x = int(round((p_x_max - p_x_min) / bar_spacing)) + 1
    for bi in range(n_bars_x):
        bar_x = p_x_min + bi * bar_spacing
        if bar_x > p_x_max + 0.01:
            break
        make_pipe(
            (bar_x, p_y_min + 0.02, plat_z + bar_r),
            (bar_x, p_y_max - 0.02, plat_z + bar_r),
            radius=bar_r, material=MS, segs=6,
            name="Sep_Grat_Y_{}".format(bar_idx))
        bar_idx += 1

    # ── Transverse bars along X axis (running left-to-right) ──
    # All bars are full-length — no hole around ladder.
    n_bars_y = int(round((p_y_max - p_y_min) / bar_spacing)) + 1
    for bi in range(n_bars_y):
        bar_y = p_y_min + bi * bar_spacing
        if bar_y > p_y_max + 0.01:
            break
        make_pipe(
            (p_x_min + 0.02, bar_y, plat_z),
            (p_x_max - 0.02, bar_y, plat_z),
            radius=bar_r, material=MS, segs=6,
            name="Sep_Grat_X_{}".format(bar_idx))
        bar_idx += 1

    # ── Toe plate (thin box around perimeter) ──
    toe_h = 0.08
    toe_t = 0.02
    
    # Front and back edges (along X)
    for y_edge, y_name in [(p_y_max, "Front"), (p_y_min, "Back")]:
        make_box(
            (SX, y_edge, plat_z + toe_h / 2),
            (plat_len / 2, toe_t / 2, toe_h / 2),
            name="Sep_Plat_Toe_{}".format(y_name), material=MS)
    # Left and right edges (along Y)
    for x_edge, x_name in [(p_x_min, "L"), (p_x_max, "R")]:
        make_box(
            (x_edge, SY, plat_z + toe_h / 2),
            (toe_t / 2, plat_w / 2, toe_h / 2),
            name="Sep_Plat_Toe_{}".format(x_name), material=MS)

    # (No hole frame — platform has no cutout, grating is continuous)

    # ── Railing posts (thin cylinders at ~1m intervals) ──
    post_r = 0.025
    n_posts_x = max(2, int(round(plat_len / 0.9)) + 1)
    n_posts_y = max(2, int(round(plat_w / 0.9)) + 1)

    # Access opening on front edge (where ladder meets)
    opening_x = SX + SL * 0.15   # aligned with ladder hole
    opening_half = 0.35

    post_index = 0
    # Posts along X-edges (front and back)
    for y_edge in [p_y_min, p_y_max]:
        for pi in range(n_posts_x):
            px = p_x_min + plat_len * pi / (n_posts_x - 1)
            # Skip posts on front edge in the access opening area
            if y_edge == p_y_max and abs(px - opening_x) < opening_half:
                continue
            make_cylinder(
                (px, y_edge, plat_z + rail_h / 2),
                post_r, rail_h,
                name="Sep_Plat_Post_{}".format(post_index),
                material=MS, segs=6)
            post_index += 1

    # Posts along Y-edges (left and right) - solid, no opening
    for x_edge in [p_x_min, p_x_max]:
        for pi in range(n_posts_y):
            py = p_y_min + plat_w * pi / (n_posts_y - 1)
            # Skip corner posts already created by X-edges
            if pi == 0 or pi == n_posts_y - 1:
                continue
            make_cylinder(
                (x_edge, py, plat_z + rail_h / 2),
                post_r, rail_h,
                name="Sep_Plat_Post_{}".format(post_index),
                material=MS, segs=6)
            post_index += 1

    # ── Cage dimensions (needed early for platform rail clipping) ──
    rail_spacing = 0.35
    cage_r = 0.40            # forward reach of the cage (Y radius)
    cage_rx = rail_spacing / 2          # cage X-radius matches ladder stringers (no side gap)
    cage_ry = cage_r                     # 0.40m  — forward reach
    cage_bar_r = 0.014       # thickness of cage bars
    cage_start_z = lad_z_bot + 0.5   # start ~0.5m above ground
    cage_end_z = plat_z + rail_h         # cage extends to railing top

    # ── Horizontal rails (3 levels: top, middle, bottom) ──
    rail_radius = 0.018
    rail_heights = [0.15, 0.50, 0.85]  # fraction of rail_h from floor
    
    for rh_frac in rail_heights:
        rh = plat_z + rh_frac
        # Front rail — with gap for ladder access opening
        # Rails extend to exact post positions (no 0.05 offset) so they touch corner posts
        rail_tag = int(rh_frac * 100)
        make_pipe(
            (p_x_min, p_y_max, rh),
            (lad_x - cage_rx, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_FL_{}".format(rail_tag))
        make_pipe(
            (lad_x + cage_rx, p_y_max, rh),
            (p_x_max, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_FR_{}".format(rail_tag))
        # Back rail (solid, no opening)
        make_pipe(
            (p_x_min, p_y_min, rh),
            (p_x_max, p_y_min, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_B_{}".format(int(rh_frac * 100)))
        # Left rail (solid, no opening)
        make_pipe(
            (p_x_min, p_y_min, rh),
            (p_x_min, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_L_{}".format(int(rh_frac * 100)))
        # Right rail (solid, no opening)
        make_pipe(
            (p_x_max, p_y_min, rh),
            (p_x_max, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_R_{}".format(int(rh_frac * 100)))

    # ═══════════════════════════════════════════════════════════
    # 5. LADDER (vertical, right side)
    # ═══════════════════════════════════════════════════════════
    # ── Ladder coordinates already defined above (section 4) ──
    # lad_x, lad_y, lad_z_top, lad_z_bot are set in the platform section

    # Side rails (thin pipes) — rotated 90°: rails along X, rungs along X too
    # rail_spacing already defined above (cage dimensions section)
    rail_r_lad = 0.02
    lad_x_l = lad_x - rail_spacing / 2   # left rail in X
    lad_x_r = lad_x + rail_spacing / 2   # right rail in X

    make_pipe(
        (lad_x_l, lad_y, lad_z_bot), (lad_x_l, lad_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_Rail_L")
    make_pipe(
        (lad_x_r, lad_y, lad_z_bot), (lad_x_r, lad_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_Rail_R")

    # Rungs at 0.3m intervals — along X (connecting left and right rails)
    rung_r = 0.015
    n_rungs = int((lad_z_top - lad_z_bot) / 0.30)
    for ri in range(n_rungs):
        rz = lad_z_bot + (ri + 0.5) * (lad_z_top - lad_z_bot) / n_rungs
        make_pipe(
            (lad_x_l, lad_y, rz), (lad_x_r, lad_y, rz),
            radius=rung_r, material=MS, segs=6,
            name="Sep_Ladder_Rung_{}".format(ri))

    # Ladder top remains open inside the safety cage for unobstructed exit.
    
    # ── Ladder safety cage (proper semicircular cage) ──
    # The cage forms a semicircular arch AROUND the front of the ladder,
    # from the left rail to the right rail, curving forward (Y+).
    # cage_rx, cage_ry, cage_bar_r, cage_start_z, cage_end_z already defined above

    if cage_end_z > cage_start_z:
        # ── Vertical cage bars (7 bars forming a semicircular arch) ──
        # Arc from π (left side at lad_x - cage_rx, lad_y) through π/2 (center front)
        # to 0 (right side at lad_x + cage_rx, lad_y), wrapping around the front.
        n_vert = 7
        for vi in range(n_vert):
            frac = vi / (n_vert - 1)  # 0.0 to 1.0
            angle = math_mod.pi * (1.0 - frac)  # π → 0 (left → right through front)
            bar_x = lad_x + math_mod.cos(angle) * cage_rx
            bar_y = lad_y + math_mod.sin(angle) * cage_ry
            make_pipe(
                (bar_x, bar_y, cage_start_z), (bar_x, bar_y, cage_end_z),
                radius=cage_bar_r, material=MS, segs=6,
                name="Sep_Ladder_CageV_{}".format(vi))

        # ── Horizontal semicircular rings at regular intervals (curve tubes) ──
        n_rings = int((cage_end_z - cage_start_z) / 0.40) + 1
        n_arc_pts = 32  # number of arc segments per ring (more = smoother)
        for ri in range(n_rings):
            rz = cage_start_z + ri * 0.40
            if rz > cage_end_z + 0.01:
                break
            ring_pts = []
            for si in range(n_arc_pts + 1):
                t = si / n_arc_pts
                angle = math_mod.pi * (1.0 - t)  # π → 0
                px = lad_x + math_mod.cos(angle) * cage_rx
                py = lad_y + math_mod.sin(angle) * cage_ry
                ring_pts.append((px, py, rz))
            make_curve_tube(
                ring_pts, radius=cage_bar_r, material=MS,
                name="Sep_Ladder_CageR_" + str(ri))

        # Top ring — full semicircular arc, same style as regular rings
        top_ring_pts = []
        for si in range(n_arc_pts + 1):
            t = si / n_arc_pts
            angle = math_mod.pi * (1.0 - t)  # π → 0
            px = lad_x + math_mod.cos(angle) * cage_rx
            py = lad_y + math_mod.sin(angle) * cage_ry
            top_ring_pts.append((px, py, cage_end_z))
        make_curve_tube(
            top_ring_pts, radius=cage_bar_r, material=MS,
            name="Sep_Ladder_CageR_Top")

    # ═══════════════════════════════════════════════════════════
    # 6. SMALL DETAILS
    # ═══════════════════════════════════════════════════════════

    # ── Warning stripes (red bands) on inlet and vent nozzles ──
    for stripe_info in [
        ("Sep_Inlet_Warn", SX - SL * 0.25, SY, SZ + SR + 0.45, 0.20, 0.015),
        ("Sep_Vent_Warn", SX + SL * 0.28, SY, SZ + SR + 0.40, 0.16, 0.015),
    ]:
        s_name, sx_s, sy_s, sz_s, s_r, s_h = stripe_info
        make_cylinder(
            (sx_s, sy_s, sz_s), s_r, s_h,
            name=s_name, material=MR, segs=12)

    # ── Platform support beams and diagonal shell braces ──
    beam_w = 0.15
    beam_h = 0.10
    beam_len = p_x_max - p_x_min
    beam_z = plat_z - beam_h / 2
    beam_y_positions = [SY - SR * 0.30, SY + SR * 0.30]

    for bi, beam_y in enumerate(beam_y_positions):
        make_box(
            (SX, beam_y, beam_z),
            (beam_len / 2, beam_w / 2, beam_h / 2),
            name="Sep_Plat_SupportBeam_{}".format(bi), material=MS)

    def make_square_brace(p1, p2, width, name):
        start = Vector(p1)
        end = Vector(p2)
        span = end - start
        length = span.length
        if length < 0.001:
            return None
        bpy.ops.mesh.primitive_cube_add(location=((p1[0] + p2[0]) / 2,
                                                  (p1[1] + p2[1]) / 2,
                                                  (p1[2] + p2[2]) / 2))
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (length / 2, width / 2, width / 2)
        obj.rotation_euler = span.to_track_quat('X', 'Z').to_euler()
        assign_mat(obj, MS)
        bpy.ops.object.shade_smooth()
        return obj

    brace_w = 0.05
    brace_x_positions = [SX - plat_len * 0.25, SX + plat_len * 0.25]
    shell_y_offset = SR * 0.72
    shell_z = SZ + math_mod.sqrt(max(0.0, SR * SR - shell_y_offset * shell_y_offset))
    for side_sgn, side_name, y_edge in [(-1, "L", p_y_min), (1, "R", p_y_max)]:
        shell_y = SY + side_sgn * shell_y_offset
        for xi, x_br in enumerate(brace_x_positions):
            make_square_brace(
                (x_br, y_edge, plat_z - plat_thick / 2),
                (x_br, shell_y, shell_z),
                brace_w,
                "Sep_Plat_DiagBrace_{}_{}".format(side_name, xi))
