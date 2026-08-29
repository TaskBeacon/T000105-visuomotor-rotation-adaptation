# CHANGELOG

## [v0.1.0] - 2026-08-29

### Added

- Implemented the one-target 30/54/6 visuomotor rotation protocol from Tsay et al. (2024).
- Added deterministic eight-direction target and clockwise/counterclockwise rotation counterbalancing.
- Added click-free continuous reach capture with veridical, 45-degree rotated, and absent visual feedback.
- Added trial-wise pointer trajectories, timing, endpoint geometry, cursor error, hit/timeout outcomes, and baseline-corrected phase summaries.
- Added Chinese instructions, comprehension and attention checks, QA and two simulation profiles, reference mappings, and automated logic tests.

### Changed

- Added a framework-owned click-free pointer-reach primitive for transformed and absent feedback.

### Fixed

- Aligned QA and simulation profiles with TAPS v0.2.0 consistency requirements.
