from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
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


class SaisiePeseeDialog(QDialog):
    def __init__(self, bande_id, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.setWindowTitle("Nouvelle pesee")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Enregistrer une pesee")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Suivi de croissance")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.poids_input = QDoubleSpinBox()
        self.poids_input.setRange(0, 10000)
        self.poids_input.setDecimals(0)
        self.poids_input.setSingleStep(10)
        self.poids_input.setValue(500)
        self.poids_input.setSuffix(" g / sujet")
        form.addRow("Poids moyen", self.poids_input)

        self.effectif_input = QSpinBox()
        self.effectif_input.setRange(0, 100000)
        self.effectif_input.setValue(30)
        self.effectif_input.setSuffix(" sujets")
        form.addRow("Effectif pese", self.effectif_input)

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observation optionnelle")
        self.observation_input.setMinimumHeight(75)
        form.addRow("Observation", self.observation_input)

        layout.addWidget(group)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("summary")
        layout.addWidget(self.summary_label)
        self.poids_input.valueChanged.connect(self.update_summary)
        self.effectif_input.valueChanged.connect(self.update_summary)

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
            f"Echantillon : {self.effectif_input.value()} sujets a "
            f"{self.poids_input.value():,.0f} g de moyenne"
        )

    def validate_and_accept(self):
        if self.poids_input.value() <= 0:
            show_validation(self, "Le poids moyen doit etre superieur a zero.")
            self.poids_input.setFocus()
            return
        if self.effectif_input.value() <= 0:
            show_validation(self, "L'effectif pese doit etre superieur a zero.")
            self.effectif_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "poids_moyen_g": self.poids_input.value(),
            "effectif_pese": self.effectif_input.value(),
            "observation": self.observation_input.toPlainText().strip(),
        }
