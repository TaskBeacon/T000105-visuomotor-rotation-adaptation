# Task Plot Review

## Review history

- Round 1: Experimental geometry and four-row comparison were correct, but the generated header-safe band was dark and incompatible with the fixed dark TaskBeacon title. Rejected for header contrast.
- Round 2: Changed only the outer canvas and top 18% header-safe band to white. Accepted after official title/logo post-processing and lossless RGB re-encoding for preview compatibility.

## Evidence Match

- [x] Task name matches `T000105-visuomotor-rotation-adaptation`.
- [x] Conditions match the canonical 30-trial baseline, 54-trial rotation, and 6-trial aftereffect sequence.
- [x] Early adaptation is identified as the first 10 rotation trials and late adaptation as the last 10.
- [x] Trial order matches the implementation: home, 500-ms hold, reach within 500 ms, then a 50-ms endpoint for visible-feedback trials.
- [x] Early adaptation shows a direct mouse path and a 45-degree displaced cursor path.
- [x] Late adaptation shows an opposite compensatory mouse path and a rotated cursor approaching the target.
- [x] Aftereffect includes the direct-reach instruction, shows a biased mouse path, and contains no visible cursor during or after movement.
- [x] Visible elements match the task: black display, white start annulus/cursor, and blue target above centre.

## Visual Quality

- [x] All labels are legible at document-preview size.
- [x] No garbled text or misspelled condition labels.
- [x] Arrows and left-to-right ordering are unambiguous.
- [x] Screens, row labels, and timing labels do not overlap.
- [x] The four rows use consistent spacing and scale; the five-step aftereffect row remains readable.
- [x] The final title is centred in the white header band.
- [x] The subtitle begins with `Construct:` and uses `/` between constructs.
- [x] The borderless TaskBeacon logo lockup is at top right without overlap.
- [x] The image model did not add a competing title, logo, watermark, or brand text.
- [x] `references/task_plot_timeline_raw.png` preserves the accepted generated timeline before fixed header/logo post-processing.

## README Embed

- [x] `README.md` contains `## 2. Task Flow`.
- [x] Its first image is exactly `![Task Flow](task_flow.png)`.
- [x] The accepted final image is saved at the task root as `task_flow.png`.

## Final decision

PASS after 2 of at most 5 permitted rounds. No overlap, stimulus, ratio, scale, feedback-visibility, or rotation-direction defect remains.

