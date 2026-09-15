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
| `docs/index.html` | The bench sheet, written for someone with no electronics background. Every part on the wiring diagram is clickable (photo, pinout, what to do with it), every technical word opens a plain-English explanation, and the resistors are drawn with their real colour bands. Styled with Tailwind from its public CDN. |
| `docs/nestbox-wiring.svg` | The wiring diagram. Clickable parts are `<g data-part="...">`. |
| `docs/nestbox-wiring.dxf` | Same drawing, AutoCAD R2000, 288 × 188 mm (A4 landscape). |
| `docs/nest-box-bench-sheet.html` | The whole page folded into one file — images, diagram and DXF inlined. Opens off a USB stick with no network. |
| `docs/nestbox-board.svg` | The perfboard layout: where every part sits on top, and every wire on the underside. |
| `make_wiring.py` | Generates the wiring SVG and the DXF from one geometry definition, so the drawing and the CAD file can't drift apart. |
| `make_board.py` | Generates the board layout SVG and `docs/board-wires.js`, the wire list the page renders. It validates the layout first and refuses to write anything if two parts want the same hole, if two modules overlap, if a wire ends in mid-air, or if a connection from the checklist is missing. |
| `bundle.py` | Folds `docs/index.html` into the single offline file. |

## Rebuilding

```
python make_wiring.py     # -> docs/nestbox-wiring.svg + .dxf
python make_board.py      # -> docs/nestbox-board.svg + docs/board-wires.js
python bundle.py          # -> docs/nest-box-bench-sheet.html
```

`bundle.py` uses Pillow to downscale oversized photos if it's installed, and works
without it. It also fetches the Tailwind script once and pastes it in, so the offline
file is styled with no network; run it with internet access.

## Bill of materials

Australian sourcing, every link checked 15 September 2026. **$372–$483** for the parts,
plus about $166 of tools if you own none. The full list with prices, links and a line on
why each thing is there is on the [bench sheet](https://h-ashrafi.github.io/nestbox-door/#parts).

**The four boards — $46.15, one order from Core Electronics**

| Part | Price | Link |
|---|---|---|
| Seeed XIAO ESP32-C3 | $10.65 | [Core Electronics](https://core-electronics.com.au/seeed-studio-xiao-esp32c3-tiny-mcu-board-with-wi-fi-and-ble-battery-charge-supported-power-efficiency-and-rich-interface.html) |
| DS3231M MEMS RTC (DFRobot DFR0641) | $11.75 | [Core Electronics](https://core-electronics.com.au/ds3231m-mems-precise-rtc.html) |
| Adafruit DRV8871 motor driver | $13.80 | [Core Electronics](https://core-electronics.com.au/adafruit-drv8871-dc-motor-driver-breakout-board-3-6a-max.html) |
| Pololu D36V6F5 5 V buck | $9.95 | [Core Electronics](https://core-electronics.com.au/pololu-5v-600ma-step-down-voltage-regulator-d36v6f5.html) |

**Power — $74.00**

| Part | Price | Link |
|---|---|---|
| 12 V 7.2 Ah SLA battery | ≈$34.95 | [Jaycar SB2486](https://www.jaycar.com.au/12v-7-2ah-sla-back-up-battery-nbn-alarm-ufb/p/SB2486), or [$38.98 Amazon AU](https://www.amazon.com.au/dp/B0G6K9KNLK) |
| 12 V 1 A automatic SLA charger | $32.95 | [Jaycar MB3619](https://www.jaycar.com.au/12v-1a-sla-battery-charger/p/MB3619). **Jaycar wins** — the [NOCO GENIUS1](https://www.amazon.com.au/dp/B08D6WV445) is $70.95 and adds nothing for one small battery |
| Inline blade fuse holder, water resistant | $4.95 | [Jaycar SZ2042](https://www.jaycar.com.au/30a-32vdc-water-resistant-inline-standard-blade-fuse-holder/p/SZ2042) |
| 2 A blade fuse | $1.15 | [Jaycar SF2127](https://www.jaycar.com.au/2a-grey-standard-blade-fuse/p/SF2127) — separate line, the holder comes empty |

**The moving part — $108–$220**

| Part | Price | Link |
|---|---|---|
| 12 V linear actuator, 300 mm, limit switches | $88.42 | [Justech, Amazon AU](https://www.amazon.com.au/dp/B0F6TV1ZVJ) — IP54, 6 mm/s, brackets included |
| …or the weatherproof one | $199.69 | [Motion Dynamics, IP65](https://www.motiondynamics.com.au/linear-actuator-300mm-stroke-20mm-sec-12v-400n-clevis-end.html) — worth it if rain reaches the actuator |
| Cord, pulley, two eye bolts, turnbuckle | ≈$20 | any hardware shop |

**Loose components — $39.14**

| Part | Price | Link |
|---|---|---|
| Resistor pack, 300 pieces (has 220k, 33k, 10k) | $12.95 | [Jaycar RR1680](https://www.jaycar.com.au/1-4-watt-carbon-film-resistors-300-pieces/p/RR1680) |
| 100 nF monolithic capacitor | $0.35 | [Jaycar RC5490](https://www.jaycar.com.au/100nf-50vdc-monolithic-capacitor/p/RC5490) |
| CR1220 coin cell (for the clock) | $4.95 | [Jaycar SB2527](https://www.jaycar.com.au/cr1220-3v-lithium-battery/p/SB2527) |
| Male header, 2.54 mm, 1×40 — buy two | $0.45 ea | [Core Electronics CE07828](https://core-electronics.com.au/male-pin-header-2-54mm-1x40.html) |
| Double-sided perfboard kit, 32 pcs (has the 7×9 cm board) | $19.99 | [Elegoo, Amazon AU](https://www.amazon.com.au/dp/B0772FK81G) — plain perfboard, **not** stripboard |

**The box and the wire — $104.51**

| Part | Price | Link |
|---|---|---|
| Sealed IP65 ABS enclosure, 171×121×80 | $24.95 | [Jaycar HB6129](https://www.jaycar.com.au/sealed-abs-enclosure-171-x-121-x-80mm/p/HB6129) |
| PG7 cable glands, 20 pack | $20.00 | [Amazon AU](https://www.amazon.com.au/Cable-Lokman-Plastic-Waterproof-Adjustable/dp/B06Y5HGYK2), or [2 pack from Jaycar, $5.95](https://www.jaycar.com.au/3-6-5mm-dia-waterproof-cable-glands-pack-of-2/p/HP0720) |
| 18 AWG 2-core red/black, 12 m | $14.61 | [Amazon AU](https://www.amazon.com.au/dp/B01LZRV0HV) |
| Hook-up wire, 8 colours, 26 AWG | $39.95 | [Jaycar WH3009](https://www.jaycar.com.au/light-duty-hook-up-wire-pack-8-colours/p/WH3009) |
| Cable ties | ≈$5 | any hardware shop |

Tools are listed separately on the [bench sheet](https://h-ashrafi.github.io/nestbox-door/#tools),
priced both ways — Jaycar and Amazon AU.

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
