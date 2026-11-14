"""Blender blockout fitted to a canon painting: "Arabiya Ink and Voices".

Run headless with the `bpy` wheel (Python 3.13):
    python blockout_canon.py OUT_DIR [--frames 72] [--passes clay,wire,depth] [--only N,M] [--size 768x512]
    python blockout_canon.py OUT_DIR --overlay assets/PAINTING.png   # frame 0 depth over the painting, to fit
    python blockout_canon.py OUT_DIR --check                         # limb/prop intersections, every frame

The earlier blockouts were modelled from scratch and the video model's
reference was re-staged to match them. This one goes the other way: the
painting is the reference, and every proxy is placed by un-projecting its
pixel position in the painting through the frame-0 camera at a chosen
distance (`at`, `on_table`). So frame 0's depth lines up with the painting,
and the video model starts from art that is already canon.

The camera then moves only a little (a slow arc of +-4 degrees and a 6 %
push-in), so the model stays close to what the painting shows.

Motion, in the 48-unit beat clock (scaled to FRAMES):
  0-8    Mācron finishes the curve stroke with his reed pen.
  8-34   The letter's dot hops off the page: three bounces, lower each time.
  12-30  Mācron looks up at Tlatoāni and lifts his free hand a little; Tlatoāni nods (18-30).
  30-48  Mācron goes back to the page.
  Always: gills sway, the tail swings, the globes and the lantern sway.
The motion and the camera path are cyclic: frame FRAMES is frame 0.
"""
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = args[0]
FRAMES = int(args[args.index("--frames") + 1]) if "--frames" in args else 72
PASSES = args[args.index("--passes") + 1].split(",") if "--passes" in args else ["clay", "wire", "depth"]
ONLY = [int(x) for x in args[args.index("--only") + 1].split(",")] if "--only" in args else None
OVERLAY = args[args.index("--overlay") + 1] if "--overlay" in args else None
assert "depth" not in PASSES or PASSES[-1] == "depth", "depth must be the last pass (it replaces materials)"
W, H = (int(v) for v in (args[args.index("--size") + 1] if "--size" in args else "768x512").split("x"))
NEAR, FAR = 0.6, 5.0                                   # depth range mapped to white..black

PINK, CORAL, CREAM, TEAL, DEEP = (0.953, 0.604, 0.604), (0.925, 0.435, 0.482), (0.937, 0.878, 0.769), (0.153, 0.427, 0.412), (0.071, 0.243, 0.259)
SCREEN, CYAN, GOLD, SHELL = (0.04, 0.05, 0.07), (0.25, 0.95, 0.9), (0.85, 0.7, 0.3), (0.894, 0.831, 0.71)
WOOD, WOOD_D, PAPER, LEAF, LEAF_D, POT, GLASS, SKY = (0.55, 0.36, 0.2), (0.4, 0.25, 0.14), (0.97, 0.96, 0.92), (0.35, 0.55, 0.3), (0.2, 0.4, 0.22), (0.72, 0.4, 0.25), (0.8, 0.9, 0.92), (0.75, 0.85, 0.9)

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
    o.location, o.scale = loc, scale
    o.rotation_euler = rot if isinstance(rot, Euler) else Euler([math.radians(a) for a in rot])
    o.data.materials.append(mat(color))
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width, b.segments = bevel / min(scale), 4           # the bevel works in local (unscaled) units
    if smooth and hasattr(o.data, "polygons"):
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def box(name, loc, size, **kw):
    return obj(bpy.ops.mesh.primitive_cube_add, name, loc, tuple(s / 2 for s in size), smooth=False, size=2, **kw)


def sphere(name, loc, radii, seg=24, **kw):
    return obj(bpy.ops.mesh.primitive_uv_sphere_add, name, loc, radii, segments=seg, ring_count=max(6, seg // 2), radius=1, **kw)


def cyl(name, loc, r, depth, verts=24, **kw):
    return obj(bpy.ops.mesh.primitive_cylinder_add, name, loc, (r, r, depth / 2), vertices=verts, radius=1, depth=2, **kw)


def pivot(name, loc, parent=None, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = rot if isinstance(rot, Euler) else Euler([math.radians(a) for a in rot])
    if parent:
        e.parent = parent
    return e


def aim(p0, p1):
    """Rotation whose local -Z points from p0 to p1."""
    return (p1 - p0).to_track_quat("-Z", "Y").to_euler()


def limb(name, p0, p1, r, color, end=1.2, parent=None):
    """A capsule from p0 to p1, hung on a pivot at p0 (rotate the pivot to move it)."""
    p = pivot(name + "-pivot", p0, rot=aim(p0, p1))
    n = (p1 - p0).length
    cyl(name, (0, 0, -n / 2), r, n, color=color, parent=p)
    if end:
        sphere(name + "-end", (0, 0, -n), (r * end,) * 3, color=color, parent=p)
    if parent:
        reparent(p, parent)
    return p


def reparent(child, parent):
    """Parent while keeping the child's world placement."""
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def quad(name, pts, thick, color):
    """A thin slab through four world points (counter-clockwise from above)."""
    me = bpy.data.meshes.new(name)
    top = [p + Vector((0, 0, thick)) for p in pts]
    me.from_pydata([*pts, *top], [], [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat(color))
    return o


# ---------------------------------------------------------------- the painting's camera
IW, IH = 1264, 848                                     # the painting's pixel grid
F = 1264.0                                             # focal length in painting pixels (53 deg across)
HORIZON_V = 330                                        # the sea line, where the drawing's eye level sits
TABLE_TOP = 0.75
CAM0 = Vector((0, 0, TABLE_TOP + 0.3))                 # 30 cm above the tabletop
PITCH = math.atan((IH / 2 - HORIZON_V) / F)            # looks down a little
FWD = Vector((0, math.cos(PITCH), -math.sin(PITCH)))
UP = Vector((0, math.sin(PITCH), math.cos(PITCH)))
RIGHT = Vector((1, 0, 0))


def ray(u, v):
    return FWD + RIGHT * ((u - IW / 2) / F) + UP * ((IH / 2 - v) / F)


def at(u, v, d):
    """World point seen at painting pixel (u, v), d metres in front of the frame-0 camera."""
    return CAM0 + ray(u, v) * d


def on_table(u, v, z=TABLE_TOP):
    r = ray(u, v)
    return CAM0 + r * ((z - CAM0.z) / r.z)


def px(n, d):
    """n painting pixels at distance d, in metres."""
    return n * d / F


# ---------------------------------------------------------------- table and props
front_y, far_y = on_table(632, 800).y, on_table(632, 590).y
box("tabletop", (0, (front_y + far_y) / 2 + 0.05, TABLE_TOP - 0.03), (3.0, far_y - front_y + 0.25, 0.06), color=WOOD, bevel=0.005)
box("table-front", (0, front_y - 0.03, TABLE_TOP - 0.2), (3.0, 0.06, 0.34), color=WOOD_D)
for x in (-1.1, 1.1):
    box(f"table-leg{x}", (x, front_y + 0.05, TABLE_TOP / 2 - 0.03), (0.09, 0.09, TABLE_TOP - 0.06), color=WOOD_D)


def jar(name, u, v_base, w_px, v_top, color=GLASS):
    b = on_table(u, v_base)
    d = (b - CAM0).dot(FWD)
    r, h = px(w_px, d) / 2, px(v_base - v_top, d)
    cyl(name, b + Vector((0, r, h / 2)), r, h, color=color)
    cyl(name + "-cork", b + Vector((0, r, h + px(18, d))), r * 0.62, px(36, d), color=WOOD)


jar("jar-a", 125, 742, 132, 548)
jar("jar-b", 192, 690, 100, 540)
jar("jar-c", 262, 778, 132, 562)
jar("inkpot", 375, 728, 92, 640, color=DEEP)
paper = quad("paper", [on_table(*p) for p in ((560, 742), (866, 666), (782, 592), (410, 638))], 0.002, PAPER)
quad("scribble", [on_table(*p) for p in ((870, 800), (1116, 690), (1052, 622), (760, 702))], 0.002, PAPER)
x_mid = on_table(490, 762)
for a in (35, -35):
    box(f"x-bar{a}", x_mid + Vector((0, 0, 0.012)), (px(110, 0.95), 0.025, 0.024), rot=(0, 0, a), color=CORAL, bevel=0.004)

# the letter's dot: it rests on the page and hops off it
DOT_REST = on_table(617, 700, TABLE_TOP + 0.002)
DOT_R = 0.02
dot = sphere("dot", DOT_REST + Vector((0, 0, DOT_R)), (DOT_R,) * 3, color=TEAL)

# ---------------------------------------------------------------- Mācron (behind the paper, left)
DM = 1.62                                              # his distance from the camera
s = lambda n: px(n, DM)                                # noqa: E731
mac = pivot("macron", at(488, 600, DM))
mac_neck = pivot("mac-neck", at(488, 470, DM))
reparent(mac_neck, mac)
head_c = at(482, 392, DM)
box("mac-head", head_c, (s(285), s(230), s(225)), color=SHELL, bevel=s(55))
reparent(bpy.data.objects["mac-head"], mac_neck)
scr = at(496, 400, DM - s(118))
box("mac-screen", scr, (s(190), s(14), s(140)), color=SCREEN, bevel=s(28))
reparent(bpy.data.objects["mac-screen"], mac_neck)
for k, u in enumerate((484, 560)):                     # exactly two eyes, marked in the depth pass
    sphere(f"mac-eye{k}", at(u, 417, DM - s(130)), (s(20), s(10), s(30)), color=CYAN)
    reparent(bpy.data.objects[f"mac-eye{k}"], mac_neck)
for k, u in enumerate((352, 612)):
    cyl(f"mac-ear{k}", at(u, 390, DM - s(10)), s(30), s(26), rot=(0, 90, 0), color=TEAL)
    reparent(bpy.data.objects[f"mac-ear{k}"], mac_neck)
limb("mac-antenna", at(490, 282, DM), at(470, 228, DM), s(5), SHELL, end=0)
reparent(bpy.data.objects["mac-antenna-pivot"], mac_neck)
sphere("mac-orb", at(468, 222, DM), (s(18),) * 3, color=CYAN)
reparent(bpy.data.objects["mac-orb"], mac_neck)
box("mac-body", at(490, 545, DM + 0.02), (s(210), s(170), s(160)), color=SHELL, bevel=s(40))
reparent(bpy.data.objects["mac-body"], mac)
sphere("mac-chest", at(505, 545, DM - s(85)), (s(30), s(8), s(30)), color=TEAL)
reparent(bpy.data.objects["mac-chest"], mac)
# right arm (painting left) holds the reed pen; the pen's tip is on the page
HAND_Z = TABLE_TOP + s(26) * 1.2 + 0.01                # the hands rest just above the tabletop
pen_hand = on_table(462, 568, HAND_Z + 0.03)          # the pen hand is lifted, writing
mac_pen_arm = limb("mac-armR", at(395, 485, DM - 0.04), pen_hand, s(26), SHELL)
pen_tip = on_table(548, 640, TABLE_TOP + 0.004)
pen = limb("pen", pen_hand + Vector((0, 0, 0.02)), pen_tip, s(9), GOLD, end=0, parent=mac_pen_arm)
mac_free_arm = limb("mac-armL", at(592, 485, DM - 0.04), on_table(652, 585, HAND_Z), s(26), SHELL)
for a in (mac_pen_arm, mac_free_arm):
    reparent(a, mac)

# ---------------------------------------------------------------- Tlatoāni (behind the table, right)
DT = 1.95
t = lambda n: px(n, DT)                                # noqa: E731
tla = pivot("tlatoani", at(920, 640, DT))
sphere("tla-robe", at(922, 520, DT), (t(185), t(150), t(175)), color=CREAM)
reparent(bpy.data.objects["tla-robe"], tla)
sphere("tla-collar", at(905, 435, DT - t(60)), (t(95), t(40), t(40)), color=TEAL)
reparent(bpy.data.objects["tla-collar"], tla)
tla_neck = pivot("tla-neck", at(905, 420, DT))
reparent(tla_neck, tla)
sphere("tla-head", at(900, 318, DT), (t(152), t(125), t(102)), color=PINK)
reparent(bpy.data.objects["tla-head"], tla_neck)
for k, u in enumerate((785, 917)):
    sphere(f"tla-eye{k}", at(u, 347, DT - t(118)), (t(24), t(10), t(26)), color=SCREEN)
    reparent(bpy.data.objects[f"tla-eye{k}"], tla_neck)
gills = []
for side, roots in ((-1, ((768, 228, 716, 175), (752, 288, 700, 288), (764, 335, 716, 362))),
                    (1, ((1035, 228, 1088, 172), (1058, 290, 1118, 282), (1042, 338, 1095, 362)))):
    for k, (u0, v0, u1, v1) in enumerate(roots):
        g = limb(f"tla-gill{side}{k}", at(u0, v0, DT), at(u1, v1, DT + 0.02), t(24), CORAL, end=1.6)
        reparent(g, tla_neck)
        gills.append((g, g.rotation_euler.copy(), side, k))
tla_arms = {}
for side, (a, b) in (("R", ((790, 445), (818, 492))), ("L", ((1035, 452), (928, 540)))):
    p = limb(f"tla-arm{side}", at(*a, DT - t(80)), at(*b, DT - t(150)), t(26), PINK)
    reparent(p, tla)
    tla_arms[side] = (p, p.rotation_euler.copy())
fork = limb("tla-fork", at(818, 455, DT - t(160)), at(944, 575, DT - t(150)), t(6), GOLD, end=0)
reparent(fork, tla)
tail = []
prev, pts = tla, ((1085, 560), (1130, 520), (1165, 478), (1190, 445))
for i in range(len(pts) - 1):
    seg = limb(f"tla-tail{i}", at(*pts[i], DT + 0.05), at(*pts[i + 1], DT + 0.08), t(46 - 10 * i), PINK, end=1.1)
    reparent(seg, prev)
    tail.append((seg, seg.rotation_euler.copy()))
    prev = seg

# ---------------------------------------------------------------- the greenhouse behind them
box("back", at(632, 424, 7.0), (12, 0.1, 9), color=SKY)
box("floor", (0, 3, 0), (10, 10, 0.02), color=WOOD_D)
for k, (u, v0, v1, d) in enumerate(((268, 0, 560, 2.4), (1062, 0, 520, 2.9))):
    a, b = at(u, v0, d), at(u, v1, d)
    box(f"post{k}", (a + b) / 2, (px(36, d), 0.12, (a - b).length + 0.6), color=WOOD)
for k, (u0, v0, u1, v1, d) in enumerate(((0, 95, 1264, 95, 3.2), (560, 105, 730, 0, 3.0), (0, 60, 320, 0, 2.2), (1264, 60, 960, 0, 2.6))):
    limb(f"beam{k}", at(u0, v0, d), at(u1, v1, d), px(18, d), WOOD, end=0)
for k, (v, d) in enumerate(((232, 2.2), (462, 2.2))):
    a = at(160, v, d)
    box(f"shelf{k}", a, (px(330, d), 0.3, px(14, d)), color=WOOD)
for k, (u, v, w, d) in enumerate(((65, 205, 70, 2.25), (288, 205, 60, 2.25), (275, 430, 70, 2.25), (1225, 620, 70, 1.9), (1105, 470, 60, 2.6))):
    b = at(u, v, d)
    cyl(f"pot{k}", b, px(w, d) / 2, px(w, d) * 0.8, color=POT)
    sphere(f"potplant{k}", b + Vector((0, 0, px(w, d) * 0.9)), (px(w, d) * 0.7,) * 3, color=LEAF)
for k, (u, v, w, h, a, d) in enumerate(((120, 300, 150, 110, 20, 1.35), (195, 360, 150, 120, -15, 1.35), (215, 440, 120, 110, 30, 1.4),
                                         (60, 430, 140, 110, -20, 1.3), (150, 560, 130, 100, 10, 1.35), (40, 260, 110, 90, 35, 1.4))):
    sphere(f"monstera{k}", at(u, v, d), (px(w, d) / 2, 0.02, px(h, d) / 2), rot=(0, a, 0), color=LEAF_D if k % 2 else LEAF)
hangers = []
for k, (u, v, r, d, kind) in enumerate(((190, 170, 72, 1.5, "globe"), (395, 140, 80, 1.9, "log"), (555, 165, 58, 2.0, "globe"),
                                        (965, 115, 40, 2.4, "lantern"), (1180, 150, 75, 1.6, "log"))):
    top = at(u, -20, d)
    hp = pivot(f"hang{k}", top)
    c = at(u, v, d)
    limb(f"string{k}", top, c, 0.004, WOOD_D, end=0, parent=hp)
    if kind == "globe":
        sphere(f"globe{k}", c, (px(r, d),) * 3, color=GLASS, parent=None)
    elif kind == "log":
        sphere(f"globe{k}", c, (px(r, d), px(r, d) * 0.5, px(r, d) * 0.35), rot=(0, -20, 0), color=WOOD)
    else:
        cyl(f"globe{k}", c, px(r, d), px(r * 2.3, d), color=GOLD)
    reparent(bpy.data.objects[f"globe{k}"], hp)
    hangers.append((hp, k))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("cam")
cam_data.sensor_fit, cam_data.sensor_width = "HORIZONTAL", 36.0
cam_data.lens = 36.0 * F / IW
cam_data.clip_start, cam_data.clip_end = 0.05, 30
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
TARGET = at(IW / 2, IH / 2, 1.7)                       # the camera turns around the gap between them


def place_camera(t):
    """Frame 0 is the painting's view; a +-4 degree arc and a 6 % push-in, periodic in t."""
    ph = 2 * math.pi * t / FRAMES
    yaw = math.radians(4 * math.sin(ph))
    push = 0.06 * (0.5 - 0.5 * math.cos(ph))
    off = CAM0 - TARGET
    off.rotate(Euler((0, 0, yaw)))
    cam.location = TARGET + off * (1 - push)
    cam.rotation_euler = Euler((math.pi / 2 - PITCH, 0, yaw))


# ---------------------------------------------------------------- motion
def smooth(a, b, x):
    x = min(max((x - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def bump(a, b, c, d, x):
    return smooth(a, b, x) * (1 - smooth(c, d, x))


BOUNCES = ((8, 20, 0.17), (20, 29, 0.09), (29, 34, 0.04))


def dot_state(u):
    for s0, e, h in BOUNCES:
        if s0 <= u < e:
            v = (u - s0) / (e - s0)
            z = 4 * h * v * (1 - v)
            squash = 1.0 - 0.28 * max(0.0, 1 - v * 6) - 0.28 * max(0.0, 1 - (1 - v) * 6)
            return z, (squash if z < 0.004 else 1.12)
    return 0.0, (0.75 if 34 <= u < 35 else 1.0)


base = {o.name: o.rotation_euler.copy() for o in (mac_neck, mac_pen_arm, mac_free_arm, tla_neck)}


def turn(o, dx=0.0, dy=0.0, dz=0.0):
    b = base[o.name]
    o.rotation_euler = Euler((b.x + math.radians(dx), b.y + math.radians(dy), b.z + math.radians(dz)))


def pose(f):
    tt = f % FRAMES
    u = tt * 48 / FRAMES
    ph = 2 * math.pi * tt / FRAMES
    place_camera(tt)
    z, sz = dot_state(u)
    sxy = 1 / math.sqrt(sz)
    dot.scale = (DOT_R * sxy, DOT_R * sxy, DOT_R * sz)
    dot.location = DOT_REST + Vector((0, 0, z + DOT_R * sz))
    drawing = 1 - bump(7, 10, 36, 40, u)
    look_up = bump(12, 17, 28, 34, u)
    cheer = bump(11, 15, 24, 30, u)
    ring = 2 * math.pi * (u % 8) / 8
    turn(mac_pen_arm, 5 * math.sin(ring) * drawing + 4 * (1 - drawing), 0, 4 * math.cos(ring) * drawing)
    turn(mac_free_arm, 18 * cheer, 0, 0)               # a small lift; a full-arm swing was drawn as a stretched arm
    turn(mac_neck, -10 * look_up + 4 * drawing, 0, -14 * look_up)
    nod = bump(18, 21, 22, 26, u) + 0.6 * bump(24, 26, 27, 30, u)
    turn(tla_neck, 9 * nod, 0, 5 * look_up)
    for g, b, side, k in gills:
        sway = 6 * math.sin(ph * 3 + k * 0.9 + (0 if side > 0 else math.pi / 2))
        g.rotation_euler = Euler((b.x + math.radians(sway), b.y, b.z))
    for i, (seg, b) in enumerate(tail):
        seg.rotation_euler = Euler((b.x, b.y, b.z + math.radians((6 + 2 * i) * math.sin(ph * 2 - 0.5 * i))))
    for hp, k in hangers:
        hp.rotation_euler = Euler((math.radians(1.5 * math.sin(ph * 2 + k)), math.radians(1.5 * math.cos(ph * 2 + 1.7 * k)), 0))


# ---------------------------------------------------------------- passes
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.image_settings.file_format = "PNG"
scene.render.dither_intensity = 0.0                     # a clean depth signal, no noise
world = bpy.data.worlds.new("world")
scene.world = world


def setup(kind):
    sh = scene.display.shading
    if kind != "wire":
        for o in scene.objects:
            if "wire" in o.modifiers:
                o.modifiers.remove(o.modifiers["wire"])
    if kind in ("clay", "wire"):
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.view_settings.view_transform = "Standard"
        sh.type, sh.light, sh.background_type = "SOLID", "STUDIO", "VIEWPORT"
        sh.show_cavity = sh.show_shadows = kind == "clay"
        sh.color_type = "MATERIAL"
        sh.background_color = (0.78, 0.88, 0.95) if kind == "clay" else (0.07, 0.1, 0.12)
        if kind == "wire":
            sh.color_type, sh.light = "OBJECT", "FLAT"
            for o in scene.objects:
                if o.type == "MESH" and "wire" not in o.modifiers:
                    w = o.modifiers.new("wire", "WIREFRAME")
                    w.thickness, w.use_relative_offset = 0.004, False
                    o.color = (0.25, 0.95, 0.9, 1.0)
        return
    scene.render.engine = "BLENDER_EEVEE"
    m = bpy.data.materials.get("depth") or bpy.data.materials.new("depth")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    cd, mr = nt.nodes.new("ShaderNodeCameraData"), nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = NEAR, FAR
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
    em, out = nt.nodes.new("ShaderNodeEmission"), nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(cd.outputs["View Z Depth"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    # Hints the model follows where depth is too faint: Mācron's two eyes and the
    # hopping dot are marked pure white.
    hint = bpy.data.materials.get("hint") or bpy.data.materials.new("hint")
    hint.use_nodes = True
    hn = hint.node_tree
    hn.nodes.clear()
    he, ho = hn.nodes.new("ShaderNodeEmission"), hn.nodes.new("ShaderNodeOutputMaterial")
    he.inputs["Color"].default_value = (1, 1, 1, 1)
    hn.links.new(he.outputs["Emission"], ho.inputs["Surface"])
    for o in scene.objects:
        if o.type == "MESH":
            for slot in o.material_slots:
                slot.material = hint if o.name.startswith(("mac-eye", "dot")) else m
    world.color = (0, 0, 0)
    scene.view_settings.view_transform = "Raw"


def check_clips(frames):
    """Report frames where a moving part cuts into the table or the props."""
    from mathutils.bvhtree import BVHTree

    def tree(o):
        dg = bpy.context.evaluated_depsgraph_get()
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        tr = BVHTree.FromPolygons([o.matrix_world @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
        e.to_mesh_clear()
        return tr

    movers = [o for o in scene.objects if o.type == "MESH" and o.name.startswith(("dot", "pen", "mac-arm", "tla-tail", "tla-arm"))]
    fixed = [o for o in scene.objects if o.type == "MESH" and o.name.startswith(("tabletop", "jar", "inkpot", "x-bar", "scribble"))]
    still = {o.name: tree(o) for o in fixed}
    bad = 0
    for f in frames:
        pose(f)
        bpy.context.view_layer.update()
        for o in movers:
            tr = tree(o)
            for name, st in still.items():
                if tr.overlap(st) and not (o.name.startswith("pen") and name == "tabletop"):
                    bad += 1
                    print(f"clip frame {f:03d}: {o.name} x {name}")
    print(f"clip check: {len(frames)} frames, {len(movers)} movers, {len(fixed)} props, {bad} overlaps")
    return bad


if "--check" in args:
    sys.exit(1 if check_clips(range(FRAMES) if ONLY is None else ONLY) else 0)

if OVERLAY:
    setup("depth")
    pose(0)
    os.makedirs(OUT, exist_ok=True)
    scene.render.filepath = os.path.join(OUT, "fit-depth.png")
    bpy.ops.render.render(write_still=True)
    from PIL import Image
    paint = Image.open(OVERLAY).convert("RGB").resize((W, H), Image.LANCZOS)
    depth = Image.open(scene.render.filepath).convert("RGB")
    Image.blend(paint, depth, 0.5).save(os.path.join(OUT, "fit-overlay.png"))
    print("overlay written")
    sys.exit(0)

for kind in PASSES:
    setup(kind)
    os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    for f in range(FRAMES) if ONLY is None else ONLY:
        pose(f)
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(OUT, kind, f"{f:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("rendered", kind)
