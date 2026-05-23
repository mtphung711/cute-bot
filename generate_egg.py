#!/usr/bin/env python3
"""Egg sprite sheet — 8 frames of idle rocking, 32×32 each.

Inert/precious shell. Cream + warm-brown speckles. Same navy rim and
ground shadow as the robot so they share a world. The whole egg tilts
as a rigid body around a pivot at its base.
"""
from PIL import Image
import math

CELL = 32
FRAMES = 8
SHEET_W = CELL * FRAMES
SHEET_H = CELL

T = (0, 0, 0, 0)
BODY_HL = (252, 247, 234, 255)
BODY = (246, 239, 224, 255)
BODY_MID = (224, 209, 178, 255)
BODY_SHADOW = (188, 165, 122, 255)
RIM = (74, 92, 120, 255)
SPECK = (122, 90, 58, 255)
SPECK_SOFT = (158, 124, 88, 255)
SHADOW_A = (0, 0, 0, 95)
SHADOW_B = (0, 0, 0, 55)

CX = 15.5
CY = 17.0
RX = 8.2
RY = 10.0
TOP_TAPER = 0.32

# Pivot for rigid-body tilt — bottom of the shell, just above ground shadow.
PIVOT_X = 15.5
PIVOT_Y = 26.0

# Fixed speckles in egg-local coords. Tilt with the shell.
SPECKLES = [
    (10, 12, SPECK),
    (18, 13, SPECK),
    (12, 18, SPECK),
    (13, 18, SPECK_SOFT),
    (19, 17, SPECK),
    (14, 22, SPECK),
    (20, 20, SPECK),
    (11, 21, SPECK),
]

# Smooth sine rock: ±6° peak, zero-crossing twice per loop.
MAX_DEG = 6.0
ANGLES_DEG = [MAX_DEG * math.sin(2 * math.pi * i / FRAMES) for i in range(FRAMES)]


def half_width(y):
    dy = y - CY
    if dy < -RY or dy > RY:
        return 0.0
    base = RX * math.sqrt(max(0.0, 1.0 - (dy / RY) ** 2))
    if dy < 0:
        base *= (1.0 - TOP_TAPER * (-dy / RY))
    return base


def in_body(x, y):
    return abs(x - CX) <= half_width(y) - 1e-6


def body_color_at(x, y):
    lx, ly = 12.0, 11.0
    d = math.hypot(x - lx, (y - ly) * 1.0)
    if d <= 1.7:
        return BODY_HL
    if d <= 5.5:
        return BODY
    if d <= 9.5:
        return BODY_MID
    return BODY_SHADOW


def set_px(img, x, y, color):
    if 0 <= x < CELL and 0 <= y < CELL:
        img.putpixel((x, y), color)


def screen_to_local(sx, sy, ca, sa):
    dx = sx - PIVOT_X
    dy = sy - PIVOT_Y
    lx = dx * ca + dy * sa + PIVOT_X
    ly = -dx * sa + dy * ca + PIVOT_Y
    return lx, ly


def local_to_screen(lx, ly, ca, sa):
    dx = lx - PIVOT_X
    dy = ly - PIVOT_Y
    sx = dx * ca - dy * sa + PIVOT_X
    sy = dx * sa + dy * ca + PIVOT_Y
    return sx, sy


def screen_in_body(sx, sy, ca, sa):
    lx, ly = screen_to_local(sx, sy, ca, sa)
    return in_body(lx, ly), lx, ly


def render_cell(angle_deg):
    cell = Image.new('RGBA', (CELL, CELL), T)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)

    # Ground shadow — fixed, pivot-anchored.
    gy = 28
    gcx = 16
    sh = 6
    for x in range(gcx - sh, gcx + sh + 1):
        set_px(cell, x, gy, SHADOW_A)
    for x in range(gcx - sh + 1, gcx + sh):
        set_px(cell, x, gy - 1, SHADOW_B)
    set_px(cell, gcx - sh - 1, gy, SHADOW_B)
    set_px(cell, gcx + sh + 1, gy, SHADOW_B)

    # Cache in-body test per screen pixel.
    inside = [[False] * CELL for _ in range(CELL)]
    local = [[(0.0, 0.0)] * CELL for _ in range(CELL)]
    for sy in range(CELL):
        for sx in range(CELL):
            inb, lx, ly = screen_in_body(sx, sy, ca, sa)
            inside[sy][sx] = inb
            local[sy][sx] = (lx, ly)

    # Body fill (shading uses local coords so the highlight tilts with the egg).
    for sy in range(CELL):
        for sx in range(CELL):
            if inside[sy][sx]:
                lx, ly = local[sy][sx]
                set_px(cell, sx, sy, body_color_at(lx, ly))

    # Rim outline in screen space (any in-body pixel with an out-of-body neighbor).
    for sy in range(CELL):
        for sx in range(CELL):
            if not inside[sy][sx]:
                continue
            rim = False
            for nx, ny in ((sx + 1, sy), (sx - 1, sy), (sx, sy + 1), (sx, sy - 1)):
                if not (0 <= nx < CELL and 0 <= ny < CELL and inside[ny][nx]):
                    rim = True
                    break
            if rim:
                set_px(cell, sx, sy, RIM)

    # Speckles — project local → screen, snap to pixel, only if interior (not rim).
    for (lx, ly, color) in SPECKLES:
        sx_f, sy_f = local_to_screen(lx, ly, ca, sa)
        sx, sy = round(sx_f), round(sy_f)
        if not (0 <= sx < CELL and 0 <= sy < CELL):
            continue
        if not inside[sy][sx]:
            continue
        # skip if this would land on the rim
        on_rim = False
        for nx, ny in ((sx + 1, sy), (sx - 1, sy), (sx, sy + 1), (sx, sy - 1)):
            if not (0 <= nx < CELL and 0 <= ny < CELL and inside[ny][nx]):
                on_rim = True
                break
        if on_rim:
            continue
        set_px(cell, sx, sy, color)

    return cell


def main():
    sheet = Image.new('RGBA', (SHEET_W, SHEET_H), T)
    for f, deg in enumerate(ANGLES_DEG):
        c = render_cell(deg)
        sheet.paste(c, (f * CELL, 0), c)
    out = '/Users/huongphung/Workspaces/cute-bot/public/egg.png'
    sheet.save(out)

    preview = sheet.resize((SHEET_W * 6, SHEET_H * 6), Image.NEAREST)
    preview.save('/Users/huongphung/Workspaces/cute-bot/egg_preview.png')

    print(f'Wrote {out} ({SHEET_W}x{SHEET_H}), angles={[round(d,1) for d in ANGLES_DEG]}')


if __name__ == '__main__':
    main()
