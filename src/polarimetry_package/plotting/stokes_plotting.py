from matplotlib.colors import Normalize
from typing import cast
import matplotlib.pyplot as plt

from ..processing.stokes.transmittance import Transmittance
from .base import setup_ax, add_colorbar
from .util import plot_line, make_extent
from .util import get_norm
from ..processing.stokes.demodulation_matrix import DemodulationMatrixFactory, Wave
from ..processing.models.image_unit import ImageUnit


def plot_stokes_para(
        image: ImageUnit,
        *,
        xc = 0,
        yc = 0,
        ax=None,
        cmap = "gray",
        stretch="asinh",
        vmin=None,
        vmax=None,
        title="",
        **kwargs,
    ):
    ax = setup_ax(ax)

    norm = get_norm(stretch, vmin=vmin, vmax=vmax)
    extent = make_extent(image, xc=xc, yc=yc)

    im = ax.imshow(
                                image.image,
                                norm=cast(Normalize,norm),
                                cmap=cmap,
                                extent= extent,
                                **kwargs,
                                )
    ax.set_title(title)
    add_colorbar(im, ax)

    return ax

def show_stokes_panel(
        I,
        Q,
        U,
        *,
        axes = None,
        figsize= (15,4),
        stretchs: tuple = ("log", "asinh","asinh"),
        vmins: tuple = (None, None, None),
        vmaxs: tuple = (None, None, None),
        **kwargs,
        ):
        
    images = {"I":I, "Q":Q, "U":U}
    if axes is None:
        _, axes = plt.subplots(1,3, figsize=figsize)
    
    n = 0
    for name, image in images.items():
        plot_stokes_para(
                image,
                ax=axes[n],
                stretch=stretchs[n],
                vmin=vmins[n],
                vmax=vmaxs[n],
                title=name,
                **kwargs,
                )
        n += 1
    return axes


def plot_position_angle(
        back_image: ImageUnit,
        position_angle: ImageUnit,
        *,
        line_ratio=1,
        ax=None,
        stretch="asinh",
        vmin=None,
        vmax=None,
        c= "white",
        linewidth= 1,
        title= "",
        **kwargs,
        ):

    ax = plot_stokes_para(
            back_image,
            ax= ax,
            stretch= stretch,
            vmin= vmin,
            vmax= vmax,
            title= title,
            **kwargs,
            )

    mx, my = position_angle.make_grid()
    ax = plot_line(
            mx,
            my,
            position_angle.image,
            length = line_ratio *position_angle.get_pix_size(),
            ax = ax,
            c= c,
            linewidth= linewidth,
            **kwargs,
            )
    return ax

def plot_curve(
    transmittance: Transmittance,
    wave: Wave,
    ax= None,
    label= None,
    title= None,
    times= 10,
    ymax= 1,
    **kwargs,
    ):

    ax = setup_ax(ax)
    trans_curve = transmittance.trans_curve_pol(wave.array())
    if transmittance.orientation == "per":
        trans_curve = trans_curve * times
        label = f"{label}(x{times})"
    ax.plot(wave.array(), trans_curve, label=label, **kwargs)
    ax.set_ylim(0,ymax)

    if title:
        ax.set_title(title)
    
    return ax

def plot_transmittance_curve(
        demodulation_matrix_factory: DemodulationMatrixFactory,
        wave: Wave,
        ax= None,
        ymax=1,
        **kwargs
        ):
    ax = setup_ax(ax)

    for pol, pol_eff in demodulation_matrix_factory.polarization_eff.items():
        ax = plot_curve(pol_eff.major, wave, label= f"{pol}_major", ax=ax, ymax=ymax, **kwargs)
        ax = plot_curve(pol_eff.minor, wave, label= f"{pol}_minor", ax=ax, ymax=ymax, **kwargs)

    ax.set_xlabel("$wave length [ \\AA ]$")
    ax.set_ylabel("transmittance")
    ax.legend()
    ax.grid(True)
    return ax


