input_grid_dir="/lustre/projects/p004_swin/jseiler/kali/densfield_grids/1024/snap_"
input_grid_suffix=".dens.dat"
input_grid_size=1024

output_grid_dir="/lustre/projects/p134_swin/jseiler/kali/density_fields/1024_subsampled_256/snap"
output_grid_suffix=".dens.dat"
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
  echo "${input_grid}"

  output_grid="${output_grid_dir}${output_snap_tag}${output_grid_suffix}"
  echo "${output_grid}"

  python3 ${script_dir} -f ${input_grid} -o ${output_grid} -s ${input_grid_size} -d ${output_grid_size} -p ${precision}

} 
