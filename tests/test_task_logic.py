from src.utils import (
    annotate_analysis,
    compensation_angle,
    generate_reach_specs,
    participant_assignment,
    summarize_phases,
)


def test_assignment_is_deterministic_and_counterbalanced():
    first = participant_assignment("105", seed=105105, target_angles=[0, 45, 90, 135], rotation_magnitude=45)
    second = participant_assignment("105", seed=105105, target_angles=[0, 45, 90, 135], rotation_magnitude=45)
    assert first == second
    assert first[0] in {0.0, 45.0, 90.0, 135.0}
    assert abs(first[1]) == 45.0


def test_exact_three_block_plan_preserves_session_factors():
    plan = generate_reach_specs(
        target_angle_deg=90,
        rotation_deg=-45,
        baseline_trials=30,
        adaptation_trials=54,
        aftereffect_trials=6,
    )
    assert [len(plan[key]) for key in ("baseline", "adaptation", "aftereffect")] == [30, 54, 6]
    assert {spec.target_angle_deg for group in plan.values() for spec in group} == {90.0}
    assert {spec.rotation_deg for group in plan.values() for spec in group} == {-45.0}
    assert plan["baseline"][0].feedback_mode == "veridical"
    assert plan["adaptation"][0].feedback_mode == "rotated"
    assert plan["aftereffect"][0].feedback_mode == "none"


def test_compensation_is_positive_opposite_each_rotation_direction():
    assert compensation_angle(45, 90, 45) == 45
    assert compensation_angle(135, 90, -45) == 45


def test_phase_summary_reports_early_late_and_aftereffect():
    rows = []
    for index in range(4):
        rows.append({"analysis_phase": "baseline", "completed": True, "hand_angle_deg": 90.0, "target_angle_deg": 90.0, "rotation_deg": 45.0, "movement_time": 0.15})
    for value in [10.0, 15.0, 30.0, 35.0]:
        rows.append({"analysis_phase": "adaptation", "completed": True, "hand_angle_deg": 90.0 - value, "target_angle_deg": 90.0, "rotation_deg": 45.0, "movement_time": 0.15})
    for value in [11.0, 13.0]:
        rows.append({"analysis_phase": "aftereffect", "completed": True, "hand_angle_deg": 90.0 - value, "target_angle_deg": 90.0, "rotation_deg": 45.0, "movement_time": 0.15})
    annotate_analysis(rows)
    summary = summarize_phases(rows, window=2)
    assert summary["early_adaptation_deg"] == 12.5
    assert summary["late_adaptation_deg"] == 32.5
    assert summary["aftereffect_deg"] == 12.0
