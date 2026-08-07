template=job_template_connect_ID_YEAR.slurm

# command line arguments
areaid=$1    # area id (always needed!)
#sample=$2    # sample id (always neede)
depends=$2   # dependency (optional), leave empty if no dependency

# set dependency string if specified
if [[ -z "$depends" ]]; then
    # empty: no dependence
    DEP_STR=''
elif [[ $depends -eq 1 ]]; then
    # 1: read last job id from tile
    PARENT_JOB=$(cat last_job_id.txt)
    DEP_STR="-d afterany:${PARENT_JOB}"
else
    # use specified job id
    DEP_STR="-d afterany:${depends}"
fi

# change these when needed:
walltime=1
tasks=90
PD=5

# loop years (and month if necessary) to simulate
#for month in 6 7
#do
for year in 2012 2013 2017 2018  
do
    runfile=sjob_connect_${areaid}_${year}_${month}_nb${sample}.sh
    sed 's/ID/'${areaid}'/g' $template > $runfile
    sed -i 's/,END//' $runfile   # UNCOMMENT this to disable email when finished without errors 
    sed -i 's/YEAR/'${year}'/g' $runfile
    sed -i 's/MONTH/'${month}'/g' $runfile
    sed -i 's/HH/'${walltime}'/' $runfile
    sed -i 's/TASKS/'${tasks}'/' $runfile
    #sed -i 's/SAMPLE/'${sample}'/' $runfile
    sed -i 's/PD/'${PD}'/' $runfile
    echo $runfile
    # create command string
    QCMD="sbatch $DEP_STR $runfile"
    # print out to check
    echo $QCMD
    # execute command, and take the new job id into variable
    id=$($QCMD)
    JOB_ID=${id##* }
    echo "parsed job id: $JOB_ID"
    # wait a bit
    sleep 2s
    # update dependency string to take into account the new job id
    #DEP_STR="-d afterany:${JOB_ID}"
done
#done
# store the last job id in a file
echo $JOB_ID > ./last_job_id.txt
