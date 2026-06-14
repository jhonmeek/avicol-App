from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
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


class SaisieMortaliteDialog(QDialog):
    def __init__(self, bande_id, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.setWindowTitle("Déclaration de mortalité")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        title = QLabel("Déclarer une mortalité")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Informations sanitaires")
        form = QFormLayout(group)
        prepare_form(form)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)
        self.nombre_input = QSpinBox()
        self.nombre_input.setRange(1, 100000)
        self.nombre_input.setSuffix(" sujets")
        form.addRow("Nombre de morts", self.nombre_input)
        self.cause_combo = QComboBox()
        self.cause_combo.addItems([
            "Sélectionner une cause",
            "Maladie infectieuse",
            "Stress thermique",
            "Problème alimentaire",
            "Manque d'eau",
            "Prédation",
            "Accident",
            "Cause inconnue",
            "Autre",
        ])
        form.addRow("Cause principale", self.cause_combo)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Observations complémentaires")
        self.desc_input.setMinimumHeight(80)
        form.addRow("Observations", self.desc_input)
        layout.addWidget(group)

        warning = QLabel(
            "Cette déclaration modifiera immédiatement l'effectif disponible."
        )
        warning.setObjectName("warning")
        warning.setWordWrap(True)
        layout.addWidget(warning)

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
        if self.cause_combo.currentIndex() == 0:
            show_validation(self, "Sélectionnez la cause principale.")
            self.cause_combo.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "nombre": self.nombre_input.value(),
            "cause": self.cause_combo.currentText(),
            "description": self.desc_input.toPlainText().strip(),
        }
