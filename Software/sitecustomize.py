# -*- coding: utf-8 -*-
"""
sitecustomize.py  –  auto-executed by Python's site module at interpreter startup,
before any frozen application code.

ROOT CAUSE OF THE CRASH
-----------------------
The frozen STRCRYST.exe embeds matlab/__init__.py (compiled for MATLAB R2023a)
inside its PYZ archive.  That PYZ version takes priority over every loose .py
file in _internal/, so editing intro_sequence.py etc. has no effect.

The original frozen _check_matlab_engine only catches ImportError, not
RuntimeError.  matlab/__init__.py (line 213) raises RuntimeError when:
  (a) _arch.txt has fewer than 2 lines, OR
  (b) any path listed in _arch.txt does not exist as a directory, OR
  (c) the MATLAB DLLs needed by the bundled .pyd cannot be loaded.

FIX STRATEGY
------------
1. If MATLAB R2023a is installed at the standard location, let the real engine
   work – just ensure DLL directories are on PATH first.
2. Otherwise, inject a sys.meta_path importer that intercepts 'import matlab'
   and 'import matlab.engine', returning a lightweight stub.  The frozen
   matlab/__init__.py is NEVER executed, so no RuntimeError is ever raised.
   The stub causes _check_matlab_engine to return True (harmless false-positive);
   when the user actually clicks Run Analysis, MatlabWorker.run() tries
   matlab.engine.start_matlab(), the stub raises ImportError, which IS caught.
"""

import sys
import os
import glob as _glob
import types as _types


# ─── Step 1 : locate the frozen bundle's _arch.txt ──────────────────────────
def _get_meipass():
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass is None:
        # Non-frozen (dev): two levels up from sitecustomize.py
        meipass = os.path.dirname(os.path.abspath(__file__))
    return meipass


def _patch_arch_txt(arch_txt, matlab_root):
    """Rewrite _arch.txt with the paths for the given MATLAB installation."""
    bin_dir    = os.path.join(matlab_root, 'bin',    'win64')
    extern_bin = os.path.join(matlab_root, 'extern', 'bin', 'win64')
    pyd_dir    = os.path.join(os.path.dirname(arch_txt), 'win64')

    lines = ['win64\n', bin_dir + '\n', pyd_dir + '\n']
    if os.path.isdir(extern_bin):
        lines.append(extern_bin + '\n')
    with open(arch_txt, 'w', encoding='utf-8') as fh:
        fh.writelines(lines)

    # Put MATLAB DLLs on PATH so the bundled .pyd can resolve them.
    path_env = os.environ.get('PATH', '')
    for d in [extern_bin, bin_dir]:
        if os.path.isdir(d) and d not in path_env:
            os.environ['PATH'] = d + os.pathsep + os.environ['PATH']


# ─── Step 2 : the stub importer ─────────────────────────────────────────────
class _MatlabStubImporter:
    """
    sys.meta_path hook that intercepts 'import matlab' / 'import matlab.engine'
    and returns safe stub modules.  This prevents the frozen matlab/__init__.py
    from ever running and avoids RuntimeError on machines without MATLAB R2023a.
    """

    _NAMES = frozenset(['matlab', 'matlab.engine'])

    # Python 3.4+ importlib protocol
    def find_module(self, fullname, path=None):      # legacy hook, still called
        return self if fullname in self._NAMES else None

    def find_spec(self, fullname, path, target=None): # modern hook
        if fullname not in self._NAMES:
            return None
        import importlib.util
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return None  # use default semantics

    def exec_module(self, module):
        name = module.__name__
        if name == 'matlab':
            module.__path__    = []
            module.__package__ = 'matlab'
        elif name == 'matlab.engine':
            module.__package__ = 'matlab'

            def _not_installed(*args, **kwargs):
                raise ImportError(
                    "MATLAB R2023a is not installed (or its Python Engine API "
                    "is not set up).  The ASTA Tool requires MATLAB R2023a plus "
                    "the MATLAB Engine API for Python to run the analysis."
                )
            module.start_matlab = _not_installed

    def load_module(self, fullname):                  # legacy fallback
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = _types.ModuleType(fullname)
        self.exec_module(mod)
        sys.modules[fullname] = mod
        return mod


# ─── Step 3 : main logic ─────────────────────────────────────────────────────
def _configure():
    try:
        meipass  = _get_meipass()
        arch_txt = os.path.join(meipass, 'matlab', 'engine', '_arch.txt')

        # Check for MATLAB R2023a at the standard Windows location.
        r2023a = r'C:\Program Files\MATLAB\R2023a'
        if os.path.isdir(os.path.join(r2023a, 'bin', 'win64')):
            # Real R2023a found – patch _arch.txt so the frozen engine works.
            if os.path.exists(arch_txt):
                try:
                    _patch_arch_txt(arch_txt, r2023a)
                except Exception:
                    pass
            # Do NOT install the stub; let the real matlab/__init__.py run.
            return

        # MATLAB R2023a not found (machine has a different version or none).
        # Insert our stub importer FIRST in sys.meta_path so it intercepts
        # 'import matlab' before the frozen PYZ importer can reach
        # matlab/__init__.py.
        if not any(isinstance(m, _MatlabStubImporter) for m in sys.meta_path):
            sys.meta_path.insert(0, _MatlabStubImporter())

        # Also make _arch.txt safe as a belt-and-suspenders measure, in case
        # the importer hook is somehow bypassed.  C:\Windows\System32 always
        # exists so os.add_dll_directory() won't raise; the .pyd will then fail
        # with ImportError (missing MATLAB DLLs) which the original frozen code
        # DOES catch.
        if os.path.exists(arch_txt):
            try:
                with open(arch_txt, 'w', encoding='utf-8') as fh:
                    fh.write('win64\n')
                    fh.write(r'C:\Windows\System32' + '\n')
            except Exception:
                pass

    except Exception:
        # This hook must NEVER crash the application.
        pass


_configure()
