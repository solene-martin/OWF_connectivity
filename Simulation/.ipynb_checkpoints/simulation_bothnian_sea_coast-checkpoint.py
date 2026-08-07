from datetime import datetime, timedelta
import datetime as dt
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers.reader_netCDF_CF_generic import Reader
import xarray as xr
import copernicusmarine
import geopandas as gpd
import sys


# create reader for opendrift using this dataset
reader_grid = Reader('/projappl/project_2018610/data/cmems_baltic_grid.nc', name='CMEMS Baltic grid')
# open cmems data
ds = copernicusmarine.open_dataset(dataset_id='cmems_mod_bal_phy_my_P1D-m', chunk_size_limit=0)
reader_cmems = Reader(ds, name='CMEMS Baltic')

# read the shapefile
shape_file = '/projappl/project_2018610/data/coastal/nemo_nordic_10-20m_polygons.shp' 
gdf = gpd.read_file(shape_file)

ID = sys.argv[1] # Select the coastal area (FI from 0 to 8, SE from 01 to 14, A from 1 to 3)
row = gdf.loc[gdf['ID'] == ID] 
loc = row['geometry'].values[0]
fid = int(row['fid'].values[0]) 

nb_p = 15 # number of particles per km²
area = int(row['Area_km2'].values[0]) # area (km²)  
nb = area * nb_p # total number of particles per seeding

year = int(sys.argv[2])
month_start = int(sys.argv[3])
month_end = int(sys.argv[4])

# name the output file
name_file = 'simulation_coast_{}_June_September_{}.nc'.format(ID,year)

t_seed = 60 #seeding duration, in days
tstep = 5 # calculation time step, in minutes
PD = 60   # maximum pelagic propagule duration, in days; not used if None
output_tstep = 60.0 # output time step, in minutes
Kh = 5      # horisontal diffusivity, in m2/s
Kv = 0  # vertical diffusivity, in m2/s
dtmix = 5.0 # vertical mixing timestep, in seconds

o = OceanDrift(loglevel=50)
o.add_reader(reader_cmems, variables=['x_sea_water_velocity', 'y_sea_water_velocity'])
o.add_reader(reader_grid, variables=['sea_floor_depth_below_sea_level','land_binary_mask'])

# Configuration settings to modify in wind farm connectivity simulations:

# calculation time step and output time step
o.set_config('general:time_step_minutes', tstep)
o.set_config('general:time_step_output_minutes', output_tstep)

# using auto landmask; if set False, need to provide landmask file
o.set_config('general:use_auto_landmask',False)
# set coastline action, 'previous' or 'stranding'
o.set_config('general:coastline_action', 'stranding')
# if particles get seeded on land, move them to the closest location in sea
o.set_config('seed:ocean_only', True)

# choosing advection scheme, using runge-kutta or runge-kutta 4
o.set_config('drift:advection_scheme', 'runge-kutta4')

# no vertical advection because no vertical velocity components
o.set_config('drift:vertical_advection', False)

# adding horizontal and vertical diffusivities if > 0
if Kh>0:
    o.set_config('environment:constant:horizontal_diffusivity', Kh)
if Kv>0:
    o.set_config('drift:vertical_mixing', True) #Probably not the right command
    o.set_config('vertical_mixing:timestep', dtmix)  # seconds
    o.set_config('vertical_mixing:diffusivitymodel', 'constant')
    o.set_config('environment:fallback:ocean_vertical_diffusivity',Kv)

# no stokes drift or wind effects; we might want to change these later
o.set_config('drift:stokes_drift', False)
o.set_config('drift:wind_drift_depth', 0.0)
o.set_config('seed:wind_drift_factor', None)

# setting maximum pelagic duration for particles
o.set_config('drift:max_age_seconds',PD*24*3600)

starttime = dt.datetime(year,month_start,1)
endtime = dt.datetime(year,month_end,1)
for i in range(0,t_seed,3): # seeding during 30 or 60 days every 3 days
    o.seed_from_geopandas(loc, z=-1, number=nb/3, radius=100, time=starttime+dt.timedelta(days=i), origin_marker=fid)
    o.seed_from_geopandas(loc, z=-5, number=nb/3, radius=100, time=starttime+dt.timedelta(days=i), origin_marker=fid)
    o.seed_from_geopandas(loc, z=-10, number=nb/3, radius=100, time=starttime+dt.timedelta(days=i), origin_marker=fid)
    
outfol = '/scratch/project_2018610/opendrift_outputs/simulation_15_part_per_km2/seeding_from_coast/'
o.run(end_time=endtime, outfile=outfol+name_file)

