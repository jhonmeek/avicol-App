from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class SaisieArticleStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvel article de stock")
        configure_dialog(self, 560, 420)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Créer un article de stock")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Informations de l'article")
        form = QFormLayout(group)
        prepare_form(form)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex. Aliment démarrage")
        form.addRow("Nom de l'article", self.nom_input)

        self.categorie_combo = QComboBox()
        self.categorie_combo.addItem("Aliment", "aliment")
        self.categorie_combo.addItem("Médicament / vaccin", "medicament")
        self.categorie_combo.addItem("Litière", "litiere")
        form.addRow("Catégorie", self.categorie_combo)

        self.unite_input = QLineEdit()
        self.unite_input.setPlaceholderText("kg, dose, botte...")
        form.addRow("Unité", self.unite_input)

        self.seuil_input = QDoubleSpinBox()
        self.seuil_input.setRange(0, 1000000)
        self.seuil_input.setDecimals(1)
        form.addRow("Seuil d'alerte", self.seuil_input)

        layout.addWidget(group)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Annuler")
        cancel.setProperty("secondary", "true")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Créer")
        save.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def validate_and_accept(self):
        if not self.nom_input.text().strip():
            show_validation(self, "Le nom de l'article est obligatoire.")
            self.nom_input.setFocus()
            return
        if not self.unite_input.text().strip():
            show_validation(self, "L'unité est obligatoire.")
            self.unite_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "nom_article": self.nom_input.text().strip(),
            "categorie": self.categorie_combo.currentData(),
            "unite": self.unite_input.text().strip(),
            "seuil_alerte": self.seuil_input.value(),
        }
