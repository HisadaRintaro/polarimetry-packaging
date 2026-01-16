# polarimetry_package

A modular polarimetric data analysis package for imaging polarimetry.

This package provides:
- image-level preprocessing
- flux and Stokes parameter calculation
- pipeline-based execution
- lightweight plotting utilities

## Installation

Install dependencies:

```bash
# Recommended: create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Or on Windows
.venv\Scripts\activate
```

```bash
git clone https://github.com/HisadaRintaro/polarimetry-package.git
cd polarimetry_package
poetry install
```

Or, without Poetry(using pip).

```bash
git clone https://github.com/HisadaRintaro/polarimetry-package.git
cd polarimetry_package
pip install .
```


## stsynphot data setup

This project uses `stsynphot` for instrument throughput and calibration.
The synphot reference data must be installed manually.

**HST reference data file**:
[download link](https://ssb.stsci.edu/trds/tarfiles/synphot1.tar.gz)
,[website](https://stsynphot.readthedocs.io/en/latest/stsynphot/data_hst.html)

1. Clone synphot_refdata
2. Set environment variable:

export PYSYN_CDBS=/path/to/synphot

## Project structure

```bash
src/polarimetry_package/
├── pipeline/        # High-level execution pipelines and results
│   ├── standard.py  # Standard analysis pipeline
│   └── result.py    # Unified container of analysis outputs
├── processing/      # Numerical processing steps
│   ├── image/       # Image-level operations (background, binning, shift)
│   ├── flux/        # Flux calculation
│   └── stokes/      # Stokes parameter calculation
├── plotting/        # Plotting utilities and mixins
├── util/            # Small helpers (reader, decorators)
```

## Quick start

A standard analysis can be executed via the pipeline interface.

```python
from polarimetry_package.pipeline.standard import StandardPipeline
from polarimetry_package.processing import InstrumentModel
from polarimetry_package.processing.models import RectangleArea, CircleArea, Wave

inst = InstrumentModel.load(file_directry="FOC_POL_C1F")
area = RectangleArea(x0=300, x1=400, y0=100, y1=200) 
wave = Wave(1000,10000,5000) # unit=Å, instrument covering wavelength

pipeline = StandardPipeline(inst, area, bin_size=10, wave=wave)
result = pipeline.run()
```

The result object provides unified access to analysis products:

```python
result.images
result.flux
result.stokes
result.polarization_degree
result.position_angle
```


## Plotting

Image-like objects provide simple plotting methods.



```python
ax = result.images.plot("POL0", title="POL0 image")
```

Physical plottings are prepared under plotting. For example,

```python
from polarimetry_package import plotting
pa_ax = plotting.plot_position_angle(
        result.raws.data["POL0"],
        result.position_angle.theta,
        stretch="log"
        )
pa_ax = area.add_region_patch(ax=pa_ax)
```

## Core data model: ImageUnit

This package uses a unified internal representation called `ImageUnit`.

`ImageUnit` is a lightweight immutable data object that represents:

- a 2D image (`numpy.ndarray`)
- pixel scale information (`x_delta`, `y_delta`)

```python
@dataclass
class ImageUnit:
    image: np.ndarray
    x_delta: int
    y_delta: int
```

All image-like data in this package are internally stored as ImageUnit, including:

- `ImageSet.data` / `ImageSet.noise`

- `FluxImage.flux` / `FluxImage.noise`

- `StokesParameter.data` / `StokesParameter.noise`

- `PolarizationDegree.P` / `PolarizationDegree.noise_P`

- `PositionAngle.theta`

***Why ImageUnit?***

- Ensures consistent handling of pixel scale

- Enables safe immutable operations via dataclasses.replace

- Supports arithmetic operations (`+`, `-`, `*` , `/`) between images

- Simplifies pipeline composition and debugging

***Example***

```python
img1 = ImageUnit.load(image1, x_delta=1, y_delta=1)
img2 = ImageUnit.load(image2, x_delta=1, y_delta=1)

summed = img1 + img2
masked = summed.apply_mask(mask)
```

***Coordinate utilities***

`ImageUnit` provides helper methods to generate coordinate arrays and grids:

```python
y_arr, x_arr = img.make_arrays(xc=0, yc=0)
Y, X = img.make_grid()
```

These are used internally for plotting, binning, and region-based operations.



## Tests

Test FITS files are placed under `tests/FOC_POL_C1F/`.
They are used for local verification and development.

## Design notes

- Processing steps are designed to be composable and stateless where possible.
- Pipelines provide orchestration, not logic.
- Plotting functionality is implemented via mixins to avoid polluting core models.
- The Result class serves as a single entry point for downstream analysis and plotting.

