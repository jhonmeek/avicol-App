from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
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


class SaisieJournaliereDialog(QDialog):
    """Saisie groupee du quotidien : morts, aliment, oeufs."""

    def __init__(self, bandes, db, parent=None):
        super().__init__(parent)
        self.bandes = bandes
        self.db = db
        self.setWindowTitle("Saisie du jour")
        configure_dialog(self, 560, 560)
        self.setup_ui()
        self.update_doublon_warning()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Saisie journalière")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        group = QGroupBox("Journée d'élevage")
        form = QFormLayout(group)
        prepare_form(form)

        self.bande_combo = QComboBox()
        for bande in self.bandes:
            self.bande_combo.addItem(bande[1], bande[0])
        form.addRow("Bande", self.bande_combo)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date", self.date_input)

        self.morts_input = QSpinBox()
        self.morts_input.setRange(0, 100000)
        self.morts_input.setSuffix(" sujets")
        form.addRow("Morts du jour", self.morts_input)

        self.cause_combo = QComboBox()
        self.cause_combo.addItems([
            "Cause inconnue",
            "Maladie infectieuse",
            "Stress thermique",
            "Problème alimentaire",
            "Manque d'eau",
            "Prédation",
            "Accident",
            "Autre",
        ])
        form.addRow("Cause (si morts)", self.cause_combo)

        self.aliment_input = QDoubleSpinBox()
        self.aliment_input.setRange(0, 100000)
        self.aliment_input.setDecimals(2)
        self.aliment_input.setSingleStep(1)
        self.aliment_input.setSuffix(" kg")
        form.addRow("Aliment distribué", self.aliment_input)

        self.type_aliment_input = QLineEdit()
        self.type_aliment_input.setPlaceholderText("Ex. : démarrage, croissance")
        form.addRow("Type d'aliment", self.type_aliment_input)

        self.oeufs_input = QSpinBox()
        self.oeufs_input.setRange(0, 1000000)
        self.oeufs_input.setSuffix(" oeufs")
        form.addRow("Oeufs ramassés", self.oeufs_input)

        self.oeufs_zero_checkbox = QCheckBox("Enregistrer explicitement 0 oeuf")
        form.addRow("", self.oeufs_zero_checkbox)

        self.observation_input = QLineEdit()
        self.observation_input.setPlaceholderText("Observation facultative")
        form.addRow("Observation", self.observation_input)

        layout.addWidget(group)

        self.doublon_label = QLabel("")
        self.doublon_label.setObjectName("warning")
        self.doublon_label.setWordWrap(True)
        layout.addWidget(self.doublon_label)

        self.bande_combo.currentIndexChanged.connect(self.update_doublon_warning)
        self.date_input.dateChanged.connect(self.update_doublon_warning)

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

    def selected_bande_id(self):
        return self.bande_combo.currentData()

    def update_doublon_warning(self):
        bande_id = self.selected_bande_id()
        if bande_id is None:
            self.doublon_label.setText("")
            return
        date_iso = self.date_input.date().toString("yyyy-MM-dd")
        compte = self.db.compter_saisies_du_jour(bande_id, date_iso)
        deja = [
            libelle
            for cle, libelle in (
                ("mortalites", "mortalité"),
                ("aliment", "aliment"),
                ("pontes", "ponte"),
            )
            if compte[cle] > 0
        ]
        if deja:
            self.doublon_label.setText(
                "Attention : déjà saisi ce jour pour cette bande : "
                + ", ".join(deja)
                + ". Vérifiez avant d'enregistrer un doublon."
            )
        else:
            self.doublon_label.setText("")

    def validate_and_accept(self):
        if (
            self.morts_input.value() == 0
            and self.aliment_input.value() == 0
            and self.oeufs_input.value() == 0
            and not self.oeufs_zero_checkbox.isChecked()
        ):
            show_validation(
                self, "Renseignez au moins une valeur (morts, aliment ou oeufs)."
            )
            return
        self.accept()

    def get_data(self):
        morts = self.morts_input.value() or None
        aliment = self.aliment_input.value() or None
        oeufs = (
            self.oeufs_input.value()
            if self.oeufs_input.value() > 0
            or self.oeufs_zero_checkbox.isChecked()
            else None
        )
        observation = self.observation_input.text().strip() or None
        return {
            "bande_id": self.selected_bande_id(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "morts": morts,
            "cause": self.cause_combo.currentText() if morts else None,
            "aliment_kg": aliment,
            "type_aliment": (
                self.type_aliment_input.text().strip() or None
            ) if aliment else None,
            "oeufs": oeufs,
            "observation": observation,
        }
