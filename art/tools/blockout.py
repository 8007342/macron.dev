"""Blender blockout of Tlatoāni and Mācron's workshop, with a 48-frame loop.

Run headless with the `bpy` wheel (Python 3.13):
    python blockout.py OUT_DIR [--frames 48] [--passes clay,wire,depth] [--only N]

Everything is real geometry: a greenhouse corner, a table, a stool, a paper
flipbook, a red ball, and simple proxies for both characters, built from the
canon's shapes. Tlatoāni is a round-headed axolotl with six gill fronds, one
tail and a tunic; Mācron is a rounded cream box robot with a dark screen face,
two cyan eyes, side discs, an antenna orb and two arms, sitting on the table.
Contacts are computed rather than eyeballed (the ball rests on the page, hands
rest on the tabletop, Mācron sits on it), so nothing clips.

The motion is a closed loop: frame 48 equals frame 0. Beats:
  0-8    Mācron draws a ring on the page with his pencil.
  8-34   The drawn ball hops off the page: three bounces, lower each time,
         squashing on each contact. Mācron lifts both arms in delight.
  12-30  Mācron turns his face up to Tlatoāni; Tlatoāni nods (18-30).
  30-48  Mācron turns back and draws again; the ball is resting on the page.
  Always: Tlatoāni's gills sway and the tail swings gently.

Passes (one PNG per frame per pass under OUT_DIR/<pass>/):
  clay   Workbench solid shading in the canon's colours (the animatic).
  wire   Workbench wireframe (the "how it was made" view).
  depth  Linear camera depth, near = white (the ControlNet / VACE control).
"""
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

# ---------------------------------------------------------------- arguments
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[0]
FRAMES = int(args[args.index("--frames") + 1]) if "--frames" in args else 48
PASSES = args[args.index("--passes") + 1].split(",") if "--passes" in args else ["clay", "wire", "depth"]
ONLY = int(args[args.index("--only") + 1]) if "--only" in args else None
W, H = 640, 480

# ---------------------------------------------------------------- palette (canon §9, §22)
PINK, CORAL, CREAM, TEAL, DEEP = (0.953, 0.604, 0.604), (0.925, 0.435, 0.482), (0.937, 0.878, 0.769), (0.153, 0.427, 0.412), (0.071, 0.243, 0.259)
SCREEN, CYAN, RED = (0.04, 0.05, 0.07), (0.25, 0.95, 0.9), (0.85, 0.12, 0.12)
WOOD, WOOD_D, FLOOR, PAPER, LEAF, POT, GLASS = (0.55, 0.36, 0.2), (0.4, 0.25, 0.14), (0.86, 0.8, 0.68), (0.97, 0.96, 0.92), (0.35, 0.55, 0.3), (0.72, 0.4, 0.25), (0.8, 0.9, 0.92)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
_mats = {}


def mat(rgb):
    if rgb not in _mats:
        m = bpy.data.materials.new(f"m{len(_mats)}")
        m.diffuse_color = (*rgb, 1.0)
        _mats[rgb] = m
    return _mats[rgb]


def obj(mesh_op, name, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), color=CREAM, parent=None, bevel=0.0, smooth=True, **kw):
    mesh_op(**kw)
    o = bpy.context.active_object
    o.name = name
    o.location, o.scale, o.rotation_euler = loc, scale, Euler([math.radians(a) for a in rot])
    o.data.materials.append(mat(color))
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width, b.segments = bevel, 4
    if smooth and hasattr(o.data, "polygons"):
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def box(name, loc, size, **kw):
    return obj(bpy.ops.mesh.primitive_cube_add, name, loc, tuple(s / 2 for s in size), smooth=False, size=2, **kw)


def sphere(name, loc, radii, **kw):
    return obj(bpy.ops.mesh.primitive_uv_sphere_add, name, loc, radii, segments=24, ring_count=12, radius=1, **kw)


def cyl(name, loc, r, depth, **kw):
    return obj(bpy.ops.mesh.primitive_cylinder_add, name, loc, (r, r, depth / 2), vertices=20, radius=1, depth=2, **kw)


def pivot(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.location = loc
    if parent:
        e.parent = parent
    return e


def capsule(name, length, r, color, parent):
    """A limb hanging down from its pivot (local -Z), ending in a round hand."""
    cyl(name, (0, 0, -length / 2), r, length, color=color, parent=parent)
    sphere(name + "-end", (0, 0, -length), (r * 1.25,) * 3, color=color, parent=parent)


# ---------------------------------------------------------------- the world
TABLE_TOP = 0.79                                     # z of the tabletop surface
box("floor", (0, 1, -0.01), (12, 10, 0.02), color=FLOOR)
for x in (-2.6, -0.4, 1.8):                          # greenhouse posts and beams
    box(f"post{x}", (x, 2.6, 1.5), (0.16, 0.16, 3.0), color=WOOD)
box("beam", (0, 2.6, 2.6), (6.0, 0.16, 0.16), color=WOOD)
box("rafter", (-0.4, 1.4, 2.95), (0.12, 2.6, 0.12), color=WOOD)
box("sill", (0, 2.65, 0.9), (6.0, 0.1, 0.08), color=WOOD_D)
for i, (x, z) in enumerate(((-1.9, 2.15), (-1.45, 1.75), (-1.0, 2.2))):   # hanging glass globes
    cyl(f"string{i}", (x, 2.2, (z + 2.9) / 2), 0.006, 2.9 - z, color=WOOD_D)
    sphere(f"globe{i}", (x, 2.2, z - 0.16), (0.16,) * 3, color=GLASS)
    sphere(f"airplant{i}", (x, 2.2, z - 0.2), (0.09, 0.09, 0.05), color=LEAF)
for i, (x, y, s) in enumerate(((-2.1, -0.6, 1.2), (2.0, 0.9, 1.0), (1.4, 2.2, 0.8))):   # potted plants
    cyl(f"pot{i}", (x, y, 0.18 * s), 0.17 * s, 0.36 * s, color=POT)
    for j in range(5):
        a = j * 72
        obj(bpy.ops.mesh.primitive_cone_add, f"leaf{i}{j}", (x + 0.08 * s * math.cos(math.radians(a)), y + 0.08 * s * math.sin(math.radians(a)), 0.55 * s),
            (0.05 * s, 0.05 * s, 0.32 * s), rot=(18 * math.cos(math.radians(a)), -18 * math.sin(math.radians(a)), 0), color=LEAF, vertices=8)

table = pivot("table", (-0.35, 0.35, 0))
table.rotation_euler = Euler((0, 0, math.radians(-12)))
box("tabletop", (0, 0, TABLE_TOP - 0.04), (1.7, 1.0, 0.08), color=WOOD, parent=table, bevel=0.01)
for sx in (-0.75, 0.75):
    for sy in (-0.42, 0.42):
        box(f"leg{sx}{sy}", (sx, sy, (TABLE_TOP - 0.08) / 2), (0.09, 0.09, TABLE_TOP - 0.08), color=WOOD_D, parent=table)

# flipbook, open on the table (in table space)
BOOK = Vector((0.02, -0.08, TABLE_TOP))
PAGE_T = 0.012
box("page-left", BOOK + Vector((-0.085, 0, PAGE_T / 2)), (0.16, 0.22, PAGE_T), color=PAPER, parent=table)
box("page-right", BOOK + Vector((0.085, 0, PAGE_T / 2)), (0.16, 0.22, PAGE_T), color=PAPER, parent=table)
box("spine", BOOK + Vector((0, 0, PAGE_T / 2)), (0.012, 0.225, PAGE_T * 1.4), color=TEAL, parent=table)
BALL_R = 0.042
BALL_REST = BOOK + Vector((-0.09, -0.05, PAGE_T))     # ball's contact point: left page, toward the viewer, clear of Mācron
ball = sphere("ball", BALL_REST + Vector((0, 0, BALL_R)), (BALL_R,) * 3, color=RED, parent=table)

# ---------------------------------------------------------------- Mācron (sits on the table, behind the book)
mac = pivot("macron", (0.07, 0.24, TABLE_TOP), parent=table)
mac.rotation_euler = Euler((0, 0, math.radians(8)))
mac.scale = (1.35, 1.35, 1.35)  # still far smaller than Tlatoāni, but readable at 640 px
box("mac-body", (0, 0, 0.065), (0.13, 0.11, 0.13), color=CREAM, parent=mac, bevel=0.025)
box("mac-belly", (0, -0.056, 0.06), (0.06, 0.004, 0.05), color=TEAL, parent=mac)
for sx in (-0.04, 0.04):                              # short legs, feet on the tabletop
    cyl(f"mac-leg{sx}", (sx, -0.04, 0.02), 0.022, 0.04, color=CREAM, parent=mac, rot=(90, 0, 0))
neck = pivot("mac-neck", (0, 0, 0.13), parent=mac)
box("mac-head", (0, 0, 0.085), (0.2, 0.16, 0.16), color=CREAM, parent=neck, bevel=0.04)
box("mac-screen", (0, -0.078, 0.085), (0.15, 0.01, 0.105), color=SCREEN, parent=neck, bevel=0.02)
for sx in (-0.032, 0.032):
    sphere(f"mac-eye{sx}", (sx, -0.084, 0.092), (0.014, 0.006, 0.02), color=CYAN, parent=neck)
for sx in (-0.105, 0.105):
    cyl(f"mac-disc{sx}", (sx, 0, 0.085), 0.035, 0.02, rot=(0, 90, 0), color=CREAM, parent=neck)
cyl("mac-antenna", (0, 0, 0.19), 0.005, 0.05, color=CREAM, parent=neck)
sphere("mac-orb", (0, 0, 0.225), (0.018,) * 3, color=(0.85, 0.97, 0.95), parent=neck)
mac_arms = {}
for side, sx in (("L", -0.078), ("R", 0.078)):
    p = pivot(f"mac-shoulder{side}", (sx, -0.01, 0.105), parent=mac)
    capsule(f"mac-arm{side}", 0.085, 0.022, CREAM if side == "L" else TEAL, p)  # modular right arm carries the teal accent
    mac_arms[side] = p
# thick enough to register in the depth pass, so the video model is told the pencil is there
pencil = cyl("pencil", (0, -0.025, -0.105), 0.011, 0.11, rot=(-60, 0, 0), color=(0.95, 0.75, 0.2), parent=mac_arms["R"])

# ---------------------------------------------------------------- Tlatoāni (on a stool, right of the table)
box("stool-top", (0.66, -0.12, 0.43), (0.34, 0.34, 0.05), color=WOOD, bevel=0.01)
for sx in (-0.13, 0.13):
    for sy in (-0.13, 0.13):
        box(f"stool-leg{sx}{sy}", (0.66 + sx, -0.12 + sy, 0.2), (0.04, 0.04, 0.41), color=WOOD_D)
tla = pivot("tlatoani", (0.68, -0.12, 0.455))
tla.rotation_euler = Euler((0, 0, math.radians(-30)))  # turned toward the book and the viewer
sphere("tla-body", (0, 0, 0.27), (0.21, 0.18, 0.27), color=PINK, parent=tla)
sphere("tla-tunic", (0, 0, 0.2), (0.225, 0.195, 0.22), color=CREAM, parent=tla)
cyl("tla-hem", (0, 0, 0.03), 0.2, 0.04, color=TEAL, parent=tla)
for sx in (-0.09, 0.09):                              # legs hang over the stool's front edge
    l = pivot(f"tla-hip{sx}", (sx, -0.1, 0.05), parent=tla)
    l.rotation_euler = Euler((math.radians(25), 0, 0))
    capsule(f"tla-leg{sx}", 0.3, 0.05, PINK, l)
tail_root = pivot("tla-tail", (0.0, 0.17, 0.12), parent=tla)
tail_segs = []
prev = tail_root
for i in range(5):                                    # one tail: a tapering chain of segments
    seg = pivot(f"tla-tail{i}", (0, 0.07 if i else 0, -0.02 if i else 0), parent=prev)
    sphere(f"tla-tailseg{i}", (0, 0.04, 0), (0.09 - 0.014 * i, 0.06, 0.06 - 0.007 * i), color=PINK, parent=seg)
    tail_segs.append(seg)
    prev = seg
head = pivot("tla-neck", (0, -0.02, 0.5), parent=tla)
sphere("tla-head", (0, 0, 0.15), (0.29, 0.24, 0.21), color=PINK, parent=head)
for sx in (-0.1, 0.1):
    sphere(f"tla-eye{sx}", (sx, -0.225, 0.18), (0.022, 0.012, 0.026), color=(0.08, 0.06, 0.06), parent=head)
    sphere(f"tla-cheek{sx}", (sx * 1.35, -0.205, 0.11), (0.03, 0.01, 0.02), color=CORAL, parent=head)
gills = []
for side in (-1, 1):                                  # three feathery fronds per side
    for k, ang in enumerate((40, 5, -30)):
        g = pivot(f"tla-gill{side}{k}", (side * 0.25, 0.02, 0.17 + 0.05 * math.sin(math.radians(ang))), parent=head)
        g.rotation_euler = Euler((0, math.radians(side * (90 - ang)), 0))
        sphere(f"tla-frond{side}{k}", (0, 0, 0.09), (0.035, 0.02, 0.1), color=CORAL, parent=g)
        gills.append((g, side, ang, k))
tla_arms = {}
for side, sx in (("L", -0.19), ("R", 0.19)):
    p = pivot(f"tla-shoulder{side}", (sx, -0.05, 0.42), parent=tla)
    capsule(f"tla-arm{side}", 0.24, 0.045, PINK, p)
    cyl(f"tla-sleeve{side}", (0, 0, -0.05), 0.058, 0.1, color=CREAM, parent=p)
    sphere(f"tla-cuff{side}", (0, 0, -0.1), (0.06, 0.06, 0.012), color=TEAL, parent=p)
    tla_arms[side] = p

# ---------------------------------------------------------------- camera and light
cam_data = bpy.data.cameras.new("cam")
cam_data.lens, cam_data.sensor_width = 30, 36
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.12, -1.85, 1.45)
look = Vector((0.14, 0.25, 0.9)) - cam.location
cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
scene.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.rotation_euler = Euler((math.radians(50), math.radians(20), math.radians(-30)))
scene.collection.objects.link(sun)

# ---------------------------------------------------------------- motion


def smooth(a, b, t):
    """0 before a, 1 after b, smoothstep between."""
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def bump(a, b, c, d, t):
    """Rises a→b, holds, falls c→d."""
    return smooth(a, b, t) * (1 - smooth(c, d, t))


BOUNCES = ((8, 20, 0.2), (20, 29, 0.11), (29, 34, 0.045))   # (start, end, apex height) of each hop


def ball_state(t):
    for s, e, h in BOUNCES:
        if s <= t < e:
            u = (t - s) / (e - s)
            z = 4 * h * u * (1 - u)
            squash = 1.0 - 0.28 * max(0.0, 1 - abs(u) * 6) - 0.28 * max(0.0, 1 - abs(1 - u) * 6)
            stretch = 1.0 + 0.18 * min(1.0, z / 0.08) * (1 if h > 0.1 else 0.5)
            return z, (squash if z < 0.01 else stretch)
    # the landing frame after the last hop gets one squash frame
    return 0.0, (0.75 if 34 <= t < 35 else 1.0)


def pose(f):
    t = f % FRAMES
    ph = 2 * math.pi * t / FRAMES
    # ball: hops straight up off its drawing; scale z keeps the bottom on the page (no clipping)
    z, sz = ball_state(t)
    sxy = 1 / math.sqrt(sz)
    ball.scale = (BALL_R * sxy, BALL_R * sxy, BALL_R * sz)
    ball.location = BALL_REST + Vector((0, 0, z + BALL_R * sz))
    # Mācron
    drawing = 1 - bump(7, 10, 36, 40, t)                      # 1 while drawing, 0 while watching
    delight = bump(9, 13, 24, 30, t)                          # arms up as the ball hops
    look_up = bump(12, 17, 28, 34, t)                         # face turns up to Tlatoāni
    ring = 2 * math.pi * (t % 8) / 8
    rx = math.radians(-55 * drawing - 160 * delight + 6 * math.sin(ring) * drawing)
    rz = math.radians(-10 * drawing + 8 * math.cos(ring) * drawing)
    mac_arms["R"].rotation_euler = Euler((rx, math.radians(-15 * delight), rz))
    mac_arms["L"].rotation_euler = Euler((math.radians(-20 - 140 * delight), math.radians(20 * delight), math.radians(10)))
    neck.rotation_euler = Euler((math.radians(-18 * drawing + 16 * look_up), 0, math.radians(32 * look_up)))
    # Tlatoāni
    nod = bump(18, 21, 22, 26, t) + 0.6 * bump(24, 26, 27, 30, t)
    head.rotation_euler = Euler((math.radians(-14 * nod - 4 * drawing), 0, math.radians(-8 + 10 * look_up)))
    for g, side, ang, k in gills:
        sway = 7 * math.sin(ph * 2 + k * 0.9 + (0 if side > 0 else math.pi / 2))
        g.rotation_euler = Euler((math.radians(sway), math.radians(side * (90 - ang)), 0))
    for i, seg in enumerate(tail_segs):
        seg.rotation_euler = Euler((math.radians(-14 if i == 0 else -6), 0, math.radians((10 + 3 * i) * math.sin(ph - 0.5 * i))))
    point = bump(10, 14, 26, 32, t)                           # left hand rises toward the hopping ball
    tla_arms["L"].rotation_euler = Euler((math.radians(-62 - 35 * point), 0, math.radians(-38 - 12 * point)))
    tla_arms["R"].rotation_euler = Euler((math.radians(-25), 0, math.radians(18)))


# ---------------------------------------------------------------- render passes
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
world = bpy.data.worlds.new("world")
scene.world = world


def setup(kind):
    s = scene.display.shading
    if kind != "wire":
        for o in scene.objects:
            if "wire" in o.modifiers:
                o.modifiers.remove(o.modifiers["wire"])
    if kind in ("clay", "wire"):
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.view_settings.view_transform = "Standard"
        scene.view_layers[0].material_override = None
        s.light = "STUDIO"
        s.show_cavity = kind == "clay"
        s.show_shadows = kind == "clay"
        s.color_type = "MATERIAL" if kind == "clay" else "SINGLE"
        s.background_type = "VIEWPORT"
        s.background_color = (0.96, 0.93, 0.86) if kind == "clay" else (0.07, 0.1, 0.12)
        s.type = "SOLID"
        if kind == "wire":  # Workbench cannot render its wireframe view; a Wireframe modifier can
            s.color_type, s.light = "OBJECT", "FLAT"
            for o in scene.objects:
                if o.type == "MESH" and "wire" not in o.modifiers:
                    w = o.modifiers.new("wire", "WIREFRAME")
                    w.thickness, w.use_relative_offset = 0.007, False
                    o.color = (0.25, 0.95, 0.9, 1.0)
    else:  # depth: emission = 1 at 1.2 m from the camera, 0 at 4.2 m
        scene.render.engine = "BLENDER_EEVEE"
        m = bpy.data.materials.get("depth") or bpy.data.materials.new("depth")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 1.2, 4.2
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
        em = nt.nodes.new("ShaderNodeEmission")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(cd.outputs["View Z Depth"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        scene.view_layers[0].material_override = m
        world.color = (0, 0, 0)
        scene.view_settings.view_transform = "Raw"  # linear depth, no display curve


for kind in PASSES:
    setup(kind)
    os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    for f in range(FRAMES) if ONLY is None else [ONLY]:
        pose(f)
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(OUT, kind, f"{f:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("rendered", kind)
