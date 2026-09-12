# Starfall

Starfall is my first hardware project. I wanted to make a macropad because it seemed cool, and I chose to use my favorite colors, black and purple, along with my group name, **LTC**. This was a cool but long project, and I learned a lot while making it.

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

A full-color `.glb` model is included in the `CAD` folder.

## Files

- `PCB/` — KiCad schematic, PCB, and project files
- `CAD/` — case and full assembly CAD files
- `production/` — STL/STEP case parts and Gerbers
- `Firmware/` — KMK firmware
- `assets/` — project screenshots and graphics
- `BOM.csv` — bill of materials

## What I learned

This was my first project, so I learned a lot about KiCad, schematics, PCB routing, key matrices, diodes, 3D models, case design, Gerbers, and firmware. It took a while, but seeing the whole project come together was worth it.
