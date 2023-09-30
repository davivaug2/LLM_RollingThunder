#!/bin/bash
#SBATCH --job-name=langchain_test
#SBATCH --output=%x.o%j
#SBATCH –-error=%x.e%j
#SBATCH --partition matador
#SBATCH --nodes=1
#SBATCH –-ntasks-per-node=10
#SBATCH --time=00:20:00
#SBATCH --gpus-per-node=2
##SBATCH --mem-per-cpu=9625MB ##9.4GB, modify based on needs
module load gcc/9.3.0 openmpi/3.1.6-cuda
mpirun ./llm_rolling_thunder_langchain_test