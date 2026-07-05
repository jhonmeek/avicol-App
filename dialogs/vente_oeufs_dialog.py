from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
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


class NouvelleVenteOeufsDialog(QDialog):
    def __init__(self, stock_disponible, parent=None):
        super().__init__(parent)
        self.stock_disponible = int(stock_disponible)
        self.setWindowTitle("Vente d'œufs")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Enregistrer une vente d'œufs")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        available = QLabel(f"Stock disponible : {self.stock_disponible:,} œufs")
        available.setObjectName("warning")
        layout.addWidget(available)

        group = QGroupBox("Détails de la vente")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date de vente", self.date_input)

        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(1, max(1, self.stock_disponible))
        self.quantite_input.setValue(min(30, max(1, self.stock_disponible)))
        self.quantite_input.setSuffix(" œufs")
        form.addRow("Quantité vendue", self.quantite_input)

        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 10000)
        self.prix_input.setDecimals(0)
        self.prix_input.setValue(100)
        self.prix_input.setSuffix(" FCFA / œuf")
        form.addRow("Prix unitaire", self.prix_input)

        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Optionnel")
        form.addRow("Client", self.client_input)

        layout.addWidget(group)

        self.total_label = QLabel()
        self.total_label.setObjectName("summary")
        layout.addWidget(self.total_label)
        self.quantite_input.valueChanged.connect(self.calculer_total)
        self.prix_input.valueChanged.connect(self.calculer_total)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Annuler")
        cancel.setProperty("secondary", "true")
        cancel.clicked.connect(self.reject)
        self.save_button = QPushButton("Enregistrer la vente")
        self.save_button.setEnabled(self.stock_disponible > 0)
        self.save_button.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(self.save_button)
        layout.addLayout(buttons)
        self.calculer_total()

    def calculer_total(self):
        total = self.quantite_input.value() * self.prix_input.value()
        self.total_label.setText(f"Montant total : {total:,.0f} FCFA")

    def validate_and_accept(self):
        if self.stock_disponible <= 0:
            show_validation(self, "Aucun œuf n'est disponible à la vente.")
            return
        if self.prix_input.value() <= 0:
            show_validation(self, "Le prix unitaire doit être supérieur à zéro.")
            self.prix_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "quantite": self.quantite_input.value(),
            "prix": self.prix_input.value(),
            "client": self.client_input.text().strip(),
        }
