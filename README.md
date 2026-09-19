# Starfall

Starfall is my first hardware project. I wanted to make a macropad because it seemed cool, and I chose to use my favorite colors, black and purple, along with my group name, **LTC**. This was a cool but long project, and I learned a lot while making it.

![Starfall Celestial case](assets/fully_assembled_preview.png)

## What it is

Starfall is a 9-key macropad with a rotary encoder and a small OLED display. I designed it around a Seeed Studio XIAO RP2040 and made a custom PCB and case for it.

The macropad has three modes:

- **Everyday** - shortcuts for normal computer use
- **Gaming** - keys for games
- **Coding** - shortcuts for VS Code and Python

The bottom-right key changes between the three modes, and the OLED shows which mode is active.

## Design

The Celestial case pairs a black shell with purple side trusses, stars, a crescent and a bold slanted LTC logo. It has a stepped OLED surround and a recessed USB-C opening. Keycap symbols and knob in the preview are illustrative accessories.

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

The current case is **Starfall Celestial** (114.4 x 116 x 22.9 mm including side trusses).

- Black: `production/Top.STEP` and `production/Bottom.STEP`.
- Purple: `production/Middle_Purple.STEP` and `production/Purple_Inlays_Print_Layout.STEP` (one set of accents).
- Matching STL files are provided. `Purple_Inlays.STEP` is the same accents in assembled positions: do not print both accent files.
- [Fully assembled STEP](CAD/Starfall_Fully_Assembled.STEP) and [colored GLB](CAD/Starfall_Fully_Assembled_Colored.glb).
- [Design changes and physical fit checks](DESIGN_NOTES.md) and [assembly instructions](CAD/MECHANICAL_NOTES.md).

The L has been shifted 0.35 mm right. The taller bottom retains M3x16 screws with recessed insert seats. The PCB layout is unchanged. Print the switch/insert coupons and check your actual cable before a full case: CAD checks do not guarantee physical fit. All files in production are current. The case PNGs and older assembly filenames are synchronized to the latest Celestial case; PCB screenshots describe the unchanged PCB.

Automated CAD results: [mechanical](production/MECHANICAL_VALIDATION.json), [exports](production/EXPORT_VALIDATION.json), [structural intersections](production/STRUCTURAL_COLLISIONS.json).

### Current case views

![Current assembled angled view](assets/case_iso.png)

![Current top view](assets/case_top.png)

![Current exploded assembly](assets/case_exploded.png)

These views are rendered from the current assembly. Keycaps, legends and knob are illustrative accessories. See [asset descriptions](assets/SCREENSHOTS.md).

### Printable Starfall encoder knob

[Download the knob print pack](production/knob/Starfall-Knob-Print-Pack.zip) or browse [individual STL/STEP files and instructions](production/knob/README.md).

![Black fluted knob with purple star](production/knob/Knob_Preview.png)

Print `Knob_Black.stl` in black and `Knob_Star_Purple.stl` in purple. Test `Dshaft_sample_6p2mm.stl` on the actual encoder first. The 6.1 and 6.3 mm samples provide fit alternatives; change the knob bore if needed before printing. Modeled clearances pass, but physical shaft fit and push travel require testing. Full-case previews still show the previous illustrative knob; the files in `production/knob/` are the printable design.

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
| M3 screw | 4 | M3 x 16 mm | Deeper bottom; checked head envelope is diameter 5.5 x height 3 mm |
| Heat-set insert | 4 | M3 x 5 x 4 mm insert | 4.7 x 4.1 mm pocket below a 5.8 mm installation well |
| PCB | 1 | Starfall 2-layer PCB, 84.89 x 96.94 mm | Gerbers in `production/` |
| Case: black | 1 set | `Top.STEP` + `Bottom.STEP` | 3D printed |
| Case: purple | 1 set | `Middle_Purple.STEP` + `Purple_Inlays.STEP` | 3D printed accents |

The full BOM with source/reference links is also available in [`BOM.csv`](BOM.csv).

## Files

- `PCB/` - KiCad schematic, PCB, and project files
- `CAD/` - case, assemblies, and full-color GLB preview
- `production/` - final STEP/STL case parts, Gerbers, print-ready check, and `main.py`
- `Firmware/` - KMK firmware source
- `assets/` - project screenshots and graphics
- `tools/` - reproducible final-case generator
- `BOM.csv` - bill of materials with reference links

## What I learned

This was my first project, so I learned a lot about KiCad, schematics, PCB routing, key matrices, diodes, 3D models, case design, Gerbers, and firmware. It took a while, but seeing the whole project come together was worth it.
