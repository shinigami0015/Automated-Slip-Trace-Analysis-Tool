import sys
import os

matlab_extern_bin = r'C:\Program Files\MATLAB\R2023a\extern\bin\win64'
if matlab_extern_bin not in sys.path:
    sys.path.insert(0, matlab_extern_bin)

from PyQt6.QtWidgets import QApplication
from core.matlab_worker import MatlabWorker

def test():
    app = QApplication(sys.argv)
    
    scripts_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2'
    input_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2'
    output_folder = r'd:\Downloads\IISc Intern 2\IISc Intern 2\Output'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    worker = MatlabWorker(
        scripts_folder=scripts_folder,
        input_folder=input_folder,
        output_folder=output_folder,
        loading_direction='X',
        ca_ratio=1.593,
        crystal_system='HCP + BCC'
    )
    
    def on_log(msg):
        print(msg)
        
    def on_err(msg):
        print('ERROR:', msg)
        app.quit()
        
    def on_ok():
        print('SUCCESS!')
        app.quit()
        
    worker.log_line.connect(on_log)
    worker.finished_err.connect(on_err)
    worker.finished_ok.connect(on_ok)
    
    print('Starting worker...')
    worker.start()
    
    app.exec()

if __name__ == '__main__':
    test()
