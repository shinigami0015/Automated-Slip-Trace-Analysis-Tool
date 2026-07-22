import sys
import os
import io

matlab_extern_bin = r'C:\Program Files\MATLAB\R2023a\extern\bin\win64'
if matlab_extern_bin not in sys.path:
    sys.path.insert(0, matlab_extern_bin)

import matlab.engine

print('Starting MATLAB engine...')
eng = matlab.engine.start_matlab()

scripts_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2'
input_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2'
output_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2\Output'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print('Injecting parameters...')
eng.workspace['inputDir'] = input_folder
eng.workspace['outputBaseDir'] = output_folder
eng.workspace['loadDirChoice'] = 'X'
eng.workspace['ca_ratio'] = 1.593
eng.workspace['crystalSystemMode'] = 0.0

print('Adding scripts to path...')
eng.addpath(scripts_folder, nargout=0)

out = io.StringIO()
err = io.StringIO()

print('Running startup_mtex...')
try:
    eng.eval('startup_mtex', nargout=0, stdout=out, stderr=err)
    print(out.getvalue())
except Exception as e:
    print('Failed startup_mtex:', e, err.getvalue())

print('Re-injecting parameters...')
eng.workspace['inputDir'] = input_folder
eng.workspace['outputBaseDir'] = output_folder
eng.workspace['loadDirChoice'] = 'X'
eng.workspace['ca_ratio'] = 1.593
eng.workspace['crystalSystemMode'] = 0.0

print('Running main.m / run_analysis.m...')
try:
    if os.path.exists(os.path.join(scripts_folder, 'run_analysis.m')):
        eng.eval('run_analysis', nargout=0, stdout=out, stderr=err)
    else:
        eng.eval(f"run('{os.path.join(scripts_folder, 'main.m').replace(chr(92), '/')}')", nargout=0, stdout=out, stderr=err)
    print(out.getvalue())
except Exception as e:
    print('Failed analysis:', e, err.getvalue())

eng.quit()
print('Done!')
