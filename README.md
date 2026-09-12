# Starfall

Starfall is my first hardware project. I wanted to make a macropad because it seemed cool, and I chose to use my favorite colors, black and purple, along with my group name, **LTC**. This was a cool but long project, and I learned a lot while making it.

![Starfall case render](assets/case_iso.png)

## What it is

Starfall is a 9-key macropad with a rotary encoder and a small OLED display. I designed it around a Seeed Studio XIAO RP2040 and made a custom PCB and case for it.

The macropad has three modes:

- **Everyday** — shortcuts for normal computer use
- **Gaming** — keys for games
- **Coding** — shortcuts for VS Code and Python

The bottom-right key changes between the three modes, and the OLED shows which mode is active.

## Design

I wanted Starfall to have a black and purple space-themed look. The case uses black as the main color with purple accents, an **LTC** logo, a purple ring around the encoder, and custom symbols on the keycaps.

## Hardware

- Seeed Studio XIAO RP2040
- 9 MX-compatible switches
- 9 1N4148 diodes
- 0.91-inch SSD1306 I2C OLED
- EC11 rotary encoder
- Custom 2-layer PCB
- Custom 3D-printed case
- 9 keycaps
- M3 screws and heat-set inserts

## Firmware

The firmware uses **KMK / CircuitPython**.

The three layers are:

### Everyday
Copy, paste, cut, undo, redo, select all, screenshot, media play/pause, and mode change.

### Gaming
A set of gaming keys plus the mode-change key.

### Coding
VS Code shortcuts such as run, debug, format, comment, terminal, split editor, command palette, quick open, and mode change.

## PCB

### Schematic

![Starfall schematic](assets/schematic.png)

### PCB layout

![Starfall PCB layout](assets/pcb_editor.png)

### Front 3D view

![Starfall PCB front](assets/pcb_3d_front.png)

### Back 3D view

![Starfall PCB back](assets/pcb_3d_back.png)

### Gerber check

![Starfall Gerber Viewer](assets/gerber_viewer.png)

## Case

The case is split into separate printable pieces:

- black top
- black bottom
- purple middle spacer
- purple decorative inlays

The case also has mounting holes, M3 screw holes, heat-set insert pockets, a USB-C opening, OLED opening, encoder opening, and switch openings.

### 3D case assembly

![Starfall case exploded view](assets/case_exploded.png)

A full-color `.glb` model is included in the `CAD` folder.

## Bill of Materials

| Item | Qty | Part / Specification | Notes |
| --- | ---: | --- | --- |
| Microcontroller | 1 | Seeed Studio XIAO RP2040 | Hackpad MCU |
| Mechanical switch | 9 | MX-compatible PCB-mount switch | 1u switches |
| Diode | 9 | 1N4148 DO-35 through-hole | One per key |
| Rotary encoder | 1 | EC11E, 20 mm D-shaft | Encoder input |
| OLED | 1 | 0.91 in 128x32 SSD1306 I2C | 4-pin module |
| Keycap | 9 | 1u MX keycaps | 9 total |
| Encoder knob | 1 | D-shaft knob sized for EC11E | Knob for encoder |
| M3 screw | 4 | M3 x 16 mm | Top pass-through fasteners |
| Heat-set insert | 4 | M3 x 5 x 4 mm insert | Fits 4.7 mm x 4 mm pockets |
| PCB | 1 | Starfall 2-layer PCB, 84.89 x 96.94 mm | Gerbers in `production/` |
| Case: black | 1 set | `Top.STEP` + `Bottom.STEP` | 3D printed |
| Case: purple | 1 set | `Middle_Purple.STEP` + `Purple_Inlays.STEP` | 3D printed accents |

The full BOM with source/reference links is also available in [`BOM.csv`](BOM.csv).

## Files

- `PCB/` — KiCad schematic, PCB, and project files
- `CAD/` — case and full assembly CAD files
- `production/` — STEP/STL case parts, Gerbers, and `main.py`
- `Firmware/` — KMK firmware source
- `assets/` — project screenshots and graphics
- `BOM.csv` — bill of materials with reference links

## What I learned

This was my first project, so I learned a lot about KiCad, schematics, PCB routing, key matrices, diodes, 3D models, case design, Gerbers, and firmware. It took a while, but seeing the whole project come together was worth it.
