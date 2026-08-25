"""
ASTA Tool - MATLAB Engine Worker
Runs the MATLAB analysis pipeline in a background QThread.
"""

import io
import sys
import os
import traceback
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


class MatlabOutputStream(io.StringIO):
    """Redirects MATLAB stdout into Qt signals line-by-line."""

    def __init__(self, signal):
        super().__init__()
        self._signal = signal
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line:
                self._signal.emit(line)
        return len(text)

    def flush(self):
        if self._buffer.strip():
            self._signal.emit(self._buffer)
            self._buffer = ""


class MatlabWorker(QThread):
    """
    Background worker that:
    1. Starts MATLAB engine
    2. Injects workspace variables
    3. Adds the scripts folder to the MATLAB path
    4. Calls startup_mtex → run_analysis (main.m logic)
    5. Reports progress via Qt signals
    """

    # Signals ──────────────────────────────────────────────────────────────────
    log_line       = pyqtSignal(str)          # One line of console output
    status_changed = pyqtSignal(str)          # Status badge text
    finished_ok    = pyqtSignal()             # Analysis completed
    finished_err   = pyqtSignal(str)          # Analysis failed – carries message
    progress       = pyqtSignal(int)          # 0-100 progress (best-effort)

    def __init__(
        self,
        scripts_folder: str,
        input_folder: str,
        output_folder: str,
        loading_direction: str,
        ca_ratio: float,
        crystal_system: str,
        parent=None,
    ):
        super().__init__(parent)
        self.scripts_folder    = scripts_folder
        self.input_folder      = input_folder
        self.output_folder     = output_folder
        self.loading_direction = loading_direction
        self.ca_ratio          = ca_ratio
        self.crystal_system    = crystal_system
        self._abort            = False
        self._eng              = None

    # ── Public API ─────────────────────────────────────────────────────────────
    def abort(self):
        """Request a graceful abort."""
        self._abort = True
        if self._eng is not None:
            try:
                self._eng.quit()
            except Exception:
                pass

    # ── Internal helpers ───────────────────────────────────────────────────────
    def _emit(self, msg: str):
        self.log_line.emit(msg)

    def _check_abort(self):
        if self._abort:
            raise InterruptedError("Analysis aborted by user.")

    # ── Main thread body ───────────────────────────────────────────────────────
    def run(self):
        try:
            # ── 1. Import matlab.engine ────────────────────────────────────────
            self.status_changed.emit("MATLAB Starting...")
            self._emit("⚙  Importing MATLAB Engine API…")
            try:
                import matlab.engine  # noqa: F401
            except ImportError:
                self.finished_err.emit(
                    "MATLAB Engine API for Python is not installed.\n\n"
                    "Please install it from your MATLAB installation:\n"
                    "  cd <matlabroot>/extern/engines/python\n"
                    "  python setup.py install"
                )
                return

            self._check_abort()

            # ── 2. Start MATLAB engine ─────────────────────────────────────────
            self._emit("⚙  Starting MATLAB engine (this may take 30–60 seconds)…")
            stdout_stream = MatlabOutputStream(self.log_line)
            stderr_stream = MatlabOutputStream(self.log_line)

            self._eng = matlab.engine.start_matlab()
            self.progress.emit(10)
            self._emit("✔  MATLAB engine started.")
            self._check_abort()

            # ── 3. Add scripts folder to MATLAB path ───────────────────────────
            self._emit(f"⚙  Adding scripts folder to MATLAB path:\n   {self.scripts_folder}")
            self._eng.addpath(self.scripts_folder, nargout=0, stdout=stdout_stream, stderr=stderr_stream)
            self.progress.emit(15)

            # ── 4. Inject workspace variables ─────────────────────────────────
            self._emit("⚙  Injecting analysis parameters into MATLAB workspace…")
            self._eng.workspace["inputDir"]      = self.input_folder
            self._eng.workspace["outputBaseDir"] = self.output_folder
            self._eng.workspace["loadDirChoice"] = self.loading_direction
            self._eng.workspace["ca_ratio"]      = float(self.ca_ratio)
            self._eng.workspace["crystalSystem"] = self.crystal_system

            # Derive a numeric selector for the crystal system
            cs_map = {
                "HCP + BCC": 0,
                "HCP only":  1,
                "BCC only":  2,
            }
            self._eng.workspace["crystalSystemMode"] = float(cs_map.get(self.crystal_system, 0))
            self._emit(f"   inputDir      → {self.input_folder}")
            self._emit(f"   outputBaseDir → {self.output_folder}")
            self._emit(f"   loadDirChoice → {self.loading_direction}")
            self._emit(f"   ca_ratio      → {self.ca_ratio}")
            self._emit(f"   crystalSystem → {self.crystal_system}")
            self.progress.emit(20)
            self._check_abort()

            # ── 5. startup_mtex ────────────────────────────────────────────────
            self.status_changed.emit("Running...")
            self._emit("\n⚙  Running startup_mtex…")
            try:
                mtex_cmd = "try, startup_mtex; catch, addpath('D:\\Abhinav Chandraker (Pls do not delete)\\Zr alloy\\Zr slip trace\\codes\\MTEX\\mtex-6.0.0\\mtex-6.0.0'); startup_mtex; end"
                self._eng.eval(mtex_cmd, nargout=0, stdout=stdout_stream, stderr=stderr_stream)
            except Exception as e:
                raise RuntimeError(
                    "startup_mtex failed — MTEX toolbox may not be installed in MATLAB.\n\n"
                    "Please install MTEX from: https://mtex-toolbox.github.io/\n\n"
                    f"MATLAB error: {e}"
                ) from e
            self.progress.emit(30)
            self._emit("✔  MTEX initialised successfully.")
            self._check_abort()

            # ── 6. Clear existing workspace vars that main.m would set ─────────
            self._emit("\n⚙  Re-injecting variables (post startup_mtex reset)…")
            self._eng.workspace["inputDir"]          = self.input_folder
            self._eng.workspace["outputBaseDir"]     = self.output_folder
            self._eng.workspace["loadDirChoice"]     = self.loading_direction
            self._eng.workspace["ca_ratio"]          = float(self.ca_ratio)
            self._eng.workspace["crystalSystemMode"] = float(cs_map.get(self.crystal_system, 0))

            # ── 7. Run main analysis script ────────────────────────────────────
            self._emit("\n⚙  Executing run_analysis (main.m pipeline)…")
            self._emit("   Note: MATLAB figure windows may appear — do not close them manually.\n")

            # Check if run_analysis.m exists, otherwise fall back to main.m
            run_analysis_path = os.path.join(self.scripts_folder, "run_analysis.m")
            main_path         = os.path.join(self.scripts_folder, "main.m")

            if os.path.exists(run_analysis_path):
                cmd = "run_analysis"
                self._emit("   Using run_analysis.m")
            elif os.path.exists(main_path):
                # main.m calls startup_mtex then 'clc; clear; close all;'
                # which wipes the injected workspace variables.
                # Best approach: warn the user and still attempt to run.
                safe_path = main_path.replace("\\", "/")
                cmd = f"run('{safe_path}')"
                self._emit("")
                self._emit("   [WARNING] run_analysis.m not found.")
                self._emit("   Falling back to main.m — but main.m calls 'clear',")
                self._emit("   which wipes the injected inputDir/outputBaseDir.")
                self._emit("   SOLUTION: Copy run_analysis.m from the ASTA Tool")
                self._emit("   folder to your scripts folder for full path injection.")
                self._emit(f"   Attempting: run('{safe_path}')")
            else:
                raise FileNotFoundError(
                    "Neither run_analysis.m nor main.m was found in the scripts folder.\n\n"
                    f"Scripts folder: {self.scripts_folder}\n\n"
                    "Please ensure your .m files are in the selected Scripts Folder."
                )

            self._eng.eval(cmd, nargout=0, stdout=stdout_stream, stderr=stderr_stream)
            self.progress.emit(95)
            self._check_abort()

            # ── 8. Flush remaining output ──────────────────────────────────────
            stdout_stream.flush()
            stderr_stream.flush()

            self._emit("\n✔  Analysis complete.")
            self.progress.emit(100)
            self.status_changed.emit("Done")
            self.finished_ok.emit()

        except InterruptedError as e:
            self.status_changed.emit("Ready")
            self._emit(f"\n⚠  {e}")
            self.finished_err.emit(str(e))

        except Exception as e:
            tb = traceback.format_exc()
            self._emit(f"\n✖  ERROR:\n{tb}")
            self.status_changed.emit("Error")
            self.finished_err.emit(str(e))

        finally:
            if self._eng is not None:
                try:
                    self._eng.quit()
                    self._emit("⚙  MATLAB engine shut down.")
                except Exception:
                    pass
                self._eng = None
