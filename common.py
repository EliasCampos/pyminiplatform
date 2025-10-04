import dataclasses
import numbers


@dataclasses.dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        raise ValueError(f"Cannot add {self} and {other}")

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            x, y = [val * other for val in (self.x, self.y)]
            return self.__class__(x, y)
        raise ValueError(f"Cannot multiply {self} and {other}")
