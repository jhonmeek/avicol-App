from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
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


class MouvementStockDialog(QDialog):
    def __init__(self, type_mouvement, articles, bande_active=None, parent=None):
        super().__init__(parent)
        self.type_mouvement = type_mouvement
        self.articles = articles
        self.bande_active = bande_active
        titre = "Entrée de stock" if type_mouvement == "entree" else "Sortie de stock"
        self.setWindowTitle(titre)
        configure_dialog(self, 560, 480)
        self.setup_ui(titre)

    def setup_ui(self, titre):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel(titre)
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Détails du mouvement")
        form = QFormLayout(group)
        prepare_form(form)

        self.article_combo = QComboBox()
        for article_id, nom_article, categorie, unite, _seuil in self.articles:
            self.article_combo.addItem(
                f"{nom_article} ({unite})",
                (article_id, categorie, unite),
            )
        self.article_combo.currentIndexChanged.connect(self.update_article_context)
        form.addRow("Article", self.article_combo)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.quantite_input = QDoubleSpinBox()
        self.quantite_input.setRange(0, 1000000)
        self.quantite_input.setDecimals(2)
        form.addRow("Quantité", self.quantite_input)

        self.motif_input = QLineEdit()
        self.motif_input.setPlaceholderText("Optionnel")
        form.addRow("Motif", self.motif_input)

        layout.addWidget(group)

        self.lien_checkbox = QCheckBox(
            "Lier à la bande active (consommation aliment)"
        )
        self.lien_checkbox.setVisible(
            self.type_mouvement == "sortie" and self.bande_active is not None
        )
        layout.addWidget(self.lien_checkbox)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Annuler")
        cancel.setProperty("secondary", "true")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Enregistrer")
        save.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.update_article_context()

    def update_article_context(self):
        data = self.article_combo.currentData()
        if not data:
            self.quantite_input.setSuffix("")
            self.lien_checkbox.setEnabled(False)
            return
        _article_id, categorie, unite = data
        self.quantite_input.setSuffix(f" {unite}")
        est_aliment = categorie == "aliment"
        self.lien_checkbox.setEnabled(
            self.type_mouvement == "sortie" and est_aliment
            and self.bande_active is not None
        )
        if not self.lien_checkbox.isEnabled():
            self.lien_checkbox.setChecked(False)

    def validate_and_accept(self):
        if self.article_combo.currentData() is None:
            show_validation(self, "Sélectionnez un article.")
            return
        if self.quantite_input.value() <= 0:
            show_validation(self, "La quantité doit être supérieure à zéro.")
            self.quantite_input.setFocus()
            return
        self.accept()

    def get_data(self):
        article_id, _categorie, _unite = self.article_combo.currentData()
        return {
            "article_id": article_id,
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "quantite": self.quantite_input.value(),
            "motif": self.motif_input.text().strip(),
            "lier_consommation": self.lien_checkbox.isChecked(),
        }
