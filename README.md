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

### Plot density maps ###
Using the jupyter notebook *Density_map/Density_map.ipynb*\
\
**Input data**:\
Raster files\
Shape file: *input_data/Wind_farms_Bothnian_Sea.shp* and *input_data/nemo_nordic_10-20m_polygons.shp*

## Calculate connectivity ##
### Generate the csv files ###
**Two options**: calculate the connectivity from OWFs to OWFs (*Post_process/calculate_connectivity_to_farm.py*) or from coastal areas to coastal areas (*Post_process/calculate_connectivity_to_coast.py*)\
\
Both scripts can be adapted to change the origin of the particles and calculate connectivity in different configuration (from coast to OWFs or from OWFs to coast)\
In *Post_process/calculate_connectivity_to_farm.py*: See lines 78 to 94\
In *Post_process/calculate_connectivity_to_coast.py*: See lines 77 to 85\
\
**Input data**:\
ncfile from the Opendrift simulation\
Shape file: *input_data/Wind_farms_Bothnian_Sea.shp* or *input_data/nemo_nordic_10-20m_polygons.shp*
### Connectivity matrices ###
Using the jupyter notebooks *connectivity/connectivity_matrix.ipynb* and *connectivity/Graph_NetworkX.ipynb*\
\
**Step 1**: Generate single csv files from simulations that were cut in half, using *connectivity/Graph_NetworkX.ipynb*\
**Step 2**: Generate one matrix and one csv file for each configuration (averaged over the 4 years) using *connectivity/connectivity_matrix.ipynb*, save the csv files\
**Step 3**: Generate one matrix with the whole network (OWFs and coastal areas) using the previous averaged csv files\
\
**Input data**:\
csv files (with the connectivity from each area)\
Shape file: *input_data/Wind_farms_Bothnian_Sea.shp* and *input_data/nemo_nordic_10-20m_polygons.shp*
## Network analysis ##

### Generate connectivity graphs ###
Using the jupyter notebooks *connectivity/Graph_NetworkX.ipynb*\
\
**Step 0**: If not already done, generate single csv files from simulations that were cut in half\
**Step 1**: Generate one graph for each configuration, save the graph as a json file (adapt the code for the configurations "from coast to farms" and "from farms to coast")\
**Step 2**: Generate one single graph by combining the 4 sub-graphs, save it as a json file\
**Step 3 (Optional)**: Plot the graph to visualize the network

**Input data**:\
csv files (with the connectivity from each area)\
Shape file: *input_data/Wind_farms_Bothnian_Sea.shp* and *input_data/nemo_nordic_10-20m_polygons.shp*

### Connectivity metrics ###
Using the jupyter notebook *connectivity/connectivity_metrics.ipynb*\
Main metrics: in and out degree centrality\

**Input data**:\
Graph saved as json file\

### Shortest paths ###

## Sensibility studies ##
