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
    QTextEdit,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class SaisieAlimentDialog(QDialog):
    def __init__(self, bande_id, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.setWindowTitle("Saisie aliment")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Saisir l'aliment distribue")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Consommation d'aliment")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.quantite_input = QDoubleSpinBox()
        self.quantite_input.setRange(0, 100000)
        self.quantite_input.setDecimals(2)
        self.quantite_input.setSingleStep(1)
        self.quantite_input.setSuffix(" kg")
        form.addRow("Quantite distribuee", self.quantite_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Demarrage",
            "Croissance",
            "Finition",
            "Autre aliment",
        ])
        form.addRow("Type d'aliment", self.type_combo)

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observation optionnelle")
        self.observation_input.setMinimumHeight(75)
        form.addRow("Observation", self.observation_input)

        layout.addWidget(group)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("summary")
        layout.addWidget(self.summary_label)
        self.quantite_input.valueChanged.connect(self.update_summary)

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

        self.update_summary()

    def update_summary(self):
        self.summary_label.setText(
            f"Aliment comptabilise : {self.quantite_input.value():,.2f} kg"
        )

    def validate_and_accept(self):
        if self.quantite_input.value() <= 0:
            show_validation(self, "La quantite d'aliment doit etre superieure a zero.")
            self.quantite_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "quantite_kg": self.quantite_input.value(),
            "type_aliment": self.type_combo.currentText(),
            "observation": self.observation_input.toPlainText().strip(),
        }
