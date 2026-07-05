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
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class SaisieCalibrageOeufsDialog(QDialog):
    def __init__(self, quantite_disponible, parent=None):
        super().__init__(parent)
        self.quantite_disponible = max(0, int(quantite_disponible or 0))
        self.setWindowTitle("Calibrage des oeufs")
        configure_dialog(self, 560, 540)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Enregistrer un calibrage d'oeufs")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        summary = QLabel(f"Reste a calibrer : {self.quantite_disponible:,} oeufs")
        summary.setObjectName("summary")
        layout.addWidget(summary)

        group = QGroupBox("Details du calibrage")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.categorie_input = QComboBox()
        self.categorie_input.addItem("Petit", "petit")
        self.categorie_input.addItem("Moyen", "moyen")
        self.categorie_input.addItem("Gros", "gros")
        self.categorie_input.addItem("Tres gros", "tres_gros")
        self.categorie_input.addItem("Declasse", "declasse")
        form.addRow("Categorie", self.categorie_input)

        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(0, self.quantite_disponible)
        self.quantite_input.setSuffix(" oeuf(s)")
        form.addRow("Quantite", self.quantite_input)

        self.poids_input = QDoubleSpinBox()
        self.poids_input.setRange(0, 200)
        self.poids_input.setDecimals(1)
        self.poids_input.setSuffix(" g")
        form.addRow("Poids moyen", self.poids_input)

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observation optionnelle")
        self.observation_input.setMinimumHeight(80)
        form.addRow("Observation", self.observation_input)

        layout.addWidget(group)

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

    def validate_and_accept(self):
        if self.quantite_input.value() <= 0:
            show_validation(self, "La quantite doit etre superieure a zero.")
            self.quantite_input.setFocus()
            return
        self.accept()

    def get_data(self):
        poids = self.poids_input.value()
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "categorie": self.categorie_input.currentData(),
            "quantite": self.quantite_input.value(),
            "poids_moyen_g": poids if poids > 0 else None,
            "observation": self.observation_input.toPlainText().strip() or None,
        }
