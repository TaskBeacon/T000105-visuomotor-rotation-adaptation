# Task Logic Audit

## 1. Paradigm Intent

- Task: Visuomotor Rotation Adaptation.
- Primary construct: sensorimotor adaptation / implicit recalibration / explicit re-aiming.
- Manipulated factors: feedback mode (veridical, 45-degree rotated, absent); rotation direction (clockwise or counterclockwise, between participants); target direction (one of eight locations, between participants).
- Dependent measures: endpoint hand angle, baseline-corrected compensation angle, target/cursor error, reaction time, movement time, search time, early adaptation, late adaptation, and aftereffect.
- Key citations: P1 is the exact web-task protocol; W2083905756, W1602511075, and W1987840011 support interpretation of rapid/slow learning and aftereffects.

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: three contiguous experimental blocks.
- Trials per block: baseline 30, adaptation 54, aftereffect 6; 90 movement trials total.
- Randomization/counterbalancing: one of eight target angles and one of two 45-degree rotation directions are selected deterministically from the participant/session seed and remain fixed for all 90 trials.
- Condition weight policy: no weighted generation. Exact block sequences are required.
- Condition generation method: a focused custom generator creates `ReachSpec` records. Simple labels are insufficient because target angle and rotation direction must remain globally fixed across all three blocks while feedback mode and exact block counts change.
- Generated condition data shape: `condition_id`, `feedback_mode`, `target_angle_deg`, `rotation_deg`, `block_trial_index`, `global_trial_index`, `analysis_phase`.
- Runtime-generated trial values: none. Every experimental factor is fixed before block execution. Pointer samples and outcome geometry are observations, not randomized factors.

### Trial State Machine

1. Homing/search:
   - Onset trigger: `homing_onset`.
   - Stimuli shown: central white annulus; veridical white cursor only when the physical pointer is within 2 degrees of center.
   - Valid input: pointer movement.
   - Timeout behavior: none; participant returns to center.
   - Next state: start hold when the pointer enters the annulus.
2. Start hold:
   - Onset trigger: `start_hold_onset`.
   - Stimuli shown: central annulus and white cursor.
   - Valid input: keep pointer inside the start annulus for 500 ms.
   - Timeout behavior: leaving the annulus resets the hold timer.
   - Next state: target onset after a continuous 500-ms hold.
3. Reach:
   - Onset trigger: `target_onset`; movement onset trigger when the physical pointer leaves start.
   - Stimuli shown: blue target and central annulus; cursor feedback is veridical, rotated, or absent according to `ReachSpec`.
   - Valid input: continuous pointer movement.
   - Timeout behavior: if target radius is not reached within 500 ms of movement onset, classify as `too_slow`.
   - Next state: endpoint freeze on completion or timeout feedback.
4. Endpoint freeze:
   - Onset trigger: `reach_complete`.
   - Stimuli shown: target plus final cursor position for 50 ms in feedback blocks; target only in no-feedback block.
   - Valid input: none.
   - Timeout behavior: not applicable.
   - Next state: next trial's homing/search.
5. Too-slow feedback, conditional:
   - Onset trigger: `reach_timeout`.
   - Stimuli shown: centered red localized “too slow” message.
   - Valid input: none.
   - Timeout behavior: screen ends after 750 ms.
   - Next state: next trial's homing/search.

Block-level participant-visible events:

- Before baseline: instruction and comprehension check; incorrect response terminates the human run.
- After baseline trial 10: attention check requiring B; incorrect response terminates the human run.
- Before adaptation: neutral reminder to continue bringing the white dot through the blue target; perturbation is not disclosed.
- Before aftereffect: explicit instruction to stop any aiming strategy and reach directly toward the target without movement feedback.

## 3. Condition Semantics

- Condition ID `baseline`:
  - Participant-facing meaning: ordinary cursor control.
  - Concrete realization: blue target, white start annulus, veridical white cursor.
  - Outcome rules: movement completes at 6-degree physical radius; baseline endpoint angle establishes directional bias.
- Condition ID `adaptation`:
  - Participant-facing meaning: same target-hitting goal; the perturbation is not named.
  - Concrete realization: same geometry with cursor direction rotated +45 or -45 degrees.
  - Outcome rules: participants must alter hand direction opposite the rotation to reduce cursor-target error.
- Condition ID `aftereffect`:
  - Participant-facing meaning: reach directly to the target without using a strategy.
  - Concrete realization: cursor disappears upon leaving start; target remains visible.
  - Outcome rules: residual baseline-corrected hand angle is the aftereffect.
- Participant-facing content source: all static wording and visual specifications are defined in `config/*.yaml`; `src/run_trial.py` only rebuilds position/feedback parameters from `ReachSpec`.
- Localization: Chinese text lives entirely in configuration and uses SimHei; localization requires no trial-code edits.

## 4. Response and Scoring Rules

- Response mapping: continuous pointer movement; A for the comprehension check; B for the attention check; Space for ordinary continuation screens.
- Response key source: configuration.
- Missing-response policy: homing and instructions wait; a reach that exceeds 500 ms after movement onset is `too_slow`.
- Correctness logic: movement completion is geometric (physical pointer reaches 6-degree radius). `cursor_hit` indicates whether the transformed endpoint intersects the blue target.
- Reward/penalty updates: none.
- Running metrics: endpoint hand angle, cursor angle/error, reaction time to 1-degree radius, movement time, search time, timeout, cursor hit, raw physical/display trajectories.
- Summary metrics: baseline directional bias; early adaptation (first ten rotated trials); late adaptation (last ten rotated trials); aftereffect (six no-feedback trials), all expressed as positive compensation opposite the assigned rotation after baseline correction.

## 5. Stimulus Layout Plan

- Reach workspace:
  - Stimulus IDs shown together: `start_annulus`, `target`, condition-dependent `reach_cursor`.
  - Layout anchors: start at `[0, 0]`; target at polar radius 6 degrees and assigned angle; cursor follows framework-resolved position.
  - Size/spacing: start and target radii 0.25 degrees; cursor radius 0.16 degrees; 6-degree center-to-target separation.
  - Readability/overlap checks: target never overlaps start; cursor is visually distinct from blue target; all coordinates remain inside the 1280 x 800 degree-calibrated viewport.
  - Rationale: reproduces the paper's center-out geometry.
- Comprehension check:
  - Stimulus IDs shown together: `comprehension_check` only.
  - Layout anchors: centered text box.
  - Size/spacing: 0.55-degree Chinese font, 24-degree wrap width.
  - Readability/overlap checks: one text element, no overlap.
- Attention check:
  - Stimulus IDs shown together: `attention_check` only.
  - Layout anchors: centered.
  - Size/spacing: 0.7-degree Chinese font.
  - Readability/overlap checks: one text element, no overlap.
- Timeout feedback:
  - Stimulus IDs shown together: `too_slow` only.
  - Layout anchors: centered.
  - Size/spacing: 0.7-degree red SimHei text.
  - Readability/overlap checks: one text element, no overlap.

## 6. Trigger Plan

| Phase/event | Code | Semantics |
|---|---:|---|
| experiment start | 1 | Session begins. |
| block start | 10/11/12 | Baseline/adaptation/aftereffect block begins. |
| homing onset | 20 | Search for the center begins. |
| start hold onset | 21 | Pointer enters center hold. |
| target onset | 30/31/32 | Target appears for baseline/adaptation/aftereffect. |
| movement onset | 40 | Pointer leaves start. |
| reach complete | 50 | Physical pointer reaches target radius. |
| reach timeout | 51 | Movement exceeds 500 ms. |
| cursor hit | 52 | Transformed endpoint intersects target. |
| attention check | 60 | B-key check appears. |
| aftereffect instruction | 61 | Direct-reach/no-feedback instruction appears. |
| block end | 90/91/92 | Baseline/adaptation/aftereffect block ends. |
| experiment end | 99 | Session ends. |

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one explicit mode-aware flow with three named blocks and visible transition screens.
- `utils.py` used: yes.
- Exact purpose: deterministic participant-level counterbalancing, `ReachSpec` generation, circular angle calculations, baseline-corrected phase summaries.
- Custom controller used: no.
- Framework gap: continuous center-out pointer capture with transformed visual feedback belongs to PsyFlow, so a public `capture_pointer_reach` primitive owns sampling, timing, feedback transformation, triggers, and raw trajectory state. Task code only supplies protocol parameters.
- Legacy/backward-compatibility fallback logic required: no.

## 8. Inference Log

- Decision: use one attention check after baseline trial 10.
  - Why inference was required: P1 reports checks within the first 20 trials but not their count or precise placement.
  - Citation-supported rationale: a single deterministic check preserves the reported mechanism without altering any of the 90 movement trials.
- Decision: express reported centimetre geometry as numerically matched degree units.
  - Why inference was required: PsychoPy and the shared web runner require a cross-platform coordinate system, while actual pixel density and viewing distance vary.
  - Citation-supported rationale: P1 itself scaled stimuli by screen size and reports geometry for a typical 13-inch display.
- Decision: completion deadline begins at movement onset.
  - Why inference was required: P1 distinguishes reaction time from movement time and describes a movement as incomplete after 500 ms without explicitly naming the timer origin.
  - Citation-supported rationale: reported reaction and movement time definitions treat movement onset as the beginning of the reach interval.
