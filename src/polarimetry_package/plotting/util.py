import numpy as np
from astropy.visualization import ImageNormalize, AsinhStretch, LogStretch, LinearStretch
from .base import setup_ax
from ..processing.models.image_unit import ImageUnit

def plot_line(
        cx,
        cy,
        theta,
        length,
        ax = None,
        c= "white",
        linewidth=1,
        **kwargs
        ):
    dx = (length/2) * np.cos(theta + np.pi/2)
    dy = (length/2) * np.sin(theta + np.pi/2)

    X1,Y1 = cx - dx, cy - dy
    X2,Y2 = cx + dx, cy + dy

    ax = setup_ax(ax)
    for x1,x2,y1,y2 in zip(X1,X2,Y1,Y2):
        ax.plot([x1,x2],[y1,y2], c=c, linewidth=linewidth, **kwargs)
    return ax

def make_grid(
        size: tuple[int, int],
        shift= 0.5
        ) -> tuple[np.ndarray, np.ndarray]:
    x = np.arange(size[0]) + shift
    y = np.arange(size[1]) + shift
    return np.meshgrid(x,y)

 

def get_norm(stretch, vmin= None, vmax=None) -> ImageNormalize:
    if stretch == "asinh":
        stretch_obj = AsinhStretch()
    elif stretch == "log":
        stretch_obj =  LogStretch()
    elif stretch == "linear":
        stretch_obj = LinearStretch()
    else:
        raise ValueError(f"Unknown stretch: {stretch}")
    norm = ImageNormalize(
        vmin=vmin,
        vmax=vmax,
        stretch= stretch_obj,
    )
    return norm

def make_extent(image: ImageUnit, xc=0, yc=0) -> tuple:
    x_arr, y_arr = image.make_arrays(xc=xc, yc=yc)
    return (
            x_arr[0], x_arr[-1],
            y_arr[0], y_arr[-1],
            )
