#!/bin/bash

#load GROMACS and PLUMED
module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

#Choose host Choose ligand Choose main directory name subdirectory for each walker distance translation   Method Topology file
HOST="$1"; LIGAND="$2"; MAIN_DIRECTORY="$3"; DIR_NAME="$4"; x="$5"; TOPOL="$6"; OUTPUT_PATH="$7"; INPUT_PATH="$8"

# System molecules
molecules=("$HOST" "$LIGAND")

cd "${OUTPUT_PATH}"|| exit 1
#echo "$PWD"

# create directories 
if [ -d "$MAIN_DIRECTORY" ]; then
    echo "'$MAIN_DIRECTORY' directory already exists."
else
    mkdir "$MAIN_DIRECTORY"
    echo "'$MAIN_DIRECTORY' directory created."
fi

cd "${MAIN_DIRECTORY}"

# create directory for every walker
if [ -d "$DIR_NAME" ]; then
    echo "'$DIR_NAME' directory already exists."
else
    mkdir "$DIR_NAME"
    echo "'$DIR_NAME' directory created."
fi


cd "${DIR_NAME}"

# introduce molecules in the center of a cubic box with ~ 7400 water molecules
gmx editconf -f "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}.gro" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c 
gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}.gro" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c
gmx editconf -f "${molecules[1]}_temp.pdb" -o "${molecules[1]}_box.pdb" -translate ${x} 0 0  # translate ligand x nm from the center on the x axis

input="merged"
output="cleaned_merged"

# merge the two molecules
cat "${molecules[0]}_box.pdb" "${molecules[1]}_box.pdb" > "${input}.pdb"

echo ">>> Files merged"
# clean merged file
awk '
    /ENDMDL/ { skip = 1; next }
    skip && (/^ATOM/ || /^HETATM/) { skip = 0 }
    !skip
' "${input}.pdb" > "${output}.pdb"

echo ">>> Clean merged file saved as $output"

# copie topol.top file
cp ${INPUT_PATH}/files/${TOPOL}.top topol.top

echo ">>> topol.top file copied."

# solvate system
gmx solvate -cp cleaned_merged.pdb -cs spc216.gro -o merged_solv.gro -p topol.top 

# delete .top extra files
find . -type f -name '#*' -exec rm -f {} \;
