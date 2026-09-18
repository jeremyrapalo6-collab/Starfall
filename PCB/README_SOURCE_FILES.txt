These are the canonical Starfall KiCad source files supplied by the project owner:
- Starfall.kicad_pro
- Starfall.kicad_sch
- Starfall.kicad_pcb

Earlier local checks recorded 0 unconnected pads and 0 footprint errors, with warnings mostly related to silkscreen/text clearance. Earlier ERC notes also recorded warnings related mainly to library path/configuration. The raw ERC/DRC report files are not stored in this repository, so those older counts should not be treated as a fresh manufacturing check.

The project-local fp-lib-table and sym-lib-table still contain machine-specific library paths from the original KiCad setup. The schematic and PCB source files remain the canonical design files, but another computer may show library-path warnings.

Before manufacturing or making PCB edits, open the project in KiCad on the target computer, repair any missing library paths if needed, rerun ERC/DRC, review all remaining warnings, and generate fresh Gerbers from the final board.
