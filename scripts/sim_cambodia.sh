#!/bin/bash

# Define which simulations to run for each duration
declare -A duration_simulations

# Duration 2: only these simulations
# duration_simulations[2]="cascading_hazards_0d cascading_hazards_1d cascading_hazards_2d
# cascading_hazards_3d cascading_hazards_4d"

# Duration 4: only these simulations
# duration_simulations[4]="cascading_hazards_0d cascading_hazards_1d cascading_hazards_2d cascading_hazards_3d cascading_hazards_4d cascading_hazards_5d cascading_hazards_6d cascading_hazards_7d cascading_hazards_8d"
duration_simulations[4]="cascading_hazards_9d cascading_hazards_10d cascading_hazards_11d cascading_hazards_12d"

# Duration 8: only these simulations
# duration_simulations[8]="cascading_hazards_0d cascading_hazards_2d cascading_hazards_4d cascading_hazards_6d cascading_hazards_8d cascading_hazards_10d cascading_hazards_12d cascading_hazards_14d cascading_hazards_16d"
duration_simulations[8]="cascading_hazards_18d cascading_hazards_20d cascading_hazards_22d cascading_hazards_24d"

# Duration 12: only these simulations
# duration_simulations[12]="cascading_hazards_0d cascading_hazards_3d cascading_hazards_6d cascading_hazards_9d cascading_hazards_12d cascading_hazards_15d cascading_hazards_18d cascading_hazards_21d cascading_hazards_24d"
duration_simulations[12]="cascading_hazards_27d cascading_hazards_30d cascading_hazards_33d cascading_hazards_36d"

# ho escluso duration 16

# Process each duration and its specific simulations
for duration in "${!duration_simulations[@]}"; do
    # Convert simulation names string to array
    read -a simulation_names <<< "${duration_simulations[$duration]}"
    
    echo "Processing duration ${duration} with simulations: ${duration_simulations[$duration]}"
    
    for simulation_name in "${simulation_names[@]}"; do
        job_name="dsc"
        
        echo "  Submitting job for duration=${duration}, simulation=${simulation_name}"
        
        sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=${job_name}
#SBATCH --error=logs/Cambodia/${job_name}_${duration}_${simulation_name}%j.err
#SBATCH --output=logs/Cambodia/${job_name}_${duration}_${simulation_name}%j.out
#SBATCH --time=96:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=16GB
echo "Job started: \$(date)"
module purge
source /projects/disruptsc/miniforge3/bin/activate /projects/disruptsc/miniforge3/envs/dsc
python src/disruptsc/main.py Cambodia --duration ${duration} --cache_isolation --simulation_name ${simulation_name}
echo "Job ended: \$(date)"
EOF
        sleep 10
    done
done