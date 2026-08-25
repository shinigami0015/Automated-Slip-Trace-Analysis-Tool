# -*- coding: utf-8 -*-
"""
ASTA Tool -- Main Entry Point
Launches the ultimate cinematic sequence: 
Intro -> Crystal Splash -> Diagnostics -> Manual -> Main Window
"""
import sys
import os

if getattr(sys, 'frozen', False):
    APP_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, APP_DIR)

# Force MATLAB R2023a to be found first by matlab.engine
matlab_path = r"C:\Program Files\MATLAB\R2023a\bin\win64"
if os.path.exists(matlab_path):
    os.environ["PATH"] = matlab_path + os.pathsep + os.environ.get("PATH", "")

# PyInstaller packages matlab into a zip, which breaks matlab.__init__.py's subdir_exists check.
# This causes it to fallback to scanning PATH and finding the wrong MATLAB.
# Injecting the correct extern/bin/win64 path into sys.path bypasses the bug.
matlab_extern_bin = r"C:\Program Files\MATLAB\R2023a\extern\bin\win64"
if matlab_extern_bin not in sys.path:
    sys.path.insert(0, matlab_extern_bin)

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
