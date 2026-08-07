#!/bin/bash
#SBATCH --job-name=coast_ID_YEAR
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
srun python3 simulation_bothnian_sea.py ID YEAR MONTH1 MONTH2
