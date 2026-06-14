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


class NouvelleBandeDialog(QDialog):
    def __init__(self, parent=None, bande=None):
        super().__init__(parent)
        self.bande = bande
        self.setWindowTitle("Modifier la bande" if bande else "Nouvelle bande")
        configure_dialog(self, 560, 450)
        self.setup_ui()
        if bande:
            self.nom_input.setText(str(bande[1]))
            self.date_input.setDate(QDate.fromString(str(bande[2]), "yyyy-MM-dd"))
            self.nombre_input.setValue(int(bande[3]))
            self.prix_input.setValue(float(bande[4] or 0))

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Modifier une bande" if self.bande else "Créer une nouvelle bande")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        hint = QLabel("Renseignez les informations de démarrage de la bande.")
        hint.setObjectName("dialogHint")
        layout.addWidget(hint)

        group = QGroupBox("Informations générales")
        form = QFormLayout(group)
        prepare_form(form)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex. Bande A - Juin 2026")
        form.addRow("Nom de la bande", self.nom_input)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Date de début", self.date_input)

        self.nombre_input = QSpinBox()
        self.nombre_input.setRange(1, 100000)
        self.nombre_input.setValue(100)
        self.nombre_input.setSuffix(" sujets")
        form.addRow("Effectif initial", self.nombre_input)

        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 1000000)
        self.prix_input.setDecimals(0)
        self.prix_input.setValue(500)
        self.prix_input.setSuffix(" FCFA / poussin")
        form.addRow("Prix d'achat", self.prix_input)
        layout.addWidget(group)

        self.calcul_label = QLabel()
        self.calcul_label.setObjectName("summary")
        layout.addWidget(self.calcul_label)
        self.nombre_input.valueChanged.connect(self.calculer_cout)
        self.prix_input.valueChanged.connect(self.calculer_cout)

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
        self.calculer_cout()

    def calculer_cout(self):
        total = self.nombre_input.value() * self.prix_input.value()
        self.calcul_label.setText(f"Coût initial estimé : {total:,.0f} FCFA")

    def validate_and_accept(self):
        if not self.nom_input.text().strip():
            show_validation(self, "Le nom de la bande est obligatoire.")
            self.nom_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "nom": self.nom_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "nombre": self.nombre_input.value(),
            "prix": self.prix_input.value(),
        }
