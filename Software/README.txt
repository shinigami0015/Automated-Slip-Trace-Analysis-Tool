ASTA Tool — Slip Trace & Schmid Factor Analysis
==============================================
Desktop UI Wrapper for MATLAB EBSD Analysis Pipeline
Version 1.1.0


PREREQUISITES
─────────────────────────────────────────────────────────────────────────────

1. MATLAB (R2021a or later)
   Download from: https://www.mathworks.com/products/matlab.html

2. MTEX Toolbox for MATLAB
   Download from: https://mtex-toolbox.github.io/
   Install by running startup_mtex in MATLAB at least once.

3. MATLAB Engine API for Python
   This must be installed manually from your MATLAB installation directory.

   Steps (Windows):
   a) Open a Command Prompt as Administrator
   b) Navigate to:
        cd "C:\Program Files\MATLAB\R2023b\extern\engines\python"
      (Replace R2023b with your actual MATLAB version)
   c) Install:
        python setup.py install

   Steps (Linux/macOS):
      cd /usr/local/MATLAB/R2023b/extern/engines/python
      python setup.py install

   Note: matlab.engine is NOT available on PyPI — do not attempt pip install.

4. Python 3.9 or later
   Download from: https://www.python.org/

5. PyQt6
   pip install PyQt6


RUNNING THE APP
─────────────────────────────────────────────────────────────────────────────

  python main.py

Or if you have the packaged .exe:

  ASTA Tool.exe


USAGE
─────────────────────────────────────────────────────────────────────────────

Note before proceeding - The current methodology assumes that the phase numbering in .ctf scan files is as follows - (unindexed-0, BCC-1, HCP-2) In case this is not being followed, use modifyctf.m MATLAB script to modify the phase numbering of your .ctf scan file.

1. Launch ASTA Tool.

2. Scripts Folder:
   You can leave this box COMPLETELY EMPTY to use the bundled internal scripts.
   Alternatively, browse to the folder containing your .m files if you want to use custom scripts:
   - run_analysis.m
   - EBSD_processing.m
   - slip_trace.m
   - activated_slips.m
   - slip_systems.m
   - computeSchmidFactors.m
   - slipsystemdist.m
   - cosTheta.m
   - angle_with_horiz.m
   - match_slip_label.m
   - modifyctf.m
   - lustermorris.m
   - EBSD_crystal_orientation_image.m

3. Input Folder:
   Browse to the folder containing your .ctf EBSD data files.

4. Output Folder:
   Browse to (or create) the folder where all PNGs and CSVs will be saved.

5. Parameters:
   - Loading Direction: X, Y, or Z
   - c/a Ratio:        default 1.5930 for Zr (edit as needed)
   - Crystal System:   HCP + BCC / HCP only / BCC only

6. Click "▶ Run Analysis".
   The MATLAB engine will start (this takes 30–60 seconds on first run).
   Progress and console output will appear in the Console Log panel.

7. When complete, thumbnails of all generated PNG files appear in the
   Generated Outputs panel. Click any thumbnail to open full size.

Important Note - The reconstructed EBSD scans with grain numbering will need to be rotated by 180 degrees to match the input EBSD scan.

8. Click "📂 Open Output Folder" to browse all generated files.


OUTPUT FILES
─────────────────────────────────────────────────────────────────────────────

For each .ctf file in the input folder, the following are generated:

  <sampleName>_EBSD_Map.png
  <sampleName>_Alpha_SlipTraces.png
  <sampleName>_Beta_SlipTraces.png
  <sampleName>_Alpha_GrainID_Map.png
  <sampleName>_Beta_GrainID_Map.png
  <sampleName>_Alpha_IPDF.png
  <sampleName>_Beta_IPDF.png
  <sampleName>_Alpha_IPF_Key.png
  <sampleName>_Beta_IPF_Key.png
  <sampleName>_Alpha_Grain_Slip_Data.csv
  <sampleName>_Beta_Grain_Slip_Data.csv
  Combined_SlipSystem_vs_Grains_AlphaBeta.png

Important Note - The reconstructed EBSD scans with grain numbering will need to be rotated by 180 degrees to match the input EBSD scan.

DEVELOPER NOTES
─────────────────────────────────────────────────────────────────────────────

- The app injects inputDir, outputBaseDir, loadDirChoice, ca_ratio, and
  crystalSystemMode into the MATLAB workspace BEFORE running any script.
  Do NOT hardcode these paths in run_analysis.m — the injection overrides them.

- The MATLAB engine is run in a background QThread so the UI remains
  responsive during analysis.

- To package as .exe:
    pip install pyinstaller
    pyinstaller ASTA.spec


PACKAGING (for distribution)
─────────────────────────────────────────────────────────────────────────────

  cd "ASTA Tool"
  pip install -r requirements.txt
  pyinstaller ASTA.spec

  The distributable will be in:  dist/ASTA Tool/


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

"MATLAB Engine API not found"
  → Follow step 3 in Prerequisites above.

"startup_mtex failed / MTEX not found"
  → Ensure MTEX is installed in MATLAB. The UI will pop up a window asking you to 
    select your MTEX installation folder if it cannot find it automatically.

"No .ctf files found"
  → Ensure the input folder contains at least one file ending in .ctf

Analysis window freezes
  → This should not happen (worker runs on background thread). If it does,
    click Abort and re-run.


CONTACT
─────────────────────────────────────────────────────────────────────────────

IISc Materials Science Lab
Built with ASTA Tool v1.1 — PyQt6 + MATLAB Engine API
