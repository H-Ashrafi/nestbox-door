# Nest box door

An automatic shutter for chicken nest boxes. It closes them mid-afternoon and opens
them again before dawn, so the hens lay in the boxes but can't sleep in them.

**Live page: https://h-ashrafi.github.io/nestbox-door/**

Battery only — no mains, no solar, no wi-fi. A XIAO ESP32-C3 works out today's
sunrise and sunset from the date and your latitude, and drives one 12 V linear
actuator that shuts every box at once.

## What's here

| Path | What it is |
|---|---|
| `docs/index.html` | The bench sheet. Every part on the wiring diagram is clickable — photo, pinout, and what to do with it. |
| `docs/nestbox-wiring.svg` | The wiring diagram. Clickable parts are `<g data-part="...">`. |
| `docs/nestbox-wiring.dxf` | Same drawing, AutoCAD R2000, 288 × 188 mm (A4 landscape). |
| `docs/nest-box-bench-sheet.html` | The whole page folded into one file — images, diagram and DXF inlined. Opens off a USB stick with no network. |
| `make_wiring.py` | Generates the SVG and the DXF from one geometry definition, so the drawing and the CAD file can't drift apart. |
| `bundle.py` | Folds `docs/index.html` into the single offline file. |

## Rebuilding

```
python make_wiring.py     # -> docs/nestbox-wiring.svg + .dxf
python bundle.py          # -> docs/nest-box-bench-sheet.html
```

`bundle.py` uses Pillow to downscale oversized photos if it's installed, and works
without it.

## Bill of materials

Australian sourcing, checked 15 September 2026. Roughly **$240–$300** plus tools.

- Seeed XIAO ESP32-C3 — $10.65, Core Electronics
- DFRobot DS3231M clock (DFR0641) — $11.75, Core Electronics
- Adafruit DRV8871 motor driver — $13.80, Core Electronics
- Pololu D36V6F5 5 V buck — $9.95, Core Electronics
- 12 V 7.2 Ah SLA battery (SB2486) — $34.95, Jaycar
- 12 V 1 A automatic SLA charger (MB3619) — $32.95, Jaycar
- 12 V linear actuator, 300 mm stroke, built-in limit switches — $56–$118, eBay AU

## Two things that bite

- **D0, D8 and D9 on the XIAO are strapping pins.** A pull-down on any of them and
  the board won't boot. IN1 and IN2 go to D1 and D3 instead.
- **Drive the panel through a cord, never a rigid link.** The actuator only ever
  lifts; gravity closes the door. Bolted straight on it pushes 100 N onto whatever
  is underneath it.

## Credits

Board photos are the manufacturers' own — [Seeed](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/),
[Adafruit](https://learn.adafruit.com/adafruit-drv8871-brushed-dc-motor-driver-breakout/pinouts),
[Pololu](https://www.pololu.com/product/3792), [DFRobot](https://wiki.dfrobot.com/dfr0641/) —
reproduced for reference while building, with attribution on each.
