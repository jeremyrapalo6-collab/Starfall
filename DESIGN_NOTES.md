# Starfall polished revision

## Changes in this revision
- Stepped OLED window: 31.2 x 12.2 mm underside clearance, 28.4 x 10.2 mm viewing window above Z=4.2. The modeled display/glass reaches Z=3.765, leaving 0.435 mm below the ledge. The modeled active area stays fully within the window. The complete assembly now shows the actual OLED glass in black rather than a floating, undersized decorative screen.
- USB: recessed outer face at Y=-50.3, only 1.06 mm ahead of the existing connector shell. Outer cable recess 22 x 9 mm; socket aperture 10.2 x 5.4 mm. PCB and connector are not moved. Actual cable overmold fit must be checked.
- Custom bold slanted LTC inlay (L shifted 0.35 mm right); twelve purple stars and a crescent across unused top areas.
- Existing M3x16 stack, insert seats and PCB layout retained. Overall case 114.4 x 116 x 22.9 mm including side trusses.

Use only this package's production files and full assembly for this revision. Top and Bottom are black; Middle_Purple and Purple_Inlays are purple. The middle band includes the side trusses; print its flat upper face on the bed. Print loose accents using Purple_Inlays_Print_Layout.

## Physical checks before a full print
Switch clearance is about 0.030 mm in the model: use the supplied fit coupon and actual switches first. Test the deep insert coupon with the real iron and insert (insert top 6.9 mm below support top). Verify cable overmold, keycap travel and actual knob skirt/head dimensions. Passing CAD checks cannot guarantee physical fit. Keycap symbols and knob in full assemblies are illustrative accessories, not validated printable replacement parts.

See production/MECHANICAL_VALIDATION.json, EXPORT_VALIDATION.json and STRUCTURAL_COLLISIONS.json for results. CAD/MECHANICAL_NOTES.md describes the retained screw/insert assembly; the OLED and USB dimensions above supersede its previous openings.
