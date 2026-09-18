# Reactor Celestial mechanical correction

This revision keeps the PCB layout, Reactor silhouette and celestial artwork. The user selected a taller bottom to retain the supplied M3 x 16 screws.

## Corrected construction

- Overall enclosure: **114.4 x 116 x 22.9 mm**, excluding keycaps/knob. Bottom Z=-17.00, top Z=5.90. This is 6.4 mm taller than the prior Reactor case.
- PCB underside: Z=-0.70; reference thickness: **1.60 mm**. PCB outline remains 84.89 x 96.94 mm, with 0.40 mm nominal side clearance. PCB and Gerber files are unchanged.
- Floor top: Z=-14.90, giving a 2.10 mm floor. Four 8.20 mm posts extend into that floor and form one solid with the shell. Their upper support surfaces are at Z=-0.70.
- Upper retaining collars end at Z=1.15, leaving 0.25 mm above the nominal PCB top. They limit movement without forcing the board into an exact zero-clearance sandwich.
- Each post has a **5.80 mm installation well** down to Z=-7.60, an open **4.70 mm diameter x 4.10 mm deep insert pocket**, and a **3.40 mm tip-relief bore to Z=-12.10**.
- Install a 4 mm long insert with its **top at Z=-7.60**, i.e. **6.90 mm below the post top**. The insert must not sit flush with the post top. Install it before the PCB blocks access.
- Screw seats are **6.40 mm diameter x 1.25 mm deep** (seat Z=4.65). A 16 mm under-head screw ends at Z=-11.35, giving **3.75 mm nominal thread engagement** and **0.75 mm tip-relief clearance**. The tested head envelope is 5.50 mm diameter x 3.00 mm high; heads stand proud of the plate.
- The encoder opening combines the circular shaft opening with rounded rectangular corner relief for the actual 12 x 11.6 mm body. Its decorated ring is trimmed to clear it.
- Switch openings keep a 14.20 mm lower aperture and 16.40 mm upper aperture. The top of the retaining lip is relieved from Z=3.85 to 4.20 to clear the modeled switch transition. Square accent frames replace circular rings that overlapped switch housings.
- Diode, OLED header and OLED flex/contact reliefs follow the updated 1.60 mm board reference, with a target 0.40 mm clearance where the remaining roof permits it.
- USB socket aperture: **10.2 x 5.4 mm** within a **22 x 9 mm** outer recess. The recessed face is 1.06 mm ahead of the fixed connector shell. Test the actual cable overmold.
- OLED window: **28.4 x 10.2 mm**, above the **31.2 x 12.2 mm** underside glass clearance. The ledge clears the modeled glass/display by 0.435 mm.
- Decorative pockets are generated from the actual insert contours with 0.18 mm XY expansion. Overlapping decorative solids are fused and details inside switch openings are removed.

## Assembly and physical checks

1. Print and test `production/fit_coupons/` with the actual switches, inserts and printer settings. The insert sample reproduces the deep access well: confirm the soldering tip reaches the pocket before printing the whole case.
2. Heat-set the four inserts in the bottom to the specified depth, let them cool and check the threads. Keep melted plastic out of the screw-tip relief.
3. Dry-fit the PCB, USB cable and electronics. Match the reference placement; extra header sockets or spacers change the fit. Shorten OLED leads as represented in the reference and keep other leads/solder within the available cavity.
4. Check switch latches, keycap travel, encoder knob skirt and actual screw heads. Fit and tighten the screw near the encoder before installing the knob. Do not use screw force to bend the PCB or pull interfering parts together.
5. Fit accents using an agreed print process. `Purple_Inlays_Print_Layout` contains separate flat pieces for single-colour printing; `Purple_Inlays` preserves assembled positions. Several accents are thin and require appropriate nozzle/layer settings or a multi-material workflow. Adhesive attachment is required for separately printed accents.

The small fit samples are needed for a reliable physical-fit decision because no delivered hardware or printed parts were available for measurement. A successful CAD collision test does not prove switch latch retention or heat-set performance.

## Which files to use

Current generator: `tools/generate_final_case.py` plus `tools/mechanical_fit.py`. The workflow pins CAD kernel versions and refuses to commit generated output when a tested collision or invalid structural solid is found.

Current production parts: `production/Top.STEP`, `Bottom.STEP`, `Middle_Purple.STEP`, and `Purple_Inlays.STEP` (or the separate accent layout). Matching STL files are provided. Current fit assembly: `CAD/Starfall_Mechanical_Assembly.STEP`. The reference PCB is corrected to 1.60 mm in `CAD/Starfall_fit_reference_1p6mm.STEP`; the original source electronics model is retained unchanged.

`CAD/build_case.py`, `CAD/Starfall_assembled.STEP`, `CAD/Starfall_case_assembly.STEP` and older case screenshots are historical. They are not the corrected production geometry. The coloured GLB includes presentation keycaps/knob, not measured hardware.

Measured results are in `production/MECHANICAL_VALIDATION.json` and included in `CASE_PRINT_READY_CHECK.json`. Their status explicitly retains the physical-fit qualification above.

