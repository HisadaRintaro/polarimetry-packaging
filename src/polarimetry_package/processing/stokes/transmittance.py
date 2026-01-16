from dataclasses import dataclass
from astropy.units import nd
import numpy as np
import stsynphot
from typing import Self
from ..models.header import HeaderRaw
from ..models.wave import Wave


@dataclass
class Transmittance:
    instrument: str  #"foc"
    costar: str      #",costor" or ""
    optical: str        #"f/96"
    polarizer: str   #"pol0"
    orientation: str #"per" or "par"
    filt: str      #"F253m"

    @classmethod
    def load(cls, header_raw: HeaderRaw, orientation: str) -> Self:
        if header_raw.optical == "F48":
            optical = "f/48"
        elif header_raw.optical == "F96":
            optical = "f/96"
        else:
            optical = header_raw.optical
        return cls(
                instrument= header_raw.instrument,
                costar= ",costar" if header_raw.costar else "",
                optical= optical,
                polarizer= header_raw.polarizer,
                orientation= orientation,
                filt = header_raw.filt,
                )


    def band_spec_base(self) -> str:
        return f"{self.instrument}{self.costar},{self.optical}"

    def band_spec_polarizer(self) -> str:
        return f"{self.instrument}{self.costar},{self.optical},{self.polarizer}_{self.orientation}"

    def band_spec_filter(self) -> str:
        return f"{self.instrument}{self.costar},{self.optical},{self.filt}"


    def trans_curve_pol(self, wave: np.ndarray) -> np.ndarray:
        band_base = stsynphot.band(self.band_spec_base())
        band_pol  = stsynphot.band(self.band_spec_polarizer())
        return band_pol(wave).value / band_base(wave).value

    def trans_curve_filter(self, wave: np.ndarray) -> np.ndarray:
        band_base = stsynphot.band(self.band_spec_base())
        band_filter  = stsynphot.band(self.band_spec_filter())
        return band_filter(wave).value / band_base(wave).value


    def trans_mean(self, wave: Wave) -> float:
        wave_array = wave.array()
        wave_diff = wave.differential()

        trans_pol = self.trans_curve_pol(wave_array)
        trans_filter = self.trans_curve_filter(wave_array)

        return (trans_pol* trans_filter).sum() * wave_diff / (trans_filter.sum() * wave_diff)
    
    def wave_mean(self, wave:Wave) -> float:
        wave_array = wave.array()
        wave_diff = wave.differential()

        trans_filter = self.trans_curve_filter(wave_array)

        return (wave_array * trans_filter).sum() * wave_diff / (trans_filter.sum() * wave_diff)


#plotting/stokes_plottingへ移植済み(2026.1.14)
#    def plot_curve(
#        self,
#        wave: Wave,
#        ax= None,
#        label= None,
#        title= None,
#        times= 10,
#        ymax= 1,
#        **kwargs,
#        ):
#
#        ax = setup_ax(ax)
#        trans_curve = self.trans_curve_pol(wave.array())
#        if self.orientation == "per":
#            trans_curve = trans_curve * times
#            label = f"{label}(x{times})"
#        ax.plot(wave.array(), trans_curve, label=label, **kwargs)
#        ax.set_ylim(0,ymax)
#
#        if title:
#            ax.set_title(title)
#        
#        return ax
