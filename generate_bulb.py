#!/usr/bin/env python3
"""Incubating bulb sprite sheet — 4 frames, 24×24 each.

Layout (left→right): unlit, lit, unlit+focus, lit+focus.
Classic incandescent A-shape: round glass envelope on top, narrow neck,
metal screw base with two thread bands, contact tip at the bottom.
Focus = 1-px cyan outline just outside the silhouette.
Palette shared with robot/egg generators.
"""
from PIL import Image

CELL = 24
FRAMES = 4
SHEET_W = CELL * FRAMES
SHEET_H = CELL

T = (0, 0, 0, 0)
RIM = (74, 92, 120, 255)

GLASS_DIM = (188, 204, 224, 255)
GLASS_DIM_HL = (232, 240, 250, 255)
GLASS_DIM_SHADE = (148, 170, 196, 255)

GLASS_LIT = (255, 232, 130, 255)
GLASS_LIT_HL = (255, 252, 220, 255)
GLASS_LIT_SHADE = (240, 188, 80, 255)

HALO = (255, 200, 110, 170)
HALO_SOFT = (255, 220, 150, 90)

FILAMENT_DIM = (90, 100, 120, 255)
FILAMENT_LIT = (255, 138, 60, 255)

BASE_LIGHT = (210, 200, 188, 255)
BASE_MID = (158, 148, 138, 255)
BASE_DARK = (108, 98, 90, 255)

FOCUS = (90, 215, 232, 255)

# A19 silhouette in half-widths (px from center column CX=11.5).
# Sphere on top → concave shoulder → short neck → threaded screw base → contact tip.
# Real A19 proportions: height:width ≈ 1.8:1, base width ≈ 43% of glass width.
GLASS_ROWS = {
    1: 3,   # crown (8 wide)
    2: 4,   # 10 wide
    3: 5,   # 12 wide
    4: 6,   # 14 wide
    5: 6,   # widest (equator) — 14 wide
    6: 6,
    7: 6,   # rounder equator (4 rows at max width)
    8: 5,
    9: 5,
    10: 4,  # bottom of glass — slightly overhangs the base
}

# Divider line — a single navy row separating the glass from the screw base.
DIVIDER_ROWS = {11: 3}

# Threaded screw base — 8 wide, alternating dark/light bands for thread illusion.
NECK_ROWS = {}
BASE_ROWS = {
    12: 3,  # thread band (dark)
    13: 3,  # thread groove (light)
    14: 3,  # thread band (dark)
    15: 2,  # taper
}

# Contact tip — small pip at the very bottom (4 wide).
TIP_ROWS = {16: 1}

CX = 11.5


def half_width(rows, y):
    return rows.get(y, -1)


def in_set(rows, x, y):
    hw = rows.get(y)
    if hw is None:
        return False
    return abs(x - CX) <= hw + 0.5 - 1e-6


def in_glass_only(x, y):
    return in_set(GLASS_ROWS, x, y)


def in_divider(x, y):
    return in_set(DIVIDER_ROWS, x, y)


def in_metal(x, y):
    return (in_set(NECK_ROWS, x, y) or in_set(BASE_ROWS, x, y) or in_set(TIP_ROWS, x, y))


def in_shape(x, y):
    return in_glass_only(x, y) or in_divider(x, y) or in_metal(x, y)


def set_px(img, x, y, color):
    if 0 <= x < CELL and 0 <= y < CELL:
        img.putpixel((x, y), color)


def is_rim_of(test, x, y):
    if not test(x, y):
        return False
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if not test(nx, ny):
            return True
    return False


def render_bulb(lit, focused):
    cell = Image.new('RGBA', (CELL, CELL), T)

    # Halo (lit only) — outside glass, a soft 2-band glow.
    if lit:
        for y in range(CELL):
            for x in range(CELL):
                if in_shape(x, y):
                    continue
                # halo only around glass area, not the metal base
                # find nearest glass row distance
                gx_dist = abs(x - CX)
                # closest glass row
                best = None
                for gy, hw in GLASS_ROWS.items():
                    d = max(abs(y - gy), gx_dist - hw)
                    if best is None or d < best:
                        best = d
                if best is None:
                    continue
                if best <= 1.2:
                    set_px(cell, x, y, HALO)
                elif best <= 2.4:
                    set_px(cell, x, y, HALO_SOFT)

    # Glass fill with shading: highlight upper-left, shade lower-right.
    hl = GLASS_LIT_HL if lit else GLASS_DIM_HL
    fill = GLASS_LIT if lit else GLASS_DIM
    shade = GLASS_LIT_SHADE if lit else GLASS_DIM_SHADE
    for y in range(CELL):
        for x in range(CELL):
            if not in_glass_only(x, y):
                continue
            # upper-left sparkle on the spherical face
            if (x == 8 and y == 4) or (x == 8 and y == 5) or (x == 9 and y == 4):
                set_px(cell, x, y, hl)
                continue
            # bottom-right shade band along glass underside (below equator)
            hw = GLASS_ROWS[y]
            on_right_underside = (x - CX) > hw - 1.5 and y >= 6
            if on_right_underside:
                set_px(cell, x, y, shade)
            else:
                set_px(cell, x, y, fill)

    # Filament — two support wires dropping from the top, joined by a coiled bridge.
    fil = FILAMENT_LIT if lit else FILAMENT_DIM
    # support wires
    set_px(cell, 10, 9, fil)
    set_px(cell, 13, 9, fil)
    set_px(cell, 10, 8, fil)
    set_px(cell, 13, 8, fil)
    # coiled filament bridge
    set_px(cell, 11, 7, fil)
    set_px(cell, 12, 7, fil)
    set_px(cell, 11, 8, fil)
    set_px(cell, 12, 8, fil)

    # Metal base fill
    for y in range(CELL):
        for x in range(CELL):
            if not in_metal(x, y):
                continue
            # Thread bands at y=12, y=14 dark; y=13 light groove; taper/tip mid
            if y in (12, 14):
                set_px(cell, x, y, BASE_DARK)
            elif y == 13:
                set_px(cell, x, y, BASE_LIGHT)
            elif y in (15, 16):
                set_px(cell, x, y, BASE_MID)
            else:
                set_px(cell, x, y, BASE_DARK)

    # Add a 1-px specular on the left side of the base for shape
    for y in (12, 14):
        # leftmost interior pixel of that row
        hw = BASE_ROWS.get(y) or NECK_ROWS.get(y)
        if hw is not None:
            lx = int(CX - hw + 0.5)
            set_px(cell, lx, y, BASE_LIGHT)

    # Rim outline — uniform navy around the full silhouette.
    for y in range(CELL):
        for x in range(CELL):
            if is_rim_of(in_shape, x, y):
                set_px(cell, x, y, RIM)

    # Divider line — single navy row separating the glass from the base.
    for y in range(CELL):
        for x in range(CELL):
            if in_divider(x, y):
                set_px(cell, x, y, RIM)

    # Focus outline — 1-px cyan just outside the silhouette.
    if focused:
        for y in range(CELL):
            for x in range(CELL):
                if in_shape(x, y):
                    continue
                touches = False
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < CELL and 0 <= ny < CELL and in_shape(nx, ny):
                        touches = True
                        break
                if touches and cell.getpixel((x, y))[3] == 0:
                    set_px(cell, x, y, FOCUS)

    return cell


def main():
    sheet = Image.new('RGBA', (SHEET_W, SHEET_H), T)
    configs = [(False, False), (True, False), (False, True), (True, True)]
    for i, (lit, foc) in enumerate(configs):
        c = render_bulb(lit, foc)
        sheet.paste(c, (i * CELL, 0), c)
    out = '/Users/huongphung/Workspaces/cute-bot/public/bulb.png'
    sheet.save(out)

    preview = sheet.resize((SHEET_W * 6, SHEET_H * 6), Image.NEAREST)
    preview.save('/Users/huongphung/Workspaces/cute-bot/bulb_preview.png')

    print(f'Wrote {out} ({SHEET_W}x{SHEET_H}) — frames: unlit, lit, unlit+focus, lit+focus')


if __name__ == '__main__':
    main()
