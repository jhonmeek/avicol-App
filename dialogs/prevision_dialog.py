from PyQt6.QtWidgets import (
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

from .styles import configure_dialog, prepare_form


class PrevisionLotDialog(QDialog):
    def __init__(self, bande_id, prevision=None, parent=None):
        super().__init__(parent)
        self.bande_id = bande_id
        self.prevision = prevision
        self.setWindowTitle("Previsions du lot")
        configure_dialog(self, 620, 650)
        self.setup_ui()
        self.load_prevision()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        title = QLabel("Previsionnel du lot")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        costs_group = QGroupBox("Charges prevues")
        costs_form = QFormLayout(costs_group)
        prepare_form(costs_form)
        self.cout_poussins_input = self._money_spin()
        self.cout_aliment_input = self._money_spin()
        self.cout_sanitaire_input = self._money_spin()
        self.autres_charges_input = self._money_spin()
        costs_form.addRow("Cout poussins", self.cout_poussins_input)
        costs_form.addRow("Aliment", self.cout_aliment_input)
        costs_form.addRow("Sanitaire", self.cout_sanitaire_input)
        costs_form.addRow("Autres charges", self.autres_charges_input)
        layout.addWidget(costs_group)

        chair_group = QGroupBox("Recettes prevues - chair")
        chair_form = QFormLayout(chair_group)
        prepare_form(chair_form)
        self.quantite_vendue_input = self._quantity_spin(" sujet(s)")
        self.prix_vente_input = self._money_spin()
        chair_form.addRow("Quantite vendue", self.quantite_vendue_input)
        chair_form.addRow("Prix unitaire", self.prix_vente_input)
        layout.addWidget(chair_group)

        ponte_group = QGroupBox("Recettes prevues - ponte")
        ponte_form = QFormLayout(ponte_group)
        prepare_form(ponte_form)
        self.oeufs_input = QSpinBox()
        self.oeufs_input.setRange(0, 100000000)
        self.oeufs_input.setSuffix(" oeuf(s)")
        self.prix_oeuf_input = self._money_spin()
        ponte_form.addRow("Oeufs prevus", self.oeufs_input)
        ponte_form.addRow("Prix par oeuf", self.prix_oeuf_input)
        layout.addWidget(ponte_group)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Hypotheses ou commentaire optionnel")
        self.note_input.setMinimumHeight(75)
        layout.addWidget(self.note_input)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Annuler")
        cancel.setProperty("secondary", "true")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Enregistrer")
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _money_spin(self):
        widget = QDoubleSpinBox()
        widget.setRange(0, 10000000000)
        widget.setDecimals(0)
        widget.setSuffix(" FCFA")
        return widget

    def _quantity_spin(self, suffix):
        widget = QDoubleSpinBox()
        widget.setRange(0, 100000000)
        widget.setDecimals(0)
        widget.setSuffix(suffix)
        return widget

    def load_prevision(self):
        if not self.prevision:
            return
        self.cout_poussins_input.setValue(self.prevision[2] or 0)
        self.cout_aliment_input.setValue(self.prevision[3] or 0)
        self.cout_sanitaire_input.setValue(self.prevision[4] or 0)
        self.autres_charges_input.setValue(self.prevision[5] or 0)
        self.quantite_vendue_input.setValue(self.prevision[6] or 0)
        self.prix_vente_input.setValue(self.prevision[7] or 0)
        self.oeufs_input.setValue(int(self.prevision[8] or 0))
        self.prix_oeuf_input.setValue(self.prevision[9] or 0)
        self.note_input.setPlainText(self.prevision[10] or "")

    def get_data(self):
        return {
            "cout_poussins_prevu": self.cout_poussins_input.value(),
            "cout_aliment_prevu": self.cout_aliment_input.value(),
            "cout_sanitaire_prevu": self.cout_sanitaire_input.value(),
            "autres_charges_prevues": self.autres_charges_input.value(),
            "quantite_vendue_prevue": self.quantite_vendue_input.value(),
            "prix_vente_unitaire_prevu": self.prix_vente_input.value(),
            "oeufs_prevus": self.oeufs_input.value(),
            "prix_oeuf_prevu": self.prix_oeuf_input.value(),
            "note": self.note_input.toPlainText().strip() or None,
        }
