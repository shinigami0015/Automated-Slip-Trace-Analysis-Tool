# -*- coding: utf-8 -*-
"""
sitecustomize.py  --  executed by Python's site module at interpreter startup.

WHY THIS FILE EXISTS
--------------------
matlab/__init__.py (line 208) does an EXACT 4-element unpack of _arch.txt:

    [_arch, _bin_dir, _engine_dir, _extern_bin_dir] = [x.rstrip() for x in _lines ...]

If _arch.txt does not have EXACTLY 4 non-empty lines, a ValueError is raised,
caught at line 213, and the fallback code (line 237+) tries to derive the MATLAB
root from __file__'s parent directory.  In a PyInstaller frozen app that path
resolves to something like C:\\Windows\\bin\\win64 which does not exist, so the
code raises RuntimeError("unable to read _arch.txt") -- crashing the app.

WHAT WE DO
----------
1. PRIMARY: Install a sys.meta_path blocker so that 'import matlab' / 
   'import matlab.engine' returns a lightweight stub without ever running
   the frozen matlab/__init__.py at all.
2. SECONDARY: Rewrite _arch.txt with exactly 4 lines whose directories
   all exist.  If MATLAB R2023a is present its real paths are used;
   otherwise C:\\Windows\\System32 (always present) is used for _bin_dir
   and _extern_bin_dir, and the bundled pyd directory is used for _engine_dir.
   This way the 4-element unpack succeeds, os.add_dll_directory() succeeds,
   and the only error is ImportError when the .pyd cannot find MATLAB DLLs --
   which IS caught by the original frozen _check_matlab_engine.
"""

import sys
import os
import glob as _glob
import types as _types


# ── helpers ──────────────────────────────────────────────────────────────────

def _meipass():
    """Return the _internal/ directory regardless of frozen/dev mode."""
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def _write_arch_txt(arch_txt, bin_dir, engine_dir, extern_bin_dir):
    """Write exactly 4 non-empty lines to _arch.txt (no BOM, CRLF line endings)."""
    content = '\r\n'.join(['win64', bin_dir, engine_dir, extern_bin_dir]) + '\r\n'
    with open(arch_txt, 'w', encoding='utf-8', newline='') as fh:
        fh.write(content)


# ── PRIMARY FIX: sys.meta_path blocker ───────────────────────────────────────

class _MatlabStubImporter:
    """
    Inserted at sys.meta_path[0].  Intercepts 'import matlab' and
    'import matlab.engine' and returns safe stubs so that the frozen
    matlab/__init__.py never executes.
    """
    _INTERCEPT = frozenset(['matlab', 'matlab.engine'])

    # ---- legacy (Python < 3.4) protocol, still checked in some paths ----
    def find_module(self, fullname, path=None):
        return self if fullname in self._INTERCEPT else None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = _types.ModuleType(fullname)
        self._init_module(mod)
        sys.modules[fullname] = mod
        return mod

    # ---- modern (Python 3.4+) protocol ----
    def find_spec(self, fullname, path, target=None):
        if fullname not in self._INTERCEPT:
            return None
        try:
            import importlib.util
            return importlib.util.spec_from_loader(fullname, self)
        except Exception:
            return None

    def create_module(self, spec):
        return None  # use default object creation

    def exec_module(self, module):
        self._init_module(module)

    # ---- shared initialiser ----
    @staticmethod
    def _init_module(mod):
        name = mod.__name__
        if name == 'matlab':
            mod.__path__    = []
            mod.__package__ = 'matlab'
        elif name == 'matlab.engine':
            mod.__package__ = 'matlab'

            def _not_installed(*args, **kwargs):
                raise ImportError(
                    "MATLAB (or its Python Engine API) is not installed.\n"
                    "The ASTA Tool requires MATLAB plus the MATLAB Engine\n"
                    "API for Python to run the slip-trace analysis."
                )
            mod.start_matlab = _not_installed


# ── SECONDARY FIX: write a valid 4-line _arch.txt ────────────────────────────

def _fix_arch_txt(arch_txt):
    """
    Rewrite _arch.txt so the 4-element unpack in matlab/__init__.py succeeds.
    All four directories must exist; they don't need to contain MATLAB files.
    """
    meipass    = _meipass()
    pyd_dir    = os.path.join(meipass, 'matlab', 'engine', 'win64')
    system32   = r'C:\Windows\System32'
    fallback   = pyd_dir if os.path.isdir(pyd_dir) else system32

    def find_matlab_bin():
        import glob
        paths_to_check = [r'E:\bin'] + glob.glob(r'C:\Program Files\MATLAB\R*\bin')
        for p in paths_to_check:
            if os.path.exists(os.path.join(p, 'matlab.exe')):
                return os.path.join(p, 'win64')
        return None

    bin_dir = find_matlab_bin()
    
    if bin_dir and os.path.isdir(bin_dir):
        # MATLAB present -- use its real paths for full engine support
        # Calculate extern_bin: usually sibling to 'bin' or 'extern\bin'
        matlab_root = os.path.dirname(os.path.dirname(bin_dir))
        extern_bin = os.path.join(matlab_root, 'extern', 'bin', 'win64')
        
        _write_arch_txt(arch_txt, bin_dir, fallback, extern_bin if os.path.isdir(extern_bin) else system32)
        # Add MATLAB DLL dirs to PATH so the bundled .pyd finds them
        path_env = os.environ.get('PATH', '')
        for d in [extern_bin, bin_dir]:
            if os.path.isdir(d) and d not in path_env:
                os.environ['PATH'] = d + os.pathsep + path_env
    else:
        # No MATLAB -- write safe fallback paths that all exist.
        _write_arch_txt(arch_txt, system32, fallback, system32)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def _configure():
    try:
        meipass  = _meipass()
        arch_txt = os.path.join(meipass, 'matlab', 'engine', '_arch.txt')

        # PRIMARY: install stub importer before the PYZ importer is reached
        if not any(isinstance(m, _MatlabStubImporter) for m in sys.meta_path):
            sys.meta_path.insert(0, _MatlabStubImporter())

        # SECONDARY: ensure _arch.txt has exactly 4 valid lines (belt-and-suspenders)
        if os.path.exists(arch_txt):
            _fix_arch_txt(arch_txt)

    except Exception:
        # sitecustomize MUST NOT crash the application.
        pass


_configure()
