# -*- coding: utf-8 -*-
"""
ASTA Tool -- Main Entry Point
Launches the ultimate cinematic sequence: 
Intro -> Crystal Splash -> Diagnostics -> Manual -> Main Window
"""
import sys
import os
import glob

if getattr(sys, 'frozen', False):
    APP_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, APP_DIR)

# ── Find MATLAB installation ──────────────────────────────────────────────────
# Scan for any installed MATLAB version and add its bin to PATH
for _matlab_bin in sorted(glob.glob(r"C:\Program Files\MATLAB\R*\bin\win64"), reverse=True):
    os.environ["PATH"] = _matlab_bin + os.pathsep + os.environ.get("PATH", "")
    break  # Use the newest found

# ── Find matlab.engine Python package ────────────────────────────────────────
# PyInstaller bundles its own Python which cannot access system site-packages.
# We search all Python installations on this machine for the matlab package
# and inject its location into sys.path so `import matlab.engine` can succeed.
def _inject_matlab_package():
    try:
        import matlab.engine  # noqa – already available, nothing to do
        return
    except Exception:
        pass

    _search_patterns = [
        r"C:\Python*\Lib\site-packages",
        r"C:\Python*\lib\site-packages",
        r"C:\Users\*\AppData\Local\Programs\Python\Python*\Lib\site-packages",
        r"C:\Users\*\AppData\Roaming\Python\Python*\site-packages",
        r"C:\ProgramData\anaconda*\Lib\site-packages",
        r"C:\ProgramData\miniconda*\Lib\site-packages",
        r"C:\Users\*\anaconda*\Lib\site-packages",
        r"C:\Users\*\miniconda*\Lib\site-packages",
        r"C:\Program Files\MATLAB\R*\extern\engines\python\build\lib",
        r"C:\Program Files\MATLAB\R*\extern\engines\python\build\lib.win*",
    ]
    for _pattern in _search_patterns:
        for _dir in sorted(glob.glob(_pattern), reverse=True):
            if os.path.isdir(os.path.join(_dir, "matlab")):
                if _dir not in sys.path:
                    sys.path.insert(0, _dir)
                try:
                    import matlab.engine  # noqa
                    return  # Found and loaded successfully
                except Exception:
                    sys.path.remove(_dir)  # Didn't work, try next

_inject_matlab_package()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont

from ui.intro_sequence import IntroSequenceHost, CinematicIntro
from ui.splash_screen  import SplashScreen
from ui.main_window    import MainWindow

def main():
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("ASTA Tool")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("IISc Materials Lab")
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # 1. Netflix-style Cinematic Intro
    intro = CinematicIntro()
    intro.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    intro.resize(700, 460)

    # 2. Crystal Splash Screen
    splash = SplashScreen()

    # 3. Diagnostics & Manual Host
    # IntroSequenceHost internally chains: Diagnostics -> Manual
    diag_host = IntroSequenceHost()
    diag_host.stack.removeWidget(diag_host.intro) # We play intro separately now
    diag_host.stack.setCurrentWidget(diag_host.diag)

    # 4. Main Window
    main_win = MainWindow()

    # ── Flow Callbacks ──
    def _show_main():
        diag_host.close()
        main_win.show()
        main_win.fade_in()

    def _show_diag():
        splash.close()
        diag_host.show()
        diag_host.diag.start()

    def _fade_splash_to_diag():
        splash.fade_out(callback=_show_diag)

    def _show_splash():
        intro.close()
        splash.show()
        splash.start_animation()
        # Splash runs for 3.2s, then goes to diagnostics
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3200, _fade_splash_to_diag)

    # Wire up the chain
    intro.finished.connect(_show_splash)
    diag_host.sequenceFinished.connect(_show_main)

    # Start the sequence
    intro.show()
    intro.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
