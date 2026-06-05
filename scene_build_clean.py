#!/usr/bin/env blender --background --python
"""scene_build_clean.py - Clean rebuild: geometry -> materials -> cameras/lights -> save.
No double execution. Cameras and lights created AFTER geometry+materials.
"""
import bpy
import math
from mathutils import Vector

SCENE_PATH = "/tmp/blender-agent-2/execute/scene.blend"

# Cabinet dimensions are meters: 900 x 500 x 1500 mm.
CABINET_W = 0.90
CABINET_D = 0.50
CABINET_H = 1.50
PANEL_THICKNESS = 0.024
FRONT_Y = -CABINET_D / 2
BACK_Y = CABINET_D / 2
LEFT_X = -CABINET_W / 2
RIGHT_X = CABINET_W / 2
FACE_ROT_Y_AXIS = (math.radians(90), 0.0, 0.0)
CABINET_MOUNT_Z_OFFSET = 0.70


def shifted(loc, x_offset=0.0):
    """Return location shifted along X for a duplicated cabinet."""
    return (loc[0] + x_offset, loc[1], loc[2])


def suffixed(name, suffix=""):
    """Return object name with duplicate suffix when building the second cabinet."""
    return f"{name}{suffix}"


def move_objects_z(objects, z_offset):
    """Lift a completed cabinet assembly without changing its local geometry."""
    for obj in objects:
        obj.location.z += z_offset

# -------------------------------------------------------------------
# GEOMETRY
# -------------------------------------------------------------------

def clear_scene():
    """Remove default Blender scene objects before rebuilding."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_box(name, loc, size, bevel_segments=0, bevel_depth=0):
    """Create a box mesh at location with given dimensions (x, y, z)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel_segments > 0 and bevel_depth > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.segments = bevel_segments
        mod.width = bevel_depth
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(45)
    return obj


def make_cylinder(name, loc, radius, depth, rot=(0.0, 0.0, 0.0), segments=32):
    """Create a cylinder mesh at location with radius and depth."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=radius,
        depth=depth,
        location=loc,
        rotation=rot,
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def shade_flat(obj):
    """Set flat shading on object."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_flat()
    obj.select_set(False)


def build_cabinet_body(x_offset=0.0, suffix=""):
    """Hollow painted-steel cabinet shell with visible open front."""
    parts = []
    parts.append(make_box(
        suffixed("geo_cabinet_body_left_side", suffix),
        shifted((LEFT_X + PANEL_THICKNESS / 2, 0.0, CABINET_H / 2), x_offset),
        (PANEL_THICKNESS, CABINET_D, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_right_side", suffix),
        shifted((RIGHT_X - PANEL_THICKNESS / 2, 0.0, CABINET_H / 2), x_offset),
        (PANEL_THICKNESS, CABINET_D, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_top", suffix),
        shifted((0.0, 0.0, CABINET_H - PANEL_THICKNESS / 2), x_offset),
        (CABINET_W, CABINET_D, PANEL_THICKNESS),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_bottom", suffix),
        shifted((0.0, 0.0, PANEL_THICKNESS / 2), x_offset),
        (CABINET_W, CABINET_D, PANEL_THICKNESS),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_back", suffix),
        shifted((0.0, BACK_Y - PANEL_THICKNESS / 2, CABINET_H / 2), x_offset),
        (CABINET_W, PANEL_THICKNESS, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    return parts


def build_interior_back_wall(x_offset=0.0, suffix=""):
    """Light-gray interior mounting plate on the inside back wall."""
    return make_box(
        suffixed("geo_interior_back_wall", suffix),
        shifted((0.0, 0.236, 0.764), x_offset),
        (0.790, 0.012, 1.350),
        bevel_segments=1,
        bevel_depth=0.004,
    )


def build_cabinet_door(x_offset=0.0, suffix=""):
    """Open left-hinged front door, swung about 100 degrees around left edge."""
    door_w = 0.86
    door_t = 0.006
    door_h = 1.46
    hinge_x = LEFT_X + x_offset
    hinge_y = FRONT_Y - 0.012

    obj = make_box(
        suffixed("geo_cabinet_door", suffix),
        (hinge_x + door_w / 2, hinge_y, door_h / 2 + 0.020),
        (door_w, door_t, door_h),
        bevel_segments=2,
        bevel_depth=0.008,
    )

    # Move origin to the left hinge edge, then rotate the door open.
    bpy.context.scene.cursor.location = (hinge_x, hinge_y, door_h / 2 + 0.020)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    obj.rotation_euler[2] = math.radians(-100.0)
    return obj


def hinge_point_for_z(z, x_offset=0.0):
    return (LEFT_X - 0.008 + x_offset, FRONT_Y - 0.012, z)


def build_door_hinges(x_offset=0.0, suffix=""):
    """Three vertical barrel hinges on the cabinet's left front edge."""
    hinges = []
    for hinge_suffix, z in [("bot", 0.230), ("mid", 0.750), ("top", 1.270)]:
        hinge = make_cylinder(
            suffixed(f"geo_door_hinge_{hinge_suffix}", suffix),
            hinge_point_for_z(z, x_offset),
            0.016,
            0.110,
            segments=18,
        )
        hinges.append(hinge)
    return hinges


def open_door_local_to_world(local_x, local_y, local_z, x_offset=0.0):
    """Convert closed-door local coordinates to world after the 100 degree swing."""
    hinge = Vector((LEFT_X + x_offset, FRONT_Y - 0.012, 0.0))
    angle = math.radians(-100.0)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x = hinge.x + local_x * cos_a - local_y * sin_a
    y = hinge.y + local_x * sin_a + local_y * cos_a
    return (x, y, local_z)


def build_door_locks(x_offset=0.0, suffix=""):
    """Two screw-type locks on the opened door's free edge."""
    locks = []
    for lock_suffix, z in [("bot", 0.330), ("top", 1.200)]:
        loc = open_door_local_to_world(0.790, -0.008, z, x_offset)
        lock = make_cylinder(
            suffixed(f"geo_door_lock_{lock_suffix}", suffix),
            loc,
            0.014,
            0.030,
            rot=FACE_ROT_Y_AXIS,
            segments=16,
        )
        lock.rotation_euler[2] = math.radians(-100.0)
        locks.append(lock)
    return locks


def build_latch_handle(x_offset=0.0, suffix=""):
    """Black latch handle on the opened door."""
    loc = open_door_local_to_world(0.740, -0.012, 1.160, x_offset)
    obj = make_box(suffixed("geo_latch_handle", suffix), loc, (0.052, 0.012, 0.028), bevel_segments=1, bevel_depth=0.004)
    obj.rotation_euler[2] = math.radians(-100.0)
    return obj


def build_panel_controls(side, x_off, panel_y, panel_z, x_offset=0.0, suffix=""):
    """Add screws, indicators and switches to one internal controller face."""
    controls = []
    for index, (sx, sz) in enumerate([(-0.100, 0.060), (-0.100, -0.060), (0.100, 0.060), (0.100, -0.060)]):
        controls.append(make_cylinder(
            suffixed(f"geo_panel_screw_{side}_{index + 1}", suffix),
            shifted((x_off + sx, panel_y - 0.052, panel_z + sz), x_offset),
            0.0044,
            0.008,
            rot=FACE_ROT_Y_AXIS,
            segments=6,
        ))

    indicators = [
        ("flame_1", -0.060, 0.040),
        ("flame_2", -0.020, 0.040),
        ("flame_3", 0.020, 0.040),
        ("flame_4", 0.060, 0.040),
        ("ignition", 0.040, 0.008),
    ]
    for index, (iname, ix, iz) in enumerate(indicators):
        label = "flame" if "flame" in iname else "ignition"
        controls.append(make_cylinder(
            suffixed(f"geo_indicator_{side}_{label}_{index + 1}", suffix),
            shifted((x_off + ix, panel_y - 0.052, panel_z + iz), x_offset),
            0.006,
            0.006,
            rot=FACE_ROT_Y_AXIS,
            segments=16,
        ))

    controls.append(make_cylinder(
        suffixed(f"geo_rotary_switch_{side}", suffix),
        shifted((x_off, panel_y - 0.052, panel_z - 0.040), x_offset),
        0.024,
        0.020,
        rot=FACE_ROT_Y_AXIS,
        segments=24,
    ))
    controls.append(make_box(
        suffixed(f"geo_switch_pointer_{side}", suffix),
        shifted((x_off, panel_y - 0.052, panel_z - 0.052), x_offset),
        (0.008, 0.006, 0.040),
    ))
    controls.append(make_box(
        suffixed(f"geo_toggle_switch_{side}", suffix),
        shifted((x_off - 0.070, panel_y - 0.052, panel_z - 0.090), x_offset),
        (0.016, 0.014, 0.024),
        bevel_segments=1,
        bevel_depth=0.002,
    ))
    return controls


def build_control_panels(x_offset=0.0, suffix=""):
    """Two identical controller blocks inside the cabinet on the upper DIN rail."""
    panels = []
    panel_y = 0.190
    panel_z = 1.120
    for side, x_off in [("L", -0.140), ("R", 0.140)]:
        frame = make_box(
            suffixed(f"geo_panel_frame_{side}", suffix),
            shifted((x_off, panel_y, panel_z), x_offset),
            (0.250, 0.100, 0.170),
            bevel_segments=1,
            bevel_depth=0.006,
        )
        face = make_box(
            suffixed(f"geo_control_panel_{side}", suffix),
            shifted((x_off, panel_y - 0.050, panel_z), x_offset),
            (0.230, 0.008, 0.150),
            bevel_segments=1,
            bevel_depth=0.004,
        )
        panels.extend([frame, face])
        panels.extend(build_panel_controls(side, x_off, panel_y, panel_z, x_offset, suffix))
    return panels


def build_upper_din_rail(x_offset=0.0, suffix=""):
    """DIN rail supporting the two controller blocks."""
    rail = make_box(suffixed("geo_din_rail_upper", suffix), shifted((0.0, 0.216, 1.120), x_offset), (0.660, 0.020, 0.070))
    shade_flat(rail)
    return rail


def build_din_rail(x_offset=0.0, suffix=""):
    """Scaled Omega-profile DIN rail in the middle zone."""
    rail = make_box(suffixed("geo_din_rail", suffix), shifted((0.0, 0.208, 0.840), x_offset), (0.700, 0.020, 0.070))
    shade_flat(rail)
    return rail


def build_terminal_blocks(x_offset=0.0, suffix=""):
    """Twelve WAGO-style terminal blocks on the middle DIN rail."""
    blocks = []
    for i in range(12):
        x = -0.330 + i * 0.060
        block = make_box(
            suffixed(f"geo_terminal_block_{i + 1:02d}", suffix),
            shifted((x, 0.174, 0.840), x_offset),
            (0.048, 0.060, 0.080),
            bevel_segments=1,
            bevel_depth=0.004,
        )
        blocks.append(block)
    return blocks


def make_tube(name, points, radius=0.0030, bevel_resolution=4):
    """Create a tube (bevelled curve) from a list of (x,y,z) points.
       Uses Bezier curves with automatic handles for smooth bends."""
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = bevel_resolution
    curve_data.use_fill_caps = True

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, (px, py, pz) in enumerate(points):
        pt = spline.bezier_points[i]
        pt.co = (px, py, pz)
        pt.handle_left_type = 'AUTO'
        pt.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj


def build_panel_wires(x_offset=0.0, suffix=""):
    """Wiring: each relay has 2 colored wires coming DOWN from the panel,
       which SMOOTHLY MERGE into a single black trunk over a length (not a sharp Y).
       The colored wires start offset, gradually converge inward over ~60mm,
       then run alongside the trunk for another ~20mm before disappearing into it.
       Plus a main bundle from cable gland rising up the left wall."""

    left_x = -0.450  # cabinet left wall
    panel_y = 0.190  # panel center depth
    panel_bottom_z = 1.036  # bottom edge of panel frames (relay output)
    trunk_start_z = 0.970  # where the trunk begins (higher, closer to panel)
    trunk_end_z = 0.680  # shared merge point for the two black trunks
    merge_complete_z = 0.940  # where colored wires fully converge to trunk center

    # === Main wire bundle: cable exit → up left wall → connect to trunk merge point ===
    bundle_pts = [
        shifted((left_x + 0.040, 0.190, 0.200), x_offset),  # cable exit on left wall
        shifted((left_x + 0.040, 0.190, 0.400), x_offset),  # running up left wall
        shifted((left_x + 0.040, 0.190, 0.560), x_offset),  # still on left wall
        shifted((-0.200, 0.190, 0.620), x_offset),          # curving inward and upward
        shifted((0.0, 0.190, trunk_end_z), x_offset),       # connects directly to trunk merge point
    ]
    make_tube(suffixed("geo_wire_bundle", suffix), bundle_pts, radius=0.014, bevel_resolution=6)

    # === Two colored wires per relay → smooth merge into black trunk ===
    # Each colored wire:
    #   1. Starts offset from panel center (±24mm)
    #   2. Gradually curves inward over ~60mm height
    #   3. Runs alongside the trunk for ~20mm (nearly touching)
    #   4. Disappears into the trunk at merge_complete_z
    #
    # The trunk starts higher and the colored wires merge into it smoothly.

    panel_specs = [
        # (panel_x, trunk_name, w1_name, w1_mat, w1_dx, w2_name, w2_mat, w2_dx)
        (-0.140, "geo_wire_trunk_L", "geo_wire_L1", "mat_wire_red", -0.024, "geo_wire_L2", "mat_wire_blue", 0.024),
        ( 0.140, "geo_wire_trunk_R", "geo_wire_R1", "mat_wire_green", -0.024, "geo_wire_R2", "mat_wire_yellow", 0.024),
    ]

    for panel_x, trunk_name, w1_name, w1_mat, w1_dx, w2_name, w2_mat, w2_dx in panel_specs:
        # Wire 1 (colored): starts offset, gradually curves inward, then merges
        w1_pts = [
            shifted((panel_x + w1_dx, panel_y, panel_bottom_z), x_offset),  # start offset on panel
            shifted((panel_x + w1_dx * 0.65, panel_y, panel_bottom_z - 0.024), x_offset),  # curving inward
            shifted((panel_x + w1_dx * 0.25, panel_y, merge_complete_z + 0.016), x_offset),  # almost at center
            shifted((panel_x, panel_y, merge_complete_z), x_offset),  # merged into trunk
        ]
        make_tube(suffixed(w1_name, suffix), w1_pts, radius=0.0030)

        # Wire 2 (colored): same path on the other side
        w2_pts = [
            shifted((panel_x + w2_dx, panel_y, panel_bottom_z), x_offset),  # start offset on panel
            shifted((panel_x + w2_dx * 0.65, panel_y, panel_bottom_z - 0.024), x_offset),  # curving inward
            shifted((panel_x + w2_dx * 0.25, panel_y, merge_complete_z + 0.016), x_offset),  # almost at center
            shifted((panel_x, panel_y, merge_complete_z), x_offset),  # merged into trunk
        ]
        make_tube(suffixed(w2_name, suffix), w2_pts, radius=0.0030)

        # Trunk (black): starts higher, colored wires merge into it along the way
        trunk_pts = [
            shifted((panel_x, panel_y, trunk_start_z), x_offset),  # top of trunk (near panel bottom)
            shifted((panel_x, panel_y, 0.840), x_offset),          # starts as a relay-specific trunk
            shifted((panel_x * 0.45, panel_y, 0.730), x_offset),   # curves inward toward common merge
            shifted((0.0, panel_y, trunk_end_z), x_offset),        # merged into common trunk
        ]
        make_tube(suffixed(trunk_name, suffix), trunk_pts, radius=0.006)


def build_cable(x_offset=0.0, suffix=""):
    """Black rubber cable exits left wall lower third and descends to pedestal."""
    exit_obj = make_cylinder(
        suffixed("geo_cable_exit", suffix),
        shifted((LEFT_X - 0.008, 0.200, 0.200), x_offset),
        0.018,
        0.036,
        rot=(0.0, math.radians(90), 0.0),
        segments=18,
    )
    hose = make_cylinder(
        suffixed("geo_cable_hose", suffix),
        shifted((LEFT_X - 0.036, 0.200, 0.060), x_offset),
        0.016,
        0.280,
        segments=18,
    )
    rings = []
    for i in range(8):
        z = -0.064 + i * 0.036
        ring = make_cylinder(
            suffixed(f"geo_cable_hose_corrugation_{i + 1:02d}", suffix),
            shifted((LEFT_X - 0.036, 0.200, z), x_offset),
            0.0190,
            0.008,
            segments=18,
        )
        rings.append(ring)
    return [exit_obj, hose] + rings


def build_cabinet(x_offset=0.0, suffix=""):
    """Build one complete cabinet at the requested X offset."""
    existing = set(bpy.data.objects)
    build_cabinet_body(x_offset, suffix)
    build_interior_back_wall(x_offset, suffix)
    build_cabinet_door(x_offset, suffix)
    build_door_hinges(x_offset, suffix)
    build_door_locks(x_offset, suffix)
    build_latch_handle(x_offset, suffix)
    build_upper_din_rail(x_offset, suffix)
    build_control_panels(x_offset, suffix)
    build_din_rail(x_offset, suffix)
    build_terminal_blocks(x_offset, suffix)
    build_panel_wires(x_offset, suffix)
    build_cable(x_offset, suffix)
    move_objects_z([obj for obj in bpy.data.objects if obj not in existing], CABINET_MOUNT_Z_OFFSET)


def duplicate_cabinet(offset_x):
    """Duplicate the cabinet by rebuilding every part with a suffix and X offset."""
    build_cabinet(offset_x, "_2")


def build_support_structure():
    """Outdoor support posts, crossbars, foundations, and ground plane."""
    foundation_size = (0.80, 0.80, 1.20)
    foundation_z = foundation_size[2] / 2
    post_width = 0.32
    post_height = 3.20
    post_z = foundation_size[2] + post_height / 2
    left_post_x = -1.20
    right_post_x = 3.40
    support_y = 0.500
    crossbar_size = 0.12
    crossbar_x = (left_post_x + right_post_x) / 2
    crossbar_length = (right_post_x - left_post_x) - post_width

    make_box("geo_ground", (0.0, 0.0, -0.010), (4.0, 4.0, 0.02))
    for name, x in [("left", left_post_x), ("right", right_post_x)]:
        make_box(
            f"geo_concrete_foundation_{name}",
            (x, support_y, foundation_z),
            foundation_size,
            bevel_segments=1,
            bevel_depth=0.008,
        )
        make_box(
            f"geo_support_post_{name}",
            (x, support_y, post_z),
            (post_width, post_width, post_height),
            bevel_segments=1,
            bevel_depth=0.006,
        )
    make_box(
        "geo_crossbar_upper",
        (crossbar_x, support_y, 3.40),
        (crossbar_length, crossbar_size, crossbar_size),
        bevel_segments=1,
        bevel_depth=0.006,
    )
    make_box(
        "geo_crossbar_lower",
        (crossbar_x, support_y, 1.80),
        (crossbar_length, crossbar_size, crossbar_size),
        bevel_segments=1,
        bevel_depth=0.006,
    )


def build_geometry():
    """Build all geometry objects."""
    build_support_structure()
    build_cabinet()
    duplicate_cabinet(2.20)
    print(f"GEOMETRY_DONE: {len([o for o in bpy.data.objects if o.type in ('MESH', 'CURVE')])} meshes+curves created")


# -------------------------------------------------------------------
# MATERIALS
# -------------------------------------------------------------------

def create_principled(name, color_hex, roughness=0.45, metallic=0.0):
    """Create a Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    r = int(color_hex[1:3], 16) / 255.0
    g = int(color_hex[3:5], 16) / 255.0
    b = int(color_hex[5:7], 16) / 255.0
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def create_bump_material(name, color_hex, roughness=0.45, metallic=0.0, bump_strength=0.035):
    """Create a material with noise bump for painted steel."""
    mat = create_principled(name, color_hex, roughness, metallic)
    if bump_strength > 0:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 50.0
        noise.inputs["Detail"].default_value = 4.0
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_all_materials():
    """Create all PBR materials for the cabinet."""
    materials = {}
    materials["mat_painted_steel"] = create_bump_material(
        "mat_painted_steel", "#D4E4F0", roughness=0.45, metallic=0.3, bump_strength=0.035)
    materials["mat_painted_steel_door"] = create_principled(
        "mat_painted_steel_door", "#D6DBE0", roughness=0.45, metallic=0.3)
    materials["mat_interior_back_wall"] = create_principled(
        "mat_interior_back_wall", "#ECEFF1", roughness=0.42, metallic=0.15)
    materials["mat_galvanized_hinge"] = create_principled(
        "mat_galvanized_hinge", "#888888", roughness=0.3, metallic=0.8)
    materials["mat_black_latch"] = create_principled(
        "mat_black_latch", "#1A1A1A", roughness=0.4, metallic=0.5)
    materials["mat_blue_abs"] = create_principled(
        "mat_blue_abs", "#0033A0", roughness=0.3, metallic=0.1)
    materials["mat_white_faceplate"] = create_principled(
        "mat_white_faceplate", "#F0F0F0", roughness=0.4, metallic=0.0)
    materials["mat_silver_screw"] = create_principled(
        "mat_silver_screw", "#C0C0C0", roughness=0.25, metallic=0.9)
    materials["mat_black_lens"] = create_principled(
        "mat_black_lens", "#1A1A1A", roughness=0.5, metallic=0.0)
    materials["mat_black_knob"] = create_principled(
        "mat_black_knob", "#222222", roughness=0.4, metallic=0.0)
    materials["mat_red_pointer"] = create_principled(
        "mat_red_pointer", "#CC0000", roughness=0.3, metallic=0.1)
    materials["mat_galvanized_rail"] = create_principled(
        "mat_galvanized_rail", "#A8A8A0", roughness=0.35, metallic=0.85)
    materials["mat_terminal_wago"] = create_principled(
        "mat_terminal_wago", "#E0E0DC", roughness=0.5, metallic=0.0)
    materials["mat_black_rubber"] = create_principled(
        "mat_black_rubber", "#1A1A1A", roughness=0.8, metallic=0.0)
    materials["mat_corrugated"] = create_principled(
        "mat_corrugated", "#2A2A2A", roughness=0.7, metallic=0.1)
    materials["mat_black_steel"] = create_principled(
        "mat_black_steel", "#222222", roughness=0.4, metallic=0.3)
    materials["mat_concrete"] = create_principled(
        "mat_concrete", "#808080", roughness=0.95, metallic=0.0)
    materials["mat_ground"] = create_principled(
        "mat_ground", "#4A4A4A", roughness=0.95, metallic=0.0)
    materials["mat_wire_red"] = create_principled(
        "mat_wire_red", "#CC0000", roughness=0.6, metallic=0.0)
    materials["mat_wire_blue"] = create_principled(
        "mat_wire_blue", "#0044AA", roughness=0.6, metallic=0.0)
    materials["mat_wire_green"] = create_principled(
        "mat_wire_green", "#00AA44", roughness=0.6, metallic=0.0)
    materials["mat_wire_yellow"] = create_principled(
        "mat_wire_yellow", "#DDAA00", roughness=0.6, metallic=0.0)
    return materials


def assign_materials(materials):
    """Assign materials to geometry objects by naming convention."""
    mapping = {
        "geo_cabinet_body": "mat_painted_steel",
        "geo_cabinet_door": "mat_painted_steel_door",
        "geo_interior_back_wall": "mat_interior_back_wall",
        "geo_door_hinge": "mat_galvanized_hinge",
        "geo_door_lock": "mat_black_latch",
        "geo_latch_handle": "mat_black_latch",
        "geo_panel_frame": "mat_blue_abs",
        "geo_control_panel": "mat_white_faceplate",
        "geo_panel_screw": "mat_silver_screw",
        "geo_indicator": "mat_black_lens",
        "geo_rotary_switch": "mat_black_knob",
        "geo_switch_pointer": "mat_red_pointer",
        "geo_toggle_switch": "mat_black_knob",
        "geo_din_rail": "mat_galvanized_rail",
        "geo_terminal_block": "mat_terminal_wago",
        "geo_wire_trunk_L": "mat_black_rubber",
        "geo_wire_trunk_R": "mat_black_rubber",
        "geo_wire_L1": "mat_wire_red",
        "geo_wire_L2": "mat_wire_blue",
        "geo_wire_R1": "mat_wire_green",
        "geo_wire_R2": "mat_wire_yellow",
        "geo_wire_bundle": "mat_black_rubber",
        "geo_cable_exit": "mat_black_rubber",
        "geo_cable_hose": "mat_corrugated",
        "geo_support_post": "mat_black_steel",
        "geo_crossbar": "mat_black_steel",
        "geo_concrete_foundation": "mat_concrete",
        "geo_ground": "mat_ground",
    }

    assigned = 0
    for obj in bpy.data.objects:
        if obj.type not in ("MESH", "CURVE"):
            continue
        mat_name = None
        for prefix, candidate in mapping.items():
            if obj.name.startswith(prefix):
                mat_name = candidate
                break
        if mat_name and mat_name in materials:
            obj.data.materials.clear()
            obj.data.materials.append(materials[mat_name])
            assigned += 1
            if obj.name.startswith("geo_din_rail"):
                shade_flat(obj)

    print(f"MATERIALS_ASSIGNED: {assigned}")
    return assigned


# -------------------------------------------------------------------
# CAMERAS & LIGHTS
# -------------------------------------------------------------------

FOCUS_POINT = Vector((0.25, 0.0, 0.55))
CAMERA_FOCAL_LENGTH = 50.0


def create_camera(name, location, target=None):
    """Create a camera with TRACK_TO constraint pointing at target."""
    if target is None:
        target = bpy.data.objects.get("camera_focus_target")

    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = CAMERA_FOCAL_LENGTH
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = location
    bpy.context.collection.objects.link(cam)

    if target:
        constraint = cam.constraints.new(type="TRACK_TO")
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    return cam


def create_lights():
    """Sun + fill light."""
    sun_data = bpy.data.lights.new("light_sun", type="SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("light_sun", sun_data)
    sun.location = (3.0, -2.0, 5.0)
    sun.rotation_euler = (0.785, 0.0, 0.785)
    bpy.context.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("light_fill", type="POINT")
    fill_data.energy = 1.5
    fill = bpy.data.objects.new("light_fill", fill_data)
    fill.location = (-2.0, 3.0, 4.0)
    bpy.context.collection.objects.link(fill)


def setup_world():
    """Set world background color."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.color = (0.15, 0.15, 0.15)


def build_cameras_and_lights():
    """Create scene cameras and lights."""
    target = bpy.data.objects.new("camera_focus_target", None)
    target.empty_display_type = "PLAIN_AXES"
    target.empty_display_size = 0.1
    target.location = FOCUS_POINT
    bpy.context.collection.objects.link(target)

    create_camera("cam_front", (0.25, -2.5, 0.38), target)
    create_camera("cam_fr45", (1.8, -2.0, 0.42), target)
    create_camera("cam_side", (2.5, 0.025, 0.38), target)
    create_camera("cam_top", (0.25, 0.025, 2.8), target)
    create_camera("cam_persp", (1.3, -2.0, 1.1), target)

    bpy.context.scene.camera = bpy.data.objects["cam_persp"]
    create_lights()
    setup_world()
    print("SCENE_DONE")


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

def main():
    print("=== Building Cabinet Scene ===")
    clear_scene()
    build_geometry()
    materials = make_all_materials()
    assign_materials(materials)
    build_cameras_and_lights()
    bpy.ops.wm.save_as_mainfile(filepath=SCENE_PATH)
    print("SCENE_BUILD_DONE")


if __name__ == "__main__":
    main()
