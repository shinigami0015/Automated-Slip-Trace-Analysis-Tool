import sys
from pywinauto import Desktop, Application
import time

try:
    app = Application(backend="uia").connect(title="STRCRYST", timeout=5)
    dlg = app.window(title="STRCRYST")
    with open('ui_dump.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        dlg.print_control_identifiers(depth=5)
except Exception as e:
    print(e)
