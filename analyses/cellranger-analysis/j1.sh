#!/bin/bash

set -e
set -o pipefail

########################################################################
# Load modules
module load cellranger/8.0.1

# Set up running directory
cd "$(dirname "${BASH_SOURCE[0]}")" 

# Read root path
rootdir=$(realpath "./../..")
echo "$rootdir"

########################################################################
# Read parameters from YAML file
cellranger_parameters=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'cellranger_parameters:' | awk '{print $2}')
cellranger_parameters=${cellranger_parameters//\"/}
echo "$cellranger_parameters"

multi_config_dir=$(cat ${rootdir}/project_parameters.Config.yaml | grep 'multi_config_dir:' | awk '{print $2}')
multi_config_dir=${multi_config_dir//\"/}
echo "multi_config dir: $multi_config_dir"

########################################################################
# Create output directoriescds 
module_dir="${rootdir}/analyses/cellranger-analysis"
results_dir="${module_dir}/results"
logs_dir="${results_dir}/01_logs"
output_dir="${results_dir}/02_cellranger_count/${cellranger_parameters}"

mkdir -p "$logs_dir" "$output_dir"

echo "Module dir: $module_dir"
echo "Results dir: $results_dir"
echo "Logs dir: $logs_dir"

########################################################################
# Loop through all CSV files in multi_config_dir
csv_files=(${multi_config_dir}/*.csv)
if [ ${#csv_files[@]} -eq 0 ]; then
    echo "No CSV files found in $multi_config_dir"
    exit 1
fi

for SAMPLES_FILE in "${csv_files[@]}"; do
    # Get the base filename without directory and extension
    base_name=$(basename "$SAMPLES_FILE" .csv)
    
    # Skip example config files
    if [[ "$base_name" == "multi_config_library_ID1" || "$base_name" == "multi_config_library_ID2" ]]; then
    echo "Skipping example config file"
          continue
    fi
    
    # Create subdirectory for each library using the base filename
    lib_dir="${output_dir}/${base_name}"
    mkdir -p "$lib_dir"
    run_id="multi_run_${cellranger_parameters}"
    log_id="${base_name/config/run}" # To generate log_id for each library

    echo "Processing $SAMPLES_FILE in $lib_dir"

    bsub -J "RNA_Multi_${base_name}" -n 8 -M 128000 -R "rusage[mem=16000]" \
        -o "${logs_dir}/${log_id}.out" -e "${logs_dir}/${log_id}.err" \
        "cd ${lib_dir} && \
         cellranger multi \
           --id=${run_id} \
           --csv=${SAMPLES_FILE} \
           --localcores=8 \
           --localmem=128 \
           --jobmode=lsf"
done

echo "All Cell Ranger Multi jobs submitted."

