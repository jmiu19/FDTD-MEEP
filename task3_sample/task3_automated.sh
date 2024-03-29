#!/bin/bash
#SBATCH --job-name=sample_task3
#SBATCH --cpus-per-task=4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=12g
#SBATCH --time=24:00:00

JOB_NUM=$((SLURM_ARRAY_TASK_ID))

mpirun python3 nanobeam.py -s_cav $1 > nanobeam_cavity_length$1.out;
line=$(grep harminv0: nanobeam_cavity_length$1.out |cut -d , -f2,4 |grep -v frequency);
echo "$1, $line" >> nanobeam_cavity_varylength.dat;
