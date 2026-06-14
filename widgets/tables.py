from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QMenu, QWidget, QHBoxLayout,
    QPushButton, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication
)
from PyQt6.QtCore import Qt, QModelIndex, QRect
from PyQt6.QtGui import QColor, QBrush, QPainter, QFont, QAction

class ModernTableWidget(QTableWidget):
    """Tableau moderne avec style professionnel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'apparence du tableau"""
        # Style général
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8F9FA;
                selection-background-color: #E3F2FD;
                selection-color: #1565C0;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #E0E0E0;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)
        
        # Configuration de l'en-tête
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #1E88E5;
                color: white;
                font-weight: 600;
                padding: 12px 15px;
                border: none;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:hover {
                background-color: #1565C0;
            }
        """)
        
        # Configuration verticale
        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
        
        # Propriétés du tableau
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        
        # Redimensionnement automatique
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        
        # Délégué personnalisé pour le rendu
        self.setItemDelegate(ModernTableDelegate())
    
    def add_row(self, data):
        """Ajouter une ligne de données"""
        row = self.rowCount()
        self.insertRow(row)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            
            # Style selon le type de données
            if isinstance(value, (int, float)):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if isinstance(value, float):
                    item.setText(f"{value:,.2f}")
                else:
                    item.setText(f"{value:,}")
            
            self.setItem(row, col, item)
    
    def add_action_column(self):
        """Ajouter une colonne d'actions"""
        col = self.columnCount()
        self.insertColumn(col)
        self.setHorizontalHeaderItem(col, QTableWidgetItem("Actions"))
        
        # Ajuster la largeur de la colonne d'actions
        self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(col, 100)
    
    def set_row_actions(self, row, actions):
        """Définir les actions pour une ligne spécifique"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(3)
        
        for action_text, callback in actions:
            btn = QPushButton(action_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F5F5F5;
                    color: #757575;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    min-width: 30px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                    border-color: #BDBDBD;
                }
            """)
            
            if callback:
                btn.clicked.connect(lambda checked, r=row, c=callback: c(r))
            
            layout.addWidget(btn)
        
        layout.addStretch()
        self.setCellWidget(row, self.columnCount() - 1, widget)
    
    def contextMenuEvent(self, event):
        """Menu contextuel personnalisé"""
        menu = QMenu(self)
        
        # Actions du menu
        copy_action = QAction("📋 Copier", self)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)
        
        export_action = QAction("📤 Exporter la ligne", self)
        export_action.triggered.connect(self.export_row)
        menu.addAction(export_action)
        
        menu.addSeparator()
        
        refresh_action = QAction("🔄 Actualiser", self)
        refresh_action.triggered.connect(self.refresh_data)
        menu.addAction(refresh_action)
        
        menu.exec(event.globalPos())
    
    def copy_selection(self):
        """Copier la sélection"""
        selected = self.selectedItems()
        if selected:
            text = "\t".join(item.text() for item in selected)
            QApplication.clipboard().setText(text)
    
    def export_row(self):
        """Exporter la ligne sélectionnée"""
        selected_rows = set(item.row() for item in self.selectedItems())
        for row in selected_rows:
            # Implémenter l'export
            pass
    
    def refresh_data(self):
        """Rafraîchir les données"""
        self.clearContents()
        self.setRowCount(0)


class SortableTableWidget(ModernTableWidget):
    """Tableau avec tri avancé"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.sort_column = 0
    
    def sort_items(self, column, order):
        """Trier les items par colonne"""
        self.sortByColumn(column, order)
        self.sort_column = column
        self.sort_order = order
        
        # Mettre en évidence la colonne triée
        for col in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                if col == column:
                    header_item.setText(f"{header_item.text()} {'↑' if order == Qt.SortOrder.AscendingOrder else '↓'}")
                else:
                    # Retirer les indicateurs de tri des autres colonnes
                    text = header_item.text()
                    if text.endswith(' ↑') or text.endswith(' ↓'):
                        header_item.setText(text[:-2])


class EditableTableWidget(ModernTableWidget):
    """Tableau avec édition en ligne"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | 
                            QAbstractItemView.EditTrigger.EditKeyPressed)
        
        # Connecter le signal d'édition
        self.itemChanged.connect(self.on_item_changed)
    
    def on_item_changed(self, item):
        """Quand un item est modifié"""
        row = item.row()
        col = item.column()
        new_value = item.text()
        
        # Validation basique
        if not new_value.strip():
            item.setText("N/A")
        
        # Sauvegarder les changements
        self.save_changes(row, col, new_value)
    
    def save_changes(self, row, col, value):
        """Sauvegarder les modifications"""
        # À implémenter selon la logique métier
        print(f"Saved change: row={row}, col={col}, value={value}")


class ModernTableDelegate(QStyledItemDelegate):
    """Délégué pour le rendu personnalisé des cellules"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Personnaliser le rendu des cellules"""
        if option.state & QStyle.State_Selected:
            # Fond pour les cellules sélectionnées
            painter.fillRect(option.rect, QColor(227, 242, 253))
        elif option.state & QStyle.State_MouseOver:
            # Fond au survol
            painter.fillRect(option.rect, QColor(245, 245, 245))
        elif index.row() % 2 == 1:
            # Lignes alternées
            painter.fillRect(option.rect, QColor(248, 249, 250))
        
        # Texte
        painter.save()
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        
        # Style selon le type de données
        font = QFont()
        
        # Mettre en gras les en-têtes ou valeurs importantes
        if index.column() == 0:  # Première colonne
            font.setBold(True)
        
        # Alignement
        alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        # Nombres alignés à droite
        try:
            float(text.replace(',', '').replace(' ', ''))
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        except:
            pass
        
        painter.setFont(font)
        painter.drawText(option.rect.adjusted(10, 0, -10, 0), alignment, text)
        painter.restore()
        
        # Bordure inférieure
        if index.row() < index.model().rowCount() - 1:
            painter.setPen(QColor(240, 240, 240))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
    
    def sizeHint(self, option, index):
        """Définir la taille des cellules"""
        size = super().sizeHint(option, index)
        size.setHeight(40)  # Hauteur fixe pour toutes les lignes
        return size