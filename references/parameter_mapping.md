# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| P01 | `task.total_trials` | 90 | P1 | Methods, web-based task: 90 total trials. | direct | Human profile only; QA and simulation profiles are shortened but mechanism-complete. |
| P02 | `task.baseline_trials` | 30 | P1 | Methods: 30-trial veridical-feedback baseline block. | direct | Used to compute participant-specific baseline bias. |
| P03 | `task.adaptation_trials` | 54 | P1 | Methods: 54-trial rotated-feedback block. | direct | Early adaptation is trials 1-10; late adaptation is trials 45-54. |
| P04 | `task.aftereffect_trials` | 6 | P1 | Methods: six-trial no-feedback block. | direct | All six trials define the aftereffect. |
| P05 | `task.target_angles_deg` | `[0, 45, 90, 135, 180, 225, 270, 315]` | P1 | Methods: one fixed target randomly selected from four cardinal and four diagonal locations. | direct | One deterministic counterbalanced target is assigned per participant/session. |
| P06 | `task.rotation_magnitude_deg` | 45 | P1 | Methods and Fig. 1: cursor direction offset by 45 degrees. | direct | Direction is clockwise or counterclockwise and fixed within participant. |
| P07 | `task.target_distance_deg` | 6.0 | P1 | Methods: target radius was 6 cm on the reference 13-inch monitor. | adapted | Degree units preserve a calibrated radial workspace in PsychoPy and map directly to the web coordinate system. |
| P08 | `task.marker_diameter_deg` | 0.5 | P1 | Methods: start annulus and blue target were each 0.5 cm in diameter. | adapted | Implemented as 0.25-degree radius circles. |
| P09 | `task.search_visibility_radius_deg` | 2.0 | P1 | Methods: cursor feedback appeared only within 2 cm of the start during introduction/search. | adapted | Degree-unit screen-calibrated analogue. |
| P10 | `timing.start_hold_duration` | 0.5 s | P1 | Methods: cursor had to remain at start for 500 ms before target onset. | direct | Framework pointer-reach primitive owns the hold timer. |
| P11 | `timing.movement_deadline` | 0.5 s | P1 | Methods: movements not completed within 500 ms elicited a too-slow message. | direct | Deadline starts when the cursor leaves the start annulus. |
| P12 | `timing.endpoint_freeze_duration` | 0.05 s | P1 | Methods: cursor endpoint froze for 50 ms at target radius. | direct | Applies to veridical and rotated feedback; no-feedback cursor remains hidden. |
| P13 | `timing.too_slow_duration` | 0.75 s | P1 | Methods: red too-slow message was displayed for 750 ms. | direct | Chinese localized wording; same semantic content. |
| P14 | `task.reaction_threshold_deg` | 1.0 | P1 | Data analysis: reaction time ended when radial hand motion reached 1 cm. | adapted | Degree-unit analogue. |
| P15 | `task.early_window` | first 10 adaptation trials | P1 | Data analysis definition of early adaptation. | direct | Baseline-subtracted mean hand angle. |
| P16 | `task.late_window` | last 10 adaptation trials | P1 | Data analysis definition of late adaptation. | direct | Baseline-subtracted mean hand angle. |
| P17 | `task.aftereffect_window` | all six no-feedback trials | P1 | Data analysis definition of aftereffect. | direct | Baseline-subtracted mean hand angle. |
| P18 | `task.attention_check_after_trial` | 10 | P1 | Methods: attention checks appeared sporadically within the first 20 trials; count and exact position were not reported. | inferred | One check after baseline trial 10 provides a deterministic, auditable implementation. |
| P19 | reduced outcome | endpoint hand angle opposite rotation, baseline corrected | P1 | Data analysis and Fig. 1 define positive compensation and baseline subtraction. | direct | Raw signed geometry is also retained. |
| P20 | interpretation | early/late performance may combine explicit and implicit learning; no-feedback direct reaches index implicit recalibration | W2083905756; W1602511075; P1 | Supporting studies separate rapid explicit changes from slower implicit recalibration; P1 uses direct no-feedback reaches for aftereffect. | direct | Interpretation does not alter trial control. |
