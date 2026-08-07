import xarray as xr
import shapely
import dask.array as da
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import sys

'''
Return a csv file with the connectivity value from either OWF or coastal areas to coastal areas.
Comment/uncomment lines to adapt to each situation.
'''

def opendrift_output_to_geodataframe(ncfile):
    
    # load opendrift output
    ds = xr.open_dataset(ncfile, chunks={})
    ds = ds.chunk({'trajectory': 100})

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

    return coords

#%% read windfarms

shpfile = '/projappl/project_2018610/data/coastal/nemo_nordic_10-20m_polygons.shp'
poly = gpd.read_file(shpfile)

# %% read opendrift output

startID = sys.argv[1] 
year = int(sys.argv[2])
PLD = int(sys.argv[3])

PLD_max = 60

outfol = '/scratch/project_2018610/opendrift_outputs/simulation_15_part_per_km2/seeding_from_coast/'
save_fol = f'/scratch/project_2018610/opendrift_outputs/simulation_15_part_per_km2/connectivity/PD{PLD}/from_coast_to_coast/'
file = 'simulation_coast_{}_June_September_{}.nc'.format(startID, year)

ncfile = outfol + file
csvfile = save_fol + file.replace('.nc',f'_PD{PLD}_connectivity_to_coast.csv')
coords = opendrift_output_to_geodataframe(ncfile)

# %% considering locations only within PLD (when set smaller than the maximum simulated PLD)
if PLD < PLD_max:
    arows = coords.age_hours < PLD*24+1
    coords = coords[arows]

# %% compute spatial join
print('sjoin with coordinates and polygons')
# sjoin, and dropping time, origin_marker and status
# here sjoin changes FarmID.dtype to float (because it needs to store NaNs)
# --> needs to be changed back to int later
joined = gpd.sjoin(coords[['traj','age_hours','geometry']],poly[['ID','geometry']],
              how='left', predicate='intersects')
joined.drop(columns=['index_right'],inplace=True)

# age when reaching each polygon (individual trajectories)
age = joined.groupby(['traj','ID']).min(numeric_only=True).reset_index()
age['count'] = 1
# number of timesteps spent within each polygon (individual trajectories)
count = joined.groupby(['traj','ID']).nunique()
count.drop(columns=['geometry'],inplace=True)
count.columns = ['count']
count.reset_index(inplace=True)
# calculate number of trajectories reaching each polygon
Nto = count[['ID','traj']].groupby('ID').nunique()

print('creating connectivity matrix')
# reset index, rename columns, set datatype to integer
df = Nto.reset_index().rename(columns={'ID': 'to','traj': 'N'})
df['N'] = df['N'].astype(int)
df['to'] = df['to'].astype(str)
# add column for release location id
df['from'] = startID
# drop all other columns
df = df[['from','to','N']]
# calculate total number of released particles for calculating probability
Ntot = coords.traj.max()
df['Ntot'] = Ntot
# probability of transport to each polygon
df['prob'] = df.N/Ntot

# %% save to csv
print('saving to '+csvfile)
df.to_csv(csvfile,sep=';',index=False,float_format='%.5f')