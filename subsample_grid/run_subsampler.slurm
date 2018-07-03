#!/bin/bash
#SBATCH --job-name=1024_subsampled_256

#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --mem-per-cpu=20G
#SBATCH --nodes=1

module purge

module load scipy/1.0.0-python-3.6.4
module load gsl/2.4
module load astropy/2.0.3-python-3.6.4
module load numpy/1.14.1-python-3.6.4
module load openmpi/3.0.0
module load gcc/6.4.0
module load matplotlib/2.2.2-python-3.6.4
module load mpi4py/3.0.0-python-3.6.4
module load h5py/2.7.1-python-3.6.4-serial
module load ipython/5.5.0-python-3.6.4
module load git/2.16.0

input_grid_dir="/fred/oz004/jseiler/kali/density_fields/1024/snap_"
input_grid_suffix=".vz.dat"
input_grid_size=1024

output_grid_dir="/fred/oz004/jseiler/kali/density_fields/1024_subsampled_256/snap"
output_grid_suffix=".vz.dat"
output_grid_size=256

precision="double"

LowSnap=27
HighSnap=98

script_dir="/home/jseiler/short_scripts/subsample_grid/subsample.py"

for ((snap_idx = LowSnap; snap_idx < HighSnap+ 1; ++snap_idx))
{

  echo "Running Snapshot ${snap_idx}"

  input_snap_tag=${snap_idx} # For the 1024 grids the snapshot tag is simply the snapshot number (no padding).
  printf -v output_snap_tag "%03d" ${snap_idx} # However we want the output to be padded to three digits.

  input_grid="${input_grid_dir}${input_snap_tag}${input_grid_suffix}"
  output_grid="${output_grid_dir}${output_snap_tag}${output_grid_suffix}"

  python3 ${script_dir} -f ${input_grid} -o ${output_grid} -s ${input_grid_size} -d ${output_grid_size} -p ${precision}

}
