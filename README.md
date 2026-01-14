# polarimetry_package

A modular polarimetric data analysis package for imaging polarimetry.

This package provides:
- image-level preprocessing
- flux and Stokes parameter calculation
- pipeline-based execution
- lightweight plotting utilities

## Installation

This project is managed with Poetry.

```bash
git clone https://github.com/HisadaRintaro/polarimetry-package.git
cd polarimetry_package
poetry install
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

## Basic usage

A standard analysis can be executed via the pipeline interface.

```python
from polarimetry_package.pipeline.standard import StandardPipeline

pipeline = StandardPipleline(
    instrument=instrument,
    area= background_area,
    bin_size= bin_size,
    wave= wave,
)

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
        bin_size,
        stretch="log"
        )
pa_ax = background_area.add_region_patch(ax=pa_ax)
```

## Tests

Test FITS files are placed under `tests/FOC_POL_C1F/`.
They are used for local verification and development.

## Design notes

- Processing steps are designed to be composable and stateless where possible.
- Pipelines provide orchestration, not logic.
- Plotting functionality is implemented via mixins to avoid polluting core models.
- The Result class serves as a single entry point for downstream analysis and plotting.

