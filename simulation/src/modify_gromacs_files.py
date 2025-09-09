#!/usr/bin/env python
# -*- coding: utf-8 -*-

# script for changing the number of water molecules from walkers in order to have the same in all simulations
import os
import re

def same_waters(out, dir_out_t, n, gro_file, topol_file):

    dir_out = os.path.join(out, dir_out_t)
    # find the walker with the less number of waters
    min_atoms = 100000
    file_min = None
    topol_file += ".top"
    for jj in range(n):
        try:
            file_path = os.path.join(dir_out, f"{jj}", topol_file) # open topol.top
            with open(file_path, "r") as file:
                for line in file:
                    if "SOL" in line and int(line.strip().split(" ")[-1]) < min_atoms:  # if number of waters shorter than the previous walker, update min_atoms
                        min_atoms = int(line.strip().split(" ")[-1]) 
                        file_min = jj
        except FileNotFoundError as e:
            print(f">>> TOPOL FILE NOT FOUND IN  {jj} WALKER, ALL TOPOLOGY FILES MUST HAVE THE SAME NAME")
     #################################33
    # change the number of waters of the rest topols.top to match min_atoms
    for q in range(n):
        file_path = os.path.join(dir_out, f"{q}", topol_file)
        with open(file_path, "r") as file:   # open every top file
            script = ""
            for line in file:
                if "SOL" in line and int(line.strip().split(" ")[-1]) != min_atoms: # if the number of water molecules differ from the minimum, change them
                    script += f"SOL{min_atoms:>8}" + "\n"
                    continue
                script+= line   # add rest of the lines
        
        with open(os.path.join(dir_out, f"{q}", "topol2.top"), "w") as f:
            f.write(script)
                    
    # get the NA number residue and the number of atom from the shorter merged system file
    file_path = os.path.join(dir_out, f"{file_min}", gro_file)
    lines = []
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            if i < 2:    # skip the first two rows
                continue
            line_parts = line.split()
            match = re.search(r'[A-Za-z].*', line_parts[0])  # search for residues
            if not match:
                continue  
            res = match.group()    # get residues
            if res not in ("SOL", "NA", "CL"):  # count number of host + ligand atoms
                atoms_ligand_host = int(line_parts[2])

            if res in ("NA","CL"):
                lines.append(line_parts[:2])  # get the ions 

    n_ions = len(lines)
    atoms_ligand_host += n_ions  # add the ions to get total number of not water atoms

    # create the new merged_solv_ions2.gro file where we only include the number of waters from the shorter system,
    # the NA atoms are loaded with the coordinates from the previous .gro, not from the shorter system

    num_check = min_atoms + 1#+ n_ions + 2  # min water atoms + number of ions + number of molecules (host + ligand) must be changed in further ocassion
    for i in range(n):
        file_path = os.path.join(dir_out, f"{i}", gro_file)
        script = " "
        with open(file_path, "r") as file:
            na_lines = [] 
            for j, line in enumerate(file):
                line = line.rstrip()
                if j == 0:          # keep first line
                    script += line + "\n"
                    continue
                if j == 1:     # change the number of atoms of the system in the second row
                    num_atoms = int(line)
                    if num_atoms != min_atoms:
                        line = f"{min_atoms * 4 + atoms_ligand_host}"  ### ADDED +4  MUST REVIEW
                    script += line + "\n"
                    continue

                parts = line.split()
                first_column = parts[0]

                # residue name and number
                res, number_res = None, None
                for idx, char in enumerate(first_column):
                    if char.isalpha():
                        res = first_column[idx:]
                        number_str = first_column[:idx].strip()
                        if number_str.isdigit():
                            number_res = int(number_str)
                        break

                if res == "SOL" and number_res and number_res > num_check:
                    continue                                               # avoid the extra water atoms

                if res in ("NA", "CL"): # get the ions
                    na_lines.append(line)
                    if len(na_lines) == 7:
                        for j, k in enumerate(na_lines):
                            data = k.split()
                            data[:2] = lines[j]  #  # fix the atom number of ions 
                            script += f"{data[0]:>7}{data[1]:>13}{data[2]:>8}{data[3]:>8}{data[4]:>8}\n"

                        na_lines = []  # empty the list in order not to get duplicate ions
                    continue

                script += line + "\n"  # add rest of the lines without making any changes
            
            with open(os.path.join(dir_out, f"{i}", "merged_solv_ions2.gro"), "w") as f:
                f.write(script)
    
    return min_atoms * 4 + atoms_ligand_host