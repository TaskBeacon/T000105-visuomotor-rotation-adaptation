from __future__ import annotations

import random as _random
from dataclasses import dataclass, field
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


def _screen_key(keys: list[str], stage: str) -> str | None:
    if stage == "comprehension_check":
        return "a" if "a" in keys else (keys[0] if keys else None)
    if stage == "attention_check":
        return "b" if "b" in keys else (keys[0] if keys else None)
    if "space" in keys:
        return "space"
    return keys[0] if keys else None


def _expected_compensation(factors: dict[str, Any]) -> float:
    phase = str(factors.get("analysis_phase", factors.get("condition_id", "baseline")))
    if phase == "baseline":
        return 0.0
    if phase == "aftereffect":
        return 12.0
    index = int(factors.get("block_trial_index", 0))
    count = max(1, int(factors.get("block_trial_count", 1)))
    return 12.0 + 24.0 * index / max(1, count - 1)


def _hand_angle(factors: dict[str, Any], compensation: float) -> float:
    target = float(factors.get("target_angle_deg", 0.0))
    rotation = float(factors.get("rotation_deg", 45.0))
    direction = 1.0 if rotation >= 0.0 else -1.0
    return target - direction * float(compensation)


@dataclass
class ScriptedResponder:
    reaction_time_s: float = 0.25
    movement_time_s: float = 0.15

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        return None

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None

    def act(self, observation: Observation) -> Action:
        keys = [str(value) for value in observation.valid_keys]
        factors = dict(observation.task_factors or {})
        stage = str(factors.get("stage", observation.phase))
        if stage != "reach" or "pointer_reach" not in keys:
            key = _screen_key(keys, stage)
            return Action(key=key, rt_s=0.05 if key is not None else None)
        compensation = _expected_compensation(factors)
        return Action(
            key="pointer_reach",
            rt_s=float(self.reaction_time_s),
            meta={
                "source": "visuomotor_scripted",
                "search_time_s": 0.20,
                "reaction_time_s": float(self.reaction_time_s),
                "movement_time_s": float(self.movement_time_s),
                "hand_angle_deg": _hand_angle(factors, compensation),
            },
        )


@dataclass
class TaskSamplerResponder:
    timeout_rate: float = 0.08
    angle_noise_sd_deg: float = 3.0
    reaction_time_s: float = 0.28
    movement_time_s: float = 0.18
    _rng: Any = field(default=None, init=False, repr=False)

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if hasattr(self._rng, "random") else _random.random()

    def _normal(self, mean: float, sd: float) -> float:
        if hasattr(self._rng, "normal"):
            return float(self._rng.normal(mean, sd))
        if hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(mean, sd))
        return _random.gauss(mean, sd)

    def act(self, observation: Observation) -> Action:
        keys = [str(value) for value in observation.valid_keys]
        factors = dict(observation.task_factors or {})
        stage = str(factors.get("stage", observation.phase))
        if stage != "reach" or "pointer_reach" not in keys:
            key = _screen_key(keys, stage)
            return Action(key=key, rt_s=0.05 if key is not None else None)
        if self._random() < float(self.timeout_rate):
            return Action(key=None, rt_s=None, meta={"source": "visuomotor_sampler", "timeout": True})
        compensation = _expected_compensation(factors) + self._normal(0.0, float(self.angle_noise_sd_deg))
        return Action(
            key="pointer_reach",
            rt_s=float(self.reaction_time_s),
            meta={
                "source": "visuomotor_sampler",
                "search_time_s": max(0.05, self._normal(0.35, 0.08)),
                "reaction_time_s": max(0.10, self._normal(float(self.reaction_time_s), 0.04)),
                "movement_time_s": max(0.06, self._normal(float(self.movement_time_s), 0.03)),
                "hand_angle_deg": _hand_angle(factors, compensation),
            },
        )
