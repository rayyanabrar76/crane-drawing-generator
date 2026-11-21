"""Makes a dimensioned 2D SVG drawing of a single girder overhead crane.

All lengths in mm. Every fixed number below says where it came from.
"REF" = read from the reference drawing (10 t, 25 m span crane).
These REF numbers are ESTIMATES for other sizes: I only have one example.
"""

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
        "crane_above_rail": CRANE_ABOVE_RAIL,
        "min_building_height": crane_top + ROOF_CLEARANCE,
        "roof_clearance": ROOF_CLEARANCE,
        "end_clearance_min": END_CLEARANCE_MIN,
        "wheelbase": WHEELBASE,
        "end_carriage_length": END_CARRIAGE_LENGTH,
    }


# --- SVG helpers ---
STROKE = "#111"
DIM = "#1565c0"


def _line(x1, y1, x2, y2, color=STROKE, width=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d}/>'


def _rect(x, y, w, h, fill="none", width=1.5):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{STROKE}" stroke-width="{width}"/>'


def _text(x, y, s, size=12, anchor="middle", rotate=False, color=STROKE, bold=False):
    rot = f' transform="rotate(-90 {x:.1f} {y:.1f})"' if rotate else ""
    w = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-family="Arial, sans-serif" fill="{color}"{w}{rot}>{s}</text>')


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


def _front_view(d, ox, oy, w, h):
    """Front elevation: walls, rails, girder, hoist, hook, floor."""
    total_h = d["min_building_height"]
    total_w = d["overall_length"] + 2 * d["end_clearance_min"]
    s = min(w / total_w, (h - 70) / total_h)  # 70 px kept free for top dimensions
    left = ox + (w - total_w * s) / 2
    floor_y = oy + h

    def X(mm):  # mm from left wall -> px
        return left + mm * s

    def Y(mm):  # mm above floor -> px
        return floor_y - mm * s

    ec = d["end_clearance_min"]
    crane_l, crane_r = ec, ec + d["overall_length"]
    rail_l, rail_r = ec + OVERHANG_EACH_SIDE, ec + OVERHANG_EACH_SIDE + d["span"]
    rail_y = d["rail_top_height"]
    top_y = rail_y + d["crane_above_rail"]
    roof_y = d["min_building_height"]
    girder_depth = d["crane_above_rail"] * 0.6  # drawing only, not a real size
    hoist_x = (crane_l + crane_r) / 2
    hook_y = d["lifting_height"]

    p = []
    p.append(_text(ox + w / 2, oy - 30, "FRONT VIEW", 14, bold=True))
    # floor, walls, roof line
    p.append(_line(X(0) - 20, floor_y, X(total_w) + 20, floor_y, STROKE, 2))
    p.append(_text(X(total_w / 2), floor_y + 16, "Floor ±0", 11))
    p.append(_line(X(0), floor_y, X(0), Y(roof_y), STROKE, 2))
    p.append(_line(X(total_w), floor_y, X(total_w), Y(roof_y), STROKE, 2))
    p.append(_line(X(0), Y(roof_y), X(total_w), Y(roof_y), STROKE, 1, "6 4"))
    # runway rails (small blocks)
    for rx in (rail_l, rail_r):
        p.append(_rect(X(rx) - 4, Y(rail_y), 8, 6, STROKE))
    # end carriages and girder
    p.append(_rect(X(crane_l), Y(top_y), X(crane_r) - X(crane_l), girder_depth * s, "#e0e0e0"))
    p.append(_rect(X(crane_l), Y(top_y), 14, (top_y - rail_y) * s, "#bdbdbd"))
    p.append(_rect(X(crane_r) - 14, Y(top_y), 14, (top_y - rail_y) * s, "#bdbdbd"))
    p.append(_text(X(hoist_x) - 60, Y(top_y) + girder_depth * s / 2 + 5, f'{d["capacity_t"]:g} t', 14, bold=True))
    # hoist, rope, hook
    hb = Y(top_y - girder_depth)
    p.append(_rect(X(hoist_x) - 18, hb, 36, 28, "#fff3e0"))
    p.append(_line(X(hoist_x), hb + 28, X(hoist_x), Y(hook_y), STROKE, 1))
    p.append(f'<path d="M{X(hoist_x):.1f},{Y(hook_y):.1f} v10 a6,6 0 1 1 -8,6" fill="none" stroke="{STROKE}" stroke-width="2"/>')
    # dimensions
    p.append(_hdim(X(rail_l), X(rail_r), Y(roof_y) - 60, f'Span {d["span"]}'))
    p.append(_hdim(X(crane_l), X(crane_r), Y(roof_y) - 30, f'Overall {d["overall_length"]}'))
    p.append(_hdim(X(0), X(crane_l), Y(rail_y) + 40, f'Min.{ec}', X(0) + 4, "start"))
    p.append(_vdim(X(hoist_x) + 40, floor_y, Y(hook_y), f'Lifting height {d["lifting_height"]}'))
    p.append(_vdim(X(total_w) + 35, floor_y, Y(rail_y), f'Rail top {d["rail_top_height"]}'))
    p.append(_vdim(X(total_w) + 35, Y(rail_y), Y(top_y), f'{d["crane_above_rail"]}'))
    p.append(_vdim(X(total_w) + 75, floor_y, Y(roof_y), f'Min. building height {d["min_building_height"]}'))
    return "".join(p)


def _plan_view(d, ox, oy, w, h):
    """Plan (top) view: two end carriages, girder, runway rails."""
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
    gw = 500  # girder width on plan: drawing only, not a real size

    p = []
    p.append(_text(ox + w / 2, oy - 30, "PLAN VIEW", 14, bold=True))
    for rx in (rail_l, rail_r):  # runway rails
        p.append(_line(X(rx), Y(0) - 25, X(rx), Y(ecl) + 25, STROKE, 1, "8 4"))
    p.append(_rect(X(0), Y(ecl / 2 - gw / 2), X(total_w) - X(0), gw * s, "#e0e0e0"))
    for ex in (0, total_w - 300):  # end carriages (300 mm wide: drawing only)
        p.append(_rect(X(ex), Y(0), 300 * s + 4, ecl * s, "#bdbdbd"))
    for wy in (wb_off, wb_off + d["wheelbase"]):  # wheels
        for rx in (rail_l, rail_r):
            p.append(f'<circle cx="{X(rx):.1f}" cy="{Y(wy):.1f}" r="4" fill="{STROKE}"/>')
    p.append(_hdim(X(rail_l), X(rail_r), Y(ecl) + 45, f'Span {d["span"]}'))
    p.append(_hdim(X(0), X(total_w), Y(ecl) + 75, f'Overall {d["overall_length"]}'))
    p.append(_vdim(X(0) - 25, Y(wb_off), Y(wb_off + d["wheelbase"]), f'{d["wheelbase"]}'))
    p.append(_vdim(X(0) - 55, Y(0), Y(ecl), f'{ecl}'))
    return "".join(p)


def _data_table(d, ox, oy):
    rows = [
        ("Load", f'{d["capacity_t"]:g} t'),
        ("Span", f'{d["span"]} mm'),
        ("Lifting height", f'{d["lifting_height"]} mm'),
        ("Rail top height", f'{d["rail_top_height"]} mm'),
        ("Min. building height", f'{d["min_building_height"]} mm'),
        ("Roof clearance (est.)", f'{d["roof_clearance"]} mm'),
        ("Crane type", "Single girder EOT"),
    ]
    p = [_text(ox, oy, "TECHNICAL DATA", 14, "start", bold=True)]
    for i, (k, v) in enumerate(rows):
        y = oy + 24 + i * 20
        p.append(_text(ox, y, k, 12, "start"))
        p.append(_text(ox + 260, y, v, 12, "end"))
    y = oy + 24 + len(rows) * 20 + 10
    p.append(_text(ox, y, "All dimensions in mm.", 11, "start"))
    p.append(_text(ox, y + 16, "Sizes other than inputs are ESTIMATES", 11, "start", color="#c62828"))
    p.append(_text(ox, y + 32, "from one reference drawing (10 t, 25 m).", 11, "start", color="#c62828"))
    p.append(_text(ox, y + 48, "PRELIMINARY - NOT FOR CONSTRUCTION", 11, "start", bold=True, color="#c62828"))
    return "".join(p)


def render_svg(inputs, title="Crane design"):
    d = compute_dimensions(inputs)
    W, H = 1400, 1000
    body = [
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>',
        _rect(10, 10, W - 20, H - 20, "none", 2),
        _text(30, 45, title, 18, "start", bold=True),
        _front_view(d, 90, 110, 900, 480),
        _plan_view(d, 130, 700, 820, 170),
        _data_table(d, 1080, 130),
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">' + "".join(body) + "</svg>")
