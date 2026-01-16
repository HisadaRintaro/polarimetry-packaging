from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Any, Self
import numpy as np
from matplotlib.patches import Patch, Rectangle, Circle
#from .mixin.area_mixin import AreaPlotMixin

@dataclass
class Area(ABC):

    @abstractmethod
    def make_mask(self, shape) -> np.ndarray:
        pass

    @abstractmethod
    def return_state(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def __mul__(self, other) -> Self:
        pass

    @abstractmethod
    def to_patch(self, pix_size, **kwargs) -> Patch:
        "return matplotlib patch"
        pass

    def add_region_patch(
            self,
            pix_size,
            ax = None,
            *,
            color= "red",
            linewidth = 2,
            alpha = 1.0,
            **kwargs,
            ):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots()

        patch = self.to_patch(
                pix_size,
                edgecolor = color,
                linewidth = linewidth,
                alpha = alpha,
                **kwargs,
                )
        ax.add_patch(patch)
        return ax

@dataclass
class RectangleArea(Area):
    x0: int
    x1: int
    y0: int
    y1: int

    def make_mask(self, shape) -> np.ndarray:
        mask = np.zeros(shape, dtype=bool)
        mask[self.y0: self.y1, self.x0: self.x1] = True
        return mask 

    def return_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {
                "shape" : "Rectangle",
                "x0" : self.x0,
                "x1" : self.x1,
                "y0" : self.y0,
                "y1" : self.y1,
                }
        return state

    def shape(self) -> tuple[int, int]:
        return self.y1 - self.y0, self.x1 - self.x0

    def __mul__(self, other) -> Self:
        if isinstance(other, int):
            return type(self)(
                    x0 = self.x0 * other,
                    x1 = self.x1 * other,
                    y0 = self.y0 * other,
                    y1 = self.y1 * other,
                    )
        return NotImplemented

    def to_patch(self, pix_size, **kwargs) -> Patch:
        return Rectangle(
                xy= (self.x0 *pix_size, self.y0 *pix_size),
                width= (self.x1 - self.x0) *pix_size,
                height= (self.y1 - self.y0) *pix_size,
                fill= False,
                **kwargs,
                )


@dataclass
class CircleArea(Area):
    radius: float
    cx: int
    cy: int

    def make_mask(self, shape) -> np.ndarray:
        yy, xx = np.ogrid[:shape[0], :shape[1]]
        return (xx - self.cx)**2 + (yy - self.cy)**2 <= self.radius**2

    def return_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {
                "shape" : "Circle",
                "radius" : self.radius,
                "cx" : self.cx,
                "cy" : self.cy,
                }
        return state

    def __mul__(self, other) -> Self:
        if isinstance(other, int):
            return replace(self, radius= self.radius * other)
        return NotImplemented

    def to_patch(self, pix_size, **kwargs) -> Patch:
        return Circle(
                radius= self.radius *pix_size,
                xy= (self.cx*pix_size, self.cy*pix_size),
                fill= False,
                **kwargs,
                )
