#!/bin/bash

# Parameters
#SBATCH --cpus-per-task=1
#SBATCH --error=/n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/notebooks/prospector_dhsnepal/log_test/%j/%j_0_log.err
#SBATCH --job-name=submitit
#SBATCH --mem=1GB
#SBATCH --nodes=1
#SBATCH --open-mode=append
#SBATCH --output=/n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/notebooks/prospector_dhsnepal/log_test/%j/%j_0_log.out
#SBATCH --partition=hsph
#SBATCH --signal=USR2@90
#SBATCH --time=4
#SBATCH --wckey=submitit

# command
export SUBMITIT_EXECUTOR=slurm
srun --unbuffered --output /n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/notebooks/prospector_dhsnepal/log_test/%j/%j_%t_log.out --error /n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/notebooks/prospector_dhsnepal/log_test/%j/%j_%t_log.err /n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/.venv/bin/python -u -m submitit.core._submit /n/holylabs/cgolden_lab/Lab/frontier/town/tinashe/rse-workbench/notebooks/prospector_dhsnepal/log_test/%j
