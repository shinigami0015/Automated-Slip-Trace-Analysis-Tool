# Automated Slip-Trace Analysis (ASTA) Tool — MATLAB Scripts

This repository hosts an automated workflow for crystallographic slip trace identification, Schmid factor mapping, and deformation compatibility analysis in dual-phase ($\alpha$-HCP / $\beta$-BCC) alloys using MATLAB and the MTEX toolbox.

> **If you use this tool in your research, please cite:**
> *[article details to be added]*
>
> 🌐 GitHub: [https://github.com/parardhadhar/MTEX-Slip-Trace-Analysis](https://github.com/parardhadhar/MTEX-Slip-Trace-Analysis)

---

## 🛠️ Core Features

* **Data Cleanup:** Automatic Euler-to-spatial alignment, scanning artifact purging, and grain boundary smoothing.
* **Trace Analysis:** Direct overlay of theoretical surface slip traces on Inverse Pole Figure (IPF) maps.
* **Stress Mapping:** High-throughput calculation of maximum resolved shear stress (Schmid factors).
* **Local Compatibility:** Boundary-by-boundary computation and mapping of the geometric Luster-Morris ($m'$) parameter.
* **Aggregated Statistics:** Automated phase statistics compiling active slip family distributions across all processed files.

---

## 📁 Repository Structure

* **`main.m`** – *Master Script:* Automates loop runs, scans input folders, exports plots, and graphs aggregate stats.
* **`EBSD_processing.m`** – *Data Preparation:* Handles file import, angular corrections, grain sizing filters, and spline smoothing.
* **`match_slip_label.m`** – *Helper:* Maps table string annotations to native 3-index (BCC) or 4-index (HCP) Miller indices.
* **`lustermorris.m`** – *Compatibility Module:* Computes grain pair orientation vectors and visualizes boundary compliance maps ($m'$).

---

## 🚀 Quick Start

1. Download all repository `.m` files into a single local workspace folder.
2. Ensure **MATLAB** (R2021a or later) and the **MTEX Toolbox** are installed and added to your active path.
3. Use the **ASTA Tool UI** (see the `Software/` folder and its README) to select your script folder, input folder, and output folder, then click **Run Analysis**.

   *Alternatively, run the scripts directly from MATLAB:*
   - Open `main.m` and update your data paths:
     ```matlab
     inputDir      = 'D:\YourPath\To\Input CTF';
     outputBaseDir = 'D:\YourPath\To\Output files';
     ```
   - Run `main.m` in MATLAB.

---

## ⚙️ System Requirements

| Requirement | Minimum |
|---|---|
| MATLAB | R2021a or later |
| MTEX Toolbox | Latest stable release |
| MATLAB Engine API for Python | Matching your MATLAB version |
| Python | 3.9 or later |
| PyQt6 | Latest |

---

## 📋 About `_arch.txt` (MATLAB Version Matching)

When using the bundled ASTA Tool EXE (inside `ASTA_Application/`), a file called `_arch.txt` inside `_internal\matlab\engine\` tells the application where your MATLAB is installed. 

**ASTA Tool automatically detects and patches this file at startup**, so in most cases you do not need to do anything manually.

**Manual fix** (if auto-detection fails or MATLAB is in a non-standard location):

Open `_arch.txt` and set the correct paths, e.g., for MATLAB R2024a:
```
win64
C:\Program Files\MATLAB\R2024a\bin\win64
C:\Program Files\MATLAB\R2024a\extern\engines\python\dist\matlab\engine\win64
C:\Program Files\MATLAB\R2024a\extern\bin\win64
```

The same fix applies to `ASTA_Application_Backup\_internal\matlab\engine\_arch.txt` if you use the backup copy.

---

## 📖 Usage Instructions

Full usage instructions, including GUI walkthrough, troubleshooting, and packaging steps, are in the **README.txt** file inside the `Software/` folder.

---

## 👥 Credits

- **Extreme Environment Materials Group (EEMG)**  
  Indian Institute of Science (IISc), Bangalore
- **Parardha Dhar** – UI Developer

---

## 📜 License

ASTA Tool will always be free. Kindly cite the associated publication if using this in your work so that your colleagues may also know about this tool.
