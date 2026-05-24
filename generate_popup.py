#!/usr/bin/env python3
"""Speech-bubble popup panel for the egg incubator UI — 48×40, single sprite.

Navy rim, cream fill, soft inner highlight + bottom-right inner shadow,
3-px notch on the bottom edge pointing down toward the egg.

Palette shared with robot/egg generators so the panel reads as part of
the same world.
"""
from PIL import Image

W, H = 48, 40

T = (0, 0, 0, 0)
RIM = (74, 92, 120, 255)
FILL_HL = (252, 247, 234, 255)
FILL = (246, 239, 224, 255)
FILL_MID = (224, 209, 178, 255)
INNER_SHADOW = (188, 165, 122, 255)

PANEL_TOP = 0
PANEL_BOTTOM = 33  # rows 0..33 are the rounded rect; notch lives below
CORNER = 2          # 2-px rounded corners

NOTCH_CX = 23       # tip slightly left of center for visual interest
NOTCH_TOP_Y = 34
NOTCH_HEIGHT = 3    # tapers 3 rows down to a 1-px tip


def set_px(img, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        img.putpixel((x, y), color)


def in_panel(x, y):
    if y < PANEL_TOP or y > PANEL_BOTTOM:
        return False
    if x < 0 or x >= W:
        return False
    # rounded corners
    if x < CORNER and y < CORNER:
        return (CORNER - x) + (CORNER - y) <= CORNER
    if x >= W - CORNER and y < CORNER:
        return (x - (W - 1 - CORNER)) + (CORNER - y) <= CORNER
    if x < CORNER and y > PANEL_BOTTOM - CORNER:
        return (CORNER - x) + (y - (PANEL_BOTTOM - CORNER)) <= CORNER
    if x >= W - CORNER and y > PANEL_BOTTOM - CORNER:
        return (x - (W - 1 - CORNER)) + (y - (PANEL_BOTTOM - CORNER)) <= CORNER
    return True


def in_notch(x, y):
    # triangle: 3 wide at top (y=34), 1 wide at tip (y=36)
    if y < NOTCH_TOP_Y or y > NOTCH_TOP_Y + NOTCH_HEIGHT - 1:
        return False
    inset = y - NOTCH_TOP_Y
    left = NOTCH_CX - 2 + inset
    right = NOTCH_CX + 2 - inset
    return left <= x <= right


def in_shape(x, y):
    return in_panel(x, y) or in_notch(x, y)


def is_rim(x, y):
    if not in_shape(x, y):
        return False
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if not in_shape(nx, ny):
            return True
    return False


def main():
    img = Image.new('RGBA', (W, H), T)

    # Base fill
    for y in range(H):
        for x in range(W):
            if in_shape(x, y):
                set_px(img, x, y, FILL)

    # Soft top-left inner highlight (1-px band just inside the rim)
    for x in range(W):
        for y in range(H):
            if not in_shape(x, y):
                continue
            # one pixel below/right of top-left edge
            if in_shape(x - 1, y) and in_shape(x, y - 1):
                continue
            # this pixel touches the top or left edge → highlight neighbor inside
            pass

    # Cleaner highlight pass: any interior pixel whose up or left neighbor is rim → highlight.
    # Done after rim is drawn below; here we mark candidates first.

    # Bottom-right inner shadow band (1 px inside rim along bottom & right of panel)
    for x in range(W):
        for y in range(PANEL_TOP, PANEL_BOTTOM + 1):
            if not in_panel(x, y):
                continue
            # touches bottom or right of panel interior
            below_out = not in_panel(x, y + 1) and not in_notch(x, y + 1)
            right_out = not in_panel(x + 1, y)
            if (below_out or right_out):
                # only the pixel just inside the rim, not the rim itself
                # we'll paint shadow and the rim pass will overwrite border pixels.
                set_px(img, x, y, INNER_SHADOW)

    # Top-left inner highlight (1 px inside rim along top & left of panel)
    for x in range(W):
        for y in range(PANEL_TOP, PANEL_BOTTOM + 1):
            if not in_panel(x, y):
                continue
            above_out = not in_panel(x, y - 1)
            left_out = not in_panel(x - 1, y)
            if (above_out or left_out):
                set_px(img, x, y, FILL_HL)

    # Mid-tone gradient row near the bottom interior (subtle depth)
    for x in range(2, W - 2):
        if in_panel(x, PANEL_BOTTOM - 1) and img.getpixel((x, PANEL_BOTTOM - 1)) == FILL:
            set_px(img, x, PANEL_BOTTOM - 1, FILL_MID)

    # Rim outline last
    for y in range(H):
        for x in range(W):
            if is_rim(x, y):
                set_px(img, x, y, RIM)

    out = '/Users/huongphung/Workspaces/cute-bot/public/popup.png'
    img.save(out)

    preview = img.resize((W * 8, H * 8), Image.NEAREST)
    preview.save('/Users/huongphung/Workspaces/cute-bot/popup_preview.png')

    print(f'Wrote {out} ({W}x{H}) — notch tip at x={NOTCH_CX}, y={NOTCH_TOP_Y + NOTCH_HEIGHT - 1}')


if __name__ == '__main__':
    main()
