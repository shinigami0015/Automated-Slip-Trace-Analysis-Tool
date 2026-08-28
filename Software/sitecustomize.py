# -*- coding: utf-8 -*-
"""
sitecustomize.py – auto-executed by Python at interpreter startup.

Fixes the startup crash caused by _internal/matlab/engine/_arch.txt
containing hard-coded MATLAB R2023a paths.  On machines with a different
MATLAB version (or no MATLAB) those paths do not exist, and
matlab/__init__.py raises RuntimeError at line 213, which the frozen
bytecode only catches as ImportError – crashing the app before it opens.

This file runs before any frozen application code.  It:
  1. Locates _arch.txt inside the frozen bundle.
  2. If MATLAB is installed, rewrites _arch.txt with the correct version.
  3. If MATLAB is NOT installed, empties the path list so matlab/__init__.py
     iterates over nothing and never tries os.add_dll_directory() with a
     missing path. The subsequent import attempt fails with ImportError
     (which IS caught by the original code) rather than RuntimeError (which
     is NOT).
"""

import sys
import os
import glob as _glob


def _configure_matlab_arch_txt():
    try:
        # In --onedir PyInstaller the bootloader sets sys._MEIPASS to the
        # _internal/ directory and that directory is already in sys.path when
        # sitecustomize runs.
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass is None:
            # Development / non-frozen: look two levels up from this file.
            meipass = os.path.dirname(os.path.abspath(__file__))

        arch_txt = os.path.join(meipass, 'matlab', 'engine', '_arch.txt')
        if not os.path.exists(arch_txt):
            return  # Nothing to do – matlab bundle not present.

        # ── Find the newest MATLAB installation ──────────────────────────────
        candidates = sorted(
            _glob.glob(r'C:\Program Files\MATLAB\R*'),
            reverse=True           # newest first: R2024b > R2024a > R2023b …
        )

        matlab_found = False
        for matlab_root in candidates:
            bin_dir    = os.path.join(matlab_root, 'bin',    'win64')
            extern_bin = os.path.join(matlab_root, 'extern', 'bin', 'win64')
            if not os.path.isdir(bin_dir):
                continue

            pyd_dir = os.path.join(os.path.dirname(arch_txt), 'win64')

            lines = ['win64\n', bin_dir + '\n', pyd_dir + '\n']
            if os.path.isdir(extern_bin):
                lines.append(extern_bin + '\n')

            with open(arch_txt, 'w', encoding='utf-8') as fh:
                fh.writelines(lines)

            # Also inject MATLAB DLL directories into PATH so the .pyd can
            # find its runtime dependencies at import time.
            path_env = os.environ.get('PATH', '')
            if extern_bin not in path_env:
                os.environ['PATH'] = extern_bin + os.pathsep + path_env
            if bin_dir not in path_env:
                os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']

            matlab_found = True
            break  # Patched with the best available version

        if not matlab_found:
            # No valid MATLAB installation found.  Write a minimal _arch.txt
            # that has only the architecture line and NO paths.  This means
            # matlab/__init__.py will iterate over an empty list, never call
            # os.add_dll_directory() with a non-existent path, and therefore
            # never raise RuntimeError.  The subsequent .pyd import will fail
            # with ImportError (missing DLL / module), which IS handled.
            with open(arch_txt, 'w', encoding='utf-8') as fh:
                fh.write('win64\n')

    except Exception:
        # This hook must NEVER crash the application.
        pass


_configure_matlab_arch_txt()
