"""Blender blockout v3: the full greenhouse terrace, a moving camera, a 72-frame loop.

Run headless with the `bpy` wheel (Python 3.13):
    python blockout_room.py OUT_DIR [--frames 72] [--passes clay,wire,depth] [--only N] [--size 768x576]
    python blockout_room.py OUT_DIR --check     # report limb/prop intersections in every frame, render nothing

The room follows the canon's greenhouse terrace (the "Chess Tlatoāni vs Mācron"
picture): a round wooden table with a runner, tiered plant shelves on both
sides, a low back parapet open to the sea view, a pergola of posts, beams and
rafters, hanging glass globes with air plants, a lantern, vines, potted plants
and foreground leaves. Tlatoāni sits on a stool at the left of the table;
Mācron sits on the tabletop behind an open flipbook. Contacts are computed
(Mācron's feet on the tabletop, the ball's squash keeps it on the page, the
table's rim clears Tlatoāni's tunic, his legs hang in front of the stool), and
`--check` tests his legs and tail against the stool and the table in every frame.

The camera makes a slow arc around the table, pushing in at mid-loop. It is a
closed loop (frame FRAMES equals frame 0), and so is every motion. Beats, in
the units of the 48-frame v2 loop (scaled to FRAMES):
  0-8    Mācron draws a ring on the page with his pencil.
  8-34   The drawn ball hops off the page: three bounces, lower each time.
  12-30  Mācron looks up at Tlatoāni; Tlatoāni points and nods (18-30).
  30-48  Mācron goes back to drawing.
  Always: Tlatoāni's gills sway, the tail swings, the globes and vines sway.

Passes (one PNG per frame per pass under OUT_DIR/<pass>/): clay, wire, depth
(linear camera depth, near = white: the VACE control).
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
assert "depth" not in PASSES or PASSES[-1] == "depth", "depth must be the last pass (it replaces materials)"
W, H = (int(v) for v in (args[args.index("--size") + 1] if "--size" in args else "768x576").split("x"))
NEAR, FAR = 1.0, 6.0                                  # depth range mapped to white..black

PINK, CORAL, CREAM, TEAL, DEEP = (0.953, 0.604, 0.604), (0.925, 0.435, 0.482), (0.937, 0.878, 0.769), (0.153, 0.427, 0.412), (0.071, 0.243, 0.259)
SCREEN, CYAN, RED, GOLD = (0.04, 0.05, 0.07), (0.25, 0.95, 0.9), (0.85, 0.12, 0.12), (0.95, 0.75, 0.2)
WOOD, WOOD_D, TILE, PAPER, LEAF, LEAF_D, POT, GLASS, STONE = (0.55, 0.36, 0.2), (0.4, 0.25, 0.14), (0.78, 0.55, 0.4), (0.97, 0.96, 0.92), (0.35, 0.55, 0.3), (0.2, 0.4, 0.22), (0.72, 0.4, 0.25), (0.8, 0.9, 0.92), (0.85, 0.8, 0.7)

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
        b.width, b.segments = bevel, 3
    if smooth and hasattr(o.data, "polygons"):
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def box(name, loc, size, **kw):
    return obj(bpy.ops.mesh.primitive_cube_add, name, loc, tuple(s / 2 for s in size), smooth=False, size=2, **kw)


def sphere(name, loc, radii, seg=20, **kw):
    return obj(bpy.ops.mesh.primitive_uv_sphere_add, name, loc, radii, segments=seg, ring_count=max(6, seg // 2), radius=1, **kw)


def cyl(name, loc, r, depth, verts=20, **kw):
    return obj(bpy.ops.mesh.primitive_cylinder_add, name, loc, (r, r, depth / 2), vertices=verts, radius=1, depth=2, **kw)


def cone(name, loc, r, depth, **kw):
    return obj(bpy.ops.mesh.primitive_cone_add, name, loc, (r, r, depth / 2), vertices=10, radius1=1, depth=2, **kw)


def pivot(name, loc, parent=None, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.location, e.rotation_euler = loc, Euler([math.radians(a) for a in rot])
    if parent:
        e.parent = parent
    return e


def capsule(name, length, r, color, parent):
    cyl(name, (0, 0, -length / 2), r, length, color=color, parent=parent)
    sphere(name + "-end", (0, 0, -length), (r * 1.25,) * 3, color=color, parent=parent)


def plant(name, x, y, z, s, n=7, color=LEAF):
    """A pot with a fan of leaves; z is the surface it stands on."""
    cyl(f"{name}-pot", (x, y, z + 0.13 * s), 0.13 * s, 0.26 * s, color=POT)
    cyl(f"{name}-rim", (x, y, z + 0.26 * s), 0.145 * s, 0.03 * s, color=POT)
    for j in range(n):
        a = j * 360 / n + 13 * (hash(name) % 7)
        tilt = 25 + 20 * ((j * 7) % 3) / 2
        cone(f"{name}-leaf{j}", (x + 0.07 * s * math.cos(math.radians(a)), y + 0.07 * s * math.sin(math.radians(a)), z + 0.45 * s),
             0.05 * s, 0.4 * s, rot=(tilt * math.cos(math.radians(a + 90)) * -1, tilt * math.sin(math.radians(a + 90)), 0),
             color=color if j % 2 else LEAF_D)


# ---------------------------------------------------------------- the terrace
box("floor", (0, 1.5, -0.01), (14, 14, 0.02), color=TILE)
box("parapet", (0, 2.9, 0.45), (7.0, 0.25, 0.9), color=STONE)
box("parapet-cap", (0, 2.9, 0.92), (7.1, 0.32, 0.06), color=STONE)
for x in (-2.7, -0.9, 0.9, 2.7):                      # pergola posts on the parapet line
    box(f"post{x}", (x, 2.75, 1.45), (0.16, 0.16, 2.9), color=WOOD, bevel=0.01)
box("beam-back", (0, 2.75, 2.85), (6.0, 0.18, 0.18), color=WOOD)
box("beam-front", (0, 0.2, 2.85), (6.0, 0.18, 0.18), color=WOOD)
for x in (-2.7, -1.35, 0.0, 1.35, 2.7):               # rafters over the table
    box(f"rafter{x}", (x, 1.45, 2.98), (0.12, 3.2, 0.1), color=WOOD_D)
for i, x in enumerate((-2.2, -1.55, -0.6, 0.45, 1.5, 2.25)):   # vines hanging from the back beam
    for k in range(7 + (i % 3) * 2):
        sphere(f"vine{i}-{k}", (x + 0.04 * (1 if k % 2 else -1), 2.62, 2.75 - 0.1 * k), (0.075, 0.012, 0.035), seg=8,
               rot=(0, 35 if k % 2 else -35, 0), color=LEAF if k % 2 else LEAF_D)   # leaves, alternating

for side, x0 in (("L", -2.35), ("R", 1.55)):           # tiered plant shelves, both sides
    for tier, z in enumerate((0.35, 0.85, 1.35)):
        box(f"shelf{side}{tier}", (x0 + 0.4, 2.35 - 0.12 * tier, z), (1.2, 0.36, 0.04), color=WOOD)
        for k in range(3):
            plant(f"shelf{side}{tier}{k}", x0 + 0.02 + 0.38 * k, 2.35 - 0.12 * tier, z + 0.02, 0.55 + 0.1 * ((k + tier) % 2), n=5)
    for sx in (0, 0.8):
        box(f"shelf{side}post{sx}", (x0 + sx, 2.3, 0.75), (0.05, 0.05, 1.5), color=WOOD_D)

for i, (x, y, s) in enumerate(((-1.95, 0.4, 1.4), (1.75, 0.7, 1.3), (-1.4, 1.9, 1.0), (1.15, 1.9, 0.9))):   # potted floor plants
    plant(f"floor{i}", x, y, 0.0, s, n=8)

globes = []
for i, (x, y, z) in enumerate(((-1.25, 0.9, 2.05), (-0.35, 1.5, 2.25), (0.55, 0.85, 2.0), (1.35, 1.5, 2.2))):   # hanging glass globes
    g = pivot(f"globe{i}", (x, y, 2.9))
    cyl(f"globe-string{i}", (0, 0, -(2.9 - z) / 2), 0.006, 2.9 - z, verts=6, color=WOOD_D, parent=g)
    sphere(f"globe-glass{i}", (0, 0, z - 2.9 - 0.18), (0.18,) * 3, color=GLASS, parent=g)
    sphere(f"globe-plant{i}", (0, 0, z - 2.9 - 0.22), (0.11, 0.11, 0.06), seg=10, color=LEAF, parent=g)
    globes.append((g, i))
lantern = pivot("lantern", (0.95, 1.1, 2.9))
cyl("lantern-string", (0, 0, -0.35), 0.006, 0.7, verts=6, color=WOOD_D, parent=lantern)
cyl("lantern-body", (0, 0, -0.85), 0.12, 0.3, color=GOLD, parent=lantern)
cone("lantern-cap", (0, 0, -0.65), 0.15, 0.1, color=WOOD_D, parent=lantern)
globes.append((lantern, 4))

# ---------------------------------------------------------------- round table, runner and clutter
TABLE = Vector((-0.05, 0.45, 0))
TABLE_TOP, TABLE_R = 0.74, 0.55
table = pivot("table", TABLE)
cyl("tabletop", (0, 0, TABLE_TOP - 0.035), TABLE_R, 0.07, verts=40, color=WOOD, parent=table, bevel=0.01)
cyl("pedestal", (0, 0, (TABLE_TOP - 0.07) / 2), 0.07, TABLE_TOP - 0.07, color=WOOD_D, parent=table)
for a in (90, 210, 330):
    box(f"foot{a}", (0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a)), 0.04), (0.45, 0.07, 0.08), rot=(0, 0, a), color=WOOD_D, parent=table)
box("runner", (0, 0, TABLE_TOP + 0.003), (0.35, 1.1, 0.006), rot=(0, 0, 20), color=TEAL, parent=table)
for i, (x, y, h) in enumerate(((-0.25, 0.3, 0.05), (-0.25, 0.3, 0.04))):          # two stacked books
    box(f"book{i}", (x, y, TABLE_TOP + 0.006 + 0.045 * i + h / 2), (0.2 - 0.02 * i, 0.14, h), rot=(0, 0, 10 + 15 * i), color=(DEEP, CORAL)[i], parent=table)
cyl("jar", (0.42, 0.3, TABLE_TOP + 0.08), 0.05, 0.16, color=GLASS, parent=table)
cyl("mug", (-0.32, -0.12, TABLE_TOP + 0.045), 0.04, 0.09, color=CREAM, parent=table)

# the flipbook sits in front of Mācron (table space)
MAC = Vector((0.36, 0.06, TABLE_TOP))
MAC_YAW = -37                                         # turned to face the book, Tlatoāni and the viewer
front = Vector((math.sin(math.radians(MAC_YAW)), -math.cos(math.radians(MAC_YAW)), 0))
book = pivot("flipbook", MAC + front * 0.25, parent=table, rot=(0, 0, MAC_YAW))
PAGE_T = 0.012
box("page-left", (-0.085, 0, PAGE_T / 2), (0.16, 0.22, PAGE_T), color=PAPER, parent=book)
box("page-right", (0.085, 0, PAGE_T / 2), (0.16, 0.22, PAGE_T), color=PAPER, parent=book)
box("spine", (0, 0, PAGE_T / 2), (0.012, 0.225, PAGE_T * 1.4), color=TEAL, parent=book)
BALL_R = 0.06
BALL_REST = Vector((-0.09, -0.04, PAGE_T))
ball = sphere("ball", BALL_REST + Vector((0, 0, BALL_R)), (BALL_R,) * 3, color=RED, parent=book)

# ---------------------------------------------------------------- Mācron (on the tabletop, behind the book)
mac = pivot("macron", MAC, parent=table, rot=(0, 0, MAC_YAW))
mac.scale = (1.7, 1.7, 1.7)
box("mac-body", (0, 0, 0.065), (0.13, 0.11, 0.13), color=CREAM, parent=mac, bevel=0.025)
box("mac-belly", (0, -0.056, 0.06), (0.06, 0.004, 0.05), color=TEAL, parent=mac)
for sx in (-0.04, 0.04):
    cyl(f"mac-leg{sx}", (sx, -0.04, 0.02), 0.022, 0.04, color=CREAM, parent=mac, rot=(90, 0, 0))
neck = pivot("mac-neck", (0, 0, 0.13), parent=mac)
box("mac-head", (0, 0, 0.085), (0.2, 0.16, 0.16), color=CREAM, parent=neck, bevel=0.04)
box("mac-screen", (0, -0.078, 0.085), (0.15, 0.01, 0.105), color=SCREEN, parent=neck, bevel=0.02)
for sx in (-0.04, 0.04):                            # exactly two eyes, raised so the depth pass shows them
    sphere(f"mac-eye{sx}", (sx, -0.09, 0.09), (0.018, 0.014, 0.024), color=CYAN, parent=neck)
for sx in (-0.105, 0.105):
    cyl(f"mac-disc{sx}", (sx, 0, 0.085), 0.035, 0.02, rot=(0, 90, 0), color=CREAM, parent=neck)
cyl("mac-antenna", (0, 0, 0.19), 0.005, 0.05, color=CREAM, parent=neck)
sphere("mac-orb", (0, 0, 0.225), (0.018,) * 3, color=(0.85, 0.97, 0.95), parent=neck)
mac_arms = {}
for side, sx in (("L", -0.078), ("R", 0.078)):
    p = pivot(f"mac-shoulder{side}", (sx, -0.01, 0.105), parent=mac)
    capsule(f"mac-arm{side}", 0.085, 0.022, CREAM if side == "L" else TEAL, p)
    mac_arms[side] = p
pencil = cyl("pencil", (0, -0.025, -0.105), 0.011, 0.11, rot=(-60, 0, 0), color=GOLD, parent=mac_arms["R"])

# ---------------------------------------------------------------- Tlatoāni (on a stool, left of the table)
TLA = Vector((-0.92, 0.3, 0))
SEAT = 0.455                                          # stool-top height: Tlatoāni's hips rest here
stool = pivot("stool", TLA, rot=(0, 0, 32))             # turned with him, so his legs leave over its front edge
box("stool-top", (0, 0, SEAT - 0.025), (0.36, 0.36, 0.05), color=WOOD, bevel=0.01, parent=stool)
for sx in (-0.14, 0.14):
    for sy in (-0.14, 0.14):
        box(f"stool-leg{sx}{sy}", (sx, sy, 0.2), (0.04, 0.04, 0.41), color=WOOD_D, parent=stool)
tla = pivot("tlatoani", TLA + Vector((0, 0, SEAT)), rot=(0, 0, 32))   # faces the book and the viewer
sphere("tla-body", (0, 0, 0.27), (0.21, 0.18, 0.27), color=PINK, parent=tla)
sphere("tla-tunic", (0, 0, 0.2), (0.225, 0.195, 0.22), color=TEAL, parent=tla)
cyl("tla-hem", (0, 0, 0.03), 0.2, 0.04, color=CREAM, parent=tla)
# Seated: thighs run forward along the seat top, and the shins hang in front of its edge
# (the seat's front edge is at y = -0.18 here; the knees are past it at y = -0.26).
for sx in (-0.09, 0.09):
    l = pivot(f"tla-hip{sx}", (sx, -0.08, 0.055), parent=tla, rot=(-90, 0, 0))
    capsule(f"tla-leg{sx}", 0.18, 0.05, PINK, l)
    k = pivot(f"tla-knee{sx}", (sx, -0.26, 0.055), parent=tla, rot=(-12, 0, 0))
    capsule(f"tla-shin{sx}", 0.17, 0.045, PINK, k)
tail_root = pivot("tla-tail", (0.0, 0.17, 0.12), parent=tla)
tail_segs, prev = [], tail_root
for i in range(5):
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
for side in (-1, 1):
    for k, ang in enumerate((40, 5, -30)):
        g = pivot(f"tla-gill{side}{k}", (side * 0.25, 0.02, 0.17 + 0.05 * math.sin(math.radians(ang))), parent=head)
        g.rotation_euler = Euler((0, math.radians(side * (90 - ang)), 0))
        sphere(f"tla-frond{side}{k}", (0, 0, 0.1), (0.036, 0.02, 0.11), color=CORAL, parent=g)
        gills.append((g, side, ang, k))
tla_arms = {}
for side, sx in (("L", -0.19), ("R", 0.19)):
    p = pivot(f"tla-shoulder{side}", (sx, -0.05, 0.42), parent=tla)
    capsule(f"tla-arm{side}", 0.24, 0.045, PINK, p)
    cyl(f"tla-sleeve{side}", (0, 0, -0.05), 0.058, 0.1, color=TEAL, parent=p)
    sphere(f"tla-cuff{side}", (0, 0, -0.1), (0.06, 0.06, 0.012), color=CREAM, parent=p)
    tla_arms[side] = p

# foreground leaves (parallax as the camera moves)
plant("fg-left", -1.3, -0.95, 0.0, 1.35, n=9)
plant("fg-right", 0.5, -1.05, 0.0, 1.2, n=8)

# ---------------------------------------------------------------- camera and light
cam_data = bpy.data.cameras.new("cam")
cam_data.lens, cam_data.sensor_width, cam_data.sensor_fit = 32, 36, "HORIZONTAL"
cam_data.clip_start = 0.1
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
TARGET = Vector((-0.3, 0.4, 0.92))
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.rotation_euler = Euler((math.radians(50), math.radians(20), math.radians(-30)))
scene.collection.objects.link(sun)


def place_camera(t):
    """A slow arc around the table that pushes in mid-loop; periodic in t."""
    ph = 2 * math.pi * t / FRAMES
    yaw = math.radians(10 * math.sin(ph))
    dist = 2.35 - 0.3 * (0.5 - 0.5 * math.cos(ph))
    height = 1.08 + 0.05 * math.sin(ph)
    cam.location = TARGET + Vector((dist * math.sin(yaw), -dist * math.cos(yaw), height - TARGET.z))
    cam.rotation_euler = (TARGET - cam.location).to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------- motion (beats in v2's 48-frame units)
def smooth(a, b, t):
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def bump(a, b, c, d, t):
    return smooth(a, b, t) * (1 - smooth(c, d, t))


BOUNCES = ((8, 20, 0.3), (20, 29, 0.16), (29, 34, 0.07))


def ball_state(u):
    for s, e, h in BOUNCES:
        if s <= u < e:
            v = (u - s) / (e - s)
            z = 4 * h * v * (1 - v)
            squash = 1.0 - 0.28 * max(0.0, 1 - v * 6) - 0.28 * max(0.0, 1 - (1 - v) * 6)
            stretch = 1.0 + 0.18 * min(1.0, z / 0.08) * (1 if h > 0.1 else 0.5)
            return z, (squash if z < 0.01 else stretch)
    return 0.0, (0.75 if 34 <= u < 35 else 1.0)


def pose(f):
    t = f % FRAMES
    u = t * 48 / FRAMES                                       # beat clock
    ph = 2 * math.pi * t / FRAMES
    place_camera(t)
    z, sz = ball_state(u)
    sxy = 1 / math.sqrt(sz)
    ball.scale = (BALL_R * sxy, BALL_R * sxy, BALL_R * sz)
    ball.location = BALL_REST + Vector((0, 0, z + BALL_R * sz))
    drawing = 1 - bump(7, 10, 36, 40, u)
    delight = bump(9, 13, 24, 30, u)
    look_up = bump(12, 17, 28, 34, u)
    ring = 2 * math.pi * (u % 8) / 8
    rx = math.radians(-55 * drawing - 160 * delight + 6 * math.sin(ring) * drawing)
    rz = math.radians(-10 * drawing + 8 * math.cos(ring) * drawing)
    mac_arms["R"].rotation_euler = Euler((rx, math.radians(-15 * delight), rz))
    mac_arms["L"].rotation_euler = Euler((math.radians(-20 - 140 * delight), math.radians(20 * delight), math.radians(10)))
    # face down to the page while drawing; up and to the left (toward Tlatoāni) while watching
    neck.rotation_euler = Euler((math.radians(14 * drawing - 18 * look_up), 0, math.radians(-38 * look_up)))
    nod = bump(18, 21, 22, 26, u) + 0.6 * bump(24, 26, 27, 30, u)
    head.rotation_euler = Euler((math.radians(12 * nod + 6 * drawing), 0, math.radians(18 + 8 * look_up)))
    for g, side, ang, k in gills:
        sway = 7 * math.sin(ph * 3 + k * 0.9 + (0 if side > 0 else math.pi / 2))
        g.rotation_euler = Euler((math.radians(sway), math.radians(side * (90 - ang)), 0))
    for i, seg in enumerate(tail_segs):
        seg.rotation_euler = Euler((math.radians(-14 if i == 0 else -6), 0, math.radians((10 + 3 * i) * math.sin(ph * 2 - 0.5 * i))))
    point = bump(10, 14, 26, 32, u)                           # the right hand (table side) points at the ball
    tla_arms["R"].rotation_euler = Euler((math.radians(-55 - 35 * point), 0, math.radians(30 + 25 * point)))
    tla_arms["L"].rotation_euler = Euler((math.radians(-25), 0, math.radians(-18)))
    for g, i in globes:                                       # globes and lantern sway on their strings
        g.rotation_euler = Euler((math.radians(1.5 * math.sin(ph * 2 + i)), math.radians(1.5 * math.cos(ph * 2 + 1.7 * i)), 0))


# ---------------------------------------------------------------- render passes
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.image_settings.file_format = "PNG"
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
        s.type, s.light, s.background_type = "SOLID", "STUDIO", "VIEWPORT"
        s.show_cavity = s.show_shadows = kind == "clay"
        s.color_type = "MATERIAL"
        s.background_color = (0.78, 0.88, 0.95) if kind == "clay" else (0.07, 0.1, 0.12)
        if kind == "wire":
            s.color_type, s.light = "OBJECT", "FLAT"
            for o in scene.objects:
                if o.type == "MESH" and "wire" not in o.modifiers:
                    w = o.modifiers.new("wire", "WIREFRAME")
                    w.thickness, w.use_relative_offset = 0.006, False
                    o.color = (0.25, 0.95, 0.9, 1.0)
    else:
        scene.render.engine = "BLENDER_EEVEE"
        m = bpy.data.materials.get("depth") or bpy.data.materials.new("depth")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = NEAR, FAR
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
        em = nt.nodes.new("ShaderNodeEmission")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(cd.outputs["View Z Depth"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        # Every surface gets the depth material, except Mācron's two eyes: at this distance
        # they are too shallow to show in depth, and without them the video model drew
        # three eyes. They are marked pure white (as if nearest), a hint the model follows.
        hint = bpy.data.materials.get("eye-hint") or bpy.data.materials.new("eye-hint")
        hint.use_nodes = True
        hn = hint.node_tree
        hn.nodes.clear()
        he, ho = hn.nodes.new("ShaderNodeEmission"), hn.nodes.new("ShaderNodeOutputMaterial")
        he.inputs["Color"].default_value = (1, 1, 1, 1)
        hn.links.new(he.outputs["Emission"], ho.inputs["Surface"])
        for o in scene.objects:
            if o.type == "MESH":
                for slot in o.material_slots:
                    slot.material = hint if o.name.startswith("mac-eye") else m
        world.color = (0, 0, 0)
        scene.view_settings.view_transform = "Raw"


def check_clips(frames):
    """Report any frame where Tlatoāni's legs or tail cut into the stool or the table."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()

    def tree(o):
        m = o.evaluated_get(dg).to_mesh()
        mw = o.matrix_world
        t = BVHTree.FromPolygons([mw @ v.co for v in m.vertices], [p.vertices[:] for p in m.polygons])
        o.evaluated_get(dg).to_mesh_clear()
        return t

    movers = [o for o in scene.objects if o.type == "MESH" and o.name.startswith(("tla-leg", "tla-shin", "tla-tailseg"))]
    fixed = [o for o in scene.objects if o.type == "MESH" and o.name.startswith(("stool-", "tabletop", "pedestal", "foot"))]
    still = {o.name: tree(o) for o in fixed}
    bad = 0
    for f in frames:
        pose(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        for o in movers:
            t = tree(o)
            for name, s in still.items():
                if t.overlap(s):
                    bad += 1
                    print(f"clip frame {f:03d}: {o.name} x {name}")
    print(f"clip check: {len(frames)} frames, {len(movers)} limbs, {len(fixed)} props, {bad} overlaps")
    return bad


if "--check" in args:
    sys.exit(1 if check_clips(range(FRAMES) if ONLY is None else ONLY) else 0)

for kind in PASSES:
    setup(kind)
    os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    for f in range(FRAMES) if ONLY is None else ONLY:
        pose(f)
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(OUT, kind, f"{f:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("rendered", kind)
