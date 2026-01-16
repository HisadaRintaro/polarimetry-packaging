from ..processing.image.image_set import ImageSet
from ..processing.flux.flux_image import FluxImage
from ..processing.stokes.stokes_set import StokesParameter, PolarizationDegree, PositionAngle
from dataclasses import dataclass

@dataclass(frozen=True)
class PolarimetryResult:
    filelist: list[str]
    raws: ImageSet
    images: ImageSet
    flux: FluxImage
    stokes: StokesParameter
    polarization_degree: PolarizationDegree
    position_angle: PositionAngle

    def __repr__(self) -> str:
        return (
            "PolarimetryResult(\n"
            f"filelist = {self.filelist!r}"
            f"raws = {self.raws!r},\n"
            f"images= {self.images!r},\n"
            f"flux= {self.flux!r},\n"
            f"stokes= {self.stokes!r},\n"
            f"PD= {self.polarization_degree!r},\n"
            f"PA= {self.position_angle!r},\n"
            ")"
            )
