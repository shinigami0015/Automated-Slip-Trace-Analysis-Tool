#Copyright 2014-2022 MathWorks, Inc.

import warnings
# We start with distutils to minimize disruptions to existing workflows. 
# If distutils no longer exists, we try setuptools.
try:
    # We suppress warnings about deprecation of distutils. We will remove
    # references to distutils before it is removed from Python.
    warnings.filterwarnings('ignore', 
        message='.*distutils package is deprecated.*', 
        category=DeprecationWarning)
    from distutils.core import setup
    from distutils.command.build_py import build_py
except:
    # We suppress warnings about "setup.py install", which we continue
    # to support, though we also support pip.
    warnings.filterwarnings('ignore', 
        message='.*Use build and pip and other standards-based tools.*')
    from setuptools import setup
    from setuptools.command.build_py import build_py
    
import os
import sys
import platform

# UPDATE_IF_PYTHON_VERSION_ADDED_OR_REMOVED : search for this string in codebase 
# when support for a Python version must be added or removed
_supported_versions = ['3.8', '3.9', '3.10']
_ver = sys.version_info
_version = '{0}.{1}'.format(_ver[0], _ver[1])
if not _version in _supported_versions:
    raise EnvironmentError('MATLAB Engine for Python supports Python version'
                           ' 3.8, 3.9, and 3.10, but your version of Python '
                           'is %s' % _version)
_dist = "dist"
_matlab_package = "matlab"
_engine_package = "engine"
_arch_filename = "_arch.txt"
_py_arch = platform.architecture()
_system = platform.system()
_py_bitness =_py_arch[0]

class BuildEngine(build_py):

    @staticmethod
    def _get_arch_from_system(system): 
        if system == 'Windows':
            return 'win64'
        elif system == 'Linux':
            return 'glnxa64'
        elif system == 'Darwin':
            # determine if ARM or Intel Mac machine
            if platform.mac_ver()[-1] == 'arm64':
                return 'maca64'
            return 'maci64'

    @staticmethod
    def _bin_dir_w_arch_exists(bin_dir, arch):
        ret = os.access(os.path.join(bin_dir, arch), os.F_OK)
        return ret

    @staticmethod
    def _find_arch(predicate):
        _bin_dir = predicate
        _arch = None
        _arch_bitness = {"glnxa64": "64bit", "maci64": "64bit",
                         "win32": "32bit", "win64": "64bit", "maca64": "64bit"}
        _arch_from_system = BuildEngine._get_arch_from_system(_system)
        if BuildEngine._bin_dir_w_arch_exists(_bin_dir, _arch_from_system):
            _arch = _arch_from_system
        if _arch is None:
            if _system == 'Darwin':
                if _arch_from_system == 'maci64':
                    _alt_arch = 'maca64'
                else:
                    _alt_arch = 'maci64'
                if BuildEngine._bin_dir_w_arch_exists(_bin_dir, _alt_arch):
                    raise EnvironmentError(f'MATLAB installation in {_bin_dir} is {_alt_arch}, but Python interpreter is {_arch_from_system}. Reinstall MATLAB or use a different Python interpreter.') 
            raise EnvironmentError('The installation of MATLAB is corrupted.  '
                                   'Please reinstall MATLAB or contact '
                                   'Technical Support for assistance.')

        if _py_bitness != _arch_bitness[_arch]:
            raise EnvironmentError('%s Python does not work with %s MATLAB. '
                                   'Please check your version of Python' %
                                   (_py_bitness, _arch_bitness[_arch]))
        return _arch

    def _generate_arch_file(self, target_dir):
        _arch_file_path = os.path.join(target_dir, _arch_filename)
        _cwd = os.getcwd()
        _parent = os.pardir # '..' for Windows and POSIX
        _bin_dir = os.path.join(_cwd, _parent, _parent, _parent, 'bin')
        _engine_dir = os.path.join(_cwd, _dist, _matlab_package, _engine_package)
        _extern_bin_dir = os.path.join(_cwd, _parent, _parent, _parent, 'extern', 'bin')
        _arch = self._find_arch(_bin_dir)
        _bin_dir = os.path.join(_bin_dir, _arch)
        _engine_dir = os.path.join(_engine_dir, _arch)
        _extern_bin_dir = os.path.join(_extern_bin_dir, _arch)
        try:
            _arch_file = open(_arch_file_path, 'w')
            _arch_file.write(_arch + os.linesep)
            _arch_file.write(_bin_dir + os.linesep)
            _arch_file.write(_engine_dir + os.linesep)
            _arch_file.write(_extern_bin_dir + os.linesep)
            _arch_file.close()
        except IOError:
            raise EnvironmentError('You do not have write permission '
                                   'in %s ' % target_dir)

    def run(self):
        build_py.run(self)
        _target_dir = os.path.join(self.build_lib, _matlab_package, _engine_package)
        self._generate_arch_file(_target_dir)


if __name__ == '__main__':

    setup(
        name="matlabengineforpython",
        version="9.14",
        description='A module to call MATLAB from Python',
        author='MathWorks',
        url='https://www.mathworks.com/',
        platforms=['Linux', 'Windows', 'macOS'],
        package_dir={'': 'dist'},
        packages=['matlab','matlab.engine'],
        cmdclass={'build_py': BuildEngine}
    )
