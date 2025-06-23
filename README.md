# Molecular Docking Simulation with Molecular Dynamics

This project automates molecular docking simulations using GROMACS,.

##  Structure

- All GROMACS processes are included in first_plumed.sh, exec_prod.sh, the prod_command from the main.py script and the run.sh files that will be generated for simulation.

- The procedure that undergoes in this project is the next:

    1. firs_plumed.sh:
        - Make output directory and subdirectories for every walker (one for every distance of the cv parameter from config.json).
        - Introduce our molecules in the center of a 6.1 nm of side length cubic box with ~ 7400 water molecules.
        - Translate the ligand in the x axis the distance we select in our config.json file (in nm).
        - Merge the .pdb of the molecules and clean it.
        - Solvate the system.
    2. main.py:
        - Change the number of water molecules so the all have the same.
        - Minimize the system with exec_prod.sh and.
        - Create and add plumed and run.sh files to directory.
        - Run production with chosen .mdp file.
        - Run simulation: "sbatch run.sh".
    3. make_analysis.py:
        - When the simulation is finished, COLVAR and PMF graphs are obtained from the simulation data.


## Usage

1. Edit the config.json
 
 - Change the route from the data directory, whole paths recommended.
 - Ligand, host, topology file are set.
 - You can change minimize and production files if you want, additional files are attached in the mdp_files directory.
 - You can also change he bias and height parameters of opes from the plumed file.
 


2. Run the main.py script with

```bash
python main.py
```


## Bibliography

 - Michele Invernizzi and Michele Parrinello. Rethinking metadynamics: From bias potentials to probability distributions. The Journal of Physical Chemistry Letters, 11(7):2731–2736, 2020. (OPES)
 - A. Laio and M. Parrinello. Escaping free energy minima. Proc. Natl. Acad. Sci. USA, 99:12562–12566, 2002. (METADYNAMICS)
 - A Barducci, G Bussi, and M Parrinello. Well-tempered metadynamics: A smoothly converging and tunable free-energy method. Phys. Rev. Lett., 100(2):020603, Jan 2008.