from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
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
    QTextEdit,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class NouvelleDepenseDialog(QDialog):
    def __init__(self, bande_id, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.setWindowTitle("Nouvelle dépense")
        configure_dialog(self, 580, 520)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        title = QLabel("Enregistrer une dépense")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Détails de la dépense")
        form = QFormLayout(group)
        prepare_form(form)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Aliments pour volailles",
            "Vaccins et médicaments",
            "Équipement et matériel",
            "Main d'œuvre",
            "Transport",
            "Électricité et eau",
            "Soins vétérinaires",
            "Fournitures diverses",
            "Autre dépense",
        ])
        form.addRow("Type de dépense", self.type_combo)
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setRange(0, 1000000000)
        self.montant_input.setDecimals(0)
        self.montant_input.setSuffix(" FCFA")
        form.addRow("Montant", self.montant_input)
        self.fournisseur_input = QLineEdit()
        self.fournisseur_input.setPlaceholderText("Optionnel")
        form.addRow("Fournisseur", self.fournisseur_input)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description détaillée")
        self.desc_input.setMinimumHeight(85)
        form.addRow("Description", self.desc_input)
        layout.addWidget(group)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("summary")
        layout.addWidget(self.summary_label)
        self.montant_input.valueChanged.connect(self.format_montant)

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
        self.format_montant()

    def format_montant(self):
        self.summary_label.setText(
            f"Montant total : {self.montant_input.value():,.0f} FCFA"
        )

    def validate_and_accept(self):
        if self.montant_input.value() <= 0:
            show_validation(self, "Le montant doit être supérieur à zéro.")
            self.montant_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "type": self.type_combo.currentText(),
            "montant": self.montant_input.value(),
            "description": self.desc_input.toPlainText().strip(),
            "fournisseur": self.fournisseur_input.text().strip(),
        }
