from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
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


class SaisiePonteDialog(QDialog):
    def __init__(self, bande_id, poules_presentes, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.poules_presentes = int(poules_presentes)
        self.setWindowTitle("Saisie ponte")
        configure_dialog(self, 560, 480)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Saisir la ponte du jour")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        hint = QLabel(f"Poules présentes : {self.poules_presentes:,}")
        hint.setObjectName("warning")
        layout.addWidget(hint)

        group = QGroupBox("Production d'œufs")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.nombre_oeufs_input = QSpinBox()
        self.nombre_oeufs_input.setRange(0, 100000)
        self.nombre_oeufs_input.setSuffix(" œufs")
        form.addRow("Œufs pondus", self.nombre_oeufs_input)

        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observation optionnelle")
        self.observation_input.setMinimumHeight(75)
        form.addRow("Observation", self.observation_input)

        layout.addWidget(group)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("summary")
        layout.addWidget(self.summary_label)
        self.nombre_oeufs_input.valueChanged.connect(self.update_summary)

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
        nombre = self.nombre_oeufs_input.value()
        if self.poules_presentes > 0:
            taux = nombre / self.poules_presentes * 100
            self.summary_label.setText(f"Taux de ponte du jour : {taux:.1f} %")
        else:
            self.summary_label.setText(
                "Aucune poule présente : le taux de ponte ne peut pas être calculé."
            )

    def validate_and_accept(self):
        if self.nombre_oeufs_input.value() <= 0:
            show_validation(self, "Le nombre d'œufs doit être supérieur à zéro.")
            self.nombre_oeufs_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "nombre_oeufs": self.nombre_oeufs_input.value(),
            "observation": self.observation_input.toPlainText().strip(),
        }
