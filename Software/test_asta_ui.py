import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add Software directory to path
software_dir = r"C:\Users\Parardha\Downloads\Automated Slip-Trace Analysis (ASTA) Tool\Software"
sys.path.insert(0, software_dir)


from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Set up test directories
input_dir = r"C:\Users\Parardha\Downloads\STARCRYST_REPO\STARCRYST REPO\STARTCRYST SOFTWARE v1.0\Software Files\Input files"
output_dir = r"C:\Users\Parardha\Downloads\STARCRYST_REPO_OUTPUT"
os.makedirs(output_dir, exist_ok=True)

# Step 1: Set paths in the UI
window.scripts_picker.path_edit.setText(software_dir)
window.input_picker.path_edit.setText(input_dir)
window.output_picker.path_edit.setText(output_dir)

# Step 2: Take screenshot before running
window.grab().save(os.path.join(output_dir, "ui_before.png"))

# Step 3: Trigger the analysis
window._on_run()

def check_finished():
    if not window._worker:
        # Worker finished
        window.grab().save(os.path.join(output_dir, "ui_after.png"))
        
        # Save console output
        with open(os.path.join(output_dir, "console.txt"), "w", encoding="utf-8") as f:
            f.write(window._console.toPlainText())
            
        print("Analysis completed successfully.")
        QApplication.quit()
    else:
        QTimer.singleShot(1000, check_finished)

QTimer.singleShot(2000, check_finished)
app.exec()
