import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import matplotlib
matplotlib.use("qtagg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
from pathlib import Path
import csv
import shutil

import backup as backup_module
import indicators
from app_paths import ensure_user_directories
from database import Database
from theme_avicole import AvicoleThemeManager
from dialogs.styles import DIALOG_QSS

class ModernCard(QFrame):
    """Carte moderne avec ombres et animations"""
    def __init__(self, title="", icon="", color="#1E88E5", parent=None):
        super().__init__(parent)
        self.color = color
        
        # Configuration de la carte
        self.setObjectName("card")
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 0px;
            }}
            ModernCard:hover {{
                border-color: {color};
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            }}
        """)
        
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # En-tête
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre avec icône
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"""
                font-size: 20px;
                color: {color};
                margin-right: 8px;
            """)
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: #263238;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        header_layout.addWidget(title_container)
        
        # Badge optionnel
        self.badge = QLabel()
        self.badge.setVisible(False)
        header_layout.addWidget(self.badge)
        
        layout.addWidget(header)
        
        # Valeur principale
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: #263238;
            padding: 8px 0;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Sous-valeur
        self.subvalue_label = QLabel("")
        self.subvalue_label.setStyleSheet("""
            font-size: 12px;
            color: #607D8B;
            font-weight: 400;
        """)
        self.subvalue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subvalue_label)
        
        # Barre de progression (optionnelle)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #F5F5F5;
                border-radius: 4px;
                height: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)
    
    def update_value(self, value, subvalue="", badge_text="", badge_color="primary", progress=0):
        """Mettre à jour les valeurs de la carte"""
        self.value_label.setText(str(value))
        self.subvalue_label.setText(subvalue)
        
        if badge_text:
            self.badge.setText(badge_text)
            self.badge.setStyleSheet(f"""
                background-color: {self.color};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
            """)
            self.badge.setVisible(True)
        
        if progress > 0:
            self.progress_bar.setValue(int(progress))
            self.progress_bar.setVisible(True)

class ModernSidebar(QFrame):
    """Sidebar moderne avec onglets latéraux"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame#sidebar {
                background-color: #263238;
                border-right: 1px solid #37474F;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo et titre
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1E88E5, stop:1 #1565C0);
            border: none;
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        logo = QLabel("🐔 AVICOLE PRO")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: white;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(logo)
        
        subtitle = QLabel("Gestion Avicole Intelligente")
        subtitle.setStyleSheet("""
            font-size: 11px;
            color: rgba(255,255,255,0.8);
            font-weight: 400;
            margin-top: 4px;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Onglets de navigation
        self.nav_widget = QWidget()
        nav_layout = QVBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(20, 20, 20, 20)
        nav_layout.setSpacing(8)
        
        # Boutons de navigation
        self.nav_buttons = []
        
        nav_items = [
            ("📊", "Tableau de bord", "dashboard"),
            ("🏷️", "Bandes", "bandes"),
            ("💳", "Transactions", "transactions"),
            ("📈", "Analytiques", "analytiques"),
            ("📋", "Rapports", "rapports"),
            ("⚙️", "Paramètres", "parametres"),
            ("🆘", "Aide", "aide")
        ]
        
        for icon, text, page in nav_items:
            btn = QPushButton(f"   {icon}  {text}")
            btn.setObjectName(f"nav_{page}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B0BEC5;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 20px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #37474F;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #1E88E5;
                    color: white;
                    font-weight: 600;
                    border-left: 4px solid #FF9800;
                }
            """)
            btn.setCheckable(True)
            self.nav_buttons.append((btn, page))
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        layout.addWidget(self.nav_widget)
        
        # Pied de sidebar
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background-color: #1E272C; border-top: 1px solid #37474F;")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        user_info = QLabel("👤 Administrateur")
        user_info.setStyleSheet("color: #B0BEC5; font-size: 12px;")
        footer_layout.addWidget(user_info)
        
        layout.addWidget(footer)

class ProfessionalToolBar(QToolBar):
    """Barre d'outils professionnelle"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Actions principales
        self.addAction("🆕 Nouvelle bande")
        self.addSeparator()
        self.addAction("📤 Exporter")
        self.addAction("🖨️ Imprimer")
        self.addSeparator()
        
        # Widget pour la recherche
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher...")
        search_input.setFixedWidth(200)
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
            }
        """)
        search_layout.addWidget(search_input)
        
        self.addWidget(search_widget)
        self.addSeparator()
        
        # Sélecteur de bande
        self.bande_combo = QComboBox()
        self.bande_combo.setFixedWidth(200)
        self.bande_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: white;
            }
        """)
        self.addWidget(QLabel("  Bande:"))
        self.addWidget(self.bande_combo)
        
        # Espacement
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
        
        # Indicateurs
        self.status_indicator = QLabel("🟢 En ligne")
        self.status_indicator.setStyleSheet("color: #4CAF50; font-weight: 500;")
        self.addWidget(self.status_indicator)

class AnalyticsChart(QFrame):
    """Graphique analytique moderne"""
    def __init__(self, title="", chart_type="line", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.setObjectName("card")
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête du graphique
        header = QWidget()
        header.setStyleSheet("background-color: #F8F9FA; border-radius: 12px 12px 0 0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #263238;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Options du graphique
        options_btn = QToolButton()
        options_btn.setText("⋯")
        options_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                color: #607D8B;
                font-size: 20px;
                padding: 4px;
            }
        """)
        header_layout.addWidget(options_btn)
        
        layout.addWidget(header)
        
        # Zone du graphique
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.figure.set_facecolor('#FFFFFF')
        self.ax.set_facecolor('#FFFFFF')
        
        # Style moderne
        self.ax.grid(True, alpha=0.1)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_alpha(0.3)
        self.ax.spines['bottom'].set_alpha(0.3)
        
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def update_chart(self, data, labels=None, colors=None):
        """Mettre à jour le graphique"""
        self.ax.clear()
        
        if self.chart_type == "line":
            if colors:
                self.ax.plot(data, color=colors[0], linewidth=2.5, marker='o', markersize=6)
            else:
                self.ax.plot(data, color='#1E88E5', linewidth=2.5, marker='o', markersize=6)
        
        elif self.chart_type == "bar":
            x = range(len(data))
            if colors:
                bars = self.ax.bar(x, data, color=colors, alpha=0.8)
            else:
                bars = self.ax.bar(x, data, color='#1E88E5', alpha=0.8)
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        elif self.chart_type == "pie":
            if colors:
                self.ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%',
                           startangle=90, textprops={'fontsize': 9})
            else:
                colors = plt.cm.Set3(range(len(data)))
                self.ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%',
                           startangle=90, textprops={'fontsize': 9})
        
        self.ax.grid(True, alpha=0.1)
        self.canvas.draw()

class PremiumMetricCard(QFrame):
    """Carte de synthèse sobre pour un indicateur métier."""

    def __init__(self, title="", icon="", color="#123B5D", parent=None):
        super().__init__(parent)
        self.color = color
        self.setObjectName("card")
        self.setMinimumHeight(154)
        self.setMaximumHeight(174)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(15, 35, 55, 24))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 17, 18, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(9)

        marker = QFrame()
        marker.setFixedSize(4, 26)
        marker.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        header.addWidget(marker)

        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(
                f"color: {color}; font-size: 13px; font-weight: 700;"
            )
            header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #64748B; font-size: 11px; font-weight: 700;"
        )
        header.addWidget(title_label)
        header.addStretch()

        self.badge = QLabel()
        self.badge.setVisible(False)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.badge)
        layout.addLayout(header)

        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(
            "color: #152536; font-size: 30px; font-weight: 700; padding-top: 5px;"
        )
        layout.addWidget(self.value_label)

        self.subvalue_label = QLabel("")
        self.subvalue_label.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.subvalue_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #E6ECF2;
                border-radius: 3px;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

    def update_value(
        self, value, subvalue="", badge_text="", badge_color="primary", progress=0
    ):
        self.value_label.setText(str(value))
        self.subvalue_label.setText(subvalue)

        if badge_text:
            colors = {
                "success": ("#E8F5EE", "#18794E"),
                "warning": ("#FFF3E0", "#A15C00"),
                "error": ("#FDECEC", "#B42318"),
                "primary": ("#EAF1F7", "#123B5D"),
            }
            background, foreground = colors.get(badge_color, colors["primary"])
            self.badge.setText(badge_text)
            self.badge.setStyleSheet(
                f"background-color: {background}; color: {foreground};"
                "padding: 3px 8px; border-radius: 9px; font-size: 9px;"
                "font-weight: 700;"
            )
            self.badge.setVisible(True)
        else:
            self.badge.setVisible(False)

        self.progress_bar.setVisible(progress > 0)
        if progress > 0:
            self.progress_bar.setValue(int(progress))


class PremiumSidebar(QFrame):
    """Navigation principale institutionnelle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMinimumWidth(210)
        self.setMaximumWidth(264)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("brandHeader")
        header.setFixedHeight(108)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 18, 18)
        header_layout.setSpacing(12)

        brand_mark = QLabel("AP")
        brand_mark.setObjectName("brandMark")
        brand_mark.setFixedSize(42, 42)
        brand_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(brand_mark)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        logo = QLabel("AVICOLE PRO")
        logo.setObjectName("brandName")
        brand_text.addWidget(logo)
        subtitle = QLabel("Système de gestion intégré")
        subtitle.setObjectName("brandMeta")
        brand_text.addWidget(subtitle)
        header_layout.addLayout(brand_text)
        header_layout.addStretch()
        layout.addWidget(header)

        self.nav_widget = QWidget()
        nav_layout = QVBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 18, 0, 14)
        nav_layout.setSpacing(3)

        section_label = QLabel("ESPACE DE PILOTAGE")
        section_label.setObjectName("navSection")
        section_label.setContentsMargins(20, 0, 0, 8)
        nav_layout.addWidget(section_label)

        self.nav_buttons = []
        nav_items = [
            ("01", "Tableau de bord", "dashboard"),
            ("02", "Bandes d'élevage", "bandes"),
            ("03", "Transactions", "transactions"),
            ("04", "Analyse décisionnelle", "analytiques"),
            ("05", "Rapports", "rapports"),
            ("06", "Paramètres", "parametres"),
        ]
        for index, text, page in nav_items:
            button = QPushButton(f"   {index}    {text}")
            button.setObjectName(f"nav_{page}")
            button.setProperty("nav", "true")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            self.nav_buttons.append((button, page))
            nav_layout.addWidget(button)

        nav_layout.addStretch()
        layout.addWidget(self.nav_widget)

        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        footer.setFixedHeight(72)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 16, 10)
        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        user_name = QLabel("Administrateur")
        user_name.setObjectName("sidebarUser")
        user_info.addWidget(user_name)
        user_role = QLabel("Accès sécurisé")
        user_role.setObjectName("sidebarRole")
        user_info.addWidget(user_role)
        footer_layout.addLayout(user_info)
        footer_layout.addStretch()
        status_dot = QLabel("●")
        status_dot.setObjectName("onlineDot")
        footer_layout.addWidget(status_dot)
        layout.addWidget(footer)


class PremiumToolBar(QToolBar):
    """Barre de commandes globale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setObjectName("mainToolbar")
        self.setIconSize(QSize(18, 18))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.new_action = self.addAction("Nouvelle bande")
        self.addSeparator()
        self.export_action = self.addAction("Exporter")
        self.print_action = self.addAction("Imprimer")
        self.addSeparator()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher dans l'application")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(130)
        self.search_input.setMaximumWidth(240)
        self.search_action = self.addWidget(self.search_input)
        self.addSeparator()

        self.selector_label = QLabel("Bande active")
        self.selector_label.setObjectName("toolbarLabel")
        self.selector_action = self.addWidget(self.selector_label)
        self.bande_combo = QComboBox()
        self.bande_combo.setMinimumWidth(150)
        self.bande_combo.setMaximumWidth(220)
        self.combo_action = self.addWidget(self.bande_combo)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.addWidget(spacer)
        status = QLabel("●  Système opérationnel")
        status.setObjectName("systemStatus")
        self.status_indicator = status
        self.status_action = self.addWidget(status)


class PremiumAnalyticsChart(QFrame):
    """Graphique analytique cohérent avec le thème institutionnel."""

    def __init__(self, title="", chart_type="line", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.setObjectName("chartCard")
        self.setMinimumHeight(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("chartHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 13, 14, 11)

        title_label = QLabel(title)
        title_label.setObjectName("chartTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        options_btn = QToolButton()
        options_btn.setText("•••")
        options_btn.setToolTip("Options du graphique")
        header_layout.addWidget(options_btn)
        layout.addWidget(header)

        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.figure.set_facecolor("#FFFFFF")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self._apply_chart_style()

    def _apply_chart_style(self, surface="#FFFFFF", border="#D9E2EC"):
        self.ax.set_facecolor(surface)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color(border)
        self.ax.spines["bottom"].set_color(border)
        self.ax.tick_params(colors="#64748B", labelsize=8)
        self.ax.grid(True, color="#E8EEF4", linewidth=0.8)

    def update_chart(self, data, labels=None, colors=None):
        self.ax.clear()
        color = colors[0] if colors else "#123B5D"

        if self.chart_type == "line":
            x_values = range(len(data))
            self.ax.plot(
                x_values,
                data,
                color=color,
                linewidth=2.4,
                marker="o",
                markersize=5,
                markerfacecolor="#FFFFFF",
                markeredgewidth=2,
            )
            self.ax.fill_between(x_values, data, color=color, alpha=0.08)
            if labels:
                self.ax.set_xticks(list(x_values))
                self.ax.set_xticklabels(labels)
        elif self.chart_type == "bar":
            x_values = range(len(data))
            bars = self.ax.bar(x_values, data, color=color, alpha=0.92)
            if labels:
                self.ax.set_xticks(list(x_values))
                self.ax.set_xticklabels(labels)
            for bar in bars:
                height = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{height:,.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#64748B",
                )
        elif self.chart_type == "pie":
            palette = colors or ["#123B5D", "#1E6B57", "#C9A227", "#7895AD"]
            self.ax.pie(
                data,
                labels=labels,
                colors=palette[:len(data)],
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"width": 0.42, "edgecolor": "#FFFFFF"},
                textprops={"fontsize": 8, "color": "#475569"},
            )

        self._apply_chart_style()
        self.figure.tight_layout(pad=1.8)
        self.canvas.draw_idle()

    def apply_theme(self, theme):
        surface = theme["surface"]
        primary = theme["primary"]
        self.figure.set_facecolor(surface)
        self.ax.set_facecolor(surface)
        for line in self.ax.lines:
            line.set_color(primary)
            line.set_markeredgecolor(primary)
        for patch in self.ax.patches:
            if hasattr(patch, "set_facecolor"):
                patch.set_facecolor(primary)
        self._apply_chart_style(surface, theme["border"])
        self.canvas.draw_idle()


# Les pages existantes utilisent ces noms; les alias permettent une refonte ciblée
# sans perturber la logique métier.
ModernCard = PremiumMetricCard
ModernSidebar = PremiumSidebar
ProfessionalToolBar = PremiumToolBar
AnalyticsChart = PremiumAnalyticsChart


class ProfessionalMainWindow(QMainWindow):
    """Fenêtre principale professionnelle"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_bande_id = None
        self.theme_manager = AvicoleThemeManager('pro_avicole')
        
        self.init_ui()
        self.load_bandes()
        self.apply_theme()
        
        # Centrer la fenêtre
        self.center_window()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, 
                  (screen.height() - size.height()) // 2)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        self.setWindowTitle("Avicole Pro | Système intégré de gestion avicole")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(900, 640)
        
        # Configuration du style
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        
        # Configuration de la barre de menu
        self.create_menu()
        
        # Configuration de la barre d'outils
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralRoot")
        self.setCentralWidget(central_widget)
        
        # Layout principal avec sidebar
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = ModernSidebar()
        main_layout.addWidget(self.sidebar)
        
        # Zone de contenu principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Stacked widget pour les pages
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Créer les pages
        self.create_dashboard_page()
        self.create_bandes_page()
        self.create_transactions_page()
        self.create_analytics_page()
        self.create_reports_page()
        self.create_settings_page()
        self.configure_data_tables()
        
        main_layout.addWidget(content_widget, 1)
        
        # Barre de statut
        self.create_statusbar()
        
        # Connecter les boutons de navigation
        self.connect_navigation()
        
        # Afficher le dashboard par défaut
        self.show_dashboard()
        self.update_responsive_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"):
            self.update_responsive_layout()

    def update_responsive_layout(self):
        """Adapter navigation, barre d'outils et grilles à la largeur disponible."""
        width = self.width()
        compact = width < 1180
        self.sidebar.setMaximumWidth(220 if compact else 264)
        self.sidebar.setMinimumWidth(190 if compact else 210)

        if hasattr(self, "main_toolbar"):
            self.main_toolbar.search_action.setVisible(width >= 1280)
            self.main_toolbar.status_action.setVisible(width >= 1100)
            self.main_toolbar.selector_action.setVisible(width >= 980)

        card_columns = 2 if width < 1250 else 4
        if hasattr(self, "dashboard_card_widgets"):
            self._reflow_grid(
                self.dashboard_cards_grid,
                self.dashboard_card_widgets,
                card_columns,
            )

        chart_columns = 1 if width < 1350 else 2
        if hasattr(self, "dashboard_chart_widgets"):
            self._reflow_grid(
                self.dashboard_charts_grid,
                self.dashboard_chart_widgets,
                chart_columns,
            )
        if hasattr(self, "analytics_chart_widgets"):
            self._reflow_grid(
                self.analytics_charts_grid,
                self.analytics_chart_widgets,
                chart_columns,
            )

    @staticmethod
    def _reflow_grid(grid, widgets, columns):
        for widget in widgets:
            grid.removeWidget(widget)
        for index, widget in enumerate(widgets):
            grid.addWidget(widget, index // columns, index % columns)
        for column in range(columns):
            grid.setColumnStretch(column, 1)

    def configure_data_tables(self):
        """Appliquer une présentation cohérente à tous les tableaux métier."""
        for table in self.findChildren(QTableWidget):
            table.setAlternatingRowColors(True)
            table.setShowGrid(False)
            table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            table.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(42)
            table.horizontalHeader().setMinimumHeight(40)
            table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
    
    def create_menu(self):
        """Créer le menu professionnel"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        new_action = file_menu.addAction("Nouveau projet")
        new_action.triggered.connect(self.nouvelle_bande)
        file_menu.addSeparator()
        save_action = file_menu.addAction("Enregistrer")
        save_action.triggered.connect(self.save_settings)
        save_as_action = file_menu.addAction("Enregistrer sous")
        save_as_action.triggered.connect(self.backup_database)
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu("Exporter")
        report_action = export_menu.addAction("Rapport texte / CSV")
        report_action.triggered.connect(self.export_report)
        excel_action = export_menu.addAction("Excel / CSV")
        excel_action.triggered.connect(self.export_bandes)
        image_action = export_menu.addAction("Capture de l'écran")
        image_action.triggered.connect(self.export_screenshot)
        
        file_menu.addSeparator()
        preferences_action = file_menu.addAction("Préférences")
        preferences_action.triggered.connect(
            lambda: self.show_page("parametres")
        )
        file_menu.addSeparator()
        cloture_action = file_menu.addAction("Clôturer la bande active")
        cloture_action.triggered.connect(self.cloturer_bande_active)
        file_menu.addSeparator()
        quit_action = file_menu.addAction("Quitter")
        quit_action.triggered.connect(self.close)
        
        # Menu Édition
        edit_menu = menubar.addMenu("Édition")
        undo_action = edit_menu.addAction("Annuler")
        undo_action.setEnabled(False)
        redo_action = edit_menu.addAction("Rétablir")
        redo_action.setEnabled(False)
        edit_menu.addSeparator()
        cut_action = edit_menu.addAction("Couper")
        cut_action.triggered.connect(lambda: self.dispatch_edit_action("cut"))
        copy_action = edit_menu.addAction("Copier")
        copy_action.triggered.connect(lambda: self.dispatch_edit_action("copy"))
        paste_action = edit_menu.addAction("Coller")
        paste_action.triggered.connect(lambda: self.dispatch_edit_action("paste"))
        
        # Menu Affichage
        view_menu = menubar.addMenu("Affichage")
        zoom_in = view_menu.addAction("Zoom avant")
        zoom_in.setEnabled(False)
        zoom_out = view_menu.addAction("Zoom arrière")
        zoom_out.setEnabled(False)
        view_menu.addSeparator()
        
        theme_menu = view_menu.addMenu("Thème")
        theme_menu.addAction("Institutionnel").triggered.connect(
            lambda: self.apply_theme("pro_avicole")
        )
        theme_menu.addAction("Fermier").triggered.connect(
            lambda: self.apply_theme("fermier")
        )
        
        view_menu.addSeparator()
        fullscreen_action = view_menu.addAction("Plein écran")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        documentation = help_menu.addAction("Documentation")
        documentation.triggered.connect(self.show_help)
        tutorials = help_menu.addAction("Tutoriels")
        tutorials.setEnabled(False)
        help_menu.addSeparator()
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about)
    
    def create_toolbar(self):
        """Créer la barre d'outils professionnelle"""
        self.main_toolbar = ProfessionalToolBar()
        self.addToolBar(self.main_toolbar)
        
        # Connecter les signaux
        self.main_toolbar.bande_combo.currentIndexChanged.connect(
            self.on_bande_selected
        )
        self.main_toolbar.new_action.triggered.connect(self.nouvelle_bande)
        self.main_toolbar.export_action.triggered.connect(self.export_bandes)
        self.main_toolbar.print_action.triggered.connect(self.print_current_page)
        self.main_toolbar.search_input.returnPressed.connect(
            self.search_current_page
        )
    
    def create_dashboard_page(self):
        """Créer la page dashboard professionnelle"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Tableau de bord")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        # Boutons d'action rapide
        action_buttons = QWidget()
        action_layout = QGridLayout(action_buttons)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        
        buttons = [
            ("Nouvelle bande", self.nouvelle_bande, "success"),
            ("Déclarer une mortalité", self.ajouter_mortalite, "primary"),
            ("Enregistrer une dépense", self.ajouter_depense, "warning"),
            ("Enregistrer une vente", self.ajouter_vente, "info"),
            ("Saisir aliment", self.ajouter_aliment, "secondary"),
            ("Nouvelle pesée", self.ajouter_pesee, "secondary"),
        ]
        
        for index, (text, callback, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self.theme_manager.get_button_style(style, 'small'))
            if callback:
                btn.clicked.connect(callback)
            action_layout.addWidget(btn, index // 2, index % 2)
        
        header_layout.addWidget(action_buttons)
        layout.addWidget(header)
        
        # Grille de cartes
        cards_grid = QGridLayout()
        cards_grid.setSpacing(20)
        self.dashboard_cards_grid = cards_grid
        self.dashboard_card_widgets = []
        
        self.cards = {}
        card_data = [
            ("Poulets disponibles", "restants", "#123B5D"),
            ("Taux de mortalité", "mortalite", "#B42318"),
            ("Dépenses cumulées", "depenses", "#A15C00"),
            ("Recettes cumulées", "recettes", "#18794E"),
            ("Résultat net", "benefice", "#6941C6"),
            ("Retour sur investissement", "roi", "#175CD3"),
            ("Indice de consommation", "ic", "#1E6B57"),
            ("GMQ", "gmq", "#0077B6"),
            ("Efficacité de production", "efficacite", "#1E6B57"),
            ("Revenu par sujet", "rentabilite", "#7A5C00")
        ]
        
        for i, (icon, key, color) in enumerate(card_data):
            row = i // 4
            col = i % 4
            card = ModernCard(icon, color=color)
            self.cards[key] = card
            self.dashboard_card_widgets.append(card)
            cards_grid.addWidget(card, row, col)
        
        layout.addLayout(cards_grid)
        
        # Graphiques en grille 2x2
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)
        
        charts_title = QLabel("Indicateurs et tendances")
        charts_title.setObjectName("subtitle")
        charts_layout.addWidget(charts_title)
        
        # Grille de graphiques
        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        self.dashboard_charts_grid = charts_grid
        
        # Graphique 1: Évolution des ventes
        self.chart_sales = AnalyticsChart("Évolution des ventes", "line")
        charts_grid.addWidget(self.chart_sales, 0, 0)
        
        # Graphique 2: Répartition des dépenses
        self.chart_expenses = AnalyticsChart("Répartition des dépenses", "pie")
        charts_grid.addWidget(self.chart_expenses, 0, 1)
        
        # Graphique 3: Mortalités
        self.chart_mortality = AnalyticsChart("Tendance des mortalités", "line")
        charts_grid.addWidget(self.chart_mortality, 1, 0)
        
        # Graphique 4: Croissance
        self.chart_comparison = AnalyticsChart("Croissance poids moyen", "line")
        charts_grid.addWidget(self.chart_comparison, 1, 1)
        self.dashboard_chart_widgets = [
            self.chart_sales,
            self.chart_expenses,
            self.chart_mortality,
            self.chart_comparison,
        ]
        
        charts_layout.addLayout(charts_grid)
        
        # Conteneur avec carte
        charts_frame = QFrame()
        charts_frame.setObjectName("sectionContainer")
        charts_frame_layout = QVBoxLayout(charts_frame)
        charts_frame_layout.setContentsMargins(0, 0, 0, 0)
        charts_frame_layout.addWidget(charts_container)
        
        layout.addWidget(charts_frame)
        
        # Tableau des dernières transactions
        recent_frame = QFrame()
        recent_frame.setObjectName("card")
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        
        recent_title = QWidget()
        recent_title_layout = QHBoxLayout(recent_title)
        recent_title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Activité récente")
        title_label.setObjectName("subtitle")
        recent_title_layout.addWidget(title_label)
        
        recent_title_layout.addStretch()
        
        filter_btn = QPushButton("Filtrer")
        filter_btn.setStyleSheet(self.theme_manager.get_button_style("secondary", "small"))
        filter_btn.clicked.connect(lambda: self.show_page("transactions"))
        recent_title_layout.addWidget(filter_btn)
        
        recent_layout.addWidget(recent_title)
        
        # Tableau
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Montant", "Statut"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        recent_layout.addWidget(self.recent_table)
        
        layout.addWidget(recent_frame)
        
        self.content_stack.addWidget(scroll)
    
    def create_bandes_page(self):
        """Créer la page de gestion des bandes"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        title = QLabel("Bandes d'élevage")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        # Boutons d'action
        action_buttons = QWidget()
        action_layout = QHBoxLayout(action_buttons)
        action_layout.setSpacing(10)
        
        action_btns = [
            ("Nouvelle bande", self.nouvelle_bande, "success"),
            ("Exporter", self.export_bandes, "secondary"),
            ("Actualiser", self.load_bandes, "primary")
        ]
        
        for text, callback, style in action_btns:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self.theme_manager.get_button_style(style, 'small'))
            if callback:
                btn.clicked.connect(callback)
            action_layout.addWidget(btn)
        
        header_layout.addWidget(action_buttons)
        layout.addWidget(header)
        
        # Tableau des bandes avec onglets
        tabs = QTabWidget()
        
        # Onglet Toutes les bandes
        all_bandes_tab = QWidget()
        all_layout = QVBoxLayout(all_bandes_tab)
        
        self.bandes_table = QTableWidget()
        self.bandes_table.setColumnCount(9)
        self.bandes_table.setHorizontalHeaderLabels(["ID", "Nom", "Activité", "Date début", "Initial",
                                                     "Restants", "Mortalité", "Bénéfice", "Actions"])
        self.bandes_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.bandes_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.bandes_table.horizontalHeader().setSectionResizeMode(
            8, QHeaderView.ResizeMode.Fixed
        )
        self.bandes_table.setColumnWidth(8, 220)
        self.bandes_table.verticalHeader().setVisible(False)
        self.bandes_table.verticalHeader().setDefaultSectionSize(52)
        all_layout.addWidget(self.bandes_table)
        
        # Onglet Statistiques
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        stats_data = [
            ("Bandes actives", "5", "#1E88E5"),
            ("Total poulets", "1250", "#4CAF50"),
            ("Taux mortalité", "4.2%", "#E53935"),
            ("Bénéfice total", "1,250,000 FCFA", "#FF9800")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            card = ModernCard(title, color=color)
            card.update_value(value)
            stats_grid.addWidget(card, i // 2, i % 2)
        
        stats_layout.addLayout(stats_grid)
        
        tabs.addTab(all_bandes_tab, "Toutes les bandes")
        tabs.addTab(stats_tab, "Statistiques")
        
        layout.addWidget(tabs)
        
        self.content_stack.addWidget(page)
    
    def create_transactions_page(self):
        """Créer la page des transactions avec onglets horizontaux"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        title = QLabel("Transactions")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        # Filtres
        filters = QWidget()
        filters_layout = QHBoxLayout(filters)
        filters_layout.setSpacing(10)
        
        period_combo = QComboBox()
        period_combo.addItems(["Aujourd'hui", "7 derniers jours", "30 derniers jours", "3 mois", "Tout"])
        self.transaction_period_combo = period_combo
        filters_layout.addWidget(QLabel("Période:"))
        filters_layout.addWidget(period_combo)
        
        bande_combo = QComboBox()
        bande_combo.addItem("Toutes les bandes", None)
        self.transaction_bande_combo = bande_combo
        filters_layout.addWidget(QLabel("Bande:"))
        filters_layout.addWidget(bande_combo)
        
        filters_layout.addStretch()
        
        export_btn = QPushButton("Exporter")
        export_btn.setStyleSheet(self.theme_manager.get_button_style("secondary", "small"))
        export_btn.clicked.connect(self.export_transactions)
        filters_layout.addWidget(export_btn)
        period_combo.currentIndexChanged.connect(self.filter_transactions)
        bande_combo.currentIndexChanged.connect(self.filter_transactions)
        
        header_layout.addWidget(filters)
        layout.addWidget(header)
        
        # Onglets des transactions
        self.trans_tabs = QTabWidget()
        self.trans_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Onglet Mortalités
        mortalites_tab = QWidget()
        mortalites_layout = QVBoxLayout(mortalites_tab)
        mortalites_layout.setContentsMargins(10, 10, 10, 10)
        
        mortalites_header = QHBoxLayout()
        mortalites_header.addWidget(QLabel("Mortalités déclarées"))
        mortalites_header.addStretch()
        
        add_mortalite_btn = QPushButton("Ajouter")
        add_mortalite_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_mortalite_btn.clicked.connect(self.ajouter_mortalite)
        mortalites_header.addWidget(add_mortalite_btn)
        
        mortalites_layout.addLayout(mortalites_header)
        
        self.mortalites_table = QTableWidget()
        self.mortalites_table.setColumnCount(7)
        self.mortalites_table.setHorizontalHeaderLabels([
            "Date",
            "Bande",
            "Nombre",
            "Cause",
            "Observation",
            "Taux",
            "Actions",
        ])
        mortalites_layout.addWidget(self.mortalites_table)
        
        # Onglet Dépenses
        depenses_tab = QWidget()
        depenses_layout = QVBoxLayout(depenses_tab)
        depenses_layout.setContentsMargins(10, 10, 10, 10)
        
        depenses_header = QHBoxLayout()
        depenses_header.addWidget(QLabel("Dépenses enregistrées"))
        depenses_header.addStretch()
        
        add_depense_btn = QPushButton("Ajouter")
        add_depense_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_depense_btn.clicked.connect(self.ajouter_depense)
        depenses_header.addWidget(add_depense_btn)
        
        depenses_layout.addLayout(depenses_header)
        
        self.depenses_table = QTableWidget()
        self.depenses_table.setColumnCount(7)
        self.depenses_table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Montant", "Bande", "Catégorie", "Actions"])
        depenses_layout.addWidget(self.depenses_table)
        
        # Onglet Ventes
        ventes_tab = QWidget()
        ventes_layout = QVBoxLayout(ventes_tab)
        ventes_layout.setContentsMargins(10, 10, 10, 10)
        
        ventes_header = QHBoxLayout()
        ventes_header.addWidget(QLabel("Ventes enregistrées"))
        ventes_header.addStretch()
        
        add_vente_btn = QPushButton("Ajouter")
        add_vente_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_vente_btn.clicked.connect(self.ajouter_vente)
        ventes_header.addWidget(add_vente_btn)
        
        ventes_layout.addLayout(ventes_header)
        
        self.ventes_table = QTableWidget()
        self.ventes_table.setColumnCount(8)
        self.ventes_table.setHorizontalHeaderLabels(["Date", "Bande", "Nombre", "Prix unitaire", "Total", "Client", "Moyen", "Actions"])
        ventes_layout.addWidget(self.ventes_table)

        # Onglet Aliment
        aliment_tab = QWidget()
        aliment_layout = QVBoxLayout(aliment_tab)
        aliment_layout.setContentsMargins(10, 10, 10, 10)

        aliment_header = QHBoxLayout()
        aliment_header.addWidget(QLabel("Aliment distribué"))
        aliment_header.addStretch()

        add_aliment_btn = QPushButton("Ajouter")
        add_aliment_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_aliment_btn.clicked.connect(self.ajouter_aliment)
        aliment_header.addWidget(add_aliment_btn)

        aliment_layout.addLayout(aliment_header)

        self.aliment_table = QTableWidget()
        self.aliment_table.setColumnCount(7)
        self.aliment_table.setHorizontalHeaderLabels([
            "Date",
            "Bande",
            "Quantité",
            "Type",
            "Observation",
            "Indicateur",
            "Actions",
        ])
        aliment_layout.addWidget(self.aliment_table)

        # Onglet Pesées
        pesees_tab = QWidget()
        pesees_layout = QVBoxLayout(pesees_tab)
        pesees_layout.setContentsMargins(10, 10, 10, 10)

        pesees_header = QHBoxLayout()
        pesees_header.addWidget(QLabel("Pesées de croissance"))
        pesees_header.addStretch()

        add_pesee_btn = QPushButton("Ajouter")
        add_pesee_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_pesee_btn.clicked.connect(self.ajouter_pesee)
        pesees_header.addWidget(add_pesee_btn)

        pesees_layout.addLayout(pesees_header)

        self.pesees_table = QTableWidget()
        self.pesees_table.setColumnCount(7)
        self.pesees_table.setHorizontalHeaderLabels([
            "Date",
            "Bande",
            "Poids moyen",
            "Effectif pesé",
            "Observation",
            "Indicateur",
            "Actions",
        ])
        pesees_layout.addWidget(self.pesees_table)

        # Onglet Œufs
        oeufs_tab = QWidget()
        oeufs_layout = QVBoxLayout(oeufs_tab)
        oeufs_layout.setContentsMargins(10, 10, 10, 10)

        oeufs_header = QHBoxLayout()
        oeufs_header.addWidget(QLabel("Production d'œufs"))
        oeufs_header.addStretch()

        add_ponte_btn = QPushButton("Ajouter une ponte")
        add_ponte_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_ponte_btn.clicked.connect(self.ajouter_ponte)
        oeufs_header.addWidget(add_ponte_btn)

        add_vente_oeufs_btn = QPushButton("Vendre des œufs")
        add_vente_oeufs_btn.setStyleSheet(self.theme_manager.get_button_style("secondary", "small"))
        add_vente_oeufs_btn.clicked.connect(self.ajouter_vente_oeufs)
        oeufs_header.addWidget(add_vente_oeufs_btn)

        oeufs_layout.addLayout(oeufs_header)

        self.oeufs_summary_label = QLabel(
            "Sélectionnez une bande pour voir le stock d'œufs et le taux de ponte."
        )
        self.oeufs_summary_label.setObjectName("summary")
        oeufs_layout.addWidget(self.oeufs_summary_label)

        self.ponte_table = QTableWidget()
        self.ponte_table.setColumnCount(6)
        self.ponte_table.setHorizontalHeaderLabels([
            "Date",
            "Bande",
            "Œufs",
            "Taux du jour",
            "Observation",
            "Actions",
        ])
        oeufs_layout.addWidget(self.ponte_table)

        ventes_oeufs_label = QLabel("Ventes d'œufs")
        oeufs_layout.addWidget(ventes_oeufs_label)

        self.ventes_oeufs_table = QTableWidget()
        self.ventes_oeufs_table.setColumnCount(6)
        self.ventes_oeufs_table.setHorizontalHeaderLabels([
            "Date",
            "Bande",
            "Quantité",
            "Prix unitaire",
            "Total",
            "Client",
        ])
        oeufs_layout.addWidget(self.ventes_oeufs_table)

        # Onglet Stocks
        stocks_tab = QWidget()
        stocks_layout = QVBoxLayout(stocks_tab)
        stocks_layout.setContentsMargins(10, 10, 10, 10)

        stocks_header = QHBoxLayout()
        stocks_header.addWidget(QLabel("Gestion des stocks"))
        stocks_header.addStretch()

        add_article_btn = QPushButton("Nouvel article")
        add_article_btn.setStyleSheet(self.theme_manager.get_button_style("secondary", "small"))
        add_article_btn.clicked.connect(self.nouvel_article_stock)
        stocks_header.addWidget(add_article_btn)

        add_entree_stock_btn = QPushButton("Entrée de stock")
        add_entree_stock_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        add_entree_stock_btn.clicked.connect(self.ajouter_entree_stock)
        stocks_header.addWidget(add_entree_stock_btn)

        add_sortie_stock_btn = QPushButton("Sortie de stock")
        add_sortie_stock_btn.setStyleSheet(self.theme_manager.get_button_style("secondary", "small"))
        add_sortie_stock_btn.clicked.connect(self.ajouter_sortie_stock)
        stocks_header.addWidget(add_sortie_stock_btn)

        stocks_layout.addLayout(stocks_header)

        self.stocks_table = QTableWidget()
        self.stocks_table.setColumnCount(6)
        self.stocks_table.setHorizontalHeaderLabels([
            "Article",
            "Catégorie",
            "Unité",
            "Stock actuel",
            "Seuil d'alerte",
            "Statut",
        ])
        stocks_layout.addWidget(self.stocks_table)

        self.trans_tabs.addTab(mortalites_tab, "Mortalités")
        self.trans_tabs.addTab(depenses_tab, "Dépenses")
        self.trans_tabs.addTab(ventes_tab, "Ventes")
        self.trans_tabs.addTab(aliment_tab, "Aliment")
        self.trans_tabs.addTab(pesees_tab, "Pesées")
        self.trans_tabs.addTab(oeufs_tab, "Œufs")
        self.trans_tabs.addTab(stocks_tab, "Stocks")
        
        layout.addWidget(self.trans_tabs)
        
        self.content_stack.addWidget(page)
    
    def create_analytics_page(self):
        """Créer la page analytique avancée"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        title = QLabel("Analyse décisionnelle")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        # Période d'analyse
        period_widget = QWidget()
        period_layout = QHBoxLayout(period_widget)
        period_layout.setSpacing(10)
        
        period_layout.addWidget(QLabel("Période:"))
        
        start_date = QDateEdit()
        start_date.setDate(QDate.currentDate().addMonths(-3))
        period_layout.addWidget(start_date)
        
        period_layout.addWidget(QLabel("à"))
        
        end_date = QDateEdit()
        end_date.setDate(QDate.currentDate())
        period_layout.addWidget(end_date)
        
        apply_btn = QPushButton("Appliquer")
        apply_btn.setStyleSheet(self.theme_manager.get_button_style("primary", "small"))
        apply_btn.clicked.connect(
            lambda: self.refresh_analytics(start_date.date(), end_date.date())
        )
        period_layout.addWidget(apply_btn)
        
        header_layout.addWidget(period_widget)
        layout.addWidget(header)
        
        # Graphiques principaux
        main_charts = QWidget()
        main_layout = QVBoxLayout(main_charts)
        
        # Grille 2x2
        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        self.analytics_charts_grid = charts_grid
        
        # Graphique 1: Performance financière
        finance_chart = AnalyticsChart("Performance financière", "line")
        self.analytics_finance_chart = finance_chart
        charts_grid.addWidget(finance_chart, 0, 0)
        
        # Graphique 2: Analyse des coûts
        cost_chart = AnalyticsChart("Analyse des coûts", "pie")
        self.analytics_cost_chart = cost_chart
        charts_grid.addWidget(cost_chart, 0, 1)
        
        # Graphique 3: Tendance des mortalités
        mortality_chart = AnalyticsChart("Tendance des mortalités", "line")
        self.analytics_mortality_chart = mortality_chart
        charts_grid.addWidget(mortality_chart, 1, 0)
        
        # Graphique 4: Productivité
        productivity_chart = AnalyticsChart("Productivité", "bar")
        self.analytics_productivity_chart = productivity_chart
        charts_grid.addWidget(productivity_chart, 1, 1)
        self.analytics_chart_widgets = [
            finance_chart,
            cost_chart,
            mortality_chart,
            productivity_chart,
        ]
        
        main_layout.addLayout(charts_grid)
        
        layout.addWidget(main_charts)
        
        # Métriques KPIs
        kpis_widget = QWidget()
        kpis_layout = QGridLayout(kpis_widget)
        kpis_layout.setSpacing(15)
        
        kpi_data = [
            ("ROI", "28.5%", "+2.3%", "success"),
            ("Coût par poulet", "1,250 FCFA", "-150 FCFA", "success"),
            ("Taux mortalité", "4.2%", "+0.5%", "warning"),
            ("Prix moyen vente", "2,800 FCFA", "+200 FCFA", "success"),
            ("Bénéfice/m²", "15,000 FCFA", "+1,200 FCFA", "success"),
            ("Efficacité aliment", "82%", "+3%", "success")
        ]
        
        for i, (title, value, change, status) in enumerate(kpi_data):
            card = ModernCard(title, color="#1E88E5")
            card.update_value(value, change)
            kpis_layout.addWidget(card, i // 3, i % 3)
        
        layout.addWidget(kpis_widget)
        
        self.content_stack.addWidget(scroll)
    
    def create_reports_page(self):
        """Créer la page des rapports"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Rapports et éditions")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Options de rapport
        options = QWidget()
        options_layout = QGridLayout(options)
        options_layout.setSpacing(20)
        
        # Type de rapport
        report_type = QComboBox()
        report_type.addItems(["Rapport financier", "Rapport production", "Rapport sanitaire", "Rapport complet"])
        self.report_type_combo = report_type
        options_layout.addWidget(QLabel("Type de rapport:"), 0, 0)
        options_layout.addWidget(report_type, 0, 1)
        
        # Format
        format_combo = QComboBox()
        format_combo.addItems(["Texte", "CSV"])
        self.report_format_combo = format_combo
        options_layout.addWidget(QLabel("Format:"), 1, 0)
        options_layout.addWidget(format_combo, 1, 1)
        
        # Boutons d'action
        generate_btn = QPushButton("Générer")
        generate_btn.setStyleSheet(self.theme_manager.get_button_style("success"))
        generate_btn.clicked.connect(self.generate_report)
        options_layout.addWidget(generate_btn, 0, 2)
        
        export_btn = QPushButton("Exporter")
        export_btn.setStyleSheet(self.theme_manager.get_button_style("primary"))
        export_btn.clicked.connect(self.export_report)
        options_layout.addWidget(export_btn, 1, 2)
        options_layout.setColumnStretch(1, 1)
        
        layout.addWidget(options)
        
        # Aperçu du rapport
        preview = QTextEdit()
        self.report_preview = preview
        preview.setReadOnly(True)
        preview.setMinimumHeight(400)
        preview.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px;
                background-color: white;
                font-family: 'Courier New', monospace;
            }
        """)
        
        layout.addWidget(preview)
        
        self.content_stack.addWidget(page)
    
    def create_settings_page(self):
        """Créer la page des paramètres"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Paramètres et configuration")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Onglets des paramètres
        settings_tabs = QTabWidget()
        
        # Onglet Apparence
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Thème
        theme_group = QGroupBox("Thème de l'interface")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Institutionnel", "Fermier"])
        theme_combo.setCurrentText("Institutionnel")
        theme_combo.currentTextChanged.connect(
            lambda name: self.apply_theme(
                "fermier" if name == "Fermier" else "pro_avicole"
            )
        )
        theme_layout.addWidget(theme_combo)
        
        # Prévisualisation
        preview = QLabel("Aperçu du thème")
        preview.setFixedHeight(100)
        preview.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0B1F33, stop:0.82 #123B5D, stop:0.83 #C9A227);
                border-radius: 8px;
                color: white;
                padding: 20px;
                font-weight: 600;
            }
        """)
        theme_layout.addWidget(preview)
        
        appearance_layout.addWidget(theme_group)
        appearance_layout.addStretch()
        
        # Onglet Données
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        backup_group = QGroupBox("Sauvegarde des données")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_btn = QPushButton("Sauvegarder maintenant")
        backup_btn.setStyleSheet(self.theme_manager.get_button_style("primary"))
        backup_btn.clicked.connect(self.backup_database)
        backup_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("Restaurer")
        restore_btn.setStyleSheet(self.theme_manager.get_button_style("secondary"))
        restore_btn.clicked.connect(self.restore_database)
        backup_layout.addWidget(restore_btn)
        
        data_layout.addWidget(backup_group)
        data_layout.addStretch()
        
        settings_tabs.addTab(appearance_tab, "Apparence")
        settings_tabs.addTab(data_tab, "Données")
        
        layout.addWidget(settings_tabs)
        
        # Boutons d'action
        action_buttons = QWidget()
        action_layout = QHBoxLayout(action_buttons)
        action_layout.addStretch()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet(self.theme_manager.get_button_style("success"))
        save_btn.clicked.connect(self.save_settings)
        action_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(self.theme_manager.get_button_style("secondary"))
        cancel_btn.clicked.connect(self.show_dashboard)
        action_layout.addWidget(cancel_btn)
        
        layout.addWidget(action_buttons)
        
        self.content_stack.addWidget(page)
    
    def create_statusbar(self):
        """Créer la barre de statut professionnelle"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        # Widget de statut
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(20)
        
        # Indicateur de connexion
        connection = QLabel("●  Connecté")
        connection.setObjectName("systemStatus")
        status_layout.addWidget(connection)
        
        status_layout.addWidget(self.create_separator())
        
        # Base de données
        db_status = QLabel("Base de données : opérationnelle")
        db_status.setObjectName("mutedText")
        status_layout.addWidget(db_status)
        
        status_layout.addWidget(self.create_separator())
        
        # Mémoire
        memory = QLabel("Session sécurisée")
        memory.setObjectName("mutedText")
        status_layout.addWidget(memory)
        
        status_layout.addStretch()
        
        # Heure et date
        self.time_label = QLabel()
        self.update_time()
        status_layout.addWidget(self.time_label)
        
        statusbar.addWidget(status_widget)
        
        # Timer pour l'heure
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)
    
    def create_separator(self):
        """Créer un séparateur vertical"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #E0E0E0;")
        separator.setFixedWidth(1)
        return separator
    
    def update_time(self):
        """Mettre à jour l'heure"""
        now = datetime.now()
        self.time_label.setText(now.strftime("%d/%m/%Y  •  %H:%M:%S"))
    
    def connect_navigation(self):
        """Connecter les boutons de navigation"""
        for btn, page in self.sidebar.nav_buttons:
            btn.clicked.connect(lambda checked, p=page: self.show_page(p))
    
    def show_page(self, page_name):
        """Afficher une page spécifique"""
        page_map = {
            'dashboard': 0,
            'bandes': 1,
            'transactions': 2,
            'analytiques': 3,
            'rapports': 4,
            'parametres': 5
        }
        
        if page_name in page_map:
            self.content_stack.setCurrentIndex(page_map[page_name])
            
            # Mettre à jour les boutons de navigation
            for btn, page in self.sidebar.nav_buttons:
                btn.setChecked(page == page_name)
    
    def show_dashboard(self):
        """Afficher le dashboard"""
        self.show_page('dashboard')
    
    def apply_theme(self, theme_name=None):
        """Appliquer le thème"""
        if theme_name:
            self.theme_manager.set_theme(theme_name)
        
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        self.restyle_buttons()
        theme = self.theme_manager.get_theme()
        for chart in self.findChildren(PremiumAnalyticsChart):
            chart.apply_theme(theme)

    def restyle_buttons(self):
        """Réappliquer les variantes de boutons après un changement de thème."""
        secondary = {
            "Annuler", "Exporter", "Filtrer", "Restaurer", "Modifier"
        }
        success = {
            "Nouvelle bande", "Générer", "Enregistrer",
            "Sauvegarder maintenant", "Enregistrer la vente"
        }
        warning = {"Enregistrer une dépense"}
        for button in self.findChildren(QPushButton):
            if (
                button.property("nav") == "true"
                or button.property("tableAction") is True
            ):
                continue
            text = button.text().strip()
            if text in secondary:
                variant = "secondary"
            elif text in success:
                variant = "success"
            elif text in warning:
                variant = "warning"
            else:
                variant = "primary"
            button.setStyleSheet(
                self.theme_manager.get_button_style(variant, "small")
            )
    
    def load_bandes(self):
        """Charger les bandes"""
        try:
            bandes = self.db.get_bandes()
            
            # Mettre à jour la combo box
            toolbar = self.findChild(ProfessionalToolBar)
            if toolbar:
                toolbar.bande_combo.clear()
                toolbar.bande_combo.addItem("Sélectionner une bande", None)
                
                for bande in bandes:
                    toolbar.bande_combo.addItem(f"{bande[1]} ({bande[2]})", bande[0])

            if hasattr(self, "transaction_bande_combo"):
                selected = self.transaction_bande_combo.currentData()
                self.transaction_bande_combo.blockSignals(True)
                self.transaction_bande_combo.clear()
                self.transaction_bande_combo.addItem("Toutes les bandes", None)
                for bande in bandes:
                    self.transaction_bande_combo.addItem(bande[1], bande[0])
                selected_index = self.transaction_bande_combo.findData(selected)
                self.transaction_bande_combo.setCurrentIndex(max(0, selected_index))
                self.transaction_bande_combo.blockSignals(False)
            
            # Mettre à jour le tableau des bandes
            if hasattr(self, 'bandes_table'):
                self.bandes_table.setRowCount(len(bandes))
                for row, bande in enumerate(bandes):
                    bande_id = bande[0]
                    initial = int(bande[3] or 0)
                    restants = self.db.get_poulets_restants(bande_id)
                    morts = self.db.get_total_mortalites(bande_id)
                    cout_total = self.db.get_total_couts(bande_id) or 0
                    ventes = self.db.get_total_ventes(bande_id) or 0
                    benefice = ventes - cout_total
                    mortalite = (morts / initial * 100) if initial else 0

                    activite = bande[6] if len(bande) > 6 and bande[6] else "chair"
                    activite_label = (
                        "Poule pondeuse" if activite == "ponte" else "Poulet de chair"
                    )
                    values = [
                        bande_id,
                        bande[1],
                        activite_label,
                        bande[2],
                        f"{initial:,}",
                        f"{restants:,}",
                        f"{mortalite:.1f} %",
                        f"{benefice:,.0f} FCFA",
                    ]
                    for col, value in enumerate(values):
                        self.bandes_table.setItem(
                            row, col, QTableWidgetItem(str(value))
                        )
                    
                    # Colonne actions
                    btn_widget = QWidget()
                    btn_widget.setObjectName("tableActions")
                    btn_widget.setMinimumHeight(50)
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(8, 7, 8, 7)
                    btn_layout.setSpacing(8)
                    
                    view_btn = QPushButton("Voir")
                    view_btn.setObjectName("tableActionPrimary")
                    view_btn.setProperty("tableAction", True)
                    view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    view_btn.setFixedSize(78, 34)
                    view_btn.clicked.connect(lambda checked, b=bande_id: self.view_bande(b))
                    
                    edit_btn = QPushButton("Modifier")
                    edit_btn.setObjectName("tableActionSecondary")
                    edit_btn.setProperty("tableAction", True)
                    edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    edit_btn.setFixedSize(98, 34)
                    edit_btn.clicked.connect(
                        lambda checked, b=bande_id: self.edit_bande(b)
                    )
                    
                    btn_layout.addStretch()
                    btn_layout.addWidget(view_btn)
                    btn_layout.addWidget(edit_btn)
                    btn_layout.addStretch()
                    
                    self.bandes_table.setCellWidget(row, 8, btn_widget)
                    self.bandes_table.setRowHeight(row, 52)

            self.load_transactions()
        
        except Exception as e:
            print(f"Erreur lors du chargement des bandes: {e}")
    
    def on_bande_selected(self):
        """Quand une bande est sélectionnée"""
        toolbar = self.findChild(ProfessionalToolBar)
        if toolbar:
            bande_id = toolbar.bande_combo.currentData()
            if bande_id:
                self.current_bande_id = bande_id
                self.update_dashboard()

    @staticmethod
    def _days_between(date_debut, date_fin):
        try:
            debut = datetime.strptime(str(date_debut), "%Y-%m-%d")
            fin = datetime.strptime(str(date_fin), "%Y-%m-%d")
        except (TypeError, ValueError):
            return 0
        return (fin - debut).days

    def _zootechnie_metrics_for_bande(self, bande_info):
        bande_id = bande_info[0]
        restants = self.db.get_poulets_restants(bande_id) or 0
        total_aliment_kg = self.db.get_total_aliment_kg(bande_id) or 0
        latest_pesee = self.db.get_latest_pesee(bande_id)
        first_pesee = self.db.get_first_pesee(bande_id)
        poids_moyen_g = latest_pesee[3] if latest_pesee else 0
        poids_vif_restant_kg = indicators.poids_vif_estime_kg(restants, poids_moyen_g)
        poids_vendu_kg = self.db.get_total_poids_vendu(bande_id) or 0
        poids_vif_kg = indicators.poids_vif_produit_kg(
            poids_vif_restant_kg, poids_vendu_kg
        )
        ic = indicators.indice_consommation(total_aliment_kg, poids_vif_kg)
        gmq = 0.0
        if latest_pesee:
            if first_pesee and first_pesee[0] != latest_pesee[0]:
                jours = self._days_between(first_pesee[2], latest_pesee[2])
                poids_initial_g = first_pesee[3]
            else:
                jours = self._days_between(bande_info[2], latest_pesee[2])
                poids_initial_g = 0
            gmq = indicators.gain_moyen_quotidien(
                poids_initial_g, latest_pesee[3], jours
            )
        return {
            "total_aliment_kg": total_aliment_kg,
            "poids_moyen_g": poids_moyen_g,
            "poids_vif_kg": poids_vif_kg,
            "ic": ic,
            "gmq": gmq,
        }
    
    def update_dashboard(self):
        """Mettre à jour le dashboard"""
        if not self.current_bande_id:
            return
        
        try:
            bande_info = self.db.get_bande_info(self.current_bande_id)
            if not bande_info:
                return
            
            # Récupérer les données
            total_morts = self.db.get_total_mortalites(self.current_bande_id) or 0
            total_depenses = self.db.get_total_depenses(self.current_bande_id) or 0
            cout_initial = self.db.get_cout_initial(self.current_bande_id) or 0
            total_couts = self.db.get_total_couts(self.current_bande_id) or 0
            total_ventes = self.db.get_total_ventes(self.current_bande_id) or 0
            restants = self.db.get_poulets_restants(self.current_bande_id) or 0
            total_vendus = self.db.get_total_vendus(self.current_bande_id) or 0
            zootech = self._zootechnie_metrics_for_bande(bande_info)
            
            # Calculs (source unique : indicators.py)
            nombre_initial = bande_info[3]
            taux_mortalite = indicators.taux_mortalite(total_morts, nombre_initial)
            benefice = indicators.benefice(total_ventes, total_couts)
            prix_moyen = indicators.prix_moyen(total_ventes, total_vendus)
            efficacite = indicators.efficacite(total_vendus, nombre_initial)
            roi = indicators.roi(benefice, total_couts)
            total_aliment_kg = zootech["total_aliment_kg"]
            poids_moyen_g = zootech["poids_moyen_g"]
            poids_vif_kg = zootech["poids_vif_kg"]
            ic = zootech["ic"]
            gmq = zootech["gmq"]
            
            # Mettre à jour les cartes
            if hasattr(self, 'cards'):
                self.cards['restants'].update_value(
                    f"{restants}",
                    f"Sur {nombre_initial} initial"
                )
                
                self.cards['mortalite'].update_value(
                    f"{taux_mortalite:.1f}%",
                    f"{total_morts} poulets",
                    "À surveiller" if taux_mortalite > 5 else "Conforme",
                    "warning" if taux_mortalite > 5 else "success"
                )
                
                self.cards['depenses'].update_value(
                    f"{total_couts:,.0f}",
                    f"FCFA - achat {cout_initial:,.0f} + dépenses {total_depenses:,.0f}"
                )
                
                self.cards['recettes'].update_value(
                    f"{total_ventes:,.0f}",
                    "FCFA"
                )
                
                self.cards['benefice'].update_value(
                    f"{benefice:,.0f}",
                    "FCFA",
                    "Positif" if benefice > 0 else "Déficitaire",
                    "success" if benefice > 0 else "error"
                )
                
                self.cards['roi'].update_value(
                    f"{roi:.1f}%",
                    "Retour sur investissement"
                )

                self.cards['ic'].update_value(
                    f"{ic:.2f}" if ic else "—",
                    (
                        f"{total_aliment_kg:,.1f} kg aliment / "
                        f"{poids_vif_kg:,.1f} kg vif"
                    ) if poids_vif_kg else "Pesée requise pour calculer l'IC",
                    "Calculé" if ic else "À compléter",
                    "success" if ic else "warning",
                )

                self.cards['gmq'].update_value(
                    f"{gmq:.1f} g/j" if gmq else "—",
                    f"Dernier poids moyen : {poids_moyen_g:,.0f} g"
                    if poids_moyen_g else "Pesée requise",
                    "Calculé" if gmq else "À compléter",
                    "success" if gmq else "warning",
                )
                
                self.cards['efficacite'].update_value(
                    f"{efficacite:.1f}%",
                    f"{total_vendus} vendus"
                )
                
                self.cards['rentabilite'].update_value(
                    f"{prix_moyen:,.0f}",
                    "FCFA/poulet"
                )
            
            # Mettre à jour les graphiques
            self.update_charts()
            
            # Mettre à jour les transactions récentes
            self.update_recent_transactions()
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour du dashboard: {e}")
    
    def update_charts(self):
        """Mettre à jour tous les graphiques"""
        if not self.current_bande_id:
            return
        
        try:
            cursor = self.db.conn.cursor()
            
            # Données pour le graphique des ventes
            cursor.execute('''
                SELECT date, SUM(montant_total) 
                FROM ventes 
                WHERE bande_id = ? 
                GROUP BY date 
                ORDER BY date
                LIMIT 10
            ''', (self.current_bande_id,))
            ventes_data = cursor.fetchall()
            
            if ventes_data and hasattr(self, 'chart_sales'):
                dates = [row[0][5:] for row in ventes_data]  # JJ-MM
                valeurs = [row[1] for row in ventes_data]
                self.chart_sales.update_chart(valeurs, dates)
            
            # Données pour le graphique des dépenses
            cursor.execute('''
                SELECT type_depense, SUM(montant) 
                FROM depenses 
                WHERE bande_id = ? 
                GROUP BY type_depense
            ''', (self.current_bande_id,))
            depenses_data = cursor.fetchall()
            
            if depenses_data and hasattr(self, 'chart_expenses'):
                types = [row[0] for row in depenses_data]
                valeurs = [row[1] for row in depenses_data]
                self.chart_expenses.update_chart(valeurs, types)
            
            # Données pour le graphique des mortalités
            cursor.execute('''
                SELECT date, SUM(nombre_morts) 
                FROM mortalites 
                WHERE bande_id = ? 
                GROUP BY date 
                ORDER BY date
                LIMIT 10
            ''', (self.current_bande_id,))
            mortalites_data = cursor.fetchall()
            
            if mortalites_data and hasattr(self, 'chart_mortality'):
                dates = [row[0][5:] for row in mortalites_data]
                valeurs = [row[1] for row in mortalites_data]
                self.chart_mortality.update_chart(valeurs, dates)

            if hasattr(self, "chart_comparison"):
                pesees = list(reversed(self.db.get_pesees(self.current_bande_id)))[:10]
                labels = [row[2][5:] for row in pesees]
                results = [row[3] for row in pesees]
                self.chart_comparison.update_chart(
                    results or [0], labels or ["Aucune pesée"]
                )
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour des graphiques: {e}")
    
    def update_recent_transactions(self):
        """Mettre à jour les transactions récentes"""
        if not self.current_bande_id:
            return
        
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                SELECT 'SAN' as icon, date, 'Mortalité' as type, 
                       nombre_morts || ' poulets' as description,
                       NULL as montant, cause as info
                FROM mortalites 
                WHERE bande_id = ?
                UNION ALL
                SELECT 'DEP' as icon, date, 'Dépense' as type, 
                       type_depense as description,
                       montant, COALESCE(description, '') as info
                FROM depenses 
                WHERE bande_id = ?
                UNION ALL
                SELECT 'VTE' as icon, date, 'Vente' as type, 
                       nombre_poulets || ' poulets' as description,
                       montant_total, '' as info
                FROM ventes 
                WHERE bande_id = ?
                UNION ALL
                SELECT 'ALI' as icon, date, 'Aliment' as type,
                       quantite_kg || ' kg distribues' as description,
                       NULL as montant, COALESCE(type_aliment, '') as info
                FROM consommations_aliment
                WHERE bande_id = ?
                UNION ALL
                SELECT 'PES' as icon, date, 'Pesee' as type,
                       poids_moyen_g || ' g moyen' as description,
                       NULL as montant, effectif_pese || ' sujets peses' as info
                FROM pesees
                WHERE bande_id = ?
                ORDER BY date DESC
                LIMIT 10
            ''', (
                self.current_bande_id,
                self.current_bande_id,
                self.current_bande_id,
                self.current_bande_id,
                self.current_bande_id,
            ))
            
            transactions = cursor.fetchall()
            
            if hasattr(self, 'recent_table'):
                self.recent_table.setRowCount(len(transactions))
                
                for row, trans in enumerate(transactions):
                    # Date
                    date_item = QTableWidgetItem(trans[1])
                    self.recent_table.setItem(row, 0, date_item)
                    
                    # Type avec icône
                    type_item = QTableWidgetItem(f"{trans[0]} {trans[2]}")
                    self.recent_table.setItem(row, 1, type_item)
                    
                    # Description
                    desc_item = QTableWidgetItem(trans[3])
                    self.recent_table.setItem(row, 2, desc_item)
                    
                    # Montant
                    montant = trans[4] or 0
                    montant_item = QTableWidgetItem(f"{montant:,.0f} FCFA" if montant else "")
                    self.recent_table.setItem(row, 3, montant_item)
                    
                    # Statut/Info
                    info_item = QTableWidgetItem(trans[5])
                    self.recent_table.setItem(row, 4, info_item)
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour des transactions: {e}")
    
    def view_bande(self, bande_id):
        """Voir les détails d'une bande"""
        self.current_bande_id = bande_id
        self.show_dashboard()
        
        # Mettre à jour la combo box
        toolbar = self.findChild(ProfessionalToolBar)
        if toolbar:
            for i in range(toolbar.bande_combo.count()):
                if toolbar.bande_combo.itemData(i) == bande_id:
                    toolbar.bande_combo.setCurrentIndex(i)
                    break

    def edit_bande(self, bande_id):
        from dialogs import NouvelleBandeDialog

        bande = self.db.get_bande_info(bande_id)
        if not bande:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande introuvable",
                "Cette bande n'existe plus dans la base de données.",
            )
            return
        dialog = NouvelleBandeDialog(self, bande=bande)
        if dialog.exec():
            data = dialog.get_data()
            self.db.modifier_bande(
                bande_id,
                data["nom"],
                data["date"],
                data["nombre"],
                data["prix"],
            )
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Mise à jour terminée",
                "La bande a été mise à jour.",
            )

    def load_transactions(self):
        """Charger les trois journaux de transactions."""
        cursor = self.db.conn.cursor()
        if hasattr(self, "mortalites_table"):
            rows = cursor.execute(
                """
                SELECT m.date, b.nom_bande, m.nombre_morts, m.cause,
                       m.description
                FROM mortalites m
                LEFT JOIN bandes b ON b.id = m.bande_id
                ORDER BY m.date DESC, m.id DESC
                """
            ).fetchall()
            self.mortalites_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1] or "",
                    row[2],
                    row[3] or "",
                    row[4] or "",
                    "",
                    "",
                ]
                for column, value in enumerate(values):
                    self.mortalites_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "depenses_table"):
            rows = cursor.execute(
                """
                SELECT d.date, d.type_depense, d.description, d.montant,
                       b.nom_bande, d.fournisseur
                FROM depenses d
                LEFT JOIN bandes b ON b.id = d.bande_id
                ORDER BY d.date DESC, d.id DESC
                """
            ).fetchall()
            self.depenses_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1],
                    row[2] or "",
                    f"{row[3]:,.0f} FCFA",
                    row[4] or "",
                    row[5] or "",
                    "",
                ]
                for column, value in enumerate(values):
                    self.depenses_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "ventes_table"):
            rows = cursor.execute(
                """
                SELECT v.date, b.nom_bande, v.nombre_poulets, v.prix_unitaire,
                       v.montant_total, v.client, v.paiement
                FROM ventes v
                LEFT JOIN bandes b ON b.id = v.bande_id
                ORDER BY v.date DESC, v.id DESC
                """
            ).fetchall()
            self.ventes_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1] or "",
                    row[2],
                    f"{row[3]:,.0f} FCFA",
                    f"{row[4]:,.0f} FCFA",
                    row[5] or "",
                    row[6] or "",
                    "",
                ]
                for column, value in enumerate(values):
                    self.ventes_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "aliment_table"):
            rows = cursor.execute(
                """
                SELECT a.date, b.nom_bande, a.quantite_kg, a.type_aliment,
                       a.observation
                FROM consommations_aliment a
                LEFT JOIN bandes b ON b.id = a.bande_id
                ORDER BY a.date DESC, a.id DESC
                """
            ).fetchall()
            self.aliment_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1] or "",
                    f"{row[2]:,.2f} kg",
                    row[3] or "",
                    row[4] or "",
                    "IC",
                    "",
                ]
                for column, value in enumerate(values):
                    self.aliment_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "pesees_table"):
            rows = cursor.execute(
                """
                SELECT p.date, b.nom_bande, p.poids_moyen_g, p.effectif_pese,
                       p.observation
                FROM pesees p
                LEFT JOIN bandes b ON b.id = p.bande_id
                ORDER BY p.date DESC, p.id DESC
                """
            ).fetchall()
            self.pesees_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1] or "",
                    f"{row[2]:,.0f} g",
                    row[3],
                    row[4] or "",
                    "GMQ",
                    "",
                ]
                for column, value in enumerate(values):
                    self.pesees_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "ponte_table"):
            rows = cursor.execute(
                """
                SELECT p.date, b.nom_bande, p.nombre_oeufs, p.observation, p.bande_id
                FROM pontes p
                LEFT JOIN bandes b ON b.id = p.bande_id
                ORDER BY p.date DESC, p.id DESC
                """
            ).fetchall()
            self.ponte_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                poules_presentes = self.db.get_poulets_restants(row[4]) or 0
                taux_jour = indicators.taux_ponte(row[2], poules_presentes)
                values = [
                    row[0],
                    row[1] or "",
                    row[2],
                    f"{taux_jour:.1f} %" if poules_presentes else "N/A",
                    row[3] or "",
                    "",
                ]
                for column, value in enumerate(values):
                    self.ponte_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "ventes_oeufs_table"):
            rows = cursor.execute(
                """
                SELECT m.date, b.nom_bande, m.quantite, m.prix_unitaire,
                       m.montant, m.client
                FROM mouvements_oeufs m
                LEFT JOIN bandes b ON b.id = m.bande_id
                WHERE m.type_mouvement = 'vente'
                ORDER BY m.date DESC, m.id DESC
                """
            ).fetchall()
            self.ventes_oeufs_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                values = [
                    row[0],
                    row[1] or "",
                    row[2],
                    f"{row[3]:,.0f} FCFA",
                    f"{row[4]:,.0f} FCFA",
                    row[5] or "",
                ]
                for column, value in enumerate(values):
                    self.ventes_oeufs_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        if hasattr(self, "oeufs_summary_label"):
            if self.current_bande_id:
                stock = self.db.get_stock_oeufs(self.current_bande_id) or 0
                total_oeufs = self.db.get_total_oeufs(self.current_bande_id) or 0
                jours = self.db.get_nombre_jours_ponte(self.current_bande_id) or 0
                poules = self.db.get_poulets_restants(self.current_bande_id) or 0
                taux_moyen = indicators.taux_ponte_moyen(total_oeufs, poules, jours)
                self.oeufs_summary_label.setText(
                    f"Bande active — Stock d'œufs : {stock:,} | "
                    f"Taux de ponte moyen : {taux_moyen:.1f} %"
                )
            else:
                self.oeufs_summary_label.setText(
                    "Sélectionnez une bande pour voir le stock d'œufs et le taux de ponte."
                )

        if hasattr(self, "stocks_table"):
            articles = self.db.get_articles_stock()
            self.stocks_table.setRowCount(len(articles))
            libelles_categorie = {
                "aliment": "Aliment",
                "medicament": "Médicament / vaccin",
                "litiere": "Litière",
            }
            for row_index, article in enumerate(articles):
                article_id, nom_article, categorie, unite, seuil = article
                quantite = self.db.get_stock_quantite(article_id) or 0
                statut = "En alerte" if quantite < seuil else "OK"
                values = [
                    nom_article,
                    libelles_categorie.get(categorie, categorie),
                    unite,
                    f"{quantite:,.1f}",
                    f"{seuil:,.1f}",
                    statut,
                ]
                for column, value in enumerate(values):
                    self.stocks_table.setItem(
                        row_index, column, QTableWidgetItem(str(value))
                    )

        self.filter_transactions()

    def filter_transactions(self):
        if not hasattr(self, "transaction_period_combo"):
            return
        period = self.transaction_period_combo.currentText()
        today = QDate.currentDate()
        cutoffs = {
            "Aujourd'hui": today,
            "7 derniers jours": today.addDays(-6),
            "30 derniers jours": today.addDays(-29),
            "3 mois": today.addMonths(-3),
        }
        cutoff = cutoffs.get(period)
        selected_bande = self.transaction_bande_combo.currentText()
        filter_bande = self.transaction_bande_combo.currentData() is not None

        tables = (
            (self.mortalites_table, 1),
            (self.depenses_table, 4),
            (self.ventes_table, 1),
            (self.aliment_table, 1),
            (self.pesees_table, 1),
        )
        for table, bande_column in tables:
            for row in range(table.rowCount()):
                date_item = table.item(row, 0)
                bande_item = table.item(row, bande_column)
                row_date = QDate.fromString(
                    date_item.text() if date_item else "", "yyyy-MM-dd"
                )
                date_matches = cutoff is None or (
                    row_date.isValid() and row_date >= cutoff
                )
                bande_matches = not filter_bande or (
                    bande_item is not None and bande_item.text() == selected_bande
                )
                table.setRowHidden(row, not (date_matches and bande_matches))

    def show_message(self, icon, title, text, details=""):
        box = QMessageBox(icon, title, text, parent=self)
        box.setStyleSheet(DIALOG_QSS)
        if details:
            box.setDetailedText(details)
        return box.exec()
    
    def export_bandes(self):
        """Exporter les bandes au format CSV."""
        default_name = f"bandes_{datetime.now():%Y%m%d_%H%M}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les bandes", default_name, "Fichier CSV (*.csv)"
        )
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        with open(path, "w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(output, delimiter=";")
            writer.writerow(
                ["ID", "Nom", "Date début", "Initial", "Restants", "Mortalité", "Bénéfice"]
            )
            for row in range(self.bandes_table.rowCount()):
                writer.writerow([
                    self.bandes_table.item(row, column).text()
                    if self.bandes_table.item(row, column) else ""
                    for column in range(7)
                ])
        self.show_message(
            QMessageBox.Icon.Information,
            "Export terminé",
            f"Le fichier a été créé :\n{path}",
        )

    def export_transactions(self):
        table = self.trans_tabs.currentWidget().findChild(QTableWidget)
        if table is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les transactions",
            f"transactions_{datetime.now():%Y%m%d_%H%M}.csv",
            "Fichier CSV (*.csv)",
        )
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        with open(path, "w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(output, delimiter=";")
            writer.writerow([
                table.horizontalHeaderItem(column).text()
                for column in range(table.columnCount() - 1)
            ])
            for row in range(table.rowCount()):
                writer.writerow([
                    table.item(row, column).text() if table.item(row, column) else ""
                    for column in range(table.columnCount() - 1)
                ])
        self.show_message(
            QMessageBox.Icon.Information, "Export terminé", f"Fichier créé :\n{path}"
        )

    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        bandes = self.db.get_bandes()
        total_initial = sum(int(row[3] or 0) for row in bandes)
        total_depenses = sum(self.db.get_total_depenses(row[0]) for row in bandes)
        cout_initial = sum(self.db.get_cout_initial(row[0]) for row in bandes)
        total_couts = total_depenses + cout_initial
        total_ventes = sum(self.db.get_total_ventes(row[0]) for row in bandes)
        total_morts = sum(self.db.get_total_mortalites(row[0]) for row in bandes)
        total_aliment = sum(self.db.get_total_aliment_kg(row[0]) for row in bandes)
        bandes_avec_pesee = sum(1 for row in bandes if self.db.get_latest_pesee(row[0]))
        report = (
            f"AVICOLE PRO\n{report_type.upper()}\n"
            f"Édité le {datetime.now():%d/%m/%Y à %H:%M}\n"
            f"{'=' * 58}\n\n"
            f"Bandes enregistrées : {len(bandes)}\n"
            f"Effectif initial cumulé : {total_initial:,}\n"
            f"Mortalités cumulées : {total_morts:,}\n"
            f"Coût initial cumulé : {cout_initial:,.0f} FCFA\n"
            f"Dépenses opérationnelles : {total_depenses:,.0f} FCFA\n"
            f"Coût total : {total_couts:,.0f} FCFA\n"
            f"Recettes cumulées : {total_ventes:,.0f} FCFA\n"
            f"Résultat net : {total_ventes - total_couts:,.0f} FCFA\n"
            f"Aliment distribué : {total_aliment:,.1f} kg\n"
            f"Bandes avec pesée : {bandes_avec_pesee}\n"
        )
        self.report_preview.setPlainText(report)

    def export_report(self):
        if not hasattr(self, "report_preview"):
            self.show_page("rapports")
        if not self.report_preview.toPlainText().strip():
            self.generate_report()
        csv_format = self.report_format_combo.currentText() == "CSV"
        extension = "csv" if csv_format else "txt"
        file_filter = "Fichier CSV (*.csv)" if csv_format else "Document texte (*.txt)"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le rapport",
            f"rapport_avicole_{datetime.now():%Y%m%d_%H%M}.{extension}",
            file_filter,
        )
        if not path:
            return
        if not path.lower().endswith(f".{extension}"):
            path += f".{extension}"
        if csv_format:
            bandes = self.db.get_bandes()
            with open(path, "w", newline="", encoding="utf-8-sig") as output:
                writer = csv.writer(output, delimiter=";")
                writer.writerow(
                    [
                        "Bande",
                        "Effectif initial",
                        "Restants",
                        "Dépenses",
                        "Coût total",
                        "Recettes",
                        "Aliment kg",
                        "Dernier poids g",
                        "IC",
                        "GMQ g/j",
                    ]
                )
                for bande in bandes:
                    cout_total = self.db.get_total_couts(bande[0])
                    zootech = self._zootechnie_metrics_for_bande(bande)
                    writer.writerow([
                        bande[1],
                        bande[3],
                        self.db.get_poulets_restants(bande[0]),
                        self.db.get_total_depenses(bande[0]),
                        cout_total,
                        self.db.get_total_ventes(bande[0]),
                        round(zootech["total_aliment_kg"], 2),
                        round(zootech["poids_moyen_g"], 0),
                        round(zootech["ic"], 2),
                        round(zootech["gmq"], 2),
                    ])
        else:
            Path(path).write_text(
                self.report_preview.toPlainText(), encoding="utf-8"
            )
        self.show_message(
            QMessageBox.Icon.Information, "Rapport exporté", f"Fichier créé :\n{path}"
        )

    def export_screenshot(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer une capture",
            f"avicole_{datetime.now():%Y%m%d_%H%M}.png",
            "Image PNG (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        self.grab().save(path, "PNG")
        self.show_message(
            QMessageBox.Icon.Information, "Capture enregistrée", f"Image créée :\n{path}"
        )

    def backup_database(self):
        self.db.conn.commit()
        backups_dir = ensure_user_directories()["backups"]
        dest = backup_module.create_backup(self.db.db_name, backups_dir)
        self.show_message(
            QMessageBox.Icon.Information,
            "Sauvegarde terminée",
            f"La base a été sauvegardée :\n{dest}",
        )

    def restore_database(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Restaurer une base", "", "Base SQLite (*.sqlite *.db)"
        )
        if not path:
            return
        answer = QMessageBox.question(
            self,
            "Confirmer la restauration",
            "La base actuelle sera remplacée. Continuer ?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        target = Path(self.db.db_name)
        backups_dir = ensure_user_directories()["backups"]
        self.db.close()
        safety = backup_module.restore_backup(path, target, backups_dir)
        self.db = Database(str(target))
        self.current_bande_id = None
        self.load_bandes()
        self.show_message(
            QMessageBox.Icon.Information,
            "Restauration terminée",
            f"La base a été restaurée.\nSauvegarde de sécurité :\n{safety}",
        )

    def save_settings(self):
        self.show_message(
            QMessageBox.Icon.Information,
            "Paramètres enregistrés",
            "Les préférences de la session ont été appliquées.",
        )

    def refresh_analytics(self, start_date, end_date):
        if start_date > end_date:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Période invalide",
                "La date de début doit précéder la date de fin.",
            )
            return
        start = start_date.toString("yyyy-MM-dd")
        end = end_date.toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()

        sales = cursor.execute(
            """
            SELECT date, SUM(montant_total)
            FROM ventes WHERE date BETWEEN ? AND ?
            GROUP BY date ORDER BY date
            """,
            (start, end),
        ).fetchall()
        self.analytics_finance_chart.update_chart(
            [row[1] for row in sales] or [0],
            [row[0][5:] for row in sales] or ["Aucune donnée"],
        )

        costs = cursor.execute(
            """
            SELECT type_depense, SUM(montant)
            FROM depenses WHERE date BETWEEN ? AND ?
            GROUP BY type_depense ORDER BY SUM(montant) DESC
            """,
            (start, end),
        ).fetchall()
        self.analytics_cost_chart.update_chart(
            [row[1] for row in costs] or [1],
            [row[0] for row in costs] or ["Aucune donnée"],
        )

        mortality = cursor.execute(
            """
            SELECT date, SUM(nombre_morts)
            FROM mortalites WHERE date BETWEEN ? AND ?
            GROUP BY date ORDER BY date
            """,
            (start, end),
        ).fetchall()
        self.analytics_mortality_chart.update_chart(
            [row[1] for row in mortality] or [0],
            [row[0][5:] for row in mortality] or ["Aucune donnée"],
        )

        bandes = self.db.get_bandes()
        self.analytics_productivity_chart.update_chart(
            [self.db.get_poulets_restants(row[0]) for row in bandes] or [0],
            [row[1] for row in bandes] or ["Aucune bande"],
        )
        self.show_message(
            QMessageBox.Icon.Information,
            "Analyse actualisée",
            "Les indicateurs ont été recalculés pour la période sélectionnée.",
        )

    def print_current_page(self):
        self.show_message(
            QMessageBox.Icon.Information,
            "Impression",
            "Utilisez l'export de capture ou de rapport pour une édition fidèle.",
        )

    def search_current_page(self):
        term = self.main_toolbar.search_input.text().strip().lower()
        table = self.content_stack.currentWidget().findChild(QTableWidget)
        if table is None:
            return
        for row in range(table.rowCount()):
            matches = not term or any(
                term in (table.item(row, col).text().lower() if table.item(row, col) else "")
                for col in range(table.columnCount())
            )
            table.setRowHidden(row, not matches)

    def dispatch_edit_action(self, action_name):
        widget = QApplication.focusWidget()
        method = getattr(widget, action_name, None)
        if callable(method):
            method()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def show_help(self):
        self.show_message(
            QMessageBox.Icon.Information,
            "Aide",
            "Sélectionnez d'abord une bande active, puis utilisez les actions du tableau de bord pour enregistrer les opérations.",
        )

    def show_about(self):
        self.show_message(
            QMessageBox.Icon.Information,
            "À propos d'Avicole Pro",
            "Avicole Pro 3.1\nSystème intégré de gestion et de pilotage avicole.",
        )
    
    # Méthodes existantes à adapter
    def nouvelle_bande(self):
        from dialogs import NouvelleBandeDialog  # À importer
        
        dialog = NouvelleBandeDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.ajouter_bande(
                data['nom'],
                data['date'],
                data['nombre'],
                data['prix'],
                activite=data['activite'],
            )
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Bande créée",
                "La nouvelle bande a été enregistrée.",
            )
    
    def ajouter_mortalite(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return
        
        from dialogs import SaisieMortaliteDialog  # À importer
        
        dialog = SaisieMortaliteDialog(self.current_bande_id, self)
        if dialog.exec():
            data = dialog.get_data()
            disponibles = self.db.get_poulets_restants(self.current_bande_id)
            if data["nombre"] > disponibles:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Effectif insuffisant",
                    f"La déclaration dépasse l'effectif disponible ({disponibles}).",
                )
                return
            self.db.ajouter_mortalite(
                self.current_bande_id,
                data['date'],
                data['nombre'],
                data['cause'],
                data['description'],
            )
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Déclaration enregistrée",
                "La mortalité a été prise en compte.",
            )
    
    def ajouter_depense(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return
        
        from dialogs import NouvelleDepenseDialog  # À importer
        
        dialog = NouvelleDepenseDialog(self.current_bande_id, self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.ajouter_depense(
                self.current_bande_id,
                data['date'],
                data['type'],
                data['montant'],
                data['description'],
                data['fournisseur'],
            )
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Dépense enregistrée",
                "La dépense a été ajoutée au journal.",
            )
    
    def ajouter_aliment(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return

        from dialogs import SaisieAlimentDialog

        dialog = SaisieAlimentDialog(self.current_bande_id, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_consommation_aliment(
                    self.current_bande_id,
                    data["date"],
                    data["quantite_kg"],
                    data["type_aliment"],
                    data["observation"],
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Saisie impossible",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Aliment enregistré",
                "La consommation d'aliment a été ajoutée au suivi.",
            )

    def ajouter_pesee(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return

        from dialogs import SaisiePeseeDialog

        dialog = SaisiePeseeDialog(self.current_bande_id, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_pesee(
                    self.current_bande_id,
                    data["date"],
                    data["poids_moyen_g"],
                    data["effectif_pese"],
                    data["observation"],
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Saisie impossible",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Pesée enregistrée",
                "La pesée a été ajoutée au suivi de croissance.",
            )

    def ajouter_ponte(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return

        poules_presentes = self.db.get_poulets_restants(self.current_bande_id) or 0

        from dialogs import SaisiePonteDialog

        dialog = SaisiePonteDialog(self.current_bande_id, poules_presentes, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_ponte(
                    self.current_bande_id,
                    data["date"],
                    data["nombre_oeufs"],
                    data["observation"],
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Saisie impossible",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Ponte enregistrée",
                "La production d'œufs a été ajoutée au suivi.",
            )

    def ajouter_vente_oeufs(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return

        stock = self.db.get_stock_oeufs(self.current_bande_id) or 0
        if stock <= 0:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Vente impossible",
                "Aucun œuf n'est disponible à la vente.",
            )
            return

        from dialogs import NouvelleVenteOeufsDialog

        dialog = NouvelleVenteOeufsDialog(stock, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_vente_oeufs(
                    self.current_bande_id,
                    data["date"],
                    data["quantite"],
                    data["prix"],
                    data["client"],
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Vente impossible",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Vente enregistrée",
                "La vente d'œufs a été ajoutée au journal.",
            )

    def nouvel_article_stock(self):
        from dialogs import SaisieArticleStockDialog

        dialog = SaisieArticleStockDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_article_stock(
                    data["nom_article"],
                    data["categorie"],
                    data["unite"],
                    data["seuil_alerte"],
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Saisie impossible",
                    str(erreur),
                )
                return
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Article créé",
                "Le nouvel article de stock a été ajouté.",
            )

    def _ouvrir_mouvement_stock(self, type_mouvement):
        articles = self.db.get_articles_stock()
        if not articles:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Aucun article",
                "Créez d'abord un article de stock.",
            )
            return

        from dialogs import MouvementStockDialog

        dialog = MouvementStockDialog(
            type_mouvement, articles, self.current_bande_id, self
        )
        if dialog.exec():
            data = dialog.get_data()
            try:
                if type_mouvement == "sortie" and data["lier_consommation"]:
                    self.db.ajouter_sortie_stock_aliment(
                        data["article_id"],
                        self.current_bande_id,
                        data["date"],
                        data["quantite"],
                        observation=data["motif"],
                    )
                else:
                    self.db.ajouter_mouvement_stock(
                        data["article_id"],
                        data["date"],
                        type_mouvement,
                        data["quantite"],
                        motif=data["motif"],
                    )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Mouvement refusé",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Mouvement enregistré",
                "Le mouvement de stock a été enregistré.",
            )

    def ajouter_entree_stock(self):
        self._ouvrir_mouvement_stock("entree")

    def ajouter_sortie_stock(self):
        self._ouvrir_mouvement_stock("sortie")

    def ajouter_vente(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return
        
        poulets_disponibles = self.db.get_poulets_restants(self.current_bande_id)
        if poulets_disponibles <= 0:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Vente impossible",
                "Aucun sujet n'est disponible à la vente.",
            )
            return
        
        from dialogs import NouvelleVenteDialog  # À importer
        
        dialog = NouvelleVenteDialog(self.current_bande_id, poulets_disponibles, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.db.ajouter_vente(
                    self.current_bande_id,
                    data['date'],
                    data['nombre'],
                    data['prix'],
                    data['client'],
                    data['paiement'],
                    poids_total=data.get('poids_total'),
                )
            except ValueError as erreur:
                self.show_message(
                    QMessageBox.Icon.Warning,
                    "Vente impossible",
                    str(erreur),
                )
                return
            self.update_dashboard()
            self.load_bandes()
            self.show_message(
                QMessageBox.Icon.Information,
                "Vente enregistrée",
                "La vente a été ajoutée au journal.",
            )
    
    def cloturer_bande_active(self):
        if not self.current_bande_id:
            self.show_message(
                QMessageBox.Icon.Warning,
                "Bande requise",
                "Sélectionnez d'abord une bande active.",
            )
            return
        answer = QMessageBox.question(
            self,
            "Clôturer la bande",
            "Clôturer définitivement cette bande ?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.db.cloturer_bande(self.current_bande_id)
        self.load_bandes()
        self.show_message(
            QMessageBox.Icon.Information,
            "Bande clôturée",
            "La bande a été marquée comme clôturée.",
        )

    def closeEvent(self, event):
        """Fermeture de l'application"""
        self.db.close()
        event.accept()
