"""Small, dependency-free data-pipeline contract.

Dataset-specific readers should implement the functions documented here rather
than coupling the model directly to raw satellite/track files.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Observation:
    storm_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    channels: tuple[str, ...]


def validate_observation(observation: Observation) -> None:
    if not -90 <= observation.latitude <= 90:
        raise ValueError("latitude must be between -90 and 90")
    if not -180 <= observation.longitude <= 180:
        raise ValueError("longitude must be between -180 and 180")
    if not observation.storm_id:
        raise ValueError("storm_id is required")


def split_by_storm(observations: list[Observation], train_ids: set[str], val_ids: set[str], test_ids: set[str]):
    """Return storm-level splits and reject overlapping IDs."""
    if train_ids & val_ids or train_ids & test_ids or val_ids & test_ids:
        raise ValueError("train/validation/test storm IDs must not overlap")

    train = [x for x in observations if x.storm_id in train_ids]
    validation = [x for x in observations if x.storm_id in val_ids]
    test = [x for x in observations if x.storm_id in test_ids]
    return train, validation, test
