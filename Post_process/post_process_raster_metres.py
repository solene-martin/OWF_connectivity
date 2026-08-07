# enchanced postprocessing script for calculating density raster
# written by Elina, with the help from copilot

import xarray as xr
import shapely
import dask.array as da
import numpy as np
import geopandas as gpd
from pyproj import CRS, Transformer
import sys

# CRSs
WGS84 = CRS('epsg:4326')  # WGS84
ETRS89UTM = CRS('epsg:25834') # ETRS89 / UTM zone 34N

infol = '/scratch/project_2018610/opendrift_outputs/simulation_15_part_per_km2/seeding_from_farm/'
# infol = '/scratch/project_2018610/opendrift_outputs/simulation_15_part_per_km2/seeding_from_coast/'
outfol = '/scratch/project_2018610/connectivity/rasters/15_part_per_km2/'

# set opendrift output file name

polygon = int(sys.argv[1])
year = int(sys.argv[2])
month_start = int(sys.argv[3])

# uncomment if it's an OWF
if month_start == 0: # small farms, one simulation for the whole summer
    ncfile = 'simulation_farm_{}_June_September_{}.nc'.format(polygon, year)
else:
    if polygon not in [11, 13]:
        ncfile = 'simulation_farm_{}_June_September_{}_{}.nc'.format(polygon, year, month_start) # medium farms, summer divided in two
    else :
        ncfile = 'simulation_farm_{}_6_part_June_September_{}_{}.nc'.format(polygon, year, month_start) # lower density of part. used for farms 11 and 13

## uncomment if it's a costal area
# ncfile = 'simulation_coast_{}_June_September_{}.nc'.format(polygon, year)
        

# set raster file name, netcdf
raster_nc = ncfile.replace('.nc','_uniqsum_raster_metres.nc')

# create the transformer
transformer_lonlatTo2dxy = Transformer.from_crs(WGS84, ETRS89UTM, always_xy=True)
transformer_2dxyTolonlat = Transformer.from_crs(ETRS89UTM, WGS84, always_xy=True)

# load opendrift output
#ds = xr.open_dataset(ncfile, chunks={'trajectory': 100})
ds = xr.open_dataset(infol+ncfile, chunks={})
ds = ds.chunk({'trajectory': 100})
# ds.lon(trajectory, time), ds.lat(trajectory, time)

# extract lon and lat and flatten
lon = ds.lon.data.reshape(-1)
lat = ds.lat.data.reshape(-1)

# vectorized Shapely point constructor
def make_points(lon_arr, lat_arr):
    return shapely.points(lon_arr, lat_arr)

# apply with dask
points = da.map_blocks(
    make_points,
    lon, lat,
    dtype=object
)

# extract and flatten needed variables from opendrift output
status = ds.status.data.reshape(-1)
age = ds.age_seconds.data.reshape(-1)/60./60.  # seconds --> hours
z = ds.z.data.reshape(-1)
origin = ds.origin_marker.data.reshape(-1)

# trajectory and time indices
traj_index = np.repeat(ds.trajectory.values, ds.time.size)+1
time_index = np.tile(ds.time.values, ds.trajectory.size)

# compute geometry and and other variables for geodataframe
geom = points.compute()
status_v = status.compute()
age_v = age.compute()
z_v = z.compute()
origin_v = origin.compute()
traj_v = traj_index
time_v = time_index

# build geodataframe
coords = gpd.GeoDataFrame(
    {
        "traj": traj_v,
        "time": time_v,
        "status": status_v,
        "age_hours": age_v,
        "z": z_v,
        "origin_marker": origin_v,
    },
    geometry=geom,
    crs="EPSG:4326"
)
# change the coordinate system
coords = coords.to_crs("EPSG:25834")
# read grid file (grid must be stored as polygons),
# grid in metres, resolution: 2km

gridfile = '/projappl/project_2018610/data/grids/test_grid_2000m.gpkg'
grid = gpd.read_file(gridfile)

# spatial join on grid and trajectory dataframes
df = gpd.sjoin(grid, coords)
# count unique trajectories passing each grid cell
nunique = df.groupby('gridid')['traj'].nunique()/df['traj'].max()
# merge the resulting geoseries with original grid dataframe
unique = grid.merge(nunique, how='left', left_on='gridid', right_index=True)
# rename column
unique.rename(columns = {'traj':'N_count'}, inplace = True)

# prepare output to be saved
# set nans to zero:
output = unique.fillna(0)
# change grid cell center coordinates to geometry
# (this part depends on the grid file, and the following works with the test grid files Elina made)
output['geometry'] = output['c_coords'].apply(shapely.wkt.loads)

# saving to netcdf 
# get center coordinates to be used as indices in xarray
output['x'] = output.geometry.x
output['y'] = output.geometry.y
# convert to xarray
da = output.set_index(['y', 'x']).N_count.to_xarray()
print('...check if nans in output: {}'.format(np.isnan(da.data).any()))
# save to netcdf
print('...saving to '+outfol+raster_nc)
da.to_netcdf(outfol+raster_nc)
