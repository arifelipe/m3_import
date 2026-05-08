# Changelog

All notable changes to the M3 Addon will be documented in this file.

## [0.5.2] - 2025

### Added
- **3D Print Preparation Feature** by MickeyKnox#1985
  - New operator: `m3.prepare_3d_print` accessible from the M3 Material Selection panel
  - Smart Adaptive Subdivision that automatically applies normal map details to geometry
  - Automatic texture detection supporting multiple naming conventions (normal, norm, spec, height)
  - Vertex group masking based on texture alpha channel
  - Multi-stage preparation process:
    - Vertex weight editing with texture-based masking
    - Subdivision modifier for detail enhancement
    - Displacement modifier using normal map
    - Decimate optimization for areas without details
  - Undo support for quick adjustments
  - Integration button in Material Selection panel with PRINT_3D icon

### Changed
- Updated version to 0.5.2
- Updated addon name to "M3 Addon (Testing/Fixed for HotS + 3D Print)"
- Updated description to include 3D print preparation feature
- Added MickeyKnox#1985 to author credits

### Fixed
- Fixed AttributeError when trying to access `bpy.context.active_node` (invalid context attribute)
- Improved robustness of normal map search through materials

---

## [0.5.1] - Previous Release

Base version from which the 3D print feature was added. Original M3 addon functionality for importing and exporting StarCraft II and Heroes of the Storm models.

### Original Features
- Import and export models in .m3 format
- Support for animations, meshes with up to 4 UV layers
- Multiple material types (standard, displacement, composite, terrain, volume, creep, volume noise, splat terrain)
- Particle systems, forces, attachment points, cameras, lights
- Rigid bodies, physics joints, projections, ribbons
- Billboard behaviors, turret behaviors, inverse kinematic chains

---

## Credits

- **Original M3 Addon**: Florian Köberle, netherh, chaos2night, Talv, Solstice245
- **3D Print Preparation Feature**: MickeyKnox#1985