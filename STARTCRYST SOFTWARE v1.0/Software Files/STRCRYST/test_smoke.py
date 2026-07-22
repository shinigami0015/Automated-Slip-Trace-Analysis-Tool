# -*- coding: utf-8 -*-
"""
STRCRYST -- Headless smoke test (no display needed).
Validates imports + window construction for the premium UI.
"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    print("Testing imports...")
    from ui.styles          import get_stylesheet, get_status_style
    from ui.splash_screen   import SplashScreen
    from ui.title_bar       import TitleBar
    from ui.thumbnail_widget import ThumbnailWidget
    from core.matlab_worker  import MatlabWorker, MatlabOutputStream
    assert get_stylesheet(), "Stylesheet is empty"
    assert get_status_style("Ready"), "get_status_style failed"
    print("  [OK] All modules imported")


def test_window():
    print("Testing MainWindow construction...")
    from PyQt6.QtWidgets import QApplication
    from ui.main_window  import MainWindow

    app = QApplication(sys.argv)
    win = MainWindow()

    # Widgets existence
    assert hasattr(win, 'scripts_picker'),   "scripts_picker missing"
    assert hasattr(win, 'input_picker'),     "input_picker missing"
    assert hasattr(win, 'output_picker'),    "output_picker missing"
    assert hasattr(win, 'loading_combo'),    "loading_combo missing"
    assert hasattr(win, 'ca_spin'),          "ca_spin missing"
    assert hasattr(win, 'crystal_combo'),    "crystal_combo missing"
    assert hasattr(win, 'run_btn'),          "run_btn missing"
    assert hasattr(win, 'abort_btn'),        "abort_btn missing"
    assert hasattr(win, 'open_output_btn'), "open_output_btn missing"
    assert hasattr(win, 'log_edit'),         "log_edit missing"
    assert hasattr(win, 'thumb_grid'),       "thumb_grid missing"
    assert hasattr(win, '_status_ind'),      "_status_ind missing"
    print("  [OK] All widgets present")

    # Default values
    assert win.loading_combo.currentText() == "X",           "Default loading dir should be X"
    assert abs(win.ca_spin.value() - 1.593) < 0.001,         "Default c/a should be ~1.593"
    assert win.crystal_combo.currentText() == "HCP + BCC",   "Default crystal system wrong"
    assert not win.open_output_btn.isEnabled(), "Open output btn should start disabled"
    assert not win.abort_btn.isEnabled(),        "Abort btn should start disabled"
    print("  [OK] Default values correct")

    # Shortcuts work
    assert win.scripts_edit is win.scripts_picker.path_edit, "scripts_edit shortcut broken"
    assert win.input_edit   is win.input_picker.path_edit,   "input_edit shortcut broken"
    assert win.output_edit  is win.output_picker.path_edit,  "output_edit shortcut broken"
    print("  [OK] Property shortcuts correct")

    win.close()
    print("  [OK] Window closed cleanly")


def test_splash():
    print("Testing SplashScreen construction...")
    from PyQt6.QtWidgets import QApplication
    from ui.splash_screen import SplashScreen
    app = QApplication.instance() or QApplication(sys.argv)
    s = SplashScreen()
    assert s.W == 700 and s.H == 420, "Splash dimensions wrong"
    s.close()
    print("  [OK] SplashScreen constructed")


if __name__ == "__main__":
    try:
        test_imports()
        test_window()
        test_splash()
        print("\nAll tests passed.")
    except Exception as e:
        import traceback; traceback.print_exc()
        sys.exit(1)
