"""Indian Ocean cyclone intensity labels used by the baseline classifier."""

IMD_CLASSES = (
    "Depression",
    "Deep Depression",
    "Cyclonic Storm",
    "Severe Cyclonic Storm",
    "Very Severe Cyclonic Storm",
    "Extremely Severe Cyclonic Storm",
    "Super Cyclonic Storm",
)


def class_index(label: str) -> int:
    try:
        return IMD_CLASSES.index(label)
    except ValueError as exc:
        raise ValueError(f"Unknown IMD class: {label}") from exc
