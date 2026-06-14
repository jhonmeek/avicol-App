from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta

class AnalyticsChart(QFrame):
    """Widget de graphique analytique moderne"""
    
    def __init__(self, title="", chart_type="line", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.title = title
        self.data = []
        self.labels = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface du graphique"""
        self.setObjectName("chartWidget")
        self.setMinimumHeight(300)
        self.setStyleSheet("""
            QFrame#chartWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 0px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête du graphique
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 10px 10px 0 0;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        header.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #263238;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Options
        self.period_combo = QComboBox()
        self.period_combo.addItems(["7j", "30j", "3m", "1a", "Tout"])
        self.period_combo.setFixedWidth(80)
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        header_layout.addWidget(self.period_combo)
        
        layout.addWidget(header)
        
        # Figure matplotlib
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor='#FFFFFF')
        self.ax = self.figure.add_subplot(111)
        
        # Style moderne
        self.ax.set_facecolor('#FFFFFF')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_alpha(0.3)
        self.ax.spines['bottom'].set_alpha(0.3)
        self.ax.grid(True, alpha=0.1)
        
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Légende interactive
        self.legend_frame = QFrame()
        self.legend_frame.setVisible(False)
        self.legend_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top: 1px solid #E0E0E0;
                padding: 10px;
            }
        """)
        
        legend_layout = QHBoxLayout(self.legend_frame)
        legend_layout.setContentsMargins(15, 5, 15, 5)
        
        self.legend_label = QLabel("")
        self.legend_label.setStyleSheet("color: #607D8B; font-size: 11px;")
        legend_layout.addWidget(self.legend_label)
        legend_layout.addStretch()
        
        layout.addWidget(self.legend_frame)
    
    def update_chart(self, data, labels=None, colors=None, title=None):
        """Mettre à jour le graphique avec de nouvelles données"""
        self.ax.clear()
        
        if title:
            self.ax.set_title(title, fontsize=12, fontweight=600, pad=10)
        
        if self.chart_type == "line":
            self.create_line_chart(data, labels, colors)
        elif self.chart_type == "bar":
            self.create_bar_chart(data, labels, colors)
        elif self.chart_type == "pie":
            self.create_pie_chart(data, labels, colors)
        elif self.chart_type == "area":
            self.create_area_chart(data, labels, colors)
        
        # Appliquer le style moderne
        self.apply_modern_style()
        
        # Redessiner
        self.canvas.draw()
    
    def create_line_chart(self, data, labels, colors):
        """Créer un graphique en ligne"""
        x = range(len(data))
        
        if colors:
            color = colors[0] if isinstance(colors, list) else colors
        else:
            color = '#1E88E5'
        
        # Ligne principale
        line = self.ax.plot(x, data, color=color, linewidth=2.5, marker='o', 
                           markersize=6, markerfacecolor='white', markeredgewidth=2)
        
        # Remplissage sous la courbe
        self.ax.fill_between(x, 0, data, alpha=0.1, color=color)
        
        # Ajouter les labels si disponibles
        if labels and len(labels) == len(data):
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        # Configurer les axes
        self.ax.set_xlabel('Temps', fontsize=10)
        self.ax.set_ylabel('Valeur', fontsize=10)
        
        # Ajouter une grille subtile
        self.ax.grid(True, alpha=0.1)
    
    def create_bar_chart(self, data, labels, colors):
        """Créer un graphique en barres"""
        x = range(len(data))
        
        if colors and isinstance(colors, list):
            bar_colors = colors
        else:
            bar_colors = plt.cm.Blues(np.linspace(0.6, 1, len(data)))
        
        bars = self.ax.bar(x, data, color=bar_colors, alpha=0.8, edgecolor='white', linewidth=1)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}', ha='center', va='bottom', 
                        fontsize=9, fontweight=600)
        
        if labels and len(labels) == len(data):
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        # Configurer les axes
        self.ax.set_xlabel('Catégories', fontsize=10)
        self.ax.set_ylabel('Montant', fontsize=10)
        self.ax.grid(True, alpha=0.1, axis='y')
    
    def create_pie_chart(self, data, labels, colors):
        """Créer un graphique circulaire"""
        if not labels:
            labels = [f'Item {i+1}' for i in range(len(data))]
        
        if colors and isinstance(colors, list):
            pie_colors = colors
        else:
            pie_colors = plt.cm.Set3(np.arange(len(data)) / len(data))
        
        # Créer le camembert
        wedges, texts, autotexts = self.ax.pie(
            data, 
            labels=labels, 
            colors=pie_colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9},
            pctdistance=0.85
        )
        
        # Style des pourcentages
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight(600)
        
        # Cercle au centre pour un look moderne
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        self.ax.add_artist(centre_circle)
        
        # Titre au centre
        total = sum(data)
        self.ax.text(0, 0, f"Total\n{total:,.0f}", 
                    ha='center', va='center', 
                    fontsize=11, fontweight=600, color='#263238')
        
        # Égaliser les axes
        self.ax.axis('equal')
    
    def create_area_chart(self, data, labels, colors):
        """Créer un graphique en aires"""
        x = range(len(data))
        
        if colors:
            color = colors[0] if isinstance(colors, list) else colors
        else:
            color = '#1E88E5'
        
        # Aire remplie
        self.ax.fill_between(x, data, alpha=0.3, color=color)
        
        # Ligne de contour
        self.ax.plot(x, data, color=color, linewidth=2)
        
        if labels and len(labels) == len(data):
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        self.ax.set_xlabel('Temps', fontsize=10)
        self.ax.set_ylabel('Valeur', fontsize=10)
        self.ax.grid(True, alpha=0.1)
    
    def apply_modern_style(self):
        """Appliquer un style moderne au graphique"""
        # Style des axes
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#B0BEC5')
        self.ax.spines['bottom'].set_color('#B0BEC5')
        
        # Couleur des ticks
        self.ax.tick_params(colors='#607D8B', labelsize=9)
        
        # Grille subtile
        self.ax.grid(True, alpha=0.1, color='#E0E0E0')
        
        # Couleur des labels
        self.ax.xaxis.label.set_color('#607D8B')
        self.ax.yaxis.label.set_color('#607D8B')
        
        # Ajuster les marges
        self.figure.tight_layout(pad=2.0)


class PieChartWidget(AnalyticsChart):
    """Widget spécialisé pour les graphiques circulaires"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, "pie", parent)


class BarChartWidget(AnalyticsChart):
    """Widget spécialisé pour les graphiques en barres"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, "bar", parent)


class LineChartWidget(AnalyticsChart):
    """Widget spécialisé pour les graphiques en ligne"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, "line", parent)