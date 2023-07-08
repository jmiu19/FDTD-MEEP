#!/bin/bash
#SBATCH --job-name=single_cav
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=12g
#SBATCH --time=100:00:00


JOB_NUM=$((SLURM_ARRAY_TASK_ID))

mpirun python3 nanobeam.py -params $1 > output/OUTPUT$1.out;
line=$(grep harminv0: output/OUTPUT$1.out |cut -d , -f2-7 |grep -v frequency);
echo "$1, $line" >> output/cavity_resonances.dat;
grep flux1: output/OUTPUT$1.out > output/FLUX$1.dat;
mpirun python3 flux_plot.py $1;

