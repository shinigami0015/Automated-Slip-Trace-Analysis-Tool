# -*- coding: utf-8 -*-
"""
STRCRYST -- Premium Stylesheet Engine
Supports dynamic switching between Dark and Light mode.
"""

def get_theme_colors(is_dark: bool) -> dict:
    if is_dark:
        return {
            "BG_APP":       "#161618",
            "BG_SIDEBAR":   "#222224",
            "BG_CONTENT":   "#1C1C1E",
            "BG_CARD":      "#2C2C2E",
            "BG_INPUT":     "#3A3A3C",
            "BG_HOVER":     "#323234",
            "BG_TITLEBAR":  "#111114",
            "BORDER_DIM":   "#38383A",
            "BORDER_NORM":  "#48484A",
            "ACCENT":       "#0A84FF",
            "ACCENT_H":     "#409CFF",
            "ACCENT_P":     "#0071E3",
            "TEXT_1":       "#F5F5F7",
            "TEXT_2":       "#8E8E93",
            "TEXT_3":       "#545456",
            "TEXT_INV":     "#FFFFFF",
            "SCROLL_BG":    "#1C1C1E",
            "CONSOLE_BG":   "#0D1117",
            "CONSOLE_FG":   "#8BC8E8",
        }
    else:
        return {
            "BG_APP":       "#F5F5F7",
            "BG_SIDEBAR":   "#EFEFF4",
            "BG_CONTENT":   "#FFFFFF",
            "BG_CARD":      "#FFFFFF",
            "BG_INPUT":     "#FFFFFF",
            "BG_HOVER":     "#E5E5EA",
            "BG_TITLEBAR":  "#E5E5E5",
            "BORDER_DIM":   "#D1D1D6",
            "BORDER_NORM":  "#C7C7CC",
            "ACCENT":       "#007AFF",
            "ACCENT_H":     "#409CFF",
            "ACCENT_P":     "#0056B3",
            "TEXT_1":       "#1D1D1F",
            "TEXT_2":       "#86868B",
            "TEXT_3":       "#A1A1A6",
            "TEXT_INV":     "#FFFFFF",
            "SCROLL_BG":    "#FFFFFF",
            "CONSOLE_BG":   "#F4F5F7",
            "CONSOLE_FG":   "#0A3069",
        }

def get_stylesheet(is_dark: bool = True) -> str:
    c = get_theme_colors(is_dark)
    
    return f"""
/* ══ Global ════════════════════════════════════════════════════════════════ */
* {{
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", sans-serif;
    font-size: 10pt;
    outline: 0;
}}

QMainWindow, QDialog {{ background: {c['BG_APP']}; }}

QWidget {{
    background: transparent;
    color: {c['TEXT_1']};
}}

/* ══ Sidebar ════════════════════════════════════════════════════════════════ */
QWidget#sidebar {{
    background: {c['BG_SIDEBAR']};
    border-right: 1px solid {c['BORDER_DIM']};
}}

QWidget#sidebarHeader {{
    background: {c['BG_TITLEBAR']};
    border-bottom: 1px solid {c['BORDER_DIM']};
}}

QWidget#controlsPanel {{
    background: {c['BG_SIDEBAR']};
    border-top: 1px solid {c['BORDER_DIM']};
}}

/* ══ Content area ═══════════════════════════════════════════════════════════ */
QWidget#contentArea {{ background: {c['BG_CONTENT']}; }}
QWidget#tabBar {{
    background: {c['BG_APP']};
    border-bottom: 1px solid {c['BORDER_DIM']};
}}

/* ══ Section labels ══════════════════════════════════════════════════════════ */
QLabel#sectionLabel {{
    color: {c['TEXT_3']};
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}}

QLabel#fieldLabel {{
    color: {c['TEXT_2']};
    font-size: 9pt;
    font-weight: 500;
}}

/* ══ Inputs ══════════════════════════════════════════════════════════════════ */
QLineEdit {{
    background: {c['BG_INPUT']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 6px;
    color: {c['TEXT_1']};
    padding: 7px 10px;
    selection-background-color: {c['ACCENT']};
}}
QLineEdit:focus {{
    border: 1px solid {c['ACCENT']};
}}
QLineEdit:disabled {{
    color: {c['TEXT_3']};
    background: {c['BG_SIDEBAR']};
}}

QDoubleSpinBox {{
    background: {c['BG_INPUT']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 6px;
    color: {c['TEXT_1']};
    padding: 7px 10px;
}}
QDoubleSpinBox:focus {{ border: 1px solid {c['ACCENT']}; }}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {c['BG_SIDEBAR']};
    border: none;
    border-radius: 3px;
    width: 16px;
}}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {c['BORDER_NORM']};
}}

QComboBox {{
    background: {c['BG_INPUT']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 6px;
    color: {c['TEXT_1']};
    padding: 7px 10px;
}}
QComboBox:focus {{ border: 1px solid {c['ACCENT']}; }}
QComboBox::drop-down {{ width: 28px; border: none; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {c['TEXT_2']};
    width: 0; height: 0;
}}
QComboBox QAbstractItemView {{
    background: {c['BG_CARD']};
    border: 1px solid {c['BORDER_NORM']};
    border-radius: 6px;
    selection-background-color: {c['ACCENT']};
    selection-color: {c['TEXT_INV']};
    color: {c['TEXT_1']};
    padding: 4px;
}}

/* ══ Primary Run Button ══════════════════════════════════════════════════════ */
QPushButton#runBtn {{
    background: qlineargradient(x1:0 y1:0 x2:0 y2:1,
        stop:0 {c['ACCENT_H']}, stop:1 {c['ACCENT_P']});
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-size: 11pt;
    font-weight: 600;
    padding: 13px 24px;
}}
QPushButton#runBtn:hover {{
    background: {c['ACCENT_H']};
}}
QPushButton#runBtn:pressed {{
    background: {c['ACCENT_P']};
}}
QPushButton#runBtn:disabled {{
    background: {c['BORDER_DIM']};
    color: {c['TEXT_3']};
}}

/* ══ Secondary Buttons ═══════════════════════════════════════════════════════ */
QPushButton#ghostBtn {{
    background: transparent;
    color: {c['TEXT_2']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 7px;
    padding: 7px 16px;
    font-weight: 500;
}}
QPushButton#ghostBtn:hover {{
    background: {c['BG_HOVER']};
    border-color: {c['BORDER_NORM']};
    color: {c['TEXT_1']};
}}
QPushButton#ghostBtn:disabled {{ color: {c['TEXT_3']}; border-color: {c['BORDER_DIM']}; }}

QPushButton#accentGhostBtn {{
    background: transparent;
    color: {c['ACCENT']};
    border: 1px solid {c['ACCENT_P']};
    border-radius: 7px;
    padding: 7px 16px;
    font-weight: 600;
}}
QPushButton#accentGhostBtn:hover {{ background: rgba(0, 122, 255, 0.1); }}
QPushButton#accentGhostBtn:disabled {{ color: {c['TEXT_3']}; border-color: {c['BORDER_DIM']}; }}

/* Browse button */
QPushButton#browseBtn {{
    background: {c['BG_HOVER']};
    color: {c['TEXT_2']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 8.5pt;
    font-weight: 600;
}}
QPushButton#browseBtn:hover {{ background: {c['ACCENT_P']}; color: white; border-color: transparent; }}

/* Tab-style toggle buttons */
QPushButton#tabBtn {{
    background: transparent;
    color: {c['TEXT_3']};
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    padding: 10px 18px;
    font-size: 9.5pt;
    font-weight: 600;
}}
QPushButton#tabBtn:hover {{ color: {c['TEXT_2']}; }}
QPushButton#tabBtn[active="true"] {{
    color: {c['TEXT_1']};
    border-bottom: 2px solid {c['ACCENT']};
}}

/* Icon buttons (Theme, Zip, Refresh) */
QPushButton#iconBtn {{
    background: transparent;
    color: {c['TEXT_2']};
    border: none;
    border-radius: 5px;
    padding: 4px;
    font-size: 11pt;
}}
QPushButton#iconBtn:hover {{
    background: {c['BG_HOVER']};
    color: {c['TEXT_1']};
}}

/* ══ Scroll Bars ══════════════════════════════════════════════════════════════ */
QScrollBar:vertical {{ background: transparent; width: 6px; margin: 0; border: none; }}
QScrollBar::handle:vertical {{ background: {c['BORDER_DIM']}; border-radius: 3px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: {c['BORDER_NORM']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0; width: 0; }}

QScrollBar:horizontal {{ background: transparent; height: 6px; border: none; }}
QScrollBar::handle:horizontal {{ background: {c['BORDER_DIM']}; border-radius: 3px; min-width: 24px; }}
QScrollBar::handle:horizontal:hover {{ background: {c['BORDER_NORM']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ background: none; height: 0; width: 0; }}

/* ══ Console log ══════════════════════════════════════════════════════════════ */
QTextEdit#consoleLog {{
    background: {c['CONSOLE_BG']};
    color: {c['CONSOLE_FG']};
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 9pt;
    border: none;
    border-radius: 0;
    padding: 10px 14px;
    line-height: 1.5;
}}

/* ══ Scroll Area ══════════════════════════════════════════════════════════════ */
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* ══ Separator ════════════════════════════════════════════════════════════════ */
QFrame[frameShape="4"] {{
    background: {c['BORDER_DIM']};
    color: {c['BORDER_DIM']};
    border: none;
    max-height: 1px;
}}

/* ══ Thumbnail Card ════════════════════════════════════════════════════════════ */
QWidget#thumbCard {{
    background: {c['BG_CARD']};
    border: 1px solid {c['BORDER_DIM']};
    border-radius: 10px;
}}
QWidget#thumbCard:hover {{
    border: 1px solid {c['ACCENT']};
}}

/* ══ Tooltips & MsgBox ═══════════════════════════════════════════════════════ */
QToolTip {{
    background: {c['BG_APP']};
    color: {c['TEXT_1']};
    border: 1px solid {c['BORDER_NORM']};
    border-radius: 5px;
}}
QMessageBox {{ background: {c['BG_APP']}; }}
QMessageBox QLabel {{ color: {c['TEXT_1']}; background: transparent; }}
"""

def get_status_style(status: str, is_dark: bool = True) -> tuple[str, str]:
    c = get_theme_colors(is_dark)
    if is_dark:
        styles = {
            "Ready":              (f"background: {c['BG_CARD']};   color: {c['TEXT_3']};", "#545456"),
            "MATLAB Starting...": (f"background: #2A2010; color: #FF9F0A;",   "#FF9F0A"),
            "Running...":         (f"background: #0D1A2A; color: {c['ACCENT']};",    c['ACCENT']),
            "Done":               (f"background: #0D2010; color: #32D74B;",     "#32D74B"),
            "Error":              (f"background: #2A0D0D; color: #FF453A;",       "#FF453A"),
        }
    else:
        styles = {
            "Ready":              (f"background: {c['BORDER_DIM']};   color: {c['TEXT_2']};", "#A1A1A6"),
            "MATLAB Starting...": (f"background: #FFF4E5; color: #E68A00;",   "#E68A00"),
            "Running...":         (f"background: #E5F1FF; color: {c['ACCENT_P']};", c['ACCENT_P']),
            "Done":               (f"background: #E8F5E9; color: #2E7D32;",     "#2E7D32"),
            "Error":              (f"background: #FFEBEE; color: #C62828;",       "#C62828"),
        }
    return styles.get(status, (f"background: {c['BG_CARD']}; color: {c['TEXT_3']};", "#545456"))
