"""
Detailed horizontal separator (knockout drum) for flare-predictor project.
Blender 4.0.2 compatible, low-poly (~2000-3000 faces).
Coordinate system matches flare_install.py: SX=-7.0, SY=-4.5, SZ=1.6, SL=7.5, SR=1.4.

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
    SX, SY, SZ, SL, SR = -7.0, -4.5, 1.6, 7.5, 1.4
    GROUND_Z = 0.0

    # ─── Helper functions ─────────────────────────────────────
    def assign_mat(obj, mat):
        obj.data.materials.clear()
        obj.data.materials.append(mat)

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

    def make_nozzle(pos, radius, length, direction_vec, name_prefix,
                    flange_scale=1.5, flange_r=0.04, material=MS):
        """Create a nozzle cylinder + flange ring pointing in direction_vec."""
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
        # Flange torus at tip
        make_torus(end_pos, radius * flange_scale, flange_r,
                   name=name_prefix + "_Flange",
                   material=material, m_segs=14, r_segs=8)
        return cyl_obj

    # ═══════════════════════════════════════════════════════════
    # 1. MAIN BODY
    # ═══════════════════════════════════════════════════════════
    # Horizontal cylinder (rotated to X-axis)
    make_cylinder((SX, SY, SZ), SR, SL,
                  rot=(0, math_mod.radians(90), 0),
                  name="Sep_Body", material=MW, segs=30)

    # Elliptical heads at both ends (elongated UV hemispheres)
    head_scale_x = 0.6  # elliptical head depth ~0.6 * SR
    for side_label, x_offset in [("L", -SL / 2), ("R", SL / 2)]:
        head = make_uvsphere(
            (SX + x_offset, SY, SZ), SR,
            name="Sep_Head_" + side_label,
            material=MW, segs=20)
        head.scale = (head_scale_x, 1.0, 1.0)

    # ═══════════════════════════════════════════════════════════
    # 2. SADDLE SUPPORTS (at ~20% and ~80% of length)
    # ═══════════════════════════════════════════════════════════
    saddle_positions = [-SL * 0.3, SL * 0.3]  # 20% / 80%

    for i, x_off in enumerate(saddle_positions):
        sx = SX + x_off
        leg_h = SZ - SR                     # height from ground to cylinder bottom

        # ── Curved saddle plate: short cylinder segment ──
        # We create a short cylinder with same radius as body + gap,
        # centered below the body, scaled to only cover bottom portion
        saddle = make_cylinder(
            (sx, SY, SZ - SR * 0.2), SR + 0.04, 0.35,
            rot=(0, math_mod.radians(90), 0),
            name="Sep_SaddlePlate_" + str(i),
            material=MS, segs=14)
        # Scale down vertically so it only wraps the bottom half
        saddle.scale = (1.0, 1.0, 0.55)

        # ── Vertical legs ──
        leg_w = 0.12
        leg_d = 0.18
        for side_sgn, side_name in [(-1, "L"), (1, "R")]:
            make_box(
                (sx, SY + side_sgn * SR * 0.55, GROUND_Z + leg_h / 2),
                (leg_w / 2, leg_d / 2, leg_h / 2),
                name="Sep_SaddleLeg_{}_{}".format(i, side_name),
                material=MS)

        # ── Base plate ──
        make_box(
            (sx, SY, GROUND_Z + 0.025),
            (0.35 / 2, SR * 0.7 / 2, 0.025),
            name="Sep_SaddleBase_" + str(i),
            material=MN)

    # ═══════════════════════════════════════════════════════════
    # 3. NOZZLES AND FITTINGS
    # ═══════════════════════════════════════════════════════════

    # ── Inlet nozzle (large, top-left, slightly angled) ──
    inlet_x = SX - SL * 0.25
    inlet_z = SZ + SR + 0.2
    make_nozzle(
        (inlet_x, SY, inlet_z), 0.18, 0.55, (0, 0, 1),
        "Sep_Inlet", flange_scale=1.6, flange_r=0.045,
        material=MS)

    # ── Vent nozzle (medium, top-right, pointing up) ──
    vent_x = SX + SL * 0.28
    vent_z = SZ + SR + 0.2
    make_nozzle(
        (vent_x, SY, vent_z), 0.14, 0.50, (0, 0, 1),
        "Sep_Vent", flange_scale=1.5, flange_r=0.04,
        material=MS)

    # ── Drain nozzle (small, bottom-center, pointing down) ──
    drain_x = SX
    drain_z = SZ - SR - 0.2
    make_nozzle(
        (drain_x, SY, drain_z), 0.10, 0.55, (0, 0, -1),
        "Sep_Drain", flange_scale=1.5, flange_r=0.035,
        material=MS)

    # ── Manhole on left head ──
    mh_x = SX - SL / 2 + 0.05  # just inside the head surface
    mh_y = SY
    mh_z = SZ
    mh_r = 0.28
    # Disc (cylinder with small depth, facing X)
    mh = make_cylinder(
        (mh_x, mh_y, mh_z), mh_r, 0.05,
        rot=(0, math_mod.radians(90), 0),
        name="Sep_Manhole_Disc", material=MS, segs=20)
    # Bolt ring (torus on the disc face)
    make_torus(
        (mh_x, mh_y + 0.02, mh_z),
        mh_r * 0.82, 0.018,
        name="Sep_Manhole_BoltRing",
        material=MS, m_segs=20, r_segs=8)

    # ── Level gauge (right side, vertical pipe with flags) ──
    lg_x = SX + SL * 0.25
    lg_y = SY + SR * 0.5      # Y-offset to be visible from camera
    lg_z_bottom = SZ - SR * 0.35
    lg_z_top = SZ + SR * 0.15
    # Vertical pipe
    make_pipe(
        (lg_x, lg_y, lg_z_bottom), (lg_x, lg_y, lg_z_top),
        radius=0.03, material=MS, segs=8,
        name="Sep_LG_Pipe")
    # Flag indicators at intervals (small yellow cylinders)
    n_flags = 6
    for fi in range(n_flags):
        frac = fi / (n_flags - 1)
        fz = lg_z_bottom + (lg_z_top - lg_z_bottom) * frac
        make_cylinder(
            (lg_x, lg_y, fz), 0.045, 0.02,
            name="Sep_LG_Flag_{}".format(fi),
            material=MY, segs=8)

    # ── Pressure gauge (top, small cylinder + face) ──
    pg_x = SX - SL * 0.15
    pg_y = SY + SR * 0.3     # slight Y-offset
    pg_z = SZ + SR + 0.35
    # Stalk
    make_cylinder(
        (pg_x, pg_y, pg_z - 0.10), 0.035, 0.18,
        name="Sep_PG_Stalk", material=MS, segs=8)
    # Gauge body (yellow)
    make_cylinder(
        (pg_x, pg_y, pg_z), 0.05, 0.06,
        name="Sep_PG_Body", material=MY, segs=10)
    # Gauge face (dark disc)
    make_cylinder(
        (pg_x, pg_y, pg_z + 0.045), 0.065, 0.015,
        name="Sep_PG_Face", material=MM, segs=12)

    # ── Instrument mounting brackets (small cubes on cylinder surface) ──
    bracket_positions = [
        (SX - SL * 0.2, SY + SR * 0.7, SZ),      # left side
        (SX + SL * 0.2, SY + SR * 0.7, SZ),      # right side
        (SX, SY + SR * 0.7, SZ + SR * 0.5),      # top-side
    ]
    for bi, (bx, by, bz) in enumerate(bracket_positions):
        make_box(
            (bx, by, bz), (0.06, 0.04, 0.04),
            name="Sep_Bracket_{}".format(bi), material=MS)

    # ── Pipe stubs connecting to FlareGas route ──
    # Small horizontal pipe from top of separator toward the gas pipe route
    stub_x = SX + SL * 0.3
    stub_z = SZ + SR + 0.35
    make_cylinder(
        (stub_x, SY + 0.3, stub_z), 0.06, 0.6,
        rot=(0, 0, math_mod.radians(90)),  # along Y
        name="Sep_GasStub", material=MY, segs=10)
    # Flange on stub
    make_torus(
        (stub_x, SY + 0.6, stub_z), 0.09, 0.025,
        name="Sep_GasStubFlange", material=MY, m_segs=12, r_segs=8)

    # ═══════════════════════════════════════════════════════════
    # 4. SERVICE PLATFORM ON TOP
    # ═══════════════════════════════════════════════════════════
    plat_len = SL * 0.65         # ~65% of cylinder length
    plat_w = SR * 2.4            # extends beyond diameter
    plat_z = SZ + SR             # on top of cylinder
    plat_thick = 0.06
    rail_h = 0.90                # railing height

    # Ladder coordinates (needed for hole and cage alignment)
    lad_x = SX + SL * 0.15              # ladder X center (stringers along X)
    lad_y = SY + SR + 0.10              # ladder Y position (on cylinder surface)
    lad_z_top = plat_z                  # top of ladder = platform level (flush with grating)
    lad_z_bot = GROUND_Z + 0.2          # above ground

    # Platform boundaries
    p_x_min = SX - plat_len / 2
    p_x_max = SX + plat_len / 2
    p_y_min = SY - plat_w / 2
    p_y_max = SY + plat_w / 2

    # Hole for ladder exit — elongated along X (ladder rotated 90°, stringers along X)
    # Shift hole slightly inward so its front edge is ~0.15m inside platform front edge
    # This ensures grating bars exist on all 4 sides of the hole
    hole_w = 0.50    # along X axis (longer — ladder stringers run along X)
    hole_d = 0.35    # along Y axis (narrower — just enough to step through)
    hole_x = lad_x                              # aligned with ladder X center
    hole_y = lad_y - (lad_y - (p_y_max - 0.15)) # shift inward so hy_max ≈ p_y_max - 0.15

    hx_min = hole_x - hole_w / 2
    hx_max = hole_x + hole_w / 2
    hy_min = hole_y - hole_d / 2
    hy_max = hole_y + hole_d / 2

    bar_r = 0.02      # pipe radius for grating
    bar_spacing = 0.18 # gap between bars

    # ── Longitudinal bars along Y axis (running front-to-back) ──
    bar_idx = 0
    n_bars_x = int(round((p_x_max - p_x_min) / bar_spacing)) + 1
    for bi in range(n_bars_x):
        bar_x = p_x_min + bi * bar_spacing
        if bar_x > p_x_max + 0.01:
            break
        in_hole = hx_min <= bar_x <= hx_max
        if in_hole:
            # Split around the ladder hole: segment below and above
            len_below = hy_min - p_y_min
            len_above = p_y_max - hy_max
            if len_below > 0.05:
                make_pipe(
                    (bar_x, p_y_min + 0.02, plat_z + bar_r),
                    (bar_x, hy_min - 0.02, plat_z + bar_r),
                    radius=bar_r, material=MS, segs=6,
                    name="Sep_Grat_Y_{}".format(bar_idx))
                bar_idx += 1
            if len_above > 0.05:
                make_pipe(
                    (bar_x, hy_max + 0.02, plat_z + bar_r),
                    (bar_x, p_y_max - 0.02, plat_z + bar_r),
                    radius=bar_r, material=MS, segs=6,
                    name="Sep_Grat_Y_{}".format(bar_idx))
                bar_idx += 1
        else:
            # Full bar across entire width
            make_pipe(
                (bar_x, p_y_min + 0.02, plat_z + bar_r),
                (bar_x, p_y_max - 0.02, plat_z + bar_r),
                radius=bar_r, material=MS, segs=6,
                name="Sep_Grat_Y_{}".format(bar_idx))
            bar_idx += 1

    # ── Transverse bars along X axis (running left-to-right) ──
    n_bars_y = int(round((p_y_max - p_y_min) / bar_spacing)) + 1
    for bi in range(n_bars_y):
        bar_y = p_y_min + bi * bar_spacing
        if bar_y > p_y_max + 0.01:
            break
        in_hole = hy_min <= bar_y <= hy_max
        if in_hole:
            # Split around the ladder hole: left and right segments
            len_left = hx_min - p_x_min
            len_right = p_x_max - hx_max
            if len_left > 0.05:
                make_pipe(
                    (p_x_min + 0.02, bar_y, plat_z),
                    (hx_min - 0.02, bar_y, plat_z),
                    radius=bar_r, material=MS, segs=6,
                    name="Sep_Grat_X_{}".format(bar_idx))
                bar_idx += 1
            if len_right > 0.05:
                make_pipe(
                    (hx_max + 0.02, bar_y, plat_z),
                    (p_x_max - 0.02, bar_y, plat_z),
                    radius=bar_r, material=MS, segs=6,
                    name="Sep_Grat_X_{}".format(bar_idx))
                bar_idx += 1
        else:
            # Full bar across entire length
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

    # ── Hole frame: thick pipes around the ladder opening ──
    # This creates a visible rim that connects grating to the ladder exit
    frame_r = 0.025  # pipe radius for the frame
    frame_z = plat_z + bar_r  # same height as grating bars
    # Front edge of hole (Y = hy_max)
    make_pipe(
        (hx_min, hy_max, frame_z), (hx_max, hy_max, frame_z),
        radius=frame_r, material=MS, segs=6,
        name="Sep_HoleFrame_Front")
    # Back edge of hole (Y = hy_min)
    make_pipe(
        (hx_min, hy_min, frame_z), (hx_max, hy_min, frame_z),
        radius=frame_r, material=MS, segs=6,
        name="Sep_HoleFrame_Back")
    # Left edge (X = hx_min)
    make_pipe(
        (hx_min, hy_min, frame_z), (hx_min, hy_max, frame_z),
        radius=frame_r, material=MS, segs=6,
        name="Sep_HoleFrame_Left")
    # Right edge (X = hx_max)
    make_pipe(
        (hx_max, hy_min, frame_z), (hx_max, hy_max, frame_z),
        radius=frame_r, material=MS, segs=6,
        name="Sep_HoleFrame_Right")

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

    # ── Horizontal rails (3 levels: top, middle, bottom) ──
    rail_radius = 0.018
    rail_heights = [0.15, 0.50, 0.85]  # fraction of rail_h from floor
    
    for rh_frac in rail_heights:
        rh = plat_z + rh_frac
        # Front rail — with gap for ladder access opening
        make_pipe(
            (p_x_min + 0.05, p_y_max, rh),
            (opening_x - opening_half, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_F1_{}".format(int(rh_frac * 100)))
        make_pipe(
            (opening_x + opening_half, p_y_max, rh),
            (p_x_max - 0.05, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_F2_{}".format(int(rh_frac * 100)))
        # Back rail (solid, no opening)
        make_pipe(
            (p_x_min + 0.05, p_y_min, rh),
            (p_x_max - 0.05, p_y_min, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_B_{}".format(int(rh_frac * 100)))
        # Left rail (solid, no opening)
        make_pipe(
            (p_x_min, p_y_min + 0.05, rh),
            (p_x_min, p_y_max - 0.05, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_L_{}".format(int(rh_frac * 100)))
        # Right rail (solid, no opening)
        make_pipe(
            (p_x_max, p_y_min + 0.05, rh),
            (p_x_max, p_y_max - 0.05, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_R_{}".format(int(rh_frac * 100)))

    # ═══════════════════════════════════════════════════════════
    # 5. LADDER (vertical, right side)
    # ═══════════════════════════════════════════════════════════
    # ── Ladder coordinates already defined above (section 4) ──
    # lad_x, lad_y, lad_z_top, lad_z_bot are set in the platform section

    # Side rails (thin pipes) — rotated 90°: rails along X, rungs along X too
    rail_spacing = 0.35
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

    # ── Exit step: connects ladder top to platform edge ──
    # Ladder top is flush with platform level (lad_z_top = plat_z)
    # Horizontal rails from ladder to front edge of platform grating
    exit_y = p_y_max   # front edge of platform
    make_pipe(
        (lad_x_l, lad_y, lad_z_top), (lad_x_l, exit_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_ExitL")
    make_pipe(
        (lad_x_r, lad_y, lad_z_top), (lad_x_r, exit_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_ExitR")
    # Exit rung (cross-bar at top, along X connecting the two rails at front edge)
    make_pipe(
        (lad_x_l, exit_y, lad_z_top), (lad_x_r, exit_y, lad_z_top),
        radius=rung_r, material=MS, segs=6,
        name="Sep_Ladder_ExitRung")
    # Cross-bar at ladder top (along X, connecting the two rails at ladder position)
    make_pipe(
        (lad_x_l, lad_y, lad_z_top), (lad_x_r, lad_y, lad_z_top),
        radius=rung_r, material=MS, segs=6,
        name="Sep_Ladder_TopRung")
    
    # ── Handrails from platform railing to ladder top ──
    # Diagonal pipes from railing height at front edge down to ladder top
    for x_hr in [lad_x_l, lad_x_r]:
        make_pipe(
            (x_hr, exit_y, plat_z + rail_h), (x_hr, lad_y, lad_z_top + 0.15),
            radius=0.02, material=MS, segs=6,
            name="Sep_Ladder_Handrail_{}".format("L" if x_hr == lad_x_l else "R"))

    # ── Ladder safety cage (full height, 4 vertical bars, semicircular rings every 0.4m) ──
    # Cage wraps around the front half of the ladder, rotated 90°: arches in X-Z plane
    # Cage offset forward (Y+) from ladder so there's clear space between ladder and cage
    cage_offset_y = 0.25     # how far the cage center sits forward of the ladder
    cage_r = 0.35            # radius of the semicircular arch (wider for clearance)
    cage_bar_r = 0.014       # thickness of cage bars
    cage_start_z = lad_z_bot + 1.0   # start 1m above ground
    cage_end_z = lad_z_top - 0.15    # end near platform
    cage_cy = lad_y + cage_offset_y  # center of cage arches, offset forward

    if cage_end_z > cage_start_z:
        # ── Vertical cage bars ──
        # Spread along X (perpendicular to cylinder axis Y), offset forward
        cage_angles = [-1.05, -0.35, 0.35, 1.05]  # wider spread in radians
        for ci, angle in enumerate(cage_angles):
            cx = lad_x + math_mod.sin(angle) * cage_r
            cy = cage_cy + math_mod.cos(angle) * cage_r * 0.35  # depth in Y
            make_pipe(
                (cx, cy, cage_start_z), (cx, cy, cage_end_z),
                radius=cage_bar_r, material=MS, segs=6,
                name="Sep_Ladder_CageV_{}".format(ci))

        # ── Horizontal semicircular rings every 0.4m ──
        # Arcs in X-Z plane (rotated 90°), center offset forward
        n_rings = int((cage_end_z - cage_start_z) / 0.40) + 1
        ring_segs = 8  # segments per semicircle
        for ri in range(n_rings):
            rz = cage_start_z + ri * 0.40
            if rz > cage_end_z:
                break
            for si in range(ring_segs):
                t1 = si / ring_segs
                t2 = (si + 1) / ring_segs
                angle1 = math_mod.pi * (t1 - 0.5)  # -90° to +90°
                angle2 = math_mod.pi * (t2 - 0.5)
                x1 = lad_x + math_mod.sin(angle1) * cage_r
                y1 = cage_cy + math_mod.cos(angle1) * cage_r * 0.35
                x2 = lad_x + math_mod.sin(angle2) * cage_r
                y2 = cage_cy + math_mod.cos(angle2) * cage_r * 0.35
                make_pipe(
                    (x1, y1, rz), (x2, y2, rz),
                    radius=cage_bar_r, material=MS, segs=4,
                    name="Sep_Ladder_CageR_{}_{}".format(ri, si))

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

    # ── L-shaped support brackets under platform (angle iron, 4 total) ──
    # Each bracket: vertical leg connects to cylinder surface, horizontal leg supports platform
    bracket_thick = 0.025
    bracket_vert_h = 0.20   # height of vertical leg
    bracket_horiz_w = 0.10  # width of horizontal leg
    bracket_len = 0.25      # length along cylinder axis

    for side_sgn, side_name in [(-1, "L"), (1, "R")]:
        bracket_x_positions = [SX - plat_len * 0.25, SX + plat_len * 0.25]
        for xi, x_br in enumerate(bracket_x_positions):
            y_br = SY + side_sgn * SR * 0.65
            # Vertical leg (connects to cylinder surface)
            make_box(
                (x_br, y_br, plat_z - bracket_vert_h / 2),
                (bracket_len / 2, bracket_thick / 2, bracket_vert_h / 2),
                name="Sep_Plat_Bracket_{}_{}_V".format(side_name, xi), material=MS)
            # Horizontal leg (supports platform from below)
            make_box(
                (x_br, y_br + side_sgn * bracket_horiz_w / 2, plat_z - bracket_thick / 2),
                (bracket_len / 2, bracket_horiz_w / 2, bracket_thick / 2),
                name="Sep_Plat_Bracket_{}_{}_H".format(side_name, xi), material=MS)
