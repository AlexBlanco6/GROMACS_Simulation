#!/bin/bash

#load GROMACS and PLUMED
module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

#Choose host Choose ligand Choose main directory name subdirectory for each walker distance translation   Method Topology file
HOST="$1"; LIGAND="$2"; MAIN_DIRECTORY="$3"; DIR_NAME="$4"; x="$5"; TOPOL="$6"; OUTPUT_PATH="$7"; INPUT_PATH="$8"; ORIENTATION="$9"; DIRECTION="${10}"; HOST_EXT="${11}"; LIGAND_EXT="${12}"


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
if [ "$ORIENTATION" -eq 1 ]; then

    if [ "$DIRECTION" == "up" ]; then
        gmx editconf -f "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${HOST_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${LIGAND_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c
    else
        gmx editconf -f "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${HOST_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${LIGAND_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c -rotate 0 0 180
    fi
    gmx editconf -f "${molecules[1]}_temp.pdb" -o "${molecules[1]}_box.pdb" -translate ${x} 0 0 # translate ligand x nm from the center on the x axis

elif [ "$ORIENTATION" -eq 2 ]; then

    if [ "$DIRECTION" == "up" ]; then
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${HOST_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c -rotate 50 0 0
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${LIGAND_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c -rotate 0 0 123
    else
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${HOST_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c -rotate 0 180 0
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${LIGAND_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c -rotate 0 0 123
    fi
    z=$(awk -v val="$x" 'BEGIN {print val/2}')
    gmx editconf -f "${molecules[1]}_temp.pdb" -o "${molecules[1]}_box.pdb" -translate ${x} 0 ${z}  # translate ligand x nm from the center

elif [ "$ORIENTATION" -eq 3 ]; then

    if [ "$DIRECTION" == "up" ]; then
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${HOST_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c -rotate 90 50 30
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${LIGAND_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c -rotate 0 0 -123
    else
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[1]}/${molecules[1]}${HOST_EXT}" -o "${molecules[1]}_temp.pdb" -bt cubic -box 6.1 -c -rotate 0 180 0
        gmx editconf -f  "${INPUT_PATH}/input/${molecules[0]}/${molecules[0]}${LIGAND_EXT}" -o "${molecules[0]}_box.pdb" -bt cubic -box 6.1 -c -rotate 0 0 -123
    fi
    #z=$(awk -v val="$x" 'BEGIN {print val/2}')
    gmx editconf -f "${molecules[1]}_temp.pdb" -o "${molecules[1]}_box.pdb" -translate ${x} 0 -${x}  # translate ligand x nm from the center 
fi

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

# copy topol.top file
cp ${INPUT_PATH}/files/${TOPOL}.top topol.top

echo ">>> topol.top file copied."

# solvate system
gmx solvate -cp cleaned_merged.pdb -cs tip4p.gro -o merged_solv.gro -p topol.top 

# solvate system  for ROC
# gmx solvate -cp cleaned_merged.pdb -cs spc216.gro -o merged_solv2.gro -p topol.top 

# # add ions to neutralize system
# gmx grompp -f "${INPUT_PATH}/mdp_files/ions.mdp" -c merged_solv2.gro -p topol.top -o ions.tpr -maxwarn 1

# echo -e "5" | gmx genion -s ions.tpr -o merged_solv.gro -p topol.top -pname NA -nname CL -neutral

# delete .top extra files
#find . -type f -name '#*' -exec rm -f {} \;
