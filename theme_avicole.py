"""Palette et styles de l'interface Avicole Pro."""


class AvicoleThemeManager:
    """Centralise les couleurs et le QSS compatible avec Qt."""

    PRO_THEME = {
        "name": "pro_avicole",
        "primary": "#123B5D",
        "primary_hover": "#0B2E49",
        "secondary": "#1E6B57",
        "accent": "#C9A227",
        "accent_soft": "#F5EBC8",
        "background": "#F3F6FA",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FAFC",
        "text_primary": "#152536",
        "text_secondary": "#64748B",
        "success": "#18794E",
        "warning": "#A15C00",
        "error": "#B42318",
        "info": "#175CD3",
        "border": "#D9E2EC",
        "border_strong": "#B8C6D4",
        "sidebar_bg": "#0B1F33",
        "sidebar_hover": "#15324D",
        "sidebar_active": "#1B4568",
        "sidebar_text": "#D5E1EC",
    }

    FARMER_THEME = {
        **PRO_THEME,
        "name": "fermier",
        "primary": "#285A3A",
        "primary_hover": "#1E452C",
        "secondary": "#527A42",
        "accent": "#B88924",
        "accent_soft": "#F3E8C8",
        "background": "#F4F7F1",
        "surface_alt": "#F8FAF6",
        "sidebar_bg": "#173524",
        "sidebar_hover": "#234A33",
        "sidebar_active": "#315F43",
    }

    DARK_PREMIUM = {
        **PRO_THEME,
        "name": "dark_premium",
        "primary": "#4F8BB8",
        "primary_hover": "#6CA0C6",
        "secondary": "#48A58C",
        "accent": "#D8B95B",
        "accent_soft": "#493F22",
        "background": "#0E1722",
        "surface": "#162231",
        "surface_alt": "#1A2939",
        "text_primary": "#F1F5F9",
        "text_secondary": "#A9B7C6",
        "border": "#2B3E50",
        "border_strong": "#40566B",
        "sidebar_bg": "#08131F",
        "sidebar_hover": "#14283B",
        "sidebar_active": "#1D3A54",
        "sidebar_text": "#D2DEE9",
    }

    def __init__(self, theme_name="pro_avicole"):
        self.themes = {
            "pro_avicole": self.PRO_THEME,
            "fermier": self.FARMER_THEME,
            "dark_premium": self.DARK_PREMIUM,
        }
        self.current_theme = theme_name

    def get_theme(self, theme_name=None):
        return self.themes.get(theme_name or self.current_theme, self.PRO_THEME)

    def set_theme(self, theme_name):
        if theme_name not in self.themes:
            return False
        self.current_theme = theme_name
        return True

    def get_stylesheet(self, theme_name=None):
        t = self.get_theme(theme_name)
        return f"""
        QMainWindow, QWidget#centralRoot {{
            background-color: {t['background']};
        }}

        QDialog, QMessageBox {{
            background-color: {t['background']};
            color: {t['text_primary']};
        }}

        QMessageBox QLabel {{
            background: transparent;
            color: {t['text_primary']};
            min-width: 280px;
        }}

        QWidget {{
            color: {t['text_primary']};
            font-family: "Segoe UI";
            font-size: 12px;
        }}

        QScrollArea, QScrollArea > QWidget > QWidget {{
            background: transparent;
            border: none;
        }}

        QLabel#pageEyebrow {{
            color: {t['accent']};
            font-size: 11px;
            font-weight: 700;
        }}

        QLabel#title, QLabel#pageTitle {{
            color: {t['text_primary']};
            font-size: 27px;
            font-weight: 700;
        }}

        QLabel#subtitle, QLabel#sectionTitle {{
            color: {t['text_primary']};
            font-size: 16px;
            font-weight: 600;
        }}

        QLabel#mutedText {{
            color: {t['text_secondary']};
        }}

        QFrame#card, QFrame#chartCard, QFrame#contentCard {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 10px;
        }}

        QFrame#filterBar {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 8px;
        }}

        QPushButton {{
            background-color: {t['primary']};
            color: #FFFFFF;
            border: 1px solid {t['primary']};
            border-radius: 6px;
            padding: 8px 16px;
            min-height: 20px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {t['primary_hover']};
            border-color: {t['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {t['sidebar_bg']};
        }}

        QPushButton:disabled {{
            background-color: {t['border']};
            border-color: {t['border']};
            color: {t['text_secondary']};
        }}

        QPushButton[variant="secondary"] {{
            background-color: {t['surface']};
            color: {t['primary']};
            border-color: {t['border_strong']};
        }}

        QPushButton[variant="secondary"]:hover {{
            background-color: {t['surface_alt']};
            border-color: {t['primary']};
        }}

        QPushButton[variant="success"] {{
            background-color: {t['success']};
            border-color: {t['success']};
        }}

        QPushButton[variant="warning"] {{
            background-color: {t['warning']};
            border-color: {t['warning']};
        }}

        QFrame#sidebar {{
            background-color: {t['sidebar_bg']};
            border: none;
            border-right: 1px solid #18364F;
        }}

        QFrame#brandHeader {{
            background-color: {t['sidebar_bg']};
            border-bottom: 1px solid #18364F;
        }}

        QLabel#brandMark {{
            background-color: {t['accent']};
            color: {t['sidebar_bg']};
            border-radius: 8px;
            font-size: 14px;
            font-weight: 800;
        }}

        QLabel#brandName {{
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 700;
        }}

        QLabel#brandMeta, QLabel#sidebarRole {{
            color: #91A8BC;
            font-size: 10px;
        }}

        QLabel#navSection {{
            color: #71899E;
            font-size: 9px;
            font-weight: 700;
        }}

        QLabel#sidebarUser {{
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 600;
        }}

        QLabel#onlineDot, QLabel#systemStatus {{
            color: {t['success']};
            font-size: 11px;
            font-weight: 600;
        }}

        QFrame#sidebarFooter {{
            background-color: #081A2B;
            border-top: 1px solid #18364F;
        }}

        QPushButton[nav="true"] {{
            background-color: transparent;
            color: {t['sidebar_text']};
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0;
            padding: 12px 18px;
            text-align: left;
            font-size: 13px;
            font-weight: 500;
        }}

        QPushButton[nav="true"]:hover {{
            background-color: {t['sidebar_hover']};
            color: #FFFFFF;
        }}

        QPushButton[nav="true"]:checked {{
            background-color: {t['sidebar_active']};
            color: #FFFFFF;
            border-left: 3px solid {t['accent']};
            font-weight: 700;
        }}

        QMenuBar {{
            background-color: {t['surface']};
            border-bottom: 1px solid {t['border']};
            padding: 3px 8px;
        }}

        QMenuBar::item {{
            padding: 7px 10px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected, QMenu::item:selected {{
            background-color: {t['accent_soft']};
            color: {t['text_primary']};
        }}

        QMenu {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            padding: 6px;
        }}

        QMenu::item {{
            padding: 8px 28px 8px 12px;
            border-radius: 4px;
        }}

        QToolBar {{
            background-color: {t['surface']};
            border: none;
            border-bottom: 1px solid {t['border']};
            spacing: 8px;
            padding: 8px 14px;
            min-height: 48px;
        }}

        QToolBar QToolButton {{
            background-color: transparent;
            color: {t['primary']};
            border: 1px solid transparent;
            border-radius: 5px;
            padding: 7px 10px;
            font-weight: 600;
        }}

        QToolBar QToolButton:hover {{
            background-color: {t['surface_alt']};
            border-color: {t['border']};
        }}

        QToolButton {{
            background-color: transparent;
            color: {t['text_secondary']};
            border: 1px solid transparent;
            border-radius: 5px;
            padding: 5px 8px;
            font-weight: 600;
        }}

        QToolButton:hover {{
            background-color: {t['surface_alt']};
            border-color: {t['border']};
            color: {t['primary']};
        }}

        QLabel#toolbarLabel {{
            color: {t['text_secondary']};
            padding: 0 8px 0 6px;
            font-size: 11px;
            font-weight: 600;
        }}

        QWidget#chartHeader {{
            background-color: {t['surface_alt']};
            border-bottom: 1px solid {t['border']};
        }}

        QLabel#chartTitle {{
            color: {t['text_primary']};
            font-size: 13px;
            font-weight: 600;
        }}

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit, QTextEdit {{
            background-color: {t['surface']};
            color: {t['text_primary']};
            border: 1px solid {t['border_strong']};
            border-radius: 6px;
            padding: 8px 10px;
            selection-background-color: {t['primary']};
            min-height: 20px;
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
        QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
            border: 1px solid {t['primary']};
        }}

        QComboBox::drop-down, QDateEdit::drop-down {{
            border: none;
            width: 28px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            selection-background-color: {t['accent_soft']};
            selection-color: {t['text_primary']};
            outline: none;
        }}

        QTabWidget::pane {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 8px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: transparent;
            color: {t['text_secondary']};
            border: none;
            border-bottom: 3px solid transparent;
            padding: 11px 18px;
            min-width: 110px;
            font-weight: 600;
        }}

        QTabBar::tab:hover {{
            color: {t['primary']};
            background-color: {t['surface_alt']};
        }}

        QTabBar::tab:selected {{
            color: {t['primary']};
            border-bottom-color: {t['accent']};
        }}

        QTableWidget {{
            background-color: {t['surface']};
            alternate-background-color: {t['surface_alt']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: 7px;
            gridline-color: {t['border']};
            outline: none;
        }}

        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {t['border']};
        }}

        QTableWidget::item:selected {{
            background-color: {t['accent_soft']};
            color: {t['text_primary']};
        }}

        QWidget#tableActions {{
            background-color: transparent;
        }}

        QPushButton#tableActionPrimary {{
            background-color: {t['primary']};
            color: #FFFFFF;
            border: 1px solid {t['primary']};
            border-radius: 6px;
            padding: 0;
            min-height: 0;
            min-width: 0;
            font-size: 11px;
            font-weight: 700;
        }}

        QPushButton#tableActionPrimary:hover {{
            background-color: {t['primary_hover']};
            border-color: {t['primary_hover']};
        }}

        QPushButton#tableActionSecondary {{
            background-color: {t['surface']};
            color: {t['primary']};
            border: 1px solid {t['border_strong']};
            border-radius: 6px;
            padding: 0;
            min-height: 0;
            min-width: 0;
            font-size: 11px;
            font-weight: 700;
        }}

        QPushButton#tableActionSecondary:hover {{
            background-color: {t['surface_alt']};
            border-color: {t['primary']};
        }}

        QHeaderView::section {{
            background-color: {t['primary']};
            color: #FFFFFF;
            border: none;
            border-right: 1px solid #315775;
            padding: 10px;
            font-size: 11px;
            font-weight: 700;
        }}

        QStatusBar {{
            background-color: {t['surface']};
            color: {t['text_secondary']};
            border-top: 1px solid {t['border']};
            padding: 5px 10px;
        }}

        QGroupBox {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 8px;
            margin-top: 14px;
            padding: 18px 14px 14px 14px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: {t['primary']};
        }}

        QProgressBar {{
            background-color: {t['border']};
            border: none;
            border-radius: 3px;
            min-height: 6px;
            max-height: 6px;
        }}

        QProgressBar::chunk {{
            background-color: {t['accent']};
            border-radius: 3px;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical {{
            background: {t['border_strong']};
            border-radius: 4px;
            min-height: 32px;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        """

    def get_button_style(self, style_type="primary", size="medium"):
        """Retourne un style local pour les boutons déjà construits dans les pages."""
        t = self.get_theme()
        sizes = {
            "small": "padding: 7px 13px; min-height: 20px; font-size: 11px;",
            "medium": "padding: 9px 17px; min-height: 22px; font-size: 12px;",
            "large": "padding: 12px 22px; min-height: 26px; font-size: 13px;",
        }
        colors = {
            "primary": (t["primary"], "#FFFFFF", t["primary"]),
            "info": (t["info"], "#FFFFFF", t["info"]),
            "success": (t["success"], "#FFFFFF", t["success"]),
            "warning": (t["warning"], "#FFFFFF", t["warning"]),
            "danger": (t["error"], "#FFFFFF", t["error"]),
            "secondary": (t["surface"], t["primary"], t["border_strong"]),
            "flat": ("transparent", t["text_secondary"], "transparent"),
        }
        background, foreground, border = colors.get(style_type, colors["primary"])
        return f"""
            background-color: {background};
            color: {foreground};
            border: 1px solid {border};
            border-radius: 6px;
            font-weight: 600;
            {sizes.get(size, sizes['medium'])}
        """
