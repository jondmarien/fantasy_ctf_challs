"""
Aachen 34C3 CTF-style convex decay scoring for CTFd dynamic challenges.

Registers a new decay function "aachen" in CTFd's DECAY_FUNCTIONS registry.
Use by setting `function: aachen` on a dynamic challenge.
"""

from CTFd.models import Solves, db
from CTFd.plugins.dynamic_challenges.decay import DECAY_FUNCTIONS

# Curve tuning values from Aachen 34C3 scoring.
AACHEN_INFLECTION = 11.92201
AACHEN_STEEPNESS = 1.206069


def aachen(challenge):
    """Compute dynamic challenge score with Aachen-style convex decay."""
    solve_count = db.session.query(Solves).filter_by(challenge_id=challenge.id).count()

    initial = challenge.initial
    minimum = challenge.minimum
    delta = initial - minimum

    if delta <= 0:
        return minimum

    value = minimum + delta / (
        1 + (max(0, solve_count - 1) / AACHEN_INFLECTION) ** AACHEN_STEEPNESS
    )
    return int(round(value))


def load(app):
    """Register the Aachen function into CTFd's decay registry."""
    DECAY_FUNCTIONS["aachen"] = aachen
    app.logger.info(
        "[dynamic_challenges_aachen] registered 'aachen' decay function "
        f"(K={AACHEN_INFLECTION}, P={AACHEN_STEEPNESS})"
    )
