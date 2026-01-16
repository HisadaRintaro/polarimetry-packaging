from dataclasses import dataclass, replace
from typing import Self, Literal
import numpy as np

from ..flux.flux_image import FluxImage
from .demodulation_matrix import DemodulationMatrixFactory
from ...plotting.plot_mixin import ImagePlotMixin
from ..models.noise_mixin import NoiseMixin
from ..models.wave import Wave
from ..models.image_unit import ImageUnit

@dataclass(frozen=True)
class StokesParameter(ImagePlotMixin, NoiseMixin):
    I: ImageUnit
    Q: ImageUnit
    U: ImageUnit
    noise_I: ImageUnit
    noise_Q: ImageUnit
    noise_U: ImageUnit

    def __repr__(self) -> str:
        shapes: set = {self.I.shape(), self.Q.shape(), self.U.shape(),
                       self.noise_I.shape(), self.noise_Q.shape(), self.noise_U.shape()}
        return (
            f"StokesParameter(\n "
            f"keys= [I, Q, U, noise_I, noise_Q, noise_U],\n "
            f"shapes={shapes},\n "
            f")"
        )

    @staticmethod
    def make_frame(images:dict[str, ImageUnit]) -> ImageUnit:
        x_delta = {v.x_delta for v in images.values()}
        y_delta = {v.y_delta for v in images.values()}
        shepe = {v.shape() for v in images.values()}
        return ImageUnit(
                image= np.zeros(list(shepe)[0]),
                x_delta= list(x_delta)[0],
                y_delta= list(y_delta)[0],
                )

    @staticmethod
    def apply_demodulation_matrix(images: dict[str, ImageUnit], matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        f_stacked = np.stack([ image.image for _, image in images.items()]).reshape(3,-1)
        shapes = {v.shape() for v in images.values()}
        I, Q, U = (matrix @ f_stacked).reshape(3, *list(shapes)[0])
        return I, Q, U
    
    @classmethod
    def load(cls, flux_image: FluxImage, wave: Wave) -> Self:
        mueller_matrix = DemodulationMatrixFactory.load(flux_image.hdr_profile, wave).matrix()
        I, Q, U = cls.apply_demodulation_matrix(flux_image.flux, mueller_matrix)
        noise_I, noise_Q, noise_U = cls.apply_demodulation_matrix(flux_image.noise, mueller_matrix)
        frame = cls.make_frame(flux_image.flux)
        return cls(
                I= replace(frame, image=I),
                Q= replace(frame, image=Q),
                U= replace(frame, image=U),
                noise_I= replace(frame, image=noise_I),
                noise_Q= replace(frame, image=noise_Q),
                noise_U= replace(frame, image=noise_U),
                )
    def _get_image(self, kind: Literal["image", "noise"], key: str) -> ImageUnit:
        if key == "I" and kind == "image":
            return self.I
        elif key == "Q" and kind == "image":
            return self.Q
        elif key == "U" and kind == "image":
            return self.U
        elif key == "I" and kind == "noise":
            return self.noise_I
        elif key == "Q" and kind == "noise":
            return self.noise_Q
        elif key == "U" and kind == "noise":
            return self.noise_U
        else:
            raise ValueError(f"Unknown kind or key: {kind},{key}")

@dataclass
class PolarizationDegree(ImagePlotMixin, NoiseMixin):
    P: ImageUnit
    noise_P: ImageUnit

    def __repr__(self) -> str:
        shapes: set = {self.P.shape(), self.noise_P.shape()}
        return (
            f"PolarizationDegree(\n "
            f"keys= [P, noise_P],\n "
            f"shapes={shapes},\n "
            f")"
        )

    @staticmethod
    def cal_pola_deg(I:np.ndarray, Q:np.ndarray, U:np.ndarray) -> np.ndarray:
        return np.sqrt(Q**2 + U**2) / I
    
    @staticmethod
    def cal_noise_pola_deg(I:np.ndarray, noise_I:np.ndarray) -> np.ndarray:
        return np.sqrt(2) * noise_I / I

    @classmethod
    def load(cls, stokes_para: StokesParameter) -> Self:
        P = cls.cal_pola_deg(
                stokes_para.I.image,
                stokes_para.Q.image,
                stokes_para.U.image,
                )
        noise_P = cls.cal_noise_pola_deg(
                stokes_para.I.image,
                stokes_para.noise_I.image
                )
        return cls(
                P= replace(stokes_para.I, image=P),
                noise_P= replace(stokes_para.I, image=noise_P),
                )

    def _get_image(self, kind: Literal["image", "noise"], key: str="POL0") -> ImageUnit:
        if kind == "image":
            return self.P
        elif kind == "noise":
            return self.noise_P

@dataclass
class PositionAngle:
    theta: ImageUnit
    #noise_theta: np.ndarray
    #そのうち実装する

    def __repr__(self) -> str:
        shapes: set = {self.theta.shape()}
        return (
            f"PositionAngle(\n "
            f"keys= [theta],\n "
            f"shapes={shapes},\n "
            f")"
        )

    @staticmethod
    def cal_position_angle(
            Q:np.ndarray,
            U:np.ndarray,
            mask: np.ndarray | None = None
            ) -> np.ndarray:
        theta =  1/2 * np.arctan2(U,Q)
        if isinstance(mask, np.ndarray):
            theta[mask == False] = np.nan
        return theta


    @classmethod
    def load(cls, stokes_para: StokesParameter, mask = None) -> Self:
        theta = cls.cal_position_angle(
                stokes_para.Q.image,
                stokes_para.U.image,
                mask = mask,
                )
        return cls(
                theta= replace(stokes_para.I, image=theta),
                )



