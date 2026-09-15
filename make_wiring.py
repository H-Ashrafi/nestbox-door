"""
Nest box controller - wiring diagram generator.

One geometry definition -> two outputs that cannot drift apart:
    nestbox-wiring.svg   standalone, self-contained, prints on A4 landscape
    nestbox-wiring.dxf   AutoCAD R2000 ASCII, one layer per net

Battery version (no solar). Run:  python make_wiring.py
"""

import os

W, H = 1520.0, 990.0          # SVG canvas, user units
DXF_SCALE = 0.19              # -> 288.8 x 188.1 mm, fits A4 landscape

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

ACCENT = "#0F766E"            # hover / focus colour, matches the bench sheet

# ─────────────────────────────────────────────────────────────────────
# nets: name -> (svg colour, AutoCAD colour index, legend label)
# ─────────────────────────────────────────────────────────────────────
NETS = {
    "V12":   ("#D0342C", 1,   "+12 V  (red)"),
    "GND":   ("#22262B", 8,   "GND  (black)"),
    "V5":    ("#E07B00", 30,  "+5 V  (orange)"),
    "V33":   ("#B0157A", 6,   "+3.3 V  (pink)"),
    "SDA":   ("#B08900", 2,   "SDA  (yellow)"),
    "SCL":   ("#2E7D32", 3,   "SCL  (green)"),
    "IN1":   ("#1565C0", 5,   "IN1  (blue)"),
    "IN2":   ("#00838F", 4,   "IN2  (cyan)"),
    "VBAT":  ("#7B3FA0", 140, "battery sense  (violet)"),
    "MOTA":  ("#6D4C41", 33,  "motor A  (brown)"),
    "MOTB":  ("#546E7A", 9,   "motor B  (grey)"),
    "BODY":  ("#3A4149", 7,   None),
    "TEXT":  ("#181C20", 7,   None),
    "NOTE":  ("#6B7480", 9,   None),
}

# ─────────────────────────────────────────────────────────────────────
# resistor colour bands - the real colours, so the drawing matches
# the part in your hand
# ─────────────────────────────────────────────────────────────────────
BAND_RGB = {
    "black": "#111111", "brown": "#6B3A1E", "red": "#D0342C", "orange": "#F0801A",
    "yellow": "#F3C623", "green": "#2E7D32", "blue": "#1E5AA8", "violet": "#7B3FA0",
    "grey": "#8C8C8C", "white": "#F5F5F5", "gold": "#C9A227", "silver": "#BDBDBD",
}
RES_BANDS = {
    "220 k": ["red", "red", "yellow", "gold"],
    "33 k":  ["orange", "orange", "orange", "gold"],
    "10 k":  ["brown", "black", "orange", "gold"],
}
RES_BODY = "#E8D9B5"

WIRE_W = 3.2

prims = []   # every drawable, in order
PART = None  # current clickable component, tagged onto each primitive


def part(name):
    """Everything drawn after this belongs to one clickable component."""
    global PART
    PART = name


def hot(x, y, w, h):
    """Invisible hit target that lights up on hover. SVG only."""
    prims.append(dict(k="hot", x=x, y=y, w=w, h=h, net="BODY", part=PART))


def rect(x, y, w, h, net="BODY", fill=None, lw=2.0, r=0):
    prims.append(dict(k="rect", x=x, y=y, w=w, h=h, net=net, fill=fill, lw=lw, r=r, part=PART))


def band(x, y, w, h, colour):
    """Solid colour stripe on a resistor body. Its own colour, not a net colour."""
    prims.append(dict(k="band", x=x, y=y, w=w, h=h, net="BODY", colour=colour, part=PART))


def line(x1, y1, x2, y2, net="BODY", lw=2.0):
    prims.append(dict(k="line", x1=x1, y1=y1, x2=x2, y2=y2, net=net, lw=lw, part=PART))


def wire(pts, net):
    """Orthogonal wire through a list of (x, y) points."""
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        line(x1, y1, x2, y2, net, WIRE_W)


def hop(x, y, net, r=9.0):
    """Semicircular bridge on a vertical wire crossing a horizontal one."""
    prims.append(dict(k="hop", x=x, y=y, r=r, net=net, lw=WIRE_W, part=PART))


def dot(x, y, net="GND", r=5.5):
    prims.append(dict(k="dot", x=x, y=y, r=r, net=net, part=PART))


def text(x, y, s, net="TEXT", size=14.0, anchor="start", weight="normal"):
    prims.append(dict(k="text", x=x, y=y, s=s, net=net, size=size,
                      anchor=anchor, weight=weight, part=PART))


def block(x, y, w, h, title, subtitle=None):
    rect(x, y, w, h, "BODY", fill="#FFFFFF", lw=2.4, r=4)
    text(x + w / 2, y + 30, title, "TEXT", 17.0, "middle", "bold")
    if subtitle:
        text(x + w / 2, y + 52, subtitle, "NOTE", 12.5, "middle")


def pin(x, y, label, side, net="BODY"):
    """Small terminal square plus its label, placed just inside the block."""
    rect(x - 5, y - 5, 10, 10, "BODY", fill="#FFFFFF", lw=1.6)
    if not label:
        return
    if side == "l":
        text(x + 14, y + 4.5, label, "TEXT", 12.5, "start")
    elif side == "r":
        text(x - 14, y + 4.5, label, "TEXT", 12.5, "end")
    elif side == "t":
        # a riser leaves this pin downwards, so the label sits beside it
        text(x + 12, y + 28, label, "TEXT", 12.5, "start")
    else:
        text(x, y - 16, label, "TEXT", 12.5, "middle")


def resistor(x, y, value, net, label="right"):
    """A real-looking 4-band resistor centred on (x, y), vertical, 46 long.
    The bands are the true colour code for that value."""
    rect(x - 11, y - 23, 22, 46, "BODY", fill=RES_BODY, lw=1.8, r=6)
    for off, colour in zip((-14, -6, 2, 12), RES_BANDS[value]):
        band(x - 11, y + off, 22, 5, BAND_RGB[colour])
    if isinstance(label, tuple):          # (dx, dy, anchor) for a tight spot
        text(x + label[0], y + label[1], value, "TEXT", 12.0, label[2])
    else:
        text(x + 18, y + 4.5, value, "TEXT", 12.0, "start")


def capacitor(x, y, value, marking, net):
    """Vertical non-polarised cap centred on (x, y)."""
    line(x - 16, y - 6, x + 16, y - 6, "BODY", 3.0)
    line(x - 16, y + 6, x + 16, y + 6, "BODY", 3.0)
    # one line, up and to the left, in the clear space above the clock block
    text(x + 41, y - 71, value + ", " + marking, "TEXT", 11.0, "end")


# ═════════════════════════════════════════════════════════════════════
# GEOMETRY
# ═════════════════════════════════════════════════════════════════════
GND_Y = 880.0
V12_TOP_Y = 180.0

# ── battery ──────────────────────────────────────────────────────────
part("battery")
block(40, 640, 190, 160, "12 V 7.2 Ah SLA", "Jaycar SB2486")
pin(230, 680, "+", "r")
pin(230, 750, "−", "r")
hot(30, 630, 212, 180)

# ── fuse on the + wire ───────────────────────────────────────────────
part("fuse")
rect(252, 666, 76, 28, "BODY", fill="#FFFFFF", lw=2.0)
line(252, 680, 328, 680, "V12", 2.0)
text(290, 658, "2 A fuse", "TEXT", 12.0, "middle")
hot(246, 648, 90, 54)

# ── buck ─────────────────────────────────────────────────────────────
part("buck")
block(470, 640, 200, 160, "5 V buck", "Pololu D36V6F5")
pin(470, 680, "VIN", "l")
pin(670, 760, "VOUT 5 V", "r")
pin(520, 800, "GND", "t")
hot(460, 630, 220, 182)

# ── RTC ──────────────────────────────────────────────────────────────
part("clock")
block(400, 330, 200, 175, "DS3231M clock", "DFRobot DFR0641")
pin(600, 370, "VCC", "r")
pin(600, 420, "SDA", "r")
pin(600, 470, "SCL", "r")
pin(440, 505, "GND", "t")
text(540, 552, "CR1220 cell on board", "NOTE", 12.0, "middle")
text(540, 570, "keeps time while you", "NOTE", 12.0, "middle")
text(540, 588, "charge the battery", "NOTE", 12.0, "middle")
hot(390, 320, 220, 196)

# ── XIAO ─────────────────────────────────────────────────────────────
part("xiao")
block(760, 300, 240, 430, "XIAO ESP32-C3", "Seeed, SS113991054")
pin(760, 370, "3V3", "l")
pin(760, 420, "D4 / SDA", "l")
pin(760, 470, "D5 / SCL", "l")
pin(760, 660, "5V", "l")
pin(850, 300, "", "b")
text(864, 293, "D2 / A2", "TEXT", 12.5, "start")    # beside the sense wire, not under it
pin(1000, 390, "D1", "r")
pin(1000, 450, "D3", "r")
pin(820, 730, "GND", "t")
text(880, 600, "D0, D8, D9 are strapping", "NOTE", 12.0, "middle")
text(880, 618, "pins — leave them empty", "NOTE", 12.0, "middle")
hot(750, 290, 260, 452)

# ── motor driver ─────────────────────────────────────────────────────
part("driver")
block(1090, 330, 220, 285, "DRV8871", "Adafruit, 3.6 A")
pin(1140, 330, "", "b")
text(1154, 318, "POWER +", "TEXT", 12.5, "start")   # beside the 12 V riser
pin(1090, 390, "IN1", "l")
pin(1090, 450, "IN2", "l")
pin(1240, 615, "GND (POWER −)", "t")
pin(1310, 400, "MOTOR 1", "r")
pin(1310, 470, "MOTOR 2", "r")
text(1200, 668, "screw terminals on top,", "NOTE", 12.0, "middle")
text(1200, 686, "solder header on the bottom", "NOTE", 12.0, "middle")
hot(1080, 320, 240, 306)

# ── actuator ─────────────────────────────────────────────────────────
part("actuator")
block(1370, 355, 120, 180, "actuator", "12 V, 300 mm")
pin(1370, 400, "", "l")
pin(1370, 470, "", "l")
text(1430, 560, "limit switches", "NOTE", 12.0, "middle")
text(1430, 578, "are inside it", "NOTE", 12.0, "middle")
hot(1360, 345, 140, 202)

# ── battery-sense divider ────────────────────────────────────────────
part("divider")
resistor(700, 225, "220 k", "VBAT")
resistor(700, 345, "33 k", "VBAT")
capacitor(645, 345, "100 nF", "marked 104", "VBAT")
text(722, 279, "sense node", "NOTE", 11.0, "start")
hot(616, 196, 130, 236)
part(None)

# ═════════════════════════════════════════════════════════════════════
# WIRES
# ═════════════════════════════════════════════════════════════════════

# +12 V: battery -> fuse -> buck VIN, with a riser to the top run
wire([(230, 680), (470, 680)], "V12")
wire([(390, 680), (390, V12_TOP_Y), (1140, V12_TOP_Y), (1140, 330)], "V12")
dot(390, 680, "V12")

# +12 V tap for the divider
wire([(700, V12_TOP_Y), (700, 202)], "V12")
dot(700, V12_TOP_Y, "V12")

# divider body
wire([(700, 248), (700, 322)], "VBAT")
wire([(700, 368), (700, 751)], "VBAT")      # split for the hop below
hop(700, 760, "VBAT")
wire([(700, 769), (700, GND_Y)], "VBAT")
dot(700, GND_Y, "VBAT")

# cap in parallel with the lower leg
wire([(700, 285), (645, 285), (645, 339)], "VBAT")
wire([(645, 351), (645, 405), (700, 405)], "VBAT")
dot(700, 285, "VBAT")
dot(700, 405, "VBAT")

# sense to the ADC pin
wire([(700, 285), (850, 285), (850, 300)], "VBAT")

# 5 V: buck -> XIAO
wire([(670, 760), (740, 760), (740, 660), (760, 660)], "V5")

# 3V3 + I2C: XIAO <-> RTC
wire([(600, 370), (760, 370)], "V33")
wire([(600, 420), (760, 420)], "SDA")
wire([(600, 470), (760, 470)], "SCL")

# signals: XIAO -> driver
wire([(1000, 390), (1090, 390)], "IN1")
wire([(1000, 450), (1090, 450)], "IN2")

# pull-downs, in the clear corridor between the XIAO and the driver.
# Clickable as one part: they are the same job twice.
part("pulldowns")
wire([(1015, 390), (1015, 677)], "IN1")
resistor(1015, 700, "10 k", "IN1", label=(-12, 44, "end"))
wire([(1015, 723), (1015, GND_Y)], "IN1")
dot(1015, 390, "IN1")
dot(1015, GND_Y, "IN1")

wire([(1050, 450), (1050, 747)], "IN2")
resistor(1050, 770, "10 k", "IN2", label=(18, 4.5, "start"))
wire([(1050, 793), (1050, GND_Y)], "IN2")
dot(1050, 450, "IN2")
dot(1050, GND_Y, "IN2")
text(1068, 836, "pull-downs", "NOTE", 11.0, "start")
hot(996, 655, 72, 190)
part(None)

# motor
wire([(1310, 400), (1370, 400)], "MOTA")
wire([(1310, 470), (1370, 470)], "MOTB")

# ── ground spine and its risers ──────────────────────────────────────
wire([(230, GND_Y), (1240, GND_Y)], "GND")
wire([(230, 750), (230, GND_Y)], "GND")
wire([(440, 505), (440, 671)], "GND")        # split for the hop
hop(440, 680, "GND")
wire([(440, 689), (440, GND_Y)], "GND")
wire([(520, 800), (520, GND_Y)], "GND")
wire([(820, 730), (820, GND_Y)], "GND")
wire([(1240, 615), (1240, GND_Y)], "GND")
for gx in (440, 520, 820):
    dot(gx, GND_Y, "GND")
text(300, 866, "ground spine", "NOTE", 11.0, "middle")
text(600, 162, "+12 V line", "NOTE", 11.0, "middle")

# ═════════════════════════════════════════════════════════════════════
# LEGEND + TITLE BLOCK
# ═════════════════════════════════════════════════════════════════════
rect(40, 896, 900, 82, "NOTE", fill=None, lw=1.4)
text(56, 920, "WIRE COLOURS", "NOTE", 11.5, "start", "bold")
legend_nets = ["V12", "GND", "V5", "V33", "SDA", "SCL", "IN1", "IN2", "VBAT", "MOTA"]
for i, n in enumerate(legend_nets):
    cx = 56 + (i % 5) * 172
    cy = 943 + (i // 5) * 22
    line(cx, cy - 4, cx + 22, cy - 4, n, 3.4)
    text(cx + 30, cy, NETS[n][2], "NOTE", 11.0, "start")

rect(1000, 896, 490, 82, "NOTE", fill=None, lw=1.4)
text(1016, 920, "NEST BOX CONTROLLER — WIRING", "TEXT", 13.0, "start", "bold")
text(1016, 942, "Battery version, no solar.  Sheet 2 of 2.", "NOTE", 11.5, "start")
text(1016, 964, "A dot means joined.  A bridge means crossing, NOT joined.",
     "NOTE", 11.5, "start")

text(760, 62, "Every ground goes to the one black spine along the bottom.",
     "NOTE", 13.0, "middle")
text(760, 84, "Nothing here is mains powered.  Nothing connects to a network.",
     "NOTE", 13.0, "middle")

# ── click targets for the two long wires, drawn last so they sit on top ──
part("spine")
hot(220, 868, 1032, 24)
part("v12")
hot(380, 168, 772, 24)
hot(336, 668, 130, 24)
part(None)


# ═════════════════════════════════════════════════════════════════════
# SVG
# ═════════════════════════════════════════════════════════════════════
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def to_svg():
    o = []
    o.append('<?xml version="1.0" encoding="UTF-8"?>')
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
             'width="%g" height="%g" role="img" '
             'aria-label="Wiring diagram for the battery-powered nest box '
             'controller: a 12 volt sealed lead-acid battery feeds a fused bus '
             'to a 5 volt buck converter and a DRV8871 motor driver; the XIAO '
             'ESP32-C3 reads a DS3231 clock over I2C, senses battery voltage '
             'through a divider, and drives the linear actuator through two '
             'signal wires with pull-down resistors.">' % (W, H, W, H))
    o.append('<style>'
             'text{font-family:"JetBrains Mono",ui-monospace,Consolas,monospace;}'
             'g[data-part]{cursor:pointer}'
             'g[data-part] .hit{fill:%s;fill-opacity:0;stroke:%s;'
             'stroke-width:2.5;stroke-opacity:0;transition:.12s}'
             'g[data-part]:hover .hit,g[data-part]:focus .hit{fill-opacity:.10;stroke-opacity:.95}'
             '</style>' % (ACCENT, ACCENT))
    o.append('<rect x="0" y="0" width="%g" height="%g" fill="#FFFFFF"/>' % (W, H))

    open_part = None
    for p in prims:
        pt = p.get("part")
        if pt != open_part:
            if open_part is not None:
                o.append('</g>')
            if pt is not None:
                o.append('<g data-part="%s" tabindex="0" role="button" '
                         'aria-label="%s — what it is and how to wire it">' % (pt, pt))
            open_part = pt

        col = NETS[p["net"]][0]
        k = p["k"]
        if k == "hot":
            o.append('<rect class="hit" x="%g" y="%g" width="%g" height="%g" rx="7"/>'
                     % (p["x"], p["y"], p["w"], p["h"]))
        elif k == "rect":
            fill = p["fill"] if p["fill"] else "none"
            o.append('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" '
                     'fill="%s" stroke="%s" stroke-width="%g"/>'
                     % (p["x"], p["y"], p["w"], p["h"], p["r"], fill, col, p["lw"]))
        elif k == "band":
            o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                     % (p["x"], p["y"], p["w"], p["h"], p["colour"]))
        elif k == "line":
            o.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" '
                     'stroke-width="%g" stroke-linecap="round"/>'
                     % (p["x1"], p["y1"], p["x2"], p["y2"], col, p["lw"]))
        elif k == "hop":
            x, y, r = p["x"], p["y"], p["r"]
            o.append('<path d="M %g %g A %g %g 0 0 1 %g %g" fill="none" '
                     'stroke="%s" stroke-width="%g"/>'
                     % (x, y - r, r, r, x, y + r, col, p["lw"]))
        elif k == "dot":
            o.append('<circle cx="%g" cy="%g" r="%g" fill="%s"/>'
                     % (p["x"], p["y"], p["r"], col))
        elif k == "text":
            o.append('<text x="%g" y="%g" fill="%s" font-size="%g" '
                     'text-anchor="%s" font-weight="%s">%s</text>'
                     % (p["x"], p["y"], col, p["size"], p["anchor"],
                        p["weight"], esc(p["s"])))
    if open_part is not None:
        o.append('</g>')
    o.append('</svg>')
    return "\n".join(o)


# ═════════════════════════════════════════════════════════════════════
# DXF  (AutoCAD R2000 / AC1015, via ezdxf)
# ═════════════════════════════════════════════════════════════════════
import ezdxf
from ezdxf import colors as dxfcolors
from ezdxf.enums import TextEntityAlignment


def dx(x):
    return x * DXF_SCALE


def dy(y):
    return (H - y) * DXF_SCALE          # DXF is Y-up


def layer_of(net):
    return "N_" + net


ALIGN = {
    "start":  TextEntityAlignment.LEFT,
    "middle": TextEntityAlignment.CENTER,
    "end":    TextEntityAlignment.RIGHT,
}


def hex_to_int(h):
    h = h.lstrip("#")
    return dxfcolors.rgb2int((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))


def write_dxf(path):
    doc = ezdxf.new("R2000", setup=True)
    doc.header["$INSUNITS"] = 4          # millimetres
    msp = doc.modelspace()

    for net, (_col, aci, _lbl) in NETS.items():
        doc.layers.add(name=layer_of(net), color=aci)
    doc.layers.add(name="BANDS", color=7)

    for p in prims:
        att = {"layer": layer_of(p["net"])}
        k = p["k"]
        if k == "hot":
            continue                       # screen-only hit target
        if k == "rect":
            x, y, w, h = p["x"], p["y"], p["w"], p["h"]
            msp.add_lwpolyline(
                [(dx(x), dy(y)), (dx(x + w), dy(y)),
                 (dx(x + w), dy(y + h)), (dx(x), dy(y + h))],
                close=True, dxfattribs=att)
        elif k == "band":
            x, y, w, h = p["x"], p["y"], p["w"], p["h"]
            pts = [(dx(x), dy(y)), (dx(x + w), dy(y)),
                   (dx(x + w), dy(y + h)), (dx(x), dy(y + h))]
            hatch = msp.add_hatch(dxfattribs={"layer": "BANDS",
                                              "true_color": hex_to_int(p["colour"])})
            hatch.paths.add_polyline_path(pts, is_closed=True)
        elif k == "line":
            msp.add_line((dx(p["x1"]), dy(p["y1"])),
                         (dx(p["x2"]), dy(p["y2"])), dxfattribs=att)
        elif k == "hop":
            msp.add_arc(center=(dx(p["x"]), dy(p["y"])),
                        radius=p["r"] * DXF_SCALE,
                        start_angle=270.0, end_angle=90.0, dxfattribs=att)
        elif k == "dot":
            msp.add_circle(center=(dx(p["x"]), dy(p["y"])),
                           radius=p["r"] * DXF_SCALE, dxfattribs=att)
        elif k == "text":
            t = msp.add_text(p["s"],
                             height=p["size"] * DXF_SCALE * 0.80,
                             dxfattribs=dict(att, style="Standard"))
            t.set_placement((dx(p["x"]), dy(p["y"])), align=ALIGN[p["anchor"]])

    doc.saveas(path)


svg_path = os.path.join(OUT_DIR, "nestbox-wiring.svg")
dxf_path = os.path.join(OUT_DIR, "nestbox-wiring.dxf")

with open(svg_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(to_svg())
write_dxf(dxf_path)

print("primitives :", len(prims))
print("svg        :", svg_path, os.path.getsize(svg_path), "bytes")
print("dxf        :", dxf_path, os.path.getsize(dxf_path), "bytes  (R2000)")
print("dxf sheet  : %.1f x %.1f mm" % (W * DXF_SCALE, H * DXF_SCALE))
