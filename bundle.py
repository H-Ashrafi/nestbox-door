"""
Fold site/index.html into ONE self-contained .html file.

Images become data: URIs, the wiring SVG is inlined (so the clickable parts work
without fetch, which file:// forbids), and the DXF/SVG downloads become data
URIs too. Result opens off a USB stick, an email attachment, or a locked-down
work laptop with no network at all.

    python bundle.py
"""

import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "docs")
OUT = os.path.join(SITE, "nest-box-bench-sheet.html")

MAX_W = 1400          # downscale anything wider, to keep the file sane


def read(path, mode="r"):
    with open(path, mode, **({} if mode == "rb" else {"encoding": "utf-8"})) as f:
        return f.read()


def shrink(path):
    """Return JPEG/PNG bytes, downscaled if the image is huge. No-op without Pillow."""
    raw = read(path, "rb")
    try:
        from PIL import Image
        import io
    except ImportError:
        return raw, os.path.splitext(path)[1].lstrip(".").lower()

    im = Image.open(io.BytesIO(raw))
    if im.width <= MAX_W:
        return raw, os.path.splitext(path)[1].lstrip(".").lower()

    h = round(im.height * MAX_W / im.width)
    im = im.resize((MAX_W, h), Image.LANCZOS)
    buf = io.BytesIO()
    if im.mode in ("RGBA", "P") and path.lower().endswith(".png"):
        im.save(buf, "PNG", optimize=True)
        return buf.getvalue(), "png"
    im.convert("RGB").save(buf, "JPEG", quality=86, optimize=True)
    return buf.getvalue(), "jpeg"


MIME = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}

html = read(os.path.join(SITE, "index.html"))
svg = read(os.path.join(SITE, "nestbox-wiring.svg"))
dxf = read(os.path.join(SITE, "nestbox-wiring.dxf"), "rb")

swaps = 0


def swap(old, new, label, required=True):
    global html, swaps
    if old not in html:
        if required:
            sys.exit("MISSING TOKEN: " + label)
        return
    n = html.count(old)
    html = html.replace(old, new)
    swaps += n
    print("  %-28s %d occurrence(s)" % (label, n))


print("inlining:")

# ── images ───────────────────────────────────────────────────────────
for name in ("xiao-pinmap.png", "drv8871.jpg", "pololu.jpg", "ds3231m.jpg"):
    p = os.path.join(SITE, "img", name)
    if not os.path.exists(p):
        print("  %-28s SKIPPED (not on disk)" % name)
        continue
    data, ext = shrink(p)

    # if we shrank it, keep the small one on disk too - the served page uses it
    same_type = ext == os.path.splitext(p)[1].lstrip(".").lower().replace("jpg", "jpeg")
    if same_type and len(data) < os.path.getsize(p):
        before = os.path.getsize(p)
        with open(p, "wb") as f:
            f.write(data)
        print("      on disk  %6.0f kB -> %6.0f kB" % (before / 1024, len(data) / 1024))

    uri = "data:%s;base64,%s" % (MIME[ext], base64.b64encode(data).decode())
    swap("img/" + name, uri, name)
    print("      inlined  %6.0f kB -> %6.0f kB base64" % (len(data) / 1024, len(uri) / 1024))

# ── the wiring drawing, inlined so the click targets survive file:// ──
swap(
    '<div class="diagram" id="diagram">\n'
    '    <img src="nestbox-wiring.svg" alt="Wiring diagram" '
    'style="display:block;min-width:960px;width:100%">\n'
    '  </div>',
    '<div class="diagram" id="diagram">\n' + svg + '\n  </div>',
    "wiring svg",
)

# ── downloads, so they still work with no server ─────────────────────
swap('href="nestbox-wiring.dxf"',
     'href="data:image/vnd.dxf;base64,%s"' % base64.b64encode(dxf).decode(),
     "dxf download")
swap('href="nestbox-wiring.svg"',
     'href="data:image/svg+xml;base64,%s"' % base64.b64encode(svg.encode()).decode(),
     "svg download")

# the "download me" link makes no sense inside the downloaded copy
swap('\n    <a href="nest-box-bench-sheet.html" download id="dl-offline">'
     'this whole page as one offline file</a>',
     "", "self-link removed", required=False)

# ── replace the fetch with direct wiring of the inlined svg ──────────
old_fetch_start = "// Inline the SVG so its parts become clickable.\nfetch("
i = html.find(old_fetch_start)
if i == -1:
    sys.exit("MISSING TOKEN: fetch block")
j = html.find("</script>", i)
html = html[:i] + (
    "// The SVG is already inline in this file - just wire up the clicks.\n"
    "document.querySelectorAll('#diagram g[data-part]').forEach(function (g) {\n"
    "  var key = g.getAttribute('data-part');\n"
    "  g.addEventListener('click', function () { openPart(key); });\n"
    "  g.addEventListener('keydown', function (e) {\n"
    "    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPart(key); }\n"
    "  });\n"
    "});\n"
) + html[j:]
swaps += 1
print("  %-28s 1 occurrence(s)" % "fetch -> direct")

# a standalone file needs no robots hint, and the title should say what it is
html = html.replace('<meta name="robots" content="noindex,nofollow">\n', "")

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print("\n%d substitutions" % swaps)
print("wrote %s  (%.1f MB)" % (OUT, os.path.getsize(OUT) / 1024 / 1024))
