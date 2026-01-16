from dataclasses import dataclass, replace
from typing import Self, Literal

from ..image.image_set import ImageSet
from ..models.header import HeaderProfile
from ..models.image_unit import ImageUnit
from ...plotting.plot_mixin import ImagePlotMixin
from ..models.noise_mixin import NoiseMixin
from . import flux

@dataclass(frozen=True)
class FluxImage(ImagePlotMixin, NoiseMixin):
    flux: dict[str, ImageUnit]
    noise: dict[str, ImageUnit]
    unit: str
    photflam: dict[str, float]
    exptime: dict[str, float]
    hdr_profile: HeaderProfile

    def __repr__(self) -> str:
        keys = list(self.flux.keys())
        shapes = {
            k: (None if v is None else v.shape())
            for k, v in self.flux.items()
        }
        return (
            f"FluxImage("
            f"keys={keys},\n "
            f"shapes={shapes},\n "
            f"unit={self.unit}\n "
            f")"
        )

    @classmethod
    def load(cls, image_set: ImageSet) -> Self:
        if image_set.status.get("binning", True) != "COMPLETE":
            raise RuntimeError(
                    "load() requires 'binning' = 'COMPLETE'"
                    )
        flux_image: dict[str, ImageUnit] = {}
        noise_image: dict[str, ImageUnit] = {}
        exptimes: dict[str, float] = {}
        photflams: dict[str, float] = {}
        for pol, data, noise in image_set:
            exptime = image_set.hdr_profile.exptime(pol)
            photflam = image_set.hdr_profile.photflam(pol)
            flux_image[pol] = replace(
                                data,
                                image= flux.to_flux(data.image, exptime, photflam, unit= "count"),
                                )
            binned_noise: ImageUnit = noise.cal_noise()
            noise_image[pol] = replace(
                                binned_noise,
                                image= flux.to_flux(binned_noise.image, exptime, photflam, unit="count"),
                                )
            exptimes[pol] = exptime
            photflams[pol] = photflam

        return cls(
                flux= flux_image,
                noise= noise_image,
                unit = "erg/s/cm-2/Å",
                exptime= exptimes,
                photflam= photflams, 
                hdr_profile= image_set.hdr_profile,
                )
        
    def to_flux(self) -> Self:
        flux_dict: dict[str, ImageUnit] = {}
        noise_dict: dict[str, ImageUnit] = {}
        for pol, _flux, noise, exptime, photflam in self:
            flux_dict[pol] = replace(
                    _flux,
                    image= flux.to_flux(_flux.image,exptime,photflam,self.unit)
                    )
            noise_dict[pol] = replace(
                    _flux,
                    image= flux.to_flux(noise.image,exptime,photflam,self.unit)
                    )
        return replace(
                self,
                flux = flux_dict,
                noise = noise_dict,
                unit = "erg/s/cm-2/Å",
                )
            


    def to_count_rate(self) -> Self:
        flux_dict: dict[str, ImageUnit] = {}
        noise_dict: dict[str, ImageUnit] = {}
        for pol, _flux, noise, exptime, photflam in self:
            flux_dict[pol] = replace(
                    _flux,
                    image= flux.to_count_rate(_flux.image,exptime,photflam,self.unit)
                    )
            noise_dict[pol] = replace(
                    _flux,
                    image= flux.to_count_rate(noise.image,exptime,photflam,self.unit)
                    )
        return replace(
                self,
                flux = flux_dict,
                noise = noise_dict,
                unit= "count/s",
                )

    def to_count(self) -> Self:
        flux_dict: dict[str, ImageUnit] = {}
        noise_dict: dict[str, ImageUnit] = {}
        for pol, _flux, noise, exptime, photflam in self:
            flux_dict[pol] = replace(
                    _flux,
                    image= flux.to_count(_flux.image,exptime,photflam,self.unit)
                    )
            noise_dict[pol] = replace(
                    _flux,
                    image= flux.to_count(noise.image,exptime,photflam,self.unit)
                    )
        return replace(
                self,
                flux = flux_dict,
                noise = noise_dict,
                unit= "count/s",
                )
    
    def _get_image(self, kind: Literal["image", "noise"], key: str) -> ImageUnit:
        if kind == "image":
            return self.flux[key]
        elif kind == "noise":
            return self.noise[key]
        
    def __iter__(self):
        yield from zip(self.flux.keys(), 
                       self.flux.values(), 
                       self.noise.values(),
                       self.exptime.values(),
                       self.photflam.values())
