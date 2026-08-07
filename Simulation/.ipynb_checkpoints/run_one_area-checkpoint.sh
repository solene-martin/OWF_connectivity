template=job_template_ID_YEAR.slurm

# command line arguments
areaid=$1    # area id (always needed!)
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
walltime=10
tasks=25
month1=6
month2=10

# loop years to simulate
for year in 2013 2017 2018
do
    runfile=sjob_${areaid}_${year}.sh
    sed 's/ID/'${areaid}'/g' $template > $runfile
    sed -i 's/,END//' $runfile   # UNCOMMENT this to disable email when finished without errors 
    sed -i 's/YEAR/'${year}'/g' $runfile
    sed -i 's/MONTH1/'${month1}'/g' $runfile
    sed -i 's/MONTH2/'${month2}'/g' $runfile
    sed -i 's/HH/'${walltime}'/' $runfile
    sed -i 's/TASKS/'${tasks}'/' $runfile
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
# store the last job id in a file
echo $JOB_ID > ./last_job_id.txt
