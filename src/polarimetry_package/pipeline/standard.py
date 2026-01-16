from dataclasses import dataclass
from ..processing.instrument.instrument import InstrumentModel
from ..processing.image.image_set import ImageSet
from ..processing.flux.flux_image import FluxImage
from ..processing.stokes.stokes_set import StokesParameter, PolarizationDegree, PositionAngle
from ..processing.stokes.transmittance import Wave
from ..processing.models.area import Area
from .result import PolarimetryResult

@dataclass
class StandardPipeline:
    instrument: InstrumentModel
    area: Area
    bin_size: int
    wave: Wave

    def run(
        self,
        method= "median",
        mask_ratio = 3,
    ):
        images = (
            ImageSet.load(self.instrument)
            .sum()
            .align()
            .backfground_subtract(self.area, method=method)
            .binning(self.bin_size)
        )
        flux = FluxImage.load(images)
        stokes = StokesParameter.load(flux, self.wave)
        polarization_degree = PolarizationDegree.load(stokes)
        mask = polarization_degree.make_mask(ratio=mask_ratio)
        position_angle = PositionAngle.load(stokes, mask=mask)

        return PolarimetryResult(
                filelist= self.instrument.path_list(),
                raws= ImageSet.load(self.instrument).sum(),
                images= images,
                flux= flux,
                stokes= stokes,
                polarization_degree= polarization_degree,
                position_angle= position_angle,
                )
