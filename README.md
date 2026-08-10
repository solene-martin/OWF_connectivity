## Run a Simulation ##
**Two options**: seeding from OWFs (*Simulation/simulation_bothnian_sea_OWF.py*) or seeding from coastal areas (*Simulation/simulation_bothnian_sea_coast.py*). \
\
Small farms (2, 3, 4, 5, 9, 14, 15, 16, 17, 18, 19): One simulation for the whole summer with a density of 15 particles/km²\
Medium farms (1, 6, 7, 8, 10, 12): Summer divided in two with a density of 15 particles/km²\
Large farms (11, 13): Summer divided in two with a density of 6 particles/km²\
\
**Input data**:\
Grid: *input_data/cmems_baltic_grid.nc*\
Shape file: *input_data/Wind_farms_Bothnian_Sea.shp* or *input_data/nemo_nordic_10-20m_polygons.shp*

## Generate a density map ##
### Generate raster files ###
Using the script *Post_process/post_process_raster_metres.py*\
\
**Input data**:\
ncfile from the Opendrift simulation\
Grid: *input_data/test_grid_2000m.gpkg*

## Calculate connectivity ##
### Generate the csv files ###

### Connectivity matrices ###

## Network analysis ##

### Generate connectivity graphs ###

### Connectivity metrics ###

### Shortest paths ###

## Sensibility studies ##
