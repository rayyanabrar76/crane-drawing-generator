"""Makes a dimensioned 2D SVG drawing of a single girder overhead crane.

All lengths in mm. Every fixed number below says where it came from.
"REF" = read from the reference drawing (10 t, 25 m span crane).
These REF numbers are ESTIMATES for other sizes: I only have one example.
Shapes marked "drawing only" make the picture readable. They are not real sizes.
"""
import html

# --- Fixed values (all ESTIMATES unless said otherwise) ---
HOOK_TOP_TO_RAIL_TOP = 810   # REF: 8710 (rail top) - 7900 (lifting height)
CRANE_ABOVE_RAIL = 1369      # REF: rail top to top of crane
ROOF_CLEARANCE = 200         # REF: gap above crane to roof
END_CLEARANCE_MIN = 235      # REF: "Min.235" crane end to wall
OVERHANG_EACH_SIDE = 135     # REF: (25270 overall - 25000 span) / 2
WHEELBASE = 3800             # REF: end carriage wheel centres (plan view)
END_CARRIAGE_LENGTH = 4310   # REF: end carriage overall length (plan view)


def compute_dimensions(inputs):
    """Turn user inputs into all the sizes we draw. Returns dict of mm values."""
    span = inputs["span_mm"]
    lift = inputs["lifting_height_mm"]
    rail_top = lift + HOOK_TOP_TO_RAIL_TOP
    crane_top = rail_top + CRANE_ABOVE_RAIL
    return {
        "capacity_t": inputs["capacity_t"],
        "span": span,
        "lifting_height": lift,
        "overall_length": span + 2 * OVERHANG_EACH_SIDE,
        "rail_top_height": rail_top,
        "hook_top_to_rail_top": HOOK_TOP_TO_RAIL_TOP,
        "crane_above_rail": CRANE_ABOVE_RAIL,
        "min_building_height": crane_top + ROOF_CLEARANCE,
        "roof_clearance": ROOF_CLEARANCE,
        "end_clearance_min": END_CLEARANCE_MIN,
        "wheelbase": WHEELBASE,
        "end_carriage_length": END_CARRIAGE_LENGTH,
    }


# --- SVG helpers ---
STROKE = "#111"
DIM = "#1565c0"     # dimensions
LABEL = "#37474f"   # part names
MUTED = "#616161"
LR, UD = "↔︎", "↕︎"   # arrows; ︎ keeps them plain text, not colour emoji

# Diagonal hatching for walls, floor and rail supports (like concrete on the reference drawing).
HATCH = ('<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" '
         'stroke="#9e9e9e" stroke-width="1"/></pattern></defs>')


def _line(x1, y1, x2, y2, color=STROKE, width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>'


def _rect(x, y, w, h, fill="none", width=1.5):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{STROKE}" stroke-width="{width}"/>'


def _circle(cx, cy, r, fill="#fff", width=1.2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{STROKE}" stroke-width="{width}"/>'


def _text(x, y, s, size=12, anchor="middle", rotate=False, color=STROKE, bold=False):
    rot = f' transform="rotate(-90 {x:.1f} {y:.1f})"' if rotate else ""
    w = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-family="Arial, sans-serif" fill="{color}"{w}{rot}>{html.escape(str(s))}</text>')


def _hdim(x1, x2, y, label, label_x=None, anchor="middle"):
    """Horizontal dimension line with arrows and a label above it."""
    lx = (x1 + x2) / 2 if label_x is None else label_x
    return "".join([
        _line(x1, y, x2, y, DIM, 1),
        _line(x1, y - 6, x1, y + 6, DIM, 1),
        _line(x2, y - 6, x2, y + 6, DIM, 1),
        f'<polygon points="{x1},{y} {x1+8},{y-3} {x1+8},{y+3}" fill="{DIM}"/>',
        f'<polygon points="{x2},{y} {x2-8},{y-3} {x2-8},{y+3}" fill="{DIM}"/>',
        _text(lx, y - 5, label, 12, anchor, color=DIM),
    ])


def _vdim(x, y1, y2, label):
    """Vertical dimension line with arrows and a rotated label beside it."""
    top, bot = min(y1, y2), max(y1, y2)
    return "".join([
        _line(x, top, x, bot, DIM, 1),
        _line(x - 6, top, x + 6, top, DIM, 1),
        _line(x - 6, bot, x + 6, bot, DIM, 1),
        f'<polygon points="{x},{top} {x-3},{top+8} {x+3},{top+8}" fill="{DIM}"/>',
        f'<polygon points="{x},{bot} {x-3},{bot-8} {x+3},{bot-8}" fill="{DIM}"/>',
        _text(x - 6, (top + bot) / 2, label, 12, rotate=True, color=DIM),
    ])


def _title(cx, y, name, subtitle):
    """View title with a plain-words subtitle under it."""
    return _text(cx, y - 30, name, 14, bold=True) + _text(cx, y - 15, subtitle, 11, color=MUTED)


def _callout(px, py, tx, ty, text, anchor="start"):
    """Part name with a thin leader line from the text to the part (px, py)."""
    gap = 3 if anchor == "start" else -3
    return "".join([
        _line(px, py, tx, ty - 4, LABEL, 0.7),
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="{LABEL}"/>',
        _text(tx + gap, ty, text, 10.5, anchor, color=LABEL),
    ])


def _front_view(d, ox, oy, w, h):
    """Front elevation: building, rails, girder, end carriages, hoist, hook."""
    total_h = d["min_building_height"]
    total_w = d["overall_length"] + 2 * d["end_clearance_min"]
    s = min(w / total_w, (h - 70) / total_h)  # 70 px kept free for top dimensions
    left = ox + (w - total_w * s) / 2
    floor_y = oy + (h + 70 + total_h * s) / 2  # centred up/down, so a wide building doesn't sink to the bottom

    def X(mm):  # mm from left wall -> px
        return left + mm * s

    def Y(mm):  # mm above floor -> px
        return floor_y - mm * s

    ec = d["end_clearance_min"]
    crane_l, crane_r = ec, ec + d["overall_length"]
    rail_l, rail_r = ec + OVERHANG_EACH_SIDE, ec + OVERHANG_EACH_SIDE + d["span"]
    rail_y = d["rail_top_height"]
    top_y = rail_y + d["crane_above_rail"]
    girder_depth = d["crane_above_rail"] * 0.6  # drawing only, not a real size

    cl, cr = X(crane_l), X(crane_r)
    rail = Y(rail_y)                                 # rail top (px)
    gt, gb = Y(top_y), Y(top_y - girder_depth)       # girder top / bottom (px)
    hx = X((crane_l + crane_r) / 2)                  # hoist shown at mid-span
    hook = Y(d["lifting_height"])                    # hook top (px)
    roof = Y(d["min_building_height"])
    wall = 12                                        # wall thickness on paper: drawing only

    p = [_title(ox + w / 2, oy, "FRONT VIEW", "looking at the crane from the front")]

    # building: hatched walls and floor, dashed roof line
    p.append(_rect(X(0) - wall, roof, wall, floor_y - roof, "url(#hatch)", 1))
    p.append(_rect(X(total_w), roof, wall, floor_y - roof, "url(#hatch)", 1))
    p.append(_rect(X(0) - wall - 20, floor_y, X(total_w) - X(0) + 2 * wall + 40, 8, "url(#hatch)", 0))
    p.append(_line(X(0) - wall - 20, floor_y, X(total_w) + wall + 20, floor_y, STROKE, 2))
    p.append(_text(X(total_w / 2), floor_y + 22, "Floor ±0", 11))
    p.append(_line(X(0), roof, X(total_w), roof, STROKE, 1, "6 4"))

    # rail supports on the walls (drawing only) and the rails on top
    p.append(_rect(X(0), rail + 6, X(rail_l) + 7 - X(0), 9, "url(#hatch)", 1))
    p.append(_rect(X(rail_r) - 7, rail + 6, X(total_w) - X(rail_r) + 7, 9, "url(#hatch)", 1))
    for rx in (rail_l, rail_r):
        p.append(_rect(X(rx) - 4, rail, 8, 6, STROKE))

    # main girder with flange lines and stiffeners (drawing only)
    p.append(_rect(cl, gt, cr - cl, gb - gt, "#e0e0e0"))
    p.append(_line(cl, gt + 3, cr, gt + 3, "#757575", 0.8))
    p.append(_line(cl, gb - 3, cr, gb - 3, "#757575", 0.8))
    n = max(4, int((cr - cl) / 45))
    for i in range(1, n):
        x = cl + i * (cr - cl) / n
        p.append(_line(x, gt + 3, x, gb - 3, "#9e9e9e", 0.8))

    # end carriages, with wheels sitting on the rails
    for x in (cl, cr - 14):
        p.append(_rect(x, gt, 14, rail - gt, "#bdbdbd"))
    wr = max(3, min(6, (rail - gt) * 0.18))
    for rx in (rail_l, rail_r):
        p.append(_circle(X(rx), rail - wr, wr))

    # capacity written in the middle of the girder
    size = max(9, min(14, gb - gt - 4))
    mid = (gt + gb) / 2
    p.append(_rect(hx - 26, mid - size / 2 - 1, 52, size + 2, "#fff", 0))
    p.append(_text(hx, mid + size * 0.36, f'{d["capacity_t"]:g} t', size, bold=True))

    # hoist hanging under the girder, rope, hook block and hook (drawing only sizes)
    gap = hook - gb
    hh = max(10, min(26, gap * 0.55))   # hoist height on paper
    br = max(2.5, min(6, gap * 0.12))   # hook block radius
    for dx in (-12, 12):  # trolley wheels running on the girder's bottom flange
        p.append(_circle(hx + dx, gb + 2.5, 2.5, STROKE, 0))
    p.append(_rect(hx - 22, gb + 4, 44, hh - 4, "#fff3e0"))
    p.append(_circle(hx - 8, gb + 4 + (hh - 4) / 2, max(2, min(7, (hh - 4) / 2 - 2)), "none", 1))
    p.append(_rect(hx + 6, gb + 4 + (hh - 4) * 0.25, 12, (hh - 4) * 0.5, "#ffcc80", 1))
    p.append(_line(hx, gb + hh, hx, hook - 2 * br, STROKE, 1))
    p.append(_circle(hx, hook - br, br))
    p.append(f'<path d="M{hx:.1f},{hook:.1f} v10 a6,6 0 1 1 -8,6" fill="none" stroke="{STROKE}" stroke-width="2"/>')

    # Tall building: the crane is drawn small, so part names go in a list outside (see below).
    names_outside = rail - gt < 45 and X(0) - wall - 20 >= 100

    # dimensions
    min_y = rail + (80 if names_outside else 48)  # keep clear of the name leader lines
    p.append(_hdim(X(rail_l), X(rail_r), roof - 60, f'Span {d["span"]}'))
    p.append(_hdim(cl, cr, roof - 30, f'Overall {d["overall_length"]}'))
    p.append(_hdim(X(0), cl, min_y, f'Min.{ec}', X(0) + 4, "start"))
    if X(total_w) - X(0) >= 250:  # room for the second label
        p.append(_hdim(cr, X(total_w), min_y, f'Min.{ec}', X(total_w) - 4, "end"))
    p.append(_vdim(hx + 40, floor_y, hook, f'Lifting height {d["lifting_height"]}'))
    p.append(_vdim(X(total_w) + 35, floor_y, rail, f'Rail top {d["rail_top_height"]}'))
    p.append(_vdim(X(total_w) + 35, rail, gt, f'{d["crane_above_rail"]}'))
    p.append(_vdim(X(total_w) + 75, floor_y, roof, f'Min. building height {d["min_building_height"]}'))

    # part names
    if names_outside:
        # List the names on the left (outside the building) with leader lines to each part.
        tx = X(0) - wall - 10
        targets = [
            ("Main beam", cl + 20, (gt + gb) / 2),
            ("End carriage", cl + 7, rail - 8),
            ("Wheel", X(rail_l), rail - wr),
            ("Rail", X(rail_l) - 4, rail + 3),
            (f"Hoist {LR}", hx - 22, gb + hh / 2),
            (f"Hook {UD}", hx - 7, hook + 15),
        ]
        for i, (name, px, py) in enumerate(targets):
            p.append(_callout(px, py, tx, gt + 4 + i * 17, name, "end"))
    else:
        # Enough room: put each name right next to its part.
        bx = cl + 0.25 * (cr - cl)
        p += [
            _callout(bx, gb, bx - 14, gb + 30, "Main beam", "end"),
            _callout(cl + 14, rail - 4, cl + 26, rail + 12, "End carriage"),
            _callout(X(rail_r) - wr, rail - wr, cr - 24, rail + 12, "Wheel", "end"),
            _callout(X(rail_r) - 4, rail + 3, cr - 24, rail + 30, "Rail", "end"),
            _callout(hx + 22, gb + hh / 2, hx + 30, gb + hh / 2 + 4, f"Hoist {LR}"),
            _callout(hx - 7, hook + 15, hx - 22, hook + 32, f"Hook {UD}", "end"),
        ]
    p += [
        _callout(X(0) - 6, Y(rail_y * 0.4), X(0) + 12, Y(rail_y * 0.4) + 4, "Wall"),
        _text(X(total_w) - 4, roof - 4, "Roof", 10.5, "end", color=LABEL),
    ]
    return "".join(p)


def _plan_view(d, ox, oy, w, h):
    """Plan (top) view: end carriages with wheels, girder, hoist, runway rails."""
    total_w = d["overall_length"]
    total_h = d["end_carriage_length"]
    s = min(w / total_w, h / total_h)
    left = ox + (w - total_w * s) / 2
    top = oy + (h - total_h * s) / 2

    def X(mm): return left + mm * s
    def Y(mm): return top + mm * s

    ecl = d["end_carriage_length"]
    wb_off = (ecl - d["wheelbase"]) / 2
    rail_l = OVERHANG_EACH_SIDE
    rail_r = OVERHANG_EACH_SIDE + d["span"]
    gw = 500             # girder width on plan: drawing only, not a real size
    ecw = 300            # end carriage width on plan: drawing only
    hw, hd = 900, 1100   # hoist size on plan: drawing only

    p = [_title(ox + w / 2, oy, "PLAN VIEW", "looking down at the crane from above")]
    for rx in (rail_l, rail_r):  # runway rails
        p.append(_line(X(rx), Y(0) - 12, X(rx), Y(ecl) + 12, STROKE, 1, "8 4"))
    p.append(_rect(X(0), Y(ecl / 2 - gw / 2), X(total_w) - X(0), gw * s, "#e0e0e0"))
    p.append(_rect(X(total_w / 2 - hw / 2), Y(ecl / 2 - hd / 2), hw * s, hd * s, "#fff3e0"))
    for ex in (0, total_w - ecw):  # end carriages
        p.append(_rect(X(ex), Y(0), ecw * s, ecl * s, "#bdbdbd"))
    for wy in (wb_off, wb_off + d["wheelbase"]):  # wheels
        for rx in (rail_l, rail_r):
            p.append(f'<circle cx="{X(rx):.1f}" cy="{Y(wy):.1f}" r="4" fill="{STROKE}"/>')

    p.append(_hdim(X(rail_l), X(rail_r), Y(ecl) + 45, f'Span {d["span"]}'))
    p.append(_hdim(X(0), X(total_w), Y(ecl) + 75, f'Overall {d["overall_length"]}'))
    p.append(_vdim(X(0) - 25, Y(wb_off), Y(wb_off + d["wheelbase"]), f'{d["wheelbase"]}'))
    p.append(_vdim(X(0) - 55, Y(0), Y(ecl), f'{ecl}'))

    # part names
    xr = X(total_w)
    bx = X(total_w * 0.2)
    p += [
        _callout(X(rail_r), Y(0) - 8, xr + 18, Y(0) - 6, "Rail"),
        _callout(X(rail_r) + 4, Y(wb_off), xr + 18, Y(wb_off) + 8, "Wheel"),
        _callout(xr, Y(ecl * 0.72), xr + 18, Y(ecl * 0.72) + 4, "End carriage"),
        _text(xr + 21, Y(ecl * 0.72) + 18, f"{UD} moves along the rails", 9.5, "start", color=MUTED),
        _callout(bx, Y(ecl / 2 + gw / 2), bx + 14, Y(ecl / 2 + gw / 2) + 24, "Main beam"),
        _text(X(total_w / 2), Y(ecl / 2 - hd / 2) - 6, f"Hoist {LR}", 10.5, color=LABEL),
    ]
    return "".join(p)


PARTS = [
    ("Main beam", "Steel beam across the building"),
    ("End carriage", "Box at each end that holds the wheels"),
    ("Wheel", "Rolls on the rail"),
    ("Rail", "Steel track on top of each wall"),
    ("Hoist", "Motor that lifts the hook"),
    ("Hook", "Holds the load"),
    ("Building", "Walls, roof and floor"),
]

MOVES = [
    "Crane: on its wheels along the rails",
    f"Hoist: left and right along the main beam {LR}",
    f"Hook: up and down {UD}",
]


def _data_table(d, ox, oy):
    rows = [
        ("Load", f'{d["capacity_t"]:g} t'),
        ("Span", f'{d["span"]} mm'),
        ("Lifting height", f'{d["lifting_height"]} mm'),
        ("Overall length", f'{d["overall_length"]} mm'),
        ("Rail top height", f'{d["rail_top_height"]} mm'),
        ("Min. building height", f'{d["min_building_height"]} mm'),
        ("Crane height above rail (est.)", f'{d["crane_above_rail"]} mm'),
        ("Hook top to rail top (est.)", f'{d["hook_top_to_rail_top"]} mm'),
        ("Roof clearance (est.)", f'{d["roof_clearance"]} mm'),
        ("End clearance (est.)", f'min. {d["end_clearance_min"]} mm'),
        ("Wheelbase (est.)", f'{d["wheelbase"]} mm'),
        ("End carriage length (est.)", f'{d["end_carriage_length"]} mm'),
        ("Crane type", "Single girder EOT"),
    ]
    p = [_text(ox, oy, "TECHNICAL DATA", 14, "start", bold=True)]
    y = oy + 6
    for k, v in rows:
        y += 18
        p.append(_text(ox, y, k, 12, "start"))
        p.append(_text(ox + 290, y, v, 12, "end"))
    y += 26
    p.append(_text(ox, y, "All dimensions in mm. (est.) = estimate.", 11, "start"))
    p.append(_text(ox, y + 16, "Sizes other than inputs are ESTIMATES", 11, "start", color="#c62828"))
    p.append(_text(ox, y + 32, "from one reference drawing (10 t, 25 m).", 11, "start", color="#c62828"))
    p.append(_text(ox, y + 48, "PRELIMINARY - NOT FOR CONSTRUCTION", 11, "start", bold=True, color="#c62828"))

    y += 88
    p.append(_text(ox, y, "PARTS", 14, "start", bold=True))
    for name, desc in PARTS:
        y += 18
        p.append(_text(ox, y, name, 11, "start", bold=True, color=LABEL))
        p.append(_text(ox + 78, y, desc, 11, "start"))
    y += 30
    p.append(_text(ox, y, "HOW IT MOVES", 14, "start", bold=True))
    for line in MOVES:
        y += 18
        p.append(_text(ox, y, line, 11, "start"))
    return "".join(p)


def render_svg(inputs, title="Crane design"):
    d = compute_dimensions(inputs)
    W, H = 1400, 1000
    body = [
        HATCH,
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>',
        _rect(10, 10, W - 20, H - 20, "none", 2),
        _text(30, 45, title, 18, "start", bold=True),
        _front_view(d, 90, 110, 900, 480),
        _plan_view(d, 130, 716, 820, 154),
        _data_table(d, 1080, 130),
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">' + "".join(body) + "</svg>")
