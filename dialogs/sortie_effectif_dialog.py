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


class SortieEffectifDialog(QDialog):
    def __init__(self, bande_id, effectif_disponible, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.effectif_disponible = int(effectif_disponible or 0)
        self.setWindowTitle("Sortie d'effectif")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Sortie d'effectif")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        hint = QLabel(f"Effectif disponible : {self.effectif_disponible:,}")
        hint.setObjectName("warning")
        layout.addWidget(hint)

        group = QGroupBox("Mouvement d'effectif")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.nombre_input = QSpinBox()
        self.nombre_input.setRange(1, max(self.effectif_disponible, 1))
        self.nombre_input.setSuffix(" sujets")
        form.addRow("Nombre", self.nombre_input)

        self.motif_combo = QComboBox()
        self.motif_combo.addItems([
            "Réforme",
            "Don",
            "Transfert",
            "Vol",
            "Ajustement",
            "Autre",
        ])
        form.addRow("Motif", self.motif_combo)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Observation optionnelle")
        self.description_input.setMinimumHeight(75)
        form.addRow("Observation", self.description_input)

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
        if self.nombre_input.value() > self.effectif_disponible:
            show_validation(
                self,
                f"La sortie dépasse l'effectif disponible "
                f"({self.effectif_disponible}).",
            )
            self.nombre_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "nombre": self.nombre_input.value(),
            "motif": self.motif_combo.currentText(),
            "description": self.description_input.toPlainText().strip(),
        }
