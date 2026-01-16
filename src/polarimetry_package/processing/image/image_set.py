from typing import Self, cast
from dataclasses import dataclass, replace
import numpy as np
import scipy
from typing import Any, Literal
from copy import deepcopy
#from .flux_image import FluxImage
from ..instrument.instrument import InstrumentModel
from ..models.header import HeaderProfile, HeaderRaw
from ..models.noise_set import Noise
from ..models.area import Area
from ..models.image_unit import ImageUnit
from ...plotting.plot_mixin import ImagePlotMixin
from ..models.noise_mixin import NoiseMixin
from ...util.reader import read_file
from . import shift, background, binning
from ...util.decorator import record_step

@dataclass(frozen=True)
class ImageSet(ImagePlotMixin, NoiseMixin):
    data: dict[str, ImageUnit]
    noise: dict[str, Noise] 
    hdr_profile: HeaderProfile 
    status: dict[str, Literal["PENDING", "PERFORM", "COMPLETE", "SKIPPED"]]
    status_keyword: dict[str, dict[str, Any]]

    def __repr__(self) -> str:
        keys = list(self.data.keys())
        shapes = {
            k: (None if v is None else v.shape())
            for k, v in self.data.items()
        }
        return (
            f"ImageSet("
            f"keys={keys},\n "
            f"shapes={shapes},\n "
            f"status={self.status}\n "
            f")"
        )

    @staticmethod
    def load_data(path_list: list, x_delta=1, y_delta=1) -> tuple[dict[str, ImageUnit], HeaderProfile]:
        dat_dict: dict[str, ImageUnit] = {}
        hdr_dict: dict[str, HeaderRaw] = {}

        for path in path_list:
            data, header = read_file(path)
            hdr = HeaderRaw.parse_header(header)
            filename: str = path.name
            dat_dict[filename] = ImageUnit(data, x_delta, y_delta)
            hdr_dict[filename] = hdr

        hdr_profile = HeaderProfile(raw= hdr_dict)

        return dat_dict, hdr_profile
        
    @classmethod
    def load(cls, instrument_info: InstrumentModel, bin_size=1) -> Self:
        path_list = instrument_info.path_list()
        data, hdr_profile = cls.load_data(path_list)

        return cls(data= data, noise= {pol: Noise.default(bin_size=bin_size) for pol,_ in data.items()}, 
                        hdr_profile= hdr_profile,
                        status={}, status_keyword={"POL0":{},"POL60":{},"POL120":{}}) 
    
    @record_step("sum")
    def sum(self) -> Self:
        summed: dict[str, ImageUnit] = {}
        noise_dict: dict[str, Noise] = {}
        for fname, data, noise in self:
            pol = self.hdr_profile.polarizer_of(fname)
            if pol not in summed:
                summed[pol] = data
            else:
                summed[pol] = data + summed[pol]

            if pol not in noise_dict:
                noise_dict[pol] = noise

        return type(self)(
                data= summed,
                noise= noise_dict,
                hdr_profile= self.hdr_profile.sum(),
                status= self.status,
                status_keyword=self.status_keyword,
                )

    @record_step("align")
    def align(self) -> Self:
        if self.status.get("sum", True) != "COMPLETE":
            raise RuntimeError(
                    "align() requires 'sum' = 'COMPLETE'"
                    )

        aligned: dict[str, ImageUnit]= {}
        noise_dict: dict[str, Noise]= {}
        new_status_kw = deepcopy(self.status_keyword)
        base_pol = next(iter(self.data))
        base_data = self.data[base_pol]

        for pol, data, noise in self:
            #For Using ndimage.shift, must input base_data to pix2.
            shifts = shift.find_shift(pix1=data.image, pix2=base_data.image)
            aligned_data: np.ndarray = scipy.ndimage.shift(data.image, shifts, mode="nearest")
            aligned[pol] = replace(data, image=aligned_data)
            count_noise: ImageUnit = replace(data, image=np.sqrt(aligned_data))
            noise_dict[pol] = replace(noise, count_noise=count_noise)
            new_status_kw[pol]["x_shift"] = shifts[1]
            new_status_kw[pol]["y_shift"] = shifts[0]

        return type(self)(
                data= aligned,
                noise= noise_dict,
                hdr_profile= self.hdr_profile,
                status= self.status,
                status_keyword= new_status_kw,
                )

    @record_step("background_subtract")
    def backfground_subtract(self, area: Area, method="mean") -> Self:
        if self.status.get("align", True) != "COMPLETE":
            raise RuntimeError(
                    "background_subtract() requires 'align' = 'COMPLETE'"
                    )

        background_subtract: dict[str, ImageUnit] = {}
        new_status_kw = deepcopy(self.status_keyword)
        noise_dict: dict[str, Noise] = {}

        for pol, data, noise in self:
            mask = area.make_mask(data.shape())
            background_value: np.floating = background.cal_background(data.image, mask, method=method)
            background_noise: np.floating = background.cal_background_noise(data.image, mask)
            background_subtract[pol] = data - background_value
            noise_dict[pol] = replace(noise, background_noise= background_noise)
            new_status_kw[pol]["background_value"] = background_value
            new_status_kw[pol]["background_noise"] = background_noise
            new_status_kw[pol]["area"] = area


        return type(self)(
                data= background_subtract,
                noise= noise_dict,
                hdr_profile= self.hdr_profile,
                status= self.status,
                status_keyword= new_status_kw,
                )

    @record_step("binning")
    def binning(self, bin_size) -> Self:
        if self.status.get("background_subtract", True) != "COMPLETE":
            raise RuntimeError(
                    "binning() requires 'background_subtract' = 'COMPLETE'"
                    )
        
        binned: dict[str, ImageUnit] = {}
        binned_noise: dict[str, Noise] = {}
        new_status_kw = deepcopy(self.status_keyword)
        
        for pol, data, noise in self:
            binned[pol] = ImageUnit(
                    image= binning.binning_image(data.image, bin_size),
                    x_delta= data.x_delta * bin_size,
                    y_delta= data.y_delta * bin_size,
                    )
            binned_noise[pol]= replace(noise, bin_size=bin_size)
            new_status_kw[pol]["bin_size"] = bin_size
        

        return type(self)(
                data= binned, 
                noise= binned_noise,
                hdr_profile= self.hdr_profile,
                status= self.status,
                status_keyword= new_status_kw,
                )

    def _get_image(self, kind: Literal["image", "noise"], key: str) -> ImageUnit:
        if kind == "image":
            return self.data[key]
        elif kind == "noise":
            return self.noise[key].cal_noise()

    def __iter__(self):
        yield from zip(self.data.keys(), self.data.values(), self.noise.values())
