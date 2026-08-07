#!/bin/bash
#SBATCH --job-name=raster_ID_YEAR_MONTH
#SBATCH --account=project_2018610
#SBATCH --partition=small
#SBATCH --time=HH:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=TASKS
#SBATCH --mail-type=FAIL,END

module purge
module load tykky
export PATH="/projappl/project_2018610/OpenDriftEnv/opendrift/opendrift/bin:$PATH"

cd /projappl/project_2018610/scripts_python/
srun python3 post_process_raster_metres.py ID YEAR MONTH 
