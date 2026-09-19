# Current case downloads

- Starfall_Fully_Assembled.STEP: full Celestial assembly.
- Starfall_Fully_Assembled_Colored.glb: full colored assembly.
- Starfall_Reactor_Celestial_FINAL_COLORED_CASE.STEP: case-only assembly.
- Starfall_Mechanical_Assembly.STEP: case with electronics used for fit checks.

Starfall_assembled.STEP and Starfall_case_assembly.STEP now mirror the current full and case-only assemblies. All GLB filenames in CAD/ and assets/ mirror the current full colored assembly. These compatibility names are refreshed by tools/make_full_assembly.py.

Use ../production/ for individual printable parts. build_case.py is the historical generator; the current generator is ../tools/generate_final_case.py. Original electronics STEP files remain source references.
