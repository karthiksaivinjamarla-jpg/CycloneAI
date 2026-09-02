from dataclasses import dataclass


@dataclass(frozen=True)
class DataConfig:
    target_basins: tuple[str, ...] = ("NIO",)
    channels: tuple[str, ...] = ("IR", "WV", "VIS", "MW")
    frame_size: int = 201
    sequence_length: int = 4


@dataclass(frozen=True)
class TrainingConfig:
    batch_size: int = 32
    epochs: int = 20
    learning_rate: float = 1e-3
    random_seed: int = 42
