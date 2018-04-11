input_dir="/home/jseiler/self_consistent_SAGE/ini_files/base_self_consistent_1024"
output_dir="/home/jseiler/self_consistent_SAGE/logs/base_self_consistent_1024"
log_prefix="" # Attaches a prefix to each of the log files (useful for different parameter runs). 

LowSnap=27
HighSnap=27

NUMPROC=32

for ((snap_idx = LowSnap; snap_idx < HighSnap+ 1; ++snap_idx))
{

  echo "Running Snapshot ${snap_idx}"
  SAGE_ini="${ini_dir}/SAGE_snap${snap_idx}.ini"
  cifog_ini="${ini_dir}/cifog_snap${snap_idx}.ini"

  # Run SAGE
  echo "Running SAGE"
  mpirun -np ${NUMPROC} /home/jseiler/self_consistent_SAGE/sage/sage ${SAGE_ini} > ${log_dir}/${log_prefix}SAGE_${snap_idx}.log
  exit_code=$? 
  if [ $exit_code -ne 0 ]; then
    echo "SAGE exited with errorcode $exit_code"
    exit $exit_code 
  fi

  # Grid SAGE output
  echo "Gridding SAGE Output"
  mpirun -np ${NUMPROC} /home/jseiler/self_consistent_SAGE/gridding/grid_sage ${SAGE_ini} > ${log_dir}/${log_prefix}grid_${snap_idx}.log 
  exit_code=$? 
  if [ $exit_code -ne 0 ]; then
    echo "The gridding code exited with errorcode $exit_code"
    exit $exit_code 
  fi

  # Run cifog with -r -s for 1 snapshot
  if ((snap_idx == LowSnap)) ; then
    cifog_run_flag="-s"
  else
    cifog_run_flag="-r -s"
  fi   

  echo "Running cifog"
  mpirun -np ${NUMPROC} /home/jseiler/grid-model/cifog ${cifog_ini} ${cifog_run_flag} > ${log_dir}/${log_prefix}cifog_${snap_idx}.log
  exit_code=$? 
  if [ $exit_code -ne 0 ]; then
    echo "cifog exited with errorcode $exit_code"
    exit $exit_code 
  fi

  # Generate reionization redshift grid and increment SAGE+cifog ini
  echo "Running Python script"
  python3 /home/jseiler/self_consistent_SAGE/misc_functions.py -f ${SAGE_ini} -c ${cifog_ini} -r 1 -i ${ini_dir}
  exit_code=$? 
  if [ $exit_code -ne 0 ]; then
    echo "The Python cleanup script exited with errorcode $exit_code"
    exit $exit_code 
  fi


#  # Generate reionization modifiers + filter masses
  if ((snap_idx == LowSnap)) ; then
    filter_mass_run_flag=1
  else
    filter_mass_run_flag=0
  fi   

  echo "Generating filter mass" 
  mpirun -np ${NUMPROC} /home/jseiler/self_consistent_SAGE/create_filter_mass ${SAGE_ini}${ini_tag} ${snap_idx} ${filter_mass_run_flag} > ${log_dir}/${log_prefix}filtermass_${snap_idx}.log 
  exit_code=$? 
  if [ $exit_code -ne 0 ]; then
    echo "create_filter_mass exited with errorcode $exit_code"
    exit $exit_code 
  fi

} 
