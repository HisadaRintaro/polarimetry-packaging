from polarimetry_package.pipeline import StandardPipeline
from polarimetry_package.processing import InstrumentModel
from polarimetry_package.processing.models import RectangleArea, CircleArea, Wave


#---variables---#

directry= "FOC_POL_C1F/"
rectangle = RectangleArea(x0=300, x1=400, y0=100, y1=200) 
circle = CircleArea(radius=50, cx=350, cy=150)
background_area = circle #optional area (rectangle or circle)
image_area = RectangleArea(x0=13, x1=43, y0=15, y1=51) #image plottin area with use plot(area=image_area)
wave = Wave(1000,10000,5000) # unit=Å, instrument covering wavelength
bin_size = 10


#---processing---#

instrument: InstrumentModel = InstrumentModel(file_directry=directry, suffix= "", extension= "")

pipeline = StandardPipeline(
        instrument, 
        background_area,
        bin_size,
        wave,
        )

result = pipeline.run()

#---image plottings---#
from polarimetry_package import plotting
pa_ax = plotting.plot_position_angle(
        result.raws.data["POL0"],
        result.position_angle.theta,
        stretch="log"
        )
pa_ax = background_area.add_region_patch(ax=pa_ax)


#---transmittance curves---#
from polarimetry_package.processing import DemodulationMatrixFactory
from polarimetry_package.plotting import plot_transmittance_curve
demodulation_matrix_factory = DemodulationMatrixFactory.load(result.flux.hdr_profile, wave)
trans_ax = plot_transmittance_curve(demodulation_matrix_factory, wave)

#---stokes panel---#
from polarimetry_package.plotting import show_stokes_panel
show_stokes_panel(result.stokes.I, result.stokes.Q, result.stokes.U)
