from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from .styles import configure_dialog, prepare_form, show_validation


class SaisieInterventionDialog(QDialog):
    def __init__(self, bande_id, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.setWindowTitle("Intervention sanitaire")
        configure_dialog(self, 560, 520)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Enregistrer une intervention sanitaire")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Details de l'intervention")
        form = QFormLayout(group)
        prepare_form(form)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Vaccination", "vaccination")
        self.type_combo.addItem("Traitement", "traitement")
        form.addRow("Type", self.type_combo)

        self.produit_input = QLineEdit()
        self.produit_input.setPlaceholderText("Ex. Vaccin Newcastle")
        form.addRow("Produit", self.produit_input)

        self.dose_input = QLineEdit()
        self.dose_input.setPlaceholderText("Ex. 1 goutte / sujet (optionnel)")
        form.addRow("Dose", self.dose_input)

        self.intervenant_input = QLineEdit()
        self.intervenant_input.setPlaceholderText("Optionnel")
        form.addRow("Intervenant", self.intervenant_input)

        layout.addWidget(group)

        self.echeance_checkbox = QCheckBox("Planifier une prochaine echeance")
        layout.addWidget(self.echeance_checkbox)

        self.echeance_input = QDateEdit(QDate.currentDate().addDays(14))
        self.echeance_input.setCalendarPopup(True)
        self.echeance_input.setEnabled(False)
        self.echeance_checkbox.toggled.connect(self.echeance_input.setEnabled)
        layout.addWidget(self.echeance_input)

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
        if not self.produit_input.text().strip():
            show_validation(self, "Le produit est obligatoire.")
            self.produit_input.setFocus()
            return
        self.accept()

    def get_data(self):
        echeance = None
        if self.echeance_checkbox.isChecked():
            echeance = self.echeance_input.date().toString("yyyy-MM-dd")
        return {
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "type_intervention": self.type_combo.currentData(),
            "produit": self.produit_input.text().strip(),
            "dose": self.dose_input.text().strip() or None,
            "intervenant": self.intervenant_input.text().strip() or None,
            "prochaine_echeance": echeance,
        }
