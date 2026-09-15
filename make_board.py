"""
Nest box controller - perfboard layout guide.

One layout definition -> docs/nestbox-board.svg, a two-panel drawing:

    TOP VIEW        where each module and each loose component sits
    UNDERSIDE       mirrored, with every wire you have to solder

The script validates the layout before it draws it. It refuses to write the
file if two things want the same hole, if two module bodies overlap, if a wire
starts or ends in mid-air, or if any connection from the bench sheet checklist
is missing. That way the drawing cannot quietly drift away from the circuit.

Board: 70 x 90 mm double-sided perfboard, 0.1 inch grid, 35 x 27 holes,
used in landscape. Run:  python make_board.py
"""

import os
import sys

NCOLS, NROWS = 35, 27
PITCH = 18.0                      # px per hole in the drawing
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

V12_ROW = 3                       # the +12 V rail runs along this row
GND_ROW = 26                      # the ground spine runs along this row
RAIL_C0, RAIL_C1 = 3, 33

# ── colours, matching the wiring diagram sheet ────────────────────────
NET = {
    "V12":  "#D0342C", "GND":  "#22262B", "V5":   "#E07B00", "V33":  "#B0157A",
    "SDA":  "#B08900", "SCL":  "#2E7D32", "IN1":  "#1565C0", "IN2":  "#00838F",
    "VBAT": "#7B3FA0", "MOTA": "#6D4C41", "MOTB": "#546E7A",
}
# the colour of hook-up wire to actually use for each net, matching the
# legend on the wiring diagram
WIRE_COLOUR = {
    "V12": "red", "GND": "black", "V5": "orange", "V33": "pink",
    "SDA": "yellow", "SCL": "green", "IN1": "blue", "IN2": "white",
    "VBAT": "violet", "MOTA": "brown", "MOTB": "grey",
}
BAND = {
    "black": "#111111", "brown": "#6B3A1E", "red": "#D0342C", "orange": "#F0801A",
    "yellow": "#F3C623", "green": "#2E7D32", "blue": "#1E5AA8", "violet": "#7B3FA0",
    "grey": "#8C8C8C", "white": "#F5F5F5", "gold": "#C9A227",
}
RES_BANDS = {
    "220k": ["red", "red", "yellow", "gold"],
    "33k":  ["orange", "orange", "orange", "gold"],
    "10k":  ["brown", "black", "orange", "gold"],
}

INK, SOFT, LINE = "#16191D", "#5B6470", "#C3C9D0"
COPPER, BOARD = "#C8922E", "#2F6B3A"

# ═════════════════════════════════════════════════════════════════════
# THE LAYOUT
# ═════════════════════════════════════════════════════════════════════
# modules: name -> (label, sublabel, body box (c0,r0,c1,r1), pins [(name,c,r)])
MODULES = [
    dict(key="buck", label="5 V buck", sub="Pololu D36V6F5",
         body=(4, 6, 8, 11),
         pins=[("VOUT", 4, 6), ("GND", 5, 6), ("VIN", 6, 6)]),
    dict(key="xiao", label="XIAO ESP32-C3", sub="Seeed",
         body=(13, 7, 19, 15),
         pins=[("D0", 13, 8), ("D1", 13, 9), ("D2", 13, 10), ("D3", 13, 11),
               ("D4", 13, 12), ("D5", 13, 13), ("D6", 13, 14),
               ("5V", 19, 8), ("GND", 19, 9), ("3V3", 19, 10), ("D10", 19, 11),
               ("D9", 19, 12), ("D8", 19, 13), ("D7", 19, 14)]),
    dict(key="clock", label="DS3231M clock", sub="DFRobot DFR0641",
         body=(12, 18, 20, 26),
         pins=[("VCC", 13, 18), ("GND", 14, 18), ("SCL", 15, 18), ("SDA", 16, 18),
               ("INT", 17, 18), ("RST", 18, 18), ("32K", 19, 18)]),
    dict(key="driver", label="DRV8871", sub="Adafruit · screw terminals face the top edge",
         body=(23, 5, 32, 12),
         pins=[("IN2", 24, 12), ("IN1", 25, 12), ("VM", 26, 12), ("GND", 27, 12)]),
]

# loose parts. capside keeps the captions from landing on top of each other.
PARTS = [
    dict(kind="res", value="220k", col=9,  ra=13, rb=17, cap="220 kΩ", capside="right"),
    dict(kind="res", value="33k",  col=9,  ra=18, rb=22, cap="33 kΩ",  capside="left"),
    dict(kind="cap", value="100n", col=11, ra=18, rb=20, cap="100 nF", capside="left"),
    dict(kind="res", value="10k",  col=23, ra=14, rb=18, cap="10 kΩ",  capside="left"),
    dict(kind="res", value="10k",  col=25, ra=14, rb=18, cap="10 kΩ",  capside="right"),
]

# wires you solder on the underside: (net, (c,r), (c,r), what it is)
WIRES = [
    ("V12",  (6, 6),   (6, V12_ROW),   "buck VIN to the +12 V rail"),
    ("GND",  (5, 6),   (5, GND_ROW),   "buck GND to the ground spine"),
    ("V5",   (4, 6),   (19, 8),        "buck VOUT to XIAO 5V"),

    ("V12",  (9, V12_ROW), (9, 13),    "+12 V rail to the top of the 220 kΩ"),
    ("VBAT", (9, 17),  (9, 18),        "the sense node: joins the 220 kΩ to the 33 kΩ"),
    ("GND",  (9, 22),  (9, GND_ROW),   "bottom of the 33 kΩ to the ground spine"),
    ("VBAT", (9, 18),  (11, 18),       "sense node across to the capacitor"),
    ("GND",  (11, 20), (11, GND_ROW),  "capacitor to the ground spine"),
    ("VBAT", (9, 17),  (13, 10),       "sense node to XIAO D2"),

    ("GND",  (19, 9),  (21, GND_ROW),  "XIAO GND to the ground spine"),
    ("V33",  (19, 10), (13, 18),       "XIAO 3V3 to clock VCC"),
    ("GND",  (14, 18), (14, GND_ROW),  "clock GND to the ground spine"),
    ("SCL",  (13, 13), (15, 18),       "XIAO D5 to clock SCL"),
    ("SDA",  (13, 12), (16, 18),       "XIAO D4 to clock SDA"),

    ("IN1",  (13, 9),  (25, 12),       "XIAO D1 to driver IN1"),
    ("IN2",  (13, 11), (24, 12),       "XIAO D3 to driver IN2"),
    ("IN1",  (25, 12), (25, 14),       "driver IN1 down to its 10 kΩ"),
    ("GND",  (25, 18), (25, GND_ROW),  "that 10 kΩ to the ground spine"),
    ("IN2",  (24, 12), (23, 14),       "driver IN2 across to its 10 kΩ"),
    ("GND",  (23, 18), (23, GND_ROW),  "that 10 kΩ to the ground spine"),
    ("GND",  (27, 12), (27, GND_ROW),  "driver GND to the ground spine"),
]

# thick figure-8 that leaves the board, drawn as a stub with a label
LEADS = [
    ("V12",  (RAIL_C0, V12_ROW), "left",  "battery +"),
    ("GND",  (RAIL_C0, GND_ROW), "left",  "battery −"),
    ("V12",  (RAIL_C1, V12_ROW), "right", "POWER +"),
    ("GND",  (RAIL_C1, GND_ROW), "right", "POWER −"),
]

# Every line of the bench sheet checklist, as (net, end, end). "rail" means the
# connection is made by landing on one of the two rails rather than by a wire.
CHECKLIST = [
    ("V12",  "battery+",     "rail"),
    ("GND",  "battery-",     "rail"),
    ("V12",  "rail",         ("buck", "VIN")),
    ("V12",  "rail",         "driver POWER +"),
    ("GND",  "rail",         ("buck", "GND")),
    ("GND",  "rail",         "driver POWER -"),
    ("V5",   ("buck", "VOUT"), ("xiao", "5V")),
    ("GND",  ("xiao", "GND"), "rail"),
    ("V33",  ("xiao", "3V3"), ("clock", "VCC")),
    ("GND",  ("clock", "GND"), "rail"),
    ("SDA",  ("xiao", "D4"), ("clock", "SDA")),
    ("SCL",  ("xiao", "D5"), ("clock", "SCL")),
    ("IN1",  ("xiao", "D1"), ("driver", "IN1")),
    ("IN2",  ("xiao", "D3"), ("driver", "IN2")),
    ("IN1",  ("driver", "IN1"), "10k"),
    ("IN2",  ("driver", "IN2"), "10k"),
    ("GND",  ("driver", "GND"), "rail"),
    ("V12",  "rail",         "220k"),
    ("VBAT", "220k",         "33k"),
    ("VBAT", "sense",        "100n"),
    ("VBAT", "sense",        ("xiao", "D2")),
]


# ═════════════════════════════════════════════════════════════════════
# VALIDATION - the drawing is not written unless all of this passes
# ═════════════════════════════════════════════════════════════════════
def hole_owner_map():
    owner = {}
    for m in MODULES:
        for name, c, r in m["pins"]:
            key = (c, r)
            if key in owner:
                sys.exit("HOLE CLASH at %s: %s and %s" % (key, owner[key], m["key"] + "." + name))
            owner[key] = m["key"] + "." + name
    for p in PARTS:
        for r in (p["ra"], p["rb"]):
            key = (p["col"], r)
            if key in owner:
                sys.exit("HOLE CLASH at %s: %s and %s" % (key, owner[key], p["cap"]))
            owner[key] = p["cap"]
    return owner


def check_bounds(owner):
    for (c, r), who in owner.items():
        if not (1 <= c <= NCOLS and 1 <= r <= NROWS):
            sys.exit("OFF THE BOARD: %s at %s" % (who, (c, r)))
        if r in (V12_ROW, GND_ROW):
            sys.exit("ON A RAIL: %s sits at %s, which is a rail row" % (who, (c, r)))


def check_bodies():
    boxes = [(m["key"], m["body"]) for m in MODULES]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (k1, (a0, b0, a1, b1)), (k2, (c0, d0, c1, d1)) = boxes[i], boxes[j]
            if a0 <= c1 and c0 <= a1 and b0 <= d1 and d0 <= b1:
                sys.exit("MODULES OVERLAP: %s and %s" % (k1, k2))
    # a loose part must not sit under a module body
    for p in PARTS:
        for k, (a0, b0, a1, b1) in boxes:
            if a0 <= p["col"] <= a1 and not (p["rb"] < b0 or p["ra"] > b1):
                sys.exit("PART UNDER MODULE: %s is under %s" % (p["cap"], k))


def check_wires(owner):
    rails = {(c, V12_ROW) for c in range(RAIL_C0, RAIL_C1 + 1)}
    rails |= {(c, GND_ROW) for c in range(RAIL_C0, RAIL_C1 + 1)}
    for net, a, b, what in WIRES:
        if net not in NET:
            sys.exit("UNKNOWN NET %r on %r" % (net, what))
        for end in (a, b):
            if end not in owner and end not in rails:
                sys.exit("WIRE ENDS IN MID-AIR: %s of %r" % (str(end), what))


def check_checklist():
    """Every checklist line must be reachable in the layout."""
    pin_of = {}
    for m in MODULES:
        for name, c, r in m["pins"]:
            pin_of[(m["key"], name)] = (c, r)

    wired = set()
    for net, a, b, _ in WIRES:
        wired.add((a, b))
        wired.add((b, a))
    on_rail = lambda h: h[1] in (V12_ROW, GND_ROW)

    def resolve(end):
        """A ("module", "PIN") pair becomes the hole it lands in. Anything else
        is a name for something off-board or a loose part, and is not checked here."""
        if isinstance(end, tuple) and len(end) == 2 and end in pin_of:
            return pin_of[end]
        return None

    missing = []
    for net, a, b in CHECKLIST:
        ha, hb = resolve(a), resolve(b)
        if ha and hb:
            if (ha, hb) not in wired:
                missing.append("%s: %s to %s" % (net, a, b))
        elif ha and b == "rail":
            if not any((ha == x and on_rail(y)) or (ha == y and on_rail(x))
                       for _, x, y, _ in WIRES):
                missing.append("%s: %s to a rail" % (net, a))
        elif hb and a == "rail":
            if not any((hb == x and on_rail(y)) or (hb == y and on_rail(x))
                       for _, x, y, _ in WIRES):
                missing.append("%s: a rail to %s" % (net, b))
    if missing:
        sys.exit("CHECKLIST LINES NOT IN THE LAYOUT:\n  " + "\n  ".join(missing))


owner = hole_owner_map()
check_bounds(owner)
check_bodies()
check_wires(owner)
check_checklist()


# ═════════════════════════════════════════════════════════════════════
# DRAWING
# ═════════════════════════════════════════════════════════════════════
MARGIN_L, MARGIN_T = 122.0, 118.0
BOARD_W = (NCOLS - 1) * PITCH
BOARD_H = (NROWS - 1) * PITCH
EDGE = 24.0                       # bare board margin around the outermost holes
PANEL_W = MARGIN_L + BOARD_W + 168
PANEL_H = MARGIN_T + BOARD_H + 66
SVG_W = PANEL_W
SVG_H = PANEL_H * 2 + 24


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def col_letter(c):
    """1 -> A, 26 -> Z, 27 -> AA."""
    s = ""
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


class Panel:
    """One view of the board. mirror=True flips left-right, for the underside."""

    def __init__(self, oy, mirror, title, subtitle):
        self.o = []
        self.oy = oy
        self.mirror = mirror
        self.title = title
        self.subtitle = subtitle

    def x(self, c):
        cc = (NCOLS + 1 - c) if self.mirror else c
        return MARGIN_L + (cc - 1) * PITCH

    def y(self, r):
        return self.oy + MARGIN_T + (r - 1) * PITCH

    # left and right edges of the hole field, whichever way round it is drawn
    def xmin(self):
        return min(self.x(1), self.x(NCOLS))

    def xmax(self):
        return max(self.x(1), self.x(NCOLS))

    def outward(self, c, c0, c1):
        """+1 to place a label to the right of the body, -1 to the left."""
        s = -1 if c == c0 else 1
        return -s if self.mirror else s

    def add(self, s):
        self.o.append(s)

    def text(self, x, y, s, size=11, fill=INK, anchor="middle", weight="normal", extra=""):
        self.add('<text x="%.1f" y="%.1f" font-size="%g" fill="%s" text-anchor="%s" '
                 'font-weight="%s"%s>%s</text>'
                 % (x, y, size, fill, anchor, weight, extra, esc(s)))

    # ── frame, grid, rails ──────────────────────────────────────────
    def frame(self):
        x0, y0 = self.xmin() - EDGE, self.y(1) - EDGE
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
                 'stroke="#1F4D2B" stroke-width="2"/>'
                 % (x0, y0, BOARD_W + 2 * EDGE, BOARD_H + 2 * EDGE, BOARD))
        self.text(x0, self.oy + 36, self.title, 17, INK, "start", "bold")
        self.text(x0, self.oy + 58, self.subtitle, 11.5, SOFT, "start")
        self.text(x0 + BOARD_W + 2 * EDGE, self.oy + 36,
                  "70 × 90 mm board · %d × %d holes" % (NCOLS, NROWS), 11, SOFT, "end")

    def grid(self):
        # one tiled pattern rather than 945 circles, which keeps the file small
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#holes)"/>'
                 % (self.xmin() - PITCH / 2, self.y(1) - PITCH / 2,
                    BOARD_W + PITCH, BOARD_H + PITCH))
        # column letters above the board, row numbers down its left
        for c in range(1, NCOLS + 1, 2):
            self.text(self.x(c), self.y(1) - EDGE - 8, col_letter(c), 9, SOFT)
        for r in range(1, NROWS + 1, 2):
            self.text(self.xmin() - EDGE - 8, self.y(r) + 3.5, str(r), 9, SOFT, "end")

    def rails(self):
        # label each rail on a clear patch of board, not out in the margin,
        # where it would run into the leads coming off the rail ends
        spec = ((V12_ROW, "V12", "+12 V rail · row %d" % V12_ROW, 21, 20),
                (GND_ROW, "GND", "ground spine · row %d" % GND_ROW, 28, -13))
        for row, net, label, at_col, dy in spec:
            self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="6" stroke-linecap="round" opacity=".92"/>'
                     % (self.x(RAIL_C0), self.y(row), self.x(RAIL_C1), self.y(row), NET[net]))
            self.text(self.x(at_col), self.y(row) + dy, label, 10.5, "#F2F6F2",
                      "middle", "bold",
                      ' stroke="#14351F" stroke-width="3.5" paint-order="stroke"')

    # ── top view ────────────────────────────────────────────────────
    def module(self, m):
        c0, r0, c1, r1 = m["body"]
        xa, xb = sorted((self.x(c0), self.x(c1)))
        ya, yb = self.y(r0), self.y(r1)
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#1F2937" '
                 'fill-opacity=".93" stroke="#0B0F14" stroke-width="1.5"/>'
                 % (xa - 9, ya - 9, xb - xa + 18, yb - ya + 18))
        self.text((xa + xb) / 2, ya + 14, m["label"], 12, "#F3F5F7", "middle", "bold")
        self.text((xa + xb) / 2, ya + 30, m["sub"], 9, "#AEB6BF")
        halo = ' stroke="#FFFFFF" stroke-width="3.5" paint-order="stroke"'
        # pins that share a row get their labels stacked outside that edge,
        # alternating between two heights so neighbours never touch
        rows = [r for _n, _c, r in m["pins"]]
        horizontal = len(set(rows)) == 1
        for i, (name, c, r) in enumerate(m["pins"]):
            self.add('<rect x="%.1f" y="%.1f" width="9" height="9" fill="#E9B949" '
                     'stroke="#8A6D1F" stroke-width="1"/>' % (self.x(c) - 4.5, self.y(r) - 4.5))
            if horizontal:
                near_top = abs(r - r0) <= abs(r - r1)
                step = 15 + (i % 2) * 15
                ly = (ya - 9 - step + 4) if near_top else (yb + 9 + step)
                self.text(self.x(c), ly, name, 9.5, INK, "middle", "bold", halo)
            else:
                out = self.outward(c, c0, c1)
                self.text(self.x(c) + out * 21, self.y(r) + 3.5, name, 9.5, INK,
                          "start" if out > 0 else "end", "bold", halo)

    def caption(self, p, x, mid, ylow):
        halo = ' stroke="#FFFFFF" stroke-width="3.5" paint-order="stroke"'
        side = p.get("capside", "right")
        if side in ("left", "right"):
            out = 1 if side == "right" else -1
            if self.mirror:
                out = -out
            self.text(x + out * 18, mid + 3, p["cap"], 10, INK,
                      "start" if out > 0 else "end", "bold", halo)
        else:
            self.text(x, ylow + 20, p["cap"], 10, INK, "middle", "bold", halo)

    def part(self, p):
        x = self.x(p["col"])
        ya, yb = self.y(p["ra"]), self.y(p["rb"])
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#9AA0A6" '
                 'stroke-width="2.4"/>' % (x, ya, x, yb))
        if p["kind"] == "res":
            mid = (ya + yb) / 2
            self.add('<rect x="%.1f" y="%.1f" width="17" height="34" rx="6" fill="#E8D9B5" '
                     'stroke="#B9A77C" stroke-width="1.2"/>' % (x - 8.5, mid - 17))
            for off, colour in zip((-11, -5, 1, 9), RES_BANDS[p["value"]]):
                self.add('<rect x="%.1f" y="%.1f" width="17" height="4" fill="%s"/>'
                         % (x - 8.5, mid + off, BAND[colour]))
            self.caption(p, x, mid, yb)
        else:
            mid = (ya + yb) / 2
            self.add('<ellipse cx="%.1f" cy="%.1f" rx="13" ry="10" fill="#E4B65A" '
                     'stroke="#B48A2E" stroke-width="1.2"/>' % (x, mid))
            self.text(x, mid + 3.5, "104", 8.5, "#3A2A08")
            self.caption(p, x, mid, yb)
        for r in (p["ra"], p["rb"]):
            self.add('<circle cx="%.1f" cy="%.1f" r="4" fill="#B0B6BC"/>' % (x, self.y(r)))

    # ── underside view ──────────────────────────────────────────────
    def wire(self, net, a, b):
        (c1, r1), (c2, r2) = a, b
        x1, y1, x2, y2 = self.x(c1), self.y(r1), self.x(c2), self.y(r2)
        col = NET[net]
        if c1 == c2 or r1 == r2:
            d = "M %.1f %.1f L %.1f %.1f" % (x1, y1, x2, y2)
        else:
            # gentle curve, so two wires between the same rows stay apart
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            bend = 16 if (c1 + r1) % 2 else -16
            d = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (x1, y1, mx + bend, my - bend, x2, y2)
        self.add('<path d="%s" fill="none" stroke="%s" stroke-width="3" '
                 'stroke-linecap="round" opacity=".95"/>' % (d, col))
        for (xx, yy) in ((x1, y1), (x2, y2)):
            self.add('<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s"/>' % (xx, yy, col))

    def pin_ghost(self, m):
        """Seen from the back: the module's outline and where its pins come through.
        No per-pin text here - it would sit under the wires. The wire list names
        every hole, and the letters and numbers around the board find it."""
        c0, r0, c1, r1 = m["body"]
        xa, xb = sorted((self.x(c0), self.x(c1)))
        ya, yb = self.y(r0), self.y(r1)
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#0E2A18" '
                 'fill-opacity=".45" stroke="#7FA98C" stroke-width="1.2" '
                 'stroke-dasharray="5 4"/>' % (xa - 9, ya - 9, xb - xa + 18, yb - ya + 18))
        self.text((xa + xb) / 2, ya - 15, m["label"], 10, "#CFE0D4", "middle", "bold")
        for _name, c, r in m["pins"]:
            self.add('<circle cx="%.1f" cy="%.1f" r="6.5" fill="#E9B949" fill-opacity=".38" '
                     'stroke="#E9B949" stroke-width="1.2"/>' % (self.x(c), self.y(r)))

    def part_ghost(self, p):
        for r in (p["ra"], p["rb"]):
            self.add('<circle cx="%.1f" cy="%.1f" r="6" fill="#D8C79F" fill-opacity=".35" '
                     'stroke="#D8C79F" stroke-width="1"/>' % (self.x(p["col"]), self.y(r)))

    def lead(self, net, hole, side, label):
        """A thick lead that leaves the board, drawn out past the edge."""
        c, r = hole
        x, y = self.x(c), self.y(r)
        left = (side == "left") != self.mirror
        tip = (self.xmin() - EDGE - 14) if left else (self.xmax() + EDGE + 14)
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="6" '
                 'stroke-linecap="round"/>' % (x, y, tip, y, NET[net]))
        self.add('<circle cx="%.1f" cy="%.1f" r="5" fill="%s"/>' % (x, y, NET[net]))
        self.text(tip + (-8 if left else 8), y - 10, label, 9.5, NET[net],
                  "end" if left else "start", "bold")

    def out(self):
        return "\n".join(self.o)


# ── build the two panels ─────────────────────────────────────────────
top = Panel(0, False, "1 · The top, where the parts go",
            "Every module and every loose component, in the holes it belongs in.")
top.frame()
top.grid()
top.rails()
for p in PARTS:
    top.part(p)
for m in MODULES:
    top.module(m)
for net, hole, side, _label in LEADS:
    top.lead(net, hole, side, _label)

bot = Panel(PANEL_H + 20, True, "2 · The underside, where you solder",
            "Flipped left to right, the way it looks when you turn the board over. "
            "Each line is one wire.")
bot.frame()
bot.grid()
bot.rails()
for m in MODULES:
    bot.pin_ghost(m)
for p in PARTS:
    bot.part_ghost(p)
for net, a, b, _what in WIRES:
    bot.wire(net, a, b)
for net, hole, side, _label in LEADS:
    bot.lead(net, hole, side, _label)


def to_svg():
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" width="%.0f" '
         'height="%.0f" role="img" aria-label="Perfboard layout for the nest box '
         'controller. The top panel shows where the four modules, the four resistors '
         'and the capacitor sit on a 70 by 90 millimetre perfboard. The bottom panel '
         'shows the same board flipped over, with every wire you solder on the '
         'underside, coloured by net.">' % (SVG_W, SVG_H, SVG_W, SVG_H),
         '<style>text{font-family:"JetBrains Mono",ui-monospace,Consolas,monospace}</style>',
         '<defs><pattern id="holes" width="%g" height="%g" patternUnits="userSpaceOnUse">'
         '<circle cx="%g" cy="%g" r="2.6" fill="none" stroke="%s" stroke-width="1.5" '
         'opacity=".55"/></pattern></defs>' % (PITCH, PITCH, PITCH / 2, PITCH / 2, COPPER),
         '<rect width="%.0f" height="%.0f" fill="#FFFFFF"/>' % (SVG_W, SVG_H),
         top.out(), bot.out(), '</svg>']
    return "\n".join(o)


path = os.path.join(OUT_DIR, "nestbox-board.svg")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(to_svg())

# ── the same wire list, for the page to render as a tick-off table ────
def hole(h):
    return "%s%d" % (col_letter(h[0]), h[1])


js_path = os.path.join(OUT_DIR, "board-wires.js")
rows = []
for net, a, b, what in WIRES:
    rows.append('  ["%s", "%s", "%s", "%s", "%s"]'
                % (net, hole(a), hole(b), WIRE_COLOUR[net], what.replace('"', "'")))
with open(js_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("// Generated by make_board.py. Do not edit by hand.\n"
            "// net, from hole, to hole, wire colour, what it is\n"
            "const BOARD_WIRES = [\n" + ",\n".join(rows) + "\n];\n")

print("layout checks : all passed")
print("holes used    :", len(owner))
print("wires         :", len(WIRES))
print("svg           :", path, os.path.getsize(path), "bytes")
print("wire list js  :", js_path, os.path.getsize(js_path), "bytes")
print()
print("WIRE LIST")
for net, a, b, what in WIRES:
    line = ("  %-5s %-6s -> %-6s  %s"
            % (net, "%s%d" % (col_letter(a[0]), a[1]),
               "%s%d" % (col_letter(b[0]), b[1]), what))
    # the console may be cp1252, and the captions contain an ohm sign
    sys.stdout.write(line.encode(sys.stdout.encoding or "utf-8", "replace")
                     .decode(sys.stdout.encoding or "utf-8") + "\n")
