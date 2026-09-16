# Starfall Reactor Celestial mechanical review

**Result: corrected CAD passes the modeled fit and export checks. Physical fit samples are still required before printing the full case.**

The inspected starting revision was `f9a30b811fe1d1366b2a4be003aab4074ceeba8e`. The user chose a deeper bottom to keep the supplied M3 x 16 screws. PCB, schematic, Gerbers and firmware were not changed.

## Problems found in that revision

- The bottom was five disconnected solids: four posts floated 2.45 mm above the floor.
- A 0.25 mm plastic cap closed each insert pocket.
- M3 x 16 screws were too long for the existing insert and floor stack.
- The reduced circular encoder opening intersected the modeled encoder body by about 16.05 mmÂ³.
- Missing underside relief caused collisions with all nine diodes and the OLED header/contact parts. The OLED header intersection alone was about 44.07 mmÂ³.
- Circular purple rings extended into the square switch openings and intersected switch bodies. Small decorations also occupied switch openings.
- The source electronics STEP used a 1.51 mm PCB while the actual board specification is 1.60 mm.
- The repository's old print-ready record checked nominal diameters and individual shape validity, but did not establish assembled mechanical fit.

## Corrections

The enclosure is now **112 x 116 x 22.9 mm**, 6.4 mm taller. The four posts join the floor, their insert seats are open and positioned for the supplied screws, and upper collars limit PCB movement. Screw pass-throughs remain 3.4 mm; head seats are enlarged to 6.4 mm. No PCB hole was moved.

The 16 mm screws have **3.75 mm nominal insert engagement** and **0.75 mm clearance to the end of the tip-relief bore**. Inserts must be installed with their tops **6.9 mm below the support-post tops**, through 5.8 mm installation wells. Check soldering-tip access on the insert sample first.

Encoder corner relief and diode/OLED underside relief were added. Switch frames are square and clear the switch openings. Inlay pockets follow the actual insert contours, with lateral clearance, and hidden details inside switch openings were removed. The USB access tunnel is **18 x 8 mm** to provide space for a cable mold through the thicker front wall.

The electronics fit reference uses a **1.60 mm PCB** with a fixed underside datum. Top-side parts follow the corrected thickness; bottom-side parts retain their underside placement. Presentation hardware is not used as proof of actual fit.

## Verification

- **217 electronics solids** checked against all three structural case parts.
- **37 decorative solids** checked against case, electronics and one another.
- All four screw envelopes checked against case, electronics and decorations. Checked screw head: 5.5 mm diameter x 3 mm height.
- No positive-volume intersections found in those tests. Intentional PCB/support contact is allowed.
- Top, bottom and middle are each one connected, valid solid.
- Production STEP files reimport as valid solids; all four STL files are watertight. STEP/STL volume differences are below 0.02%.
- PCB/production drill coordinates remain aligned with all four mount holes and all nine switch centres.

The exported top needed conversion to STEP-compatible surfaces: a live-model validity test alone did not detect a STEP round-trip failure. The generator now checks the actual exported files as well as the model, and assembly exports are checked for missing solids.

Raw results: [`production/MECHANICAL_VALIDATION.json`](production/MECHANICAL_VALIDATION.json), [`production/EXPORT_VALIDATION.json`](production/EXPORT_VALIDATION.json), and [`production/CASE_PRINT_READY_CHECK.json`](production/CASE_PRINT_READY_CHECK.json).

## What remains a physical check

The minimum modeled switch/plate gap is approximately **0.030 mm** at the retaining geometry. This is a close functional fit, not a generous FDM clearance. The switch sample tests 14.2/14.4/14.6 mm openings; use the actual switch and print settings to verify insertion and retention before committing the complete case. Change the aperture if the sample requires it.

Also test the deep insert well with the actual iron tip and insert, the actual USB cable, keycap travel, encoder knob skirt and screw head. Extra header sockets/standoffs alter the modeled stack. Thin decorative parts may need an appropriate nozzle/layer height or multi-material printing; the flat accent layout is supplied for separate printing.

Use the assembly instructions in [`CAD/MECHANICAL_NOTES.md`](CAD/MECHANICAL_NOTES.md) and the [`fit-sample guide`](production/fit_coupons/README.md). Older case screenshots and legacy assemblies are not the corrected production files.
