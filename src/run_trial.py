from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import ReachSpec, angular_difference_deg, compensation_angle, polar_point


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    if not isinstance(condition, ReachSpec):
        raise TypeError("visuomotor rotation trials require ReachSpec conditions")
    spec = condition
    trial_id = next_trial_id()
    block_name = str(block_id or spec.condition_id)
    target_position = polar_point(float(settings.target_distance_deg), spec.target_angle_deg)
    start = stim_bank.rebuild("start_annulus", pos=[0, 0])
    target = stim_bank.rebuild("target", pos=target_position)
    cursor = stim_bank.rebuild("reach_cursor", pos=[0, 0])
    unit = StimUnit("reach", win, kb, runtime=trigger_runtime)
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase="reach",
        deadline_s=float(settings.movement_deadline),
        valid_keys=["pointer_reach"],
        block_id=block_name,
        condition_id=spec.condition_id,
        task_factors={**spec.to_dict(), "stage": "reach", "target_position": target_position},
        stim_id=f"{spec.condition_id}_reach",
    )
    target_trigger = settings.triggers.get(f"target_{spec.condition_id}")
    unit.capture_pointer_reach(
        start=start,
        target=target,
        cursor=cursor,
        target_position=target_position,
        target_distance=float(settings.target_distance_deg),
        start_radius=float(settings.marker_radius_deg),
        target_radius=float(settings.marker_radius_deg),
        search_visibility_radius=float(settings.search_visibility_radius_deg),
        start_hold_duration=float(settings.start_hold_duration),
        movement_deadline=float(settings.movement_deadline),
        reaction_threshold=float(settings.reaction_threshold_deg),
        feedback_mode=spec.feedback_mode,
        rotation_deg=spec.rotation_deg if spec.feedback_mode == "rotated" else 0.0,
        endpoint_freeze_duration=float(settings.endpoint_freeze_duration),
        onset_trigger=settings.triggers.get("homing_onset"),
        hold_trigger=settings.triggers.get("start_hold_onset"),
        target_trigger=target_trigger,
        movement_trigger=settings.triggers.get("movement_onset"),
        complete_trigger=settings.triggers.get("reach_complete"),
        hit_trigger=settings.triggers.get("cursor_hit"),
        timeout_trigger=settings.triggers.get("reach_timeout"),
    )

    hand_angle = unit.get_state("hand_angle_deg", None)
    hand_error = (
        angular_difference_deg(float(hand_angle), spec.target_angle_deg)
        if isinstance(hand_angle, (int, float))
        else None
    )
    compensation = (
        compensation_angle(float(hand_angle), spec.target_angle_deg, spec.rotation_deg)
        if isinstance(hand_angle, (int, float))
        else None
    )
    data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_name,
        "block_idx": int(block_idx or 0),
        "condition": spec.condition_id,
        **spec.to_dict(),
        "target_position": target_position,
        "hand_error_deg": hand_error,
        "compensation_angle_deg": compensation,
        "completed": bool(unit.get_state("completed", False)),
        "timed_out": bool(unit.get_state("timed_out", False)),
        "search_time": unit.get_state("search_time", None),
        "reaction_time": unit.get_state("reaction_time", None),
        "movement_time": unit.get_state("movement_time", None),
        "hand_angle_deg": hand_angle,
        "cursor_angle_deg": unit.get_state("cursor_angle_deg", None),
        "cursor_error_deg": unit.get_state("cursor_error_deg", None),
        "cursor_hit": bool(unit.get_state("cursor_hit", False)),
        "physical_endpoint": unit.get_state("physical_endpoint", None),
        "display_endpoint": unit.get_state("display_endpoint", None),
        "trajectory_physical": unit.get_state("trajectory_physical", []),
        "trajectory_display": unit.get_state("trajectory_display", []),
        "sample_count": unit.get_state("sample_count", 0),
        "outcome": "complete" if unit.get_state("completed", False) else "too_slow",
    }
    unit.to_dict(data)

    if not bool(unit.get_state("completed", False)):
        feedback = StimUnit("too_slow", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("too_slow"))
        set_trial_context(
            feedback,
            trial_id=trial_id,
            phase="too_slow",
            deadline_s=float(settings.too_slow_duration),
            valid_keys=[],
            block_id=block_name,
            condition_id=spec.condition_id,
            task_factors={**spec.to_dict(), "stage": "too_slow"},
            stim_id="too_slow",
        )
        feedback.show(duration=float(settings.too_slow_duration)).to_dict(data)
    return data
