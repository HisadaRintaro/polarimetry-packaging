import numpy as np

def to_flux(data: np.ndarray, exptime: float, photflam: float, unit: str) -> np.ndarray:
    if unit == "count":
        return photflam * data / exptime
    elif unit == "count/s":
        return photflam * data
    elif unit == "erg/s/cm-2/Å":
        raise RuntimeError("data is already flux")
    else:
        raise ValueError("unit must be 'count' or 'count/s'")


def to_count_rate(data: np.ndarray, exptime: float, photflam: float, unit: str) -> np.ndarray:
    if unit == "count":
        return data / exptime
    elif unit == "count/s":
        raise RuntimeError("data is already count rate")
    elif unit == "erg/s/cm-2/Å":
        return data / photflam
    else:
        raise ValueError("unit must be 'count' or 'erg/s/cm-2/Å'")


def to_count(data: np.ndarray, exptime: float, photflam: float, unit: str) -> np.ndarray:
    if unit == "count":
        raise RuntimeError("data is already count")
    elif unit == "count/s":
        return data / exptime
    elif unit == "erg/s/cm-2/Å":
        return data / photflam * exptime
    else:
        raise ValueError("unit must be 'count' or 'count/s'")

