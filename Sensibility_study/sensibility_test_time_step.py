import sys
from datetime import datetime, timedelta
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers.reader_netCDF_CF_generic import Reader
import datetime as dt
import copernicusmarine
import numpy as np
from numpy import random
import pandas as pd

product = sys.argv[1] #'daily' or 'hourly'
if product == 'daily':
	dataset_id='cmems_mod_bal_phy_my_P1D-m'
if product == 'hourly':
	dataset_id='cmems_mod_bal_phy_anfc_PT1H-i' 
ds = copernicusmarine.open_dataset(dataset_id=dataset_id, chunk_size_limit=0)
reader_cmems = Reader(ds, name='CMEMS Baltic')

month = int(sys.argv[2])
output_tstep = 60.0 # output time step, in minutes
dtmix = 5.0 # vertical mixing timestep, in seconds

# Configuration settings to modify in wind farm connectivity simulations:
for tstep in [1, 5, 10, 15, 20]:

	o = OceanDrift(loglevel=50)
	o.add_reader(reader_cmems, variables=['x_sea_water_velocity', 'y_sea_water_velocity'])

	# calculation time step and output time step
	o.set_config('general:time_step_minutes', tstep)
	o.set_config('general:time_step_output_minutes', output_tstep)

	# using auto landmask; if set False, need to provide landmask file
	o.set_config('general:use_auto_landmask',True)
	# set coastline action, 'previous' or 'stranding'
	o.set_config('general:coastline_action','stranding')
	# if particles get seeded on land, move them to the closest location in sea
	o.set_config('seed:ocean_only', True)

	# choosing advection scheme, using runge-kutta or runge-kutta 4
	o.set_config('drift:advection_scheme', 'runge-kutta4')

	# no vertical advection because no vertical velocity components
	o.set_config('drift:vertical_advection', False)


	starttime = dt.datetime(2024,month,1)
	endtime = dt.datetime(2024,month,5)
	o.seed_elements(lon=19.5, lat=61.5, z=-5, number=100, radius=1000, time=starttime)

	outfol = '/scratch/project_2018610/opendrift_outputs/'
	name_file = 'sensibility_test_time_step_{}_{}_month_{}.nc'.format(product, tstep, month)
	pngname = name_file.replace('.nc','.png')


	o.run(end_time=endtime, outfile=outfol+name_file)
