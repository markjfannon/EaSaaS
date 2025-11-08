from dataclasses import dataclass


# python class containing  x, y and steps vars
@dataclass
class Command:
    x: int
    y: int
    steps: int
