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
    QSpinBox,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class NouvelleVenteDialog(QDialog):
    def __init__(self, bande_id, poulets_disponibles, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.poulets_disponibles = int(poulets_disponibles)
        self.setWindowTitle("Nouvelle vente")
        configure_dialog(self, 590, 540)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        title = QLabel("Enregistrer une vente")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        available = QLabel(
            f"Effectif disponible : {self.poulets_disponibles:,} sujets"
        )
        available.setObjectName("warning")
        layout.addWidget(available)

        group = QGroupBox("Détails de la vente")
        form = QFormLayout(group)
        prepare_form(form)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date de vente", self.date_input)
        self.nombre_input = QSpinBox()
        self.nombre_input.setRange(1, max(1, self.poulets_disponibles))
        self.nombre_input.setValue(min(10, max(1, self.poulets_disponibles)))
        self.nombre_input.setSuffix(" sujets")
        form.addRow("Quantité vendue", self.nombre_input)
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 10000000)
        self.prix_input.setDecimals(0)
        self.prix_input.setValue(2000)
        self.prix_input.setSuffix(" FCFA / sujet")
        form.addRow("Prix unitaire", self.prix_input)
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Optionnel")
        form.addRow("Client", self.client_input)
        self.paiement_combo = QComboBox()
        self.paiement_combo.addItems([
            "Espèces",
            "Virement bancaire",
            "Mobile money",
            "Chèque",
            "Autre",
        ])
        form.addRow("Moyen de paiement", self.paiement_combo)
        layout.addWidget(group)

        self.total_label = QLabel()
        self.total_label.setObjectName("summary")
        layout.addWidget(self.total_label)
        self.marge_label = QLabel()
        self.marge_label.setObjectName("dialogHint")
        layout.addWidget(self.marge_label)
        self.nombre_input.valueChanged.connect(self.calculer_total)
        self.prix_input.valueChanged.connect(self.calculer_total)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Annuler")
        cancel.setProperty("secondary", "true")
        cancel.clicked.connect(self.reject)
        self.save_button = QPushButton("Enregistrer la vente")
        self.save_button.setEnabled(self.poulets_disponibles > 0)
        self.save_button.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(self.save_button)
        layout.addLayout(buttons)
        self.calculer_total()

    def calculer_total(self):
        nombre = self.nombre_input.value()
        total = nombre * self.prix_input.value()
        marge = total - nombre * 1500
        self.total_label.setText(f"Montant total : {total:,.0f} FCFA")
        self.marge_label.setText(f"Marge estimée : {marge:,.0f} FCFA")

    def validate_and_accept(self):
        if self.poulets_disponibles <= 0:
            show_validation(self, "Aucun sujet n'est disponible à la vente.")
            return
        if self.prix_input.value() <= 0:
            show_validation(self, "Le prix unitaire doit être supérieur à zéro.")
            self.prix_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "nombre": self.nombre_input.value(),
            "prix": self.prix_input.value(),
            "client": self.client_input.text().strip(),
            "paiement": self.paiement_combo.currentText(),
        }
