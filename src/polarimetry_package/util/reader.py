from astropy.io import fits
import numpy as np
from typing import cast
#from ..processing.models.header import HeaderRaw, HeaderProfile

#InstrumentModelへ移植済み(2026.1.14)
#def get_path_list(file_directry: str, suffix: str, extension: str) -> list[Path]:
#    path = Path(file_directry)
#    pattern = f"*{suffix}{extension}"
#    path_list = list(path.glob(pattern))
#    return path_list

def read_file(filename: str) -> tuple[np.ndarray, fits.Header]:
    with fits.open(filename) as hdul:
        hdu = cast(fits.PrimaryHDU, hdul[0])
        data = hdu.data
        header = hdu.header
        if data is None:
            raise ValueError("data is None")
        return data, header


#HeaderRawへ移植済み(2026.1.8)
#def parse_header(header: fits.Header, ) -> HeaderRaw:
#    return HeaderRaw(
#            polarizer= str(header.get("FILTNAM1", "")),
#            filter= str(header.get("FILTNAM4","")),
#            photflam= cast(float,header.get("photflam",np.nan)),
#            exptime= cast(float,header.get("exptime",np.nan))
#            )
#これのようにreaderにheaderに関する責務を持たせるとややこしくなる。後で消すこと

#ImageSetへ移植済み（2026.1.14)
#def load_data(path_list: list) -> tuple[dict[str, np.ndarray | None], HeaderProfile]:
#    dat_dict: dict[str, np.ndarray | None] = {}
#    hdr_dict: dict[str, HeaderRaw] = {}
#
#    for path in path_list:
#        data, header = read_file(path)
#        hdr = HeaderRaw.parse_header(header)
#        filename: str = path.name
#        dat_dict[filename] = data
#        hdr_dict[filename] = hdr
#
#    hdr_profile = HeaderProfile(raw= hdr_dict)
#
#    return dat_dict, hdr_profile
#
