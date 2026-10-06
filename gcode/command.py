from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    letter: str
    code: int
    params: dict[str, float]
