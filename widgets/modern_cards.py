from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QPainter, QBrush, QPen
import math

class ModernCard(QFrame):
    """Carte moderne avec animations et effets visuels"""
    
    def __init__(self, title="", value="0", icon="", color="#1E88E5", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.hover_color = self.color.lighter(120)
        self.title = title
        self.value = value
        self.icon = icon
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Configurer l'interface de la carte"""
        self.setObjectName("modernCard")
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)
        
        # Style de base
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 0px;
            }}
            QFrame#modernCard:hover {{
                border-color: {self.color.name()};
            }}
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # En-tête avec titre et icône
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        # Icône
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet(f"""
                font-size: 24px;
                margin-right: 8px;
            """)
            header.addWidget(icon_label)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #607D8B;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        header.addWidget(title_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Valeur principale
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: #263238;
            padding: 8px 0;
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Sous-titre
        self.subtitle_label = QLabel("")
        self.subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #90A4AE;
            font-weight: 400;
        """)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label)
        
        # Badge
        self.badge = QLabel("")
        self.badge.setVisible(False)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.badge)
    
    def setup_animation(self):
        """Configurer les animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        """Animation au survol"""
        super().enterEvent(event)
        
        # Animation d'élévation
        geometry = self.geometry()
        self.hover_animation.setStartValue(geometry)
        self.hover_animation.setEndValue(geometry.adjusted(0, -2, 0, 2))
        self.hover_animation.start()
        
        # Changement de style
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background-color: white;
                border: 2px solid {self.color.name()};
                border-radius: 12px;
                padding: 0px;
                box-shadow: 0 8px 16px rgba(30, 136, 229, 0.15);
            }}
        """)
    
    def leaveEvent(self, event):
        """Animation à la sortie"""
        super().leaveEvent(event)
        
        # Retour à la position initiale
        geometry = self.geometry()
        self.hover_animation.setStartValue(geometry)
        self.hover_animation.setEndValue(geometry.adjusted(0, 2, 0, -2))
        self.hover_animation.start()
        
        # Rétablir le style
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                padding: 0px;
            }}
            QFrame#modernCard:hover {{
                border-color: {self.color.name()};
            }}
        """)
    
    def update_value(self, value, subtitle="", badge_text="", badge_color="#4CAF50"):
        """Mettre à jour les valeurs affichées"""
        self.value_label.setText(str(value))
        self.subtitle_label.setText(subtitle)
        
        if badge_text:
            self.badge.setText(badge_text)
            self.badge.setStyleSheet(f"""
                background-color: {badge_color};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                margin-top: 5px;
                max-width: 100px;
                margin-left: auto;
                margin-right: auto;
            """)
            self.badge.setVisible(True)
        else:
            self.badge.setVisible(False)


class StatCard(ModernCard):
    """Carte de statistiques avec indicateur de tendance"""
    
    def __init__(self, title="", value="0", change=0, icon="", color="#1E88E5", parent=None):
        super().__init__(title, value, icon, color, parent)
        self.change = change
        self.setup_trend_indicator()
    
    def setup_trend_indicator(self):
        """Ajouter un indicateur de tendance"""
        # Layout pour la tendance
        trend_layout = QHBoxLayout()
        trend_layout.setContentsMargins(0, 0, 0, 0)
        
        # Indicateur de tendance
        trend_icon = "📈" if self.change >= 0 else "📉"
        trend_color = "#4CAF50" if self.change >= 0 else "#E53935"
        
        trend_label = QLabel(f"{trend_icon} {abs(self.change):.1f}%")
        trend_label.setStyleSheet(f"""
            font-size: 11px;
            color: {trend_color};
            font-weight: 600;
            padding: 2px 6px;
            background-color: {trend_color}15;
            border-radius: 4px;
        """)
        
        trend_layout.addStretch()
        trend_layout.addWidget(trend_label)
        
        # Ajouter au layout principal
        self.layout().addLayout(trend_layout)


class MetricCard(ModernCard):
    """Carte métrique avec barre de progression"""
    
    def __init__(self, title="", value="0", target=100, icon="", color="#1E88E5", parent=None):
        super().__init__(title, value, icon, color, parent)
        self.target = target
        self.setup_progress_bar()
    
    def setup_progress_bar(self):
        """Ajouter une barre de progression"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #F5F5F5;
                border-radius: 4px;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {self.color.name()};
                border-radius: 4px;
            }}
        """)
        
        self.layout().addWidget(self.progress_bar)
    
    def update_progress(self, current, target=None):
        """Mettre à jour la barre de progression"""
        if target:
            self.target = target
        
        progress = int((current / self.target) * 100) if self.target > 0 else 0
        self.progress_bar.setValue(min(progress, 100))
        
        # Mettre à jour le sous-titre
        self.subtitle_label.setText(f"{current}/{self.target} ({progress}%)")