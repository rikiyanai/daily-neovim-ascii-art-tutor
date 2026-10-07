"""Read-only retrospective module-animation reward selection.

The animation catalogue and generated curriculum own the canonical art.  This
module only decides when an already-studied module may expose that art without
creating a synthetic pass event.  A passed ``.REWARD`` card is therefore
reported as ``mastered``; older study evidence remains ``prior_study`` until
the learner actually completes the new endcap.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import sys


_ANIMATION_CATALOGUE = None


def _animation_for(module_id):
    """Load the sibling catalogue by path when the gate omits ``share/``."""

    global _ANIMATION_CATALOGUE
    if _ANIMATION_CATALOGUE is None:
        path = Path(__file__).with_name("module_animations.py")
        spec = importlib.util.spec_from_file_location(
            "vim_daily_retro_module_animations", path)
        if spec is None or spec.loader is None:
            raise ImportError("module animation catalogue is unavailable")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _ANIMATION_CATALOGUE = module
    return _ANIMATION_CATALOGUE.animation_for(module_id)


# C34 deliberately starts with the two modules that predate the complete
# animation endcap.  Future retrofits can add ids here after their own proof.
RETRO_MODULE_IDS = ("M0", "M11")
MIN_PRIOR_STUDY_PASSES = 2


def _module_map(curiculum):
    if not isinstance(curiculum, dict):
        return {}
    return {module["id"]: module for module in curiculum.get("modules", ())}


def _passed(progress):
    return set(progress.get("passed_cards", ()))


def _reward_card_id(module):
    metadata = module.get("module_reward") or {}
    return metadata.get("card_id") or "%s.REWARD" % module["id"]


def _study_ids(module, passed):
    reward_id = _reward_card_id(module)
    return [card_id for card_id in module.get("card_ids", ())
            if card_id != reward_id and card_id in passed]


def _module_check_ids(module):
    return [card_id for card_id in module.get("card_ids", ())
            if card_id.endswith(".08")]


def _canonical_animation(module_id):
    # animation_for() is the single source of frame content.  Never construct
    # a fallback frame here: a missing catalogue entry must fail closed.
    animation = _animation_for(module_id)
    if len(animation.get("frames", ())) < 8:
        raise ValueError("%s retrospective reward has fewer than eight frames" % module_id)
    return deepcopy(animation)


def retrospective_rewards(curiculum, progress, *, module_ids=RETRO_MODULE_IDS):
    """Return eligible read-only reward records for studied retro modules.

    ``prior_study`` requires a small amount of genuine study evidence (rather
    than one accidental pass) and is sufficient for a preview.  It is not a
    mastery claim and does not alter ``progress`` or append an event.
    ``mastered`` is reserved for a passed generated reward endcap.
    """

    modules = _module_map(curiculum)
    passed = _passed(progress)
    rows = []
    for module_id in module_ids:
        module = modules.get(module_id)
        if not module:
            continue
        reward_id = _reward_card_id(module)
        study_ids = _study_ids(module, passed)
        mastered = reward_id in passed
        if len(study_ids) < MIN_PRIOR_STUDY_PASSES and not mastered:
            continue
        animation = _canonical_animation(module_id)
        rows.append({
            "module_id": module_id,
            "reward_card_id": reward_id,
            "status": "mastered" if mastered else "prior_study",
            "prior_study": bool(study_ids),
            "mastered": mastered,
            "legacy_completion": bool(set(_module_check_ids(module)) & passed),
            "studied_card_ids": study_ids,
            "studied_count": len(study_ids),
            "title": animation.get("title", module.get("title", module_id)),
            "credit": animation.get("credit", ""),
            "animation": animation,
        })
    return rows


def startup_rewards(curiculum, progress):
    """Select only unmastered retrospective rewards for the next launch."""

    return [row for row in retrospective_rewards(curiculum, progress)
            if row["status"] == "prior_study"]


def gallery_rewards(curiculum, progress):
    """Retrospective previews plus genuinely passed endcaps in every module."""
    return [row for row in retrospective_rewards(
        curiculum, progress, module_ids=tuple(_module_map(curiculum)))
        if row["mastered"] or row["module_id"] in RETRO_MODULE_IDS]


def completion_reward(curiculum, card):
    """Return canonical reward motion for a completed reward/check card.

    Existing generated cards carry the metadata directly.  The catalogue
    fallback keeps the result route truthful for a caller holding an older
    card shape, without manufacturing progress or art content.
    """

    if not isinstance(card, dict) or card.get("kind") not in ("module_check", "module_reward"):
        return None
    motion = card.get("module_reward")
    if isinstance(motion, dict) and len(motion.get("frames", ())) >= 8:
        return deepcopy(motion)
    module_id = card.get("module_id")
    if not module_id or module_id not in _module_map(curiculum):
        return None
    return _canonical_animation(module_id)


__all__ = [
    "RETRO_MODULE_IDS",
    "MIN_PRIOR_STUDY_PASSES",
    "completion_reward",
    "gallery_rewards",
    "retrospective_rewards",
    "startup_rewards",
]
