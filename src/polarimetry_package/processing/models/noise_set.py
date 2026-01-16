from typing import Any, Self
import numpy as np
from dataclasses import dataclass
from ..image.binning import binning_image
from .image_unit import ImageUnit

@dataclass
class Noise:
    #ここをImageUnitにかえる
    count_noise: ImageUnit | None
    background_noise: np.floating[Any] | None
    bin_size: int 

    @classmethod
    def default(cls, bin_size) -> Self:
        return cls(
                count_noise= None,
                background_noise= None,
                bin_size= bin_size,
                )

    def cal_noise(self) -> ImageUnit:
        bin_size = self.bin_size
        if self.count_noise is None:
            raise ValueError("count_noise is None")
        if self.background_noise is None:
            raise ValueError("background_noise is None")

        noise = np.sqrt(
                binning_image(
                    self.count_noise.image**2, bin_size
                    ) + bin_size**2 * self.background_noise**2
                )
        return ImageUnit(
                image= noise,
                x_delta= self.count_noise.x_delta * bin_size,
                y_delta= self.count_noise.y_delta * bin_size,
                )
