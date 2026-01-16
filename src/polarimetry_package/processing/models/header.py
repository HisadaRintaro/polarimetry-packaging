from dataclasses import dataclass
from collections import defaultdict
from astropy.io import fits
from typing import Self, cast
import numpy as np

@dataclass
class HeaderRaw:
    instrument: str
    costar: bool
    optical: str
    polarizer: str 
    filt: str
    photflam: float
    exptime: float

    @classmethod
    def parse_header(cls,header: fits.Header, ) -> Self:
        return cls(
                instrument= str(header.get("INSTRUME", "")),
                costar= True if header.get("KXDEPLOY", False) == "T" else False,
                optical= str(header.get("OPTCRLY", "")),
                polarizer= str(header.get("FILTNAM1", "")),
                filt= str(header.get("FILTNAM4","")),
                photflam= cast(float,header.get("photflam",np.nan)),
                exptime= cast(float,header.get("exptime",np.nan))
                )

    def get_pix_size(self) -> float:
        #そのうちzoomかどうかも判別することが必要。その時はImageSetのload_dataのdeltaも変更すること。
        if self.optical == "F96":
            return 14 / 512 #arcsec
        elif self.optical == "F48":
            return 28 / 512 #arcsec
        else:
            raise ValueError("get_pix_size() requires optical=='F96'or'F48'.")

@dataclass
class HeaderProfile:
    raw: dict[str, HeaderRaw]

    def sum(self) -> Self:
        summed: dict[str, HeaderRaw] = {}
        for pol, _ in self.by_polarizer().items():
            summed[pol] = HeaderRaw(
                    instrument= self.instrument(),
                    costar= self.costar(),
                    optical= self.optical(),
                    polarizer= pol,
                    filt = self.filter(),
                    photflam= self.photflam(pol),
                    exptime= self.exptime(pol)
                    )
        return type(self)(raw= summed)

    def by_polarizer(self):
        grouped: defaultdict[str, list] = defaultdict(list) 
        for _, hdr_raw in self.raw.items():
            pol = hdr_raw.polarizer
            grouped[pol].append(hdr_raw)
        return grouped

    def exptime(self, pol: str) -> float:
        return sum( [hdr_row.exptime for hdr_row in self.by_polarizer()[pol]])

    def photflam(self, pol:str, mode: str = "mean") -> float:
        values = [hdr_row.photflam for hdr_row in self.by_polarizer()[pol]]
        if not values:
            raise KeyError(pol)
        if mode=="mean":
            return sum(values)/ len(values)
        elif mode == "unique":
            return values[0]
        else:
            raise KeyError(mode)

    def instrument(self) -> str:
        instruments: list[str] = [hdr_raw.instrument for _,hdr_raw in self.raw.items()]
        if len(set(instruments)) == 1:
            return list(set(instruments))[0]
        else:
            raise ValueError(instruments)

    def optical(self) -> str:
        optical: list[str] = [hdr_raw.optical for _,hdr_raw in self.raw.items()]
        if len(set(optical)) == 1:
            return list(set(optical))[0]
        else:
            raise ValueError(optical)

    def filter(self) -> str:
        filters: list[str] = [hdr_raw.filt for _,hdr_raw in self.raw.items()]
        if len(set(filters)) == 1:
            return list(set(filters))[0]
        else:
            raise ValueError(filters)

    def costar(self) -> bool:
        costars: list[bool] = [hdr_raw.costar for _,hdr_raw in self.raw.items()]
        if len(set(costars)) == 1:
            return list(set(costars))[0]
        else:
            raise ValueError(costars)


    def polarizer_of(self,fname) -> str:
        return self.raw[fname].polarizer
