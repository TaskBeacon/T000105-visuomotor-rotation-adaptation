from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any, Iterable, Sequence


def normalize_angle_deg(value: float) -> float:
    return (float(value) + 180.0) % 360.0 - 180.0


def angular_difference_deg(value: float, reference: float) -> float:
    return normalize_angle_deg(float(value) - float(reference))


def polar_point(radius: float, angle_deg: float) -> list[float]:
    theta = math.radians(float(angle_deg))
    return [float(radius) * math.cos(theta), float(radius) * math.sin(theta)]


@dataclass(frozen=True)
class ReachSpec:
    condition_id: str
    feedback_mode: str
    target_angle_deg: float
    rotation_deg: float
    block_trial_index: int
    block_trial_count: int
    global_trial_index: int
    analysis_phase: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "feedback_mode": self.feedback_mode,
            "target_angle_deg": self.target_angle_deg,
            "rotation_deg": self.rotation_deg,
            "block_trial_index": self.block_trial_index,
            "block_trial_count": self.block_trial_count,
            "global_trial_index": self.global_trial_index,
            "analysis_phase": self.analysis_phase,
        }


def participant_assignment(
    subject_id: Any,
    *,
    seed: int,
    target_angles: Sequence[float],
    rotation_magnitude: float,
) -> tuple[float, float]:
    if not target_angles:
        raise ValueError("target_angles must not be empty")
    value = 2166136261
    for byte in f"{seed}|{subject_id}|visuomotor-rotation".encode("utf-8"):
        value ^= byte
        value = (value * 16777619) & 0xFFFFFFFF
    target_angle = float(target_angles[value % len(target_angles)])
    rotation = float(rotation_magnitude) * (1.0 if (value // len(target_angles)) % 2 == 0 else -1.0)
    return target_angle, rotation


def generate_reach_specs(
    *,
    target_angle_deg: float,
    rotation_deg: float,
    baseline_trials: int,
    adaptation_trials: int,
    aftereffect_trials: int,
) -> dict[str, list[ReachSpec]]:
    counts = {
        "baseline": int(baseline_trials),
        "adaptation": int(adaptation_trials),
        "aftereffect": int(aftereffect_trials),
    }
    if any(count <= 0 for count in counts.values()):
        raise ValueError("all reach blocks require at least one trial")
    modes = {"baseline": "veridical", "adaptation": "rotated", "aftereffect": "none"}
    output: dict[str, list[ReachSpec]] = {}
    global_index = 0
    for phase in ("baseline", "adaptation", "aftereffect"):
        output[phase] = []
        for block_index in range(counts[phase]):
            output[phase].append(
                ReachSpec(
                    condition_id=phase,
                    feedback_mode=modes[phase],
                    target_angle_deg=float(target_angle_deg),
                    rotation_deg=float(rotation_deg),
                    block_trial_index=block_index,
                    block_trial_count=counts[phase],
                    global_trial_index=global_index,
                    analysis_phase=phase,
                )
            )
            global_index += 1
    return output


def compensation_angle(hand_angle: float, target_angle: float, rotation_deg: float) -> float:
    raw_error = angular_difference_deg(hand_angle, target_angle)
    direction = 1.0 if float(rotation_deg) >= 0.0 else -1.0
    return -direction * raw_error


def _numbers(values: Iterable[Any]) -> list[float]:
    return [float(value) for value in values if isinstance(value, (int, float)) and math.isfinite(float(value))]


def annotate_analysis(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    histories: dict[str, list[float]] = {}
    for row in rows:
        phase = str(row.get("analysis_phase", "unknown"))
        history = histories.setdefault(phase, [])
        hand = row.get("hand_angle_deg")
        target = row.get("target_angle_deg")
        rotation = row.get("rotation_deg")
        completed = bool(row.get("completed"))
        movement_time = row.get("movement_time")
        hand_error = angular_difference_deg(float(hand), float(target)) if isinstance(hand, (int, float)) else None
        outlier = not completed or hand_error is None
        if hand_error is not None:
            if abs(hand_error) > 90.0 or (isinstance(movement_time, (int, float)) and float(movement_time) > 1.0):
                outlier = True
            if len(history) >= 5:
                window = history[-5:]
                spread = pstdev(window)
                if spread > 0.0 and abs(hand_error - mean(window)) > 3.0 * spread:
                    outlier = True
            history.append(hand_error)
        value = (
            compensation_angle(float(hand), float(target), float(rotation))
            if hand_error is not None and isinstance(rotation, (int, float))
            else None
        )
        row.update(hand_error_deg=hand_error, compensation_angle_deg=value, outlier=outlier)

    baseline = _numbers(
        row.get("compensation_angle_deg")
        for row in rows
        if row.get("analysis_phase") == "baseline" and not row.get("outlier")
    )
    baseline_bias = mean(baseline) if baseline else 0.0
    for row in rows:
        value = row.get("compensation_angle_deg")
        row["baseline_bias_deg"] = baseline_bias
        row["baseline_corrected_angle_deg"] = float(value) - baseline_bias if isinstance(value, (int, float)) else None
    return rows


def summarize_phases(rows: list[dict[str, Any]], *, window: int = 10) -> dict[str, Any]:
    valid = [row for row in rows if not row.get("outlier")]
    adaptation = [row for row in valid if row.get("analysis_phase") == "adaptation"]
    aftereffect = [row for row in valid if row.get("analysis_phase") == "aftereffect"]
    width = max(1, int(window))

    def average(group: Sequence[dict[str, Any]]) -> float | None:
        values = _numbers(row.get("baseline_corrected_angle_deg") for row in group)
        return mean(values) if values else None

    return {
        "trial_count": len(rows),
        "valid_trial_count": len(valid),
        "timeout_count": sum(bool(row.get("timed_out")) for row in rows),
        "baseline_bias_deg": rows[0].get("baseline_bias_deg", 0.0) if rows else 0.0,
        "early_adaptation_deg": average(adaptation[:width]),
        "late_adaptation_deg": average(adaptation[-width:]),
        "aftereffect_deg": average(aftereffect),
    }


def format_summary(summary: dict[str, Any]) -> dict[str, str]:
    def angle(value: Any) -> str:
        return "--" if value is None else f"{float(value):.1f}°"

    return {
        "trial_count": str(summary.get("trial_count", 0)),
        "valid_trial_count": str(summary.get("valid_trial_count", 0)),
        "timeout_count": str(summary.get("timeout_count", 0)),
        "early_adaptation": angle(summary.get("early_adaptation_deg")),
        "late_adaptation": angle(summary.get("late_adaptation_deg")),
        "aftereffect": angle(summary.get("aftereffect_deg")),
    }
