from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    reset_trial_counter,
    runtime_context,
    set_trial_context,
)

from src import (
    annotate_analysis,
    format_summary,
    generate_reach_specs,
    participant_assignment,
    run_trial,
    summarize_phases,
)


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _wait_screen(bank, stim_id, win, kb, triggers, **formats) -> None:
    stimulus = bank.get_and_format(stim_id, **formats) if formats else bank.get(stim_id)
    unit = StimUnit(stim_id, win, kb, runtime=triggers).add_stim(stimulus)
    set_trial_context(
        unit,
        trial_id=stim_id,
        phase=stim_id,
        deadline_s=None,
        valid_keys=["space"],
        block_id=stim_id,
        condition_id=stim_id,
        task_factors={"stage": stim_id},
        stim_id=stim_id,
    )
    unit.wait_and_continue(keys=["space"])


def _check_screen(bank, stim_id, correct_key, win, kb, settings, triggers) -> bool:
    keys = list(settings.check_keys)
    unit = StimUnit(stim_id, win, kb, runtime=triggers).add_stim(bank.get(stim_id))
    set_trial_context(
        unit,
        trial_id=stim_id,
        phase=stim_id,
        deadline_s=float(settings.check_deadline),
        valid_keys=keys,
        block_id=stim_id,
        condition_id=stim_id,
        task_factors={"stage": stim_id, "correct_key": correct_key},
        stim_id=stim_id,
    )
    unit.capture_response(
        keys=keys,
        duration=float(settings.check_deadline),
        onset_trigger=settings.triggers.get(stim_id),
        response_trigger={correct_key: settings.triggers.get("check_correct")},
        timeout_trigger=settings.triggers.get("check_failed"),
    )
    return unit.get_state("response", None) == correct_key


def _run_specs(specs, *, block_id, block_idx, settings, win, kb, bank, triggers) -> list[dict]:
    rows: list[dict] = []
    if not specs:
        return rows
    block = (
        BlockUnit(
            block_id=block_id,
            block_idx=block_idx,
            settings=settings,
            window=win,
            keyboard=kb,
            n_trials=len(specs),
        )
        .add_condition(list(specs))
        .run_trial(
            partial(
                run_trial,
                stim_bank=bank,
                trigger_runtime=triggers,
                block_id=block_id,
                block_idx=block_idx,
            )
        )
    )
    block.to_dict(rows)
    return rows


def run(options) -> None:
    root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa105"}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim105")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(config)
        win, kb = initialize_exp(settings)
        bank = StimBank(win, config["stim_config"]).preload_all()
        settings.save_to_json()
        reset_trial_counter()
        triggers.send(settings.triggers.get("experiment_start"))

        _wait_screen(bank, "instruction", win, kb, triggers)
        if not _check_screen(bank, "comprehension_check", "a", win, kb, settings, triggers):
            triggers.send(settings.triggers.get("check_failed"))
            triggers.close()
            win.close()
            return

        subject_id = subject.get("subject_id", "unknown")
        target_angle, rotation = participant_assignment(
            subject_id,
            seed=int(settings.plan_seed),
            target_angles=list(settings.target_angles_deg),
            rotation_magnitude=float(settings.rotation_magnitude_deg),
        )
        plans = generate_reach_specs(
            target_angle_deg=target_angle,
            rotation_deg=rotation,
            baseline_trials=int(settings.baseline_trials),
            adaptation_trials=int(settings.adaptation_trials),
            aftereffect_trials=int(settings.aftereffect_trials),
        )
        rows: list[dict] = []

        triggers.send(settings.triggers.get("baseline_start"))
        check_after = min(int(settings.attention_check_after_trial), len(plans["baseline"]))
        rows.extend(_run_specs(plans["baseline"][:check_after], block_id="baseline", block_idx=0, settings=settings, win=win, kb=kb, bank=bank, triggers=triggers))
        if check_after < len(plans["baseline"]) or len(plans["baseline"]) >= int(settings.attention_check_after_trial):
            if not _check_screen(bank, "attention_check", "b", win, kb, settings, triggers):
                triggers.send(settings.triggers.get("check_failed"))
                triggers.close()
                win.close()
                return
        rows.extend(_run_specs(plans["baseline"][check_after:], block_id="baseline", block_idx=0, settings=settings, win=win, kb=kb, bank=bank, triggers=triggers))
        triggers.send(settings.triggers.get("baseline_end"))

        _wait_screen(bank, "adaptation_instruction", win, kb, triggers)
        triggers.send(settings.triggers.get("adaptation_start"))
        rows.extend(_run_specs(plans["adaptation"], block_id="adaptation", block_idx=1, settings=settings, win=win, kb=kb, bank=bank, triggers=triggers))
        triggers.send(settings.triggers.get("adaptation_end"))

        triggers.send(settings.triggers.get("aftereffect_instruction"))
        _wait_screen(bank, "aftereffect_instruction", win, kb, triggers)
        triggers.send(settings.triggers.get("aftereffect_start"))
        rows.extend(_run_specs(plans["aftereffect"], block_id="aftereffect", block_idx=2, settings=settings, win=win, kb=kb, bank=bank, triggers=triggers))
        triggers.send(settings.triggers.get("aftereffect_end"))

        annotate_analysis(rows)
        summary = format_summary(summarize_phases(rows, window=int(settings.analysis_window)))
        pd.DataFrame(rows).to_csv(settings.res_file, index=False)
        _wait_screen(bank, "good_bye", win, kb, triggers, **summary)
        triggers.send(settings.triggers.get("experiment_end"))
        triggers.close()
        win.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Visuomotor Rotation Adaptation task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
