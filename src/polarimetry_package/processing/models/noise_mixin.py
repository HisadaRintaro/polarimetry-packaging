from abc import ABC, abstractmethod
from typing import Literal
import numpy as np
from .area import RectangleArea
from .image_unit import ImageUnit

class NoiseMixin(ABC):
    @abstractmethod
    def _get_image(self, kind: Literal["image", "noise"], key: str) -> ImageUnit:
        pass

    def SN(
        self,
        key: str = "POL0",
        ) -> ImageUnit:

        image = self._get_image("image", key)
        noise = self._get_image("noise", key)
        return image / noise

    def make_mask(
        self,
        key: str = "POL0",
        ratio= 3,
        ) -> np.ndarray:

        sn_img = self.SN(key)
        return sn_img.image > ratio
        
    def plot_SN(
        self,
        *,
        key: str = "POL",
        ax= None,
        cmap = "Grays",
        norm= None,
        title= None,
        colorbar= True,
        **kwargs,
        ):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots()

        sn_img = self.SN(key)
        im = ax.imshow(sn_img.image, cmap=cmap, norm=norm, **kwargs)

        if title:
            ax.set_title(title)
        if colorbar:
            plt.colorbar(im, ax=ax)

        return ax

