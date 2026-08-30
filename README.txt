================================================================================
  ASTA Tool -- Automated Slip-Trace Analysis Tool
  Version 1.1 | Extreme Environment Materials Group (EEMG), IISc Bangalore
================================================================================

ASTA Tool is a desktop application for automated crystallographic slip trace
identification, Schmid factor mapping, and deformation compatibility analysis
in dual-phase (a-HCP / b-BCC) metallic alloys using EBSD (.ctf) data.

ASTA Tool will always be free. Please cite the following article if you use
this tool in your work:

  Chandraker et al., Plasticity and damage initiation in textured Zr-2.5%Nb
  pressure tube material: A slip trace analysis-based study,
  Materials Science and Engineering: A, 2026.

--------------------------------------------------------------------------------
PREREQUISITES
--------------------------------------------------------------------------------

Before running ASTA Tool, ensure the following are installed:

1. MATLAB (R2021a or later)
   - Download from: https://www.mathworks.com

2. MTEX Toolbox (v5.x or later)
   - Download from: https://mtex-toolbox.github.io/
   - After installing, run startup_mtex in MATLAB at least once.

3. MATLAB Engine API for Python
   - Open Command Prompt as Administrator and run:
       cd "C:\Program Files\MATLAB\<your_version>\extern\engines\python"
       python setup.py install
   Replace <your_version> with your installed MATLAB version (e.g. R2023b).

4. Python (3.9 or later) -- only needed if running from source (main.py)
   - Download from: https://www.python.org

--------------------------------------------------------------------------------
QUICK START (Standalone .exe -- Recommended)
--------------------------------------------------------------------------------

1. Unzip "ASTA_Tool_Final_Release.zip" to any folder on your PC.

2. Open the extracted folder and double-click:
       ASTA_Application\ASTA Tool.exe

3. The tool will launch with a loading screen. Click "Proceed".

4. In the main window:
   - Scripts Folder : Select the folder with the .m script files
                      (or leave EMPTY -- bundled scripts will be used).
   - Input Folder   : Select the folder containing your .ctf EBSD files.
   - Output Folder  : Select where results (PNGs, CSVs) should be saved.
   - Loading Dir    : Choose X, Y, or Z loading direction.
   - c/a Ratio      : Set the axial ratio (e.g. 1.5930 for Zirconium).
   - Crystal Mode   : Choose Dual-phase, HCP-only, or BCC-only.

5. Click "Run Analysis" and monitor the real-time log.

--------------------------------------------------------------------------------
RUNNING FROM SOURCE (Advanced Users)
--------------------------------------------------------------------------------

1. Install dependencies:
       pip install PyQt6

2. Navigate to the Software folder and run:
       python main.py

--------------------------------------------------------------------------------
SCRIPTS FOLDER NOTE
--------------------------------------------------------------------------------

If you leave the "Scripts Folder" field EMPTY in the UI, ASTA Tool will
automatically use the bundled .m scripts inside the application package.
You only need to point to a custom scripts folder if you have modified them.

--------------------------------------------------------------------------------
REPOSITORY STRUCTURE
--------------------------------------------------------------------------------

  Code scripts/               -- All MATLAB .m analysis scripts
  Sample input files/         -- Sample .ctf EBSD input data
  Sample output files/        -- Example output maps, CSVs and figures
  Software/                   -- Python PyQt6 source code + ASTA_Application exe
  matlab_engine_install/      -- MATLAB Engine API for Python installer packages
  ASTA_Tool_Final_Release.zip -- Pre-built standalone Windows executable

--------------------------------------------------------------------------------
AUTHORS & CREDITS
--------------------------------------------------------------------------------

  Core Algorithms & Numerical Implementation : Dhiraj Kori
  User Interface & Application Architecture  : Parardha Dhar
  Code Script and UI Testing                 : Abhinav Chandraker

  Extreme Environment Materials Group (EEMG)
  Indian Institute of Science (IISc), Bangalore

--------------------------------------------------------------------------------
LICENSE
--------------------------------------------------------------------------------

This project is licensed under the GNU General Public License v3.0 (GPLv3).
See the LICENSE file for full details.

================================================================================
