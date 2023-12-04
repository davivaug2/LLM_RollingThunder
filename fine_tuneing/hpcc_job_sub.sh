#!/bin/bash
#SBATCH --job-name=langchain_test
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition matador
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --time=10:00:00
#SBATCH --gpus-per-node=2
##SBATCH --mem-per-cpu=9625MB ##9.4GB, modify based on needs

# submission for hpcc , activate condan enviorment in  the job
. $HOME/conda/etc/profile.d/conda.sh
conda activate llm_lang3
# make sure python name matches file
python3 ./llm_rolling_thunder_langchain_test_adding_trainingipynb.py
