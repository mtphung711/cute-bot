#!/usr/bin/env python3
"""Robot sprite sheet — 8 directions × 6 hover-walk frames, 32×32 each.

Layout: 6 cols (frames) × 8 rows (directions).
Direction order (top→bottom): S, SE, E, NE, N, NW, W, SW.
"""
from PIL import Image
import math

CELL = 32
COLS, ROWS = 6, 8
SHEET_W = CELL * COLS
SHEET_H = CELL * ROWS

T = (0, 0, 0, 0)
BODY_HL = (255, 255, 255, 255)
BODY = (240, 246, 252, 255)
BODY_MID = (198, 214, 232, 255)
BODY_SHADOW = (148, 170, 196, 255)
RIM = (74, 92, 120, 255)
ACCENT = (90, 215, 232, 255)
ACCENT_DARK = (38, 152, 180, 255)
VISOR = (42, 56, 78, 255)
VISOR_FRAME = (22, 30, 46, 255)
EYE = (255, 220, 90, 255)
ANTENNA = (148, 160, 178, 255)
ANTENNA_TIP = (255, 110, 162, 255)
SHADOW_A = (0, 0, 0, 95)
SHADOW_B = (0, 0, 0, 55)

CX, CY = 15.5, 15.5
RX, RY = 8.0, 9.0
N_EXP = 2.3


def in_body(x, y):
    dx = abs(x - CX) / RX
    dy = abs(y - CY) / RY
    return dx ** N_EXP + dy ** N_EXP <= 1.0


def is_rim(x, y):
    if not in_body(x, y):
        return False
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if not in_body(nx, ny):
            return True
    return False


def body_color_at(x, y, is_back):
    lx, ly = 10, 9
    d = math.hypot((x - lx), (y - ly) * 1.05)
    if is_back:
        if d <= 9:
            return BODY_MID
        return BODY_SHADOW
    if d <= 2.6:
        return BODY_HL
    if d <= 7.5:
        return BODY
    if d <= 12.5:
        return BODY_MID
    return BODY_SHADOW


# Per-direction face/arm config.
# eyes: list of (x, y) — 2x2 round eye anchors (top-left pixel).
# mouth: (x, y) — small cyan friendly mouth dot, or None.
# lean: antenna lean -1, 0, +1.
# arms_L / arms_R: cyan arm stub on that side.
# back: True = camera sees back of head (darker shading, no face).
DIR_CONFIG = {
    0: {'eyes': [(11, 11), (18, 11)], 'mouth': (15, 15), 'lean': 0, 'arms_L': True, 'arms_R': True, 'back': False, 'chest': 'center'},
    1: {'eyes': [(13, 11), (18, 11)], 'mouth': (16, 15), 'lean': 1, 'arms_L': False, 'arms_R': True, 'back': False, 'chest': 'right'},
    2: {'eyes': [(18, 11)],            'mouth': None,     'lean': 1, 'arms_L': False, 'arms_R': True, 'back': False, 'chest': None},
    3: {'eyes': [],                    'mouth': None,     'lean': 1, 'arms_L': False, 'arms_R': True, 'back': True,  'chest': None},
    4: {'eyes': [],                    'mouth': None,     'lean': 0, 'arms_L': True,  'arms_R': True, 'back': True,  'chest': None},
    5: {'eyes': [],                    'mouth': None,     'lean': -1,'arms_L': True,  'arms_R': False,'back': True,  'chest': None},
    6: {'eyes': [(11, 11)],            'mouth': None,     'lean': -1,'arms_L': True,  'arms_R': False,'back': False, 'chest': None},
    7: {'eyes': [(11, 11), (16, 11)], 'mouth': (14, 15), 'lean': -1,'arms_L': True,  'arms_R': False,'back': False, 'chest': 'left'},
}

BOB = [0, -1, -2, -2, -1, 0]
SHADOW_HALF = [6, 5, 4, 4, 5, 6]


def set_px(img, x, y, color):
    if 0 <= x < CELL and 0 <= y < CELL:
        img.putpixel((x, y), color)


def render_cell(direction, frame):
    cell = Image.new('RGBA', (CELL, CELL), T)
    cfg = DIR_CONFIG[direction]
    by = BOB[frame]
    sh = SHADOW_HALF[frame]

    # Ground shadow (does not bob)
    gy = 27
    gcx = 15
    for x in range(gcx - sh, gcx + sh + 2):
        set_px(cell, x, gy, SHADOW_A)
    for x in range(gcx - sh + 1, gcx + sh + 1):
        set_px(cell, x, gy - 1, SHADOW_B)
    set_px(cell, gcx - sh - 1, gy, SHADOW_B)
    set_px(cell, gcx + sh + 2, gy, SHADOW_B)

    # Body fill
    for y in range(32):
        for x in range(32):
            if in_body(x, y):
                set_px(cell, x, y + by, body_color_at(x, y, cfg['back']))

    # Rim outline
    for y in range(32):
        for x in range(32):
            if is_rim(x, y):
                set_px(cell, x, y + by, RIM)

    # Antenna pole + tip
    lean = cfg['lean']
    pole_ys = [5, 6, 7]
    for i, y in enumerate(pole_ys):
        t = i / (len(pole_ys) - 1)
        ax = round(15.5 + lean * (1 - t))
        set_px(cell, ax, y + by, ANTENNA)
    tip_x = round(15.5 + lean * 1)
    set_px(cell, tip_x, 4 + by, ANTENNA_TIP)

    # Eyes — 2x2 friendly round eye blocks with dark frame
    for (ex, ey) in cfg['eyes']:
        # frame ring (top/bottom/sides) for definition
        set_px(cell, ex, ey - 1 + by, VISOR_FRAME)
        set_px(cell, ex + 1, ey - 1 + by, VISOR_FRAME)
        set_px(cell, ex - 1, ey + by, VISOR_FRAME)
        set_px(cell, ex - 1, ey + 1 + by, VISOR_FRAME)
        set_px(cell, ex + 2, ey + by, VISOR_FRAME)
        set_px(cell, ex + 2, ey + 1 + by, VISOR_FRAME)
        set_px(cell, ex, ey + 2 + by, VISOR_FRAME)
        set_px(cell, ex + 1, ey + 2 + by, VISOR_FRAME)
        # eye glow fill
        set_px(cell, ex, ey + by, EYE)
        set_px(cell, ex + 1, ey + by, EYE)
        set_px(cell, ex, ey + 1 + by, EYE)
        set_px(cell, ex + 1, ey + 1 + by, EYE)

    # Friendly mouth — 2px cyan smile dot
    if cfg.get('mouth'):
        mx, my = cfg['mouth']
        set_px(cell, mx, my + by, ACCENT_DARK)
        set_px(cell, mx + 1, my + by, ACCENT_DARK)

    # Arms: cyan stub just outside body at widest row (2px wide for legibility)
    arm_y = 15
    if cfg['arms_L']:
        set_px(cell, 7, arm_y + by, ACCENT)
        set_px(cell, 6, arm_y + by, ACCENT_DARK)
        set_px(cell, 7, arm_y + 1 + by, ACCENT_DARK)
    if cfg['arms_R']:
        set_px(cell, 24, arm_y + by, ACCENT)
        set_px(cell, 25, arm_y + by, ACCENT_DARK)
        set_px(cell, 24, arm_y + 1 + by, ACCENT_DARK)

    # Back seam line (only for back-facing directions)
    if cfg['back']:
        for y in (10, 11, 12, 13, 14, 15):
            if cell.getpixel((15, y + by)) != T:
                set_px(cell, 15, y + by, BODY_SHADOW)

    return cell


def main():
    sheet = Image.new('RGBA', (SHEET_W, SHEET_H), T)
    for d in range(8):
        for f in range(6):
            c = render_cell(d, f)
            sheet.paste(c, (f * CELL, d * CELL), c)
    sheet.save('/Users/huongphung/Workspaces/claude-game-assets/robot.png')

    preview = sheet.resize((SHEET_W * 6, SHEET_H * 6), Image.NEAREST)
    preview.save('/Users/huongphung/Workspaces/claude-game-assets/robot_preview.png')

    print(f'Wrote robot.png ({SHEET_W}x{SHEET_H}) and robot_preview.png ({SHEET_W*6}x{SHEET_H*6})')


if __name__ == '__main__':
    main()
