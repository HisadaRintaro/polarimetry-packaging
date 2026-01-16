from dataclasses import dataclass, replace
from typing import Any, Self
import numpy as np


@dataclass
class ImageUnit:
    image: np.ndarray
    x_delta: int
    y_delta: int

    @classmethod
    def load(cls, image: np.ndarray, x_delta=1, y_delta=1):
        return cls(
                image = image,
                x_delta = x_delta,
                y_delta = y_delta,
                )

    def shape(self) -> tuple[int, int]:
        return self.image.shape

    def make_arrays(self, xc=0 , yc=0) -> tuple:
        y_size, x_size = self.image.shape
        x_arr = (np.arange(x_size) - xc ) * self.x_delta
        y_arr = (np.arange(y_size) - yc ) * self.y_delta
        return y_arr, x_arr

    def make_grid(self, xc=0, yc=0) -> tuple[np.ndarray, np.ndarray]:
        y_arr, x_arr = self.make_arrays(xc=xc, yc=yc)
        return np.meshgrid(x_arr, y_arr)

    def apply_mask(self, mask:np.ndarray) -> Self:
        return replace(
                self,
                image= self.image * mask
                )

    def __add__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image + other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image + other)
        except:
            return NotImplemented

    def __radd__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image + other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image + other)
        except:
            return NotImplemented

    def __sub__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image - other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image - other)
        except:
            return NotImplemented

    def __rsub__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image - other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image - other)
        except:
            return NotImplemented

    def __mul__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image * other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image * other)
        except:
            return NotImplemented

    def __rmul__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image * other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image * other)
        except:
            return NotImplemented

    def __truediv__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image / other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image / other)
        except:
            return NotImplemented

    def __rtruediv__(self, other: Self | Any):
        if isinstance(other, type(self)):
            return replace(self, image= self.image / other.image)
        elif other is None:
            return self
        try:
            return replace(self, image= self.image / other)
        except:
            return NotImplemented


