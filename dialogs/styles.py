"""Styles et helpers partagés par les fenêtres de saisie."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFormLayout, QMessageBox


DIALOG_QSS = """
QDialog {
    background-color: #F3F6FA;
    color: #152536;
}
QLabel {
    background: transparent;
    color: #334155;
}
QLabel#dialogTitle {
    color: #123B5D;
    font-size: 20px;
    font-weight: 700;
}
QLabel#dialogHint {
    color: #64748B;
    font-size: 11px;
}
QLabel#summary {
    background-color: #EAF1F7;
    color: #123B5D;
    border: 1px solid #B8C6D4;
    border-radius: 7px;
    padding: 12px;
    font-size: 14px;
    font-weight: 700;
}
QLabel#warning {
    background-color: #FFF3E0;
    color: #8A4B00;
    border: 1px solid #E8C58D;
    border-radius: 7px;
    padding: 10px;
}
QGroupBox {
    background-color: #FFFFFF;
    color: #123B5D;
    border: 1px solid #D9E2EC;
    border-radius: 9px;
    margin-top: 14px;
    padding: 20px 14px 14px 14px;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
    background-color: #FFFFFF;
    color: #152536;
    border: 1px solid #B8C6D4;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 22px;
    selection-background-color: #123B5D;
    selection-color: #FFFFFF;
}
QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QTextEdit:focus {
    border: 1px solid #123B5D;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #152536;
    border: 1px solid #B8C6D4;
    selection-background-color: #EAF1F7;
    selection-color: #152536;
}
QPushButton {
    background-color: #123B5D;
    color: #FFFFFF;
    border: 1px solid #123B5D;
    border-radius: 6px;
    padding: 9px 18px;
    min-height: 22px;
    font-weight: 700;
}
QPushButton:hover {
    background-color: #0B2E49;
}
QPushButton[secondary="true"] {
    background-color: #FFFFFF;
    color: #123B5D;
    border-color: #B8C6D4;
}
QPushButton[secondary="true"]:hover {
    background-color: #EAF1F7;
    border-color: #123B5D;
}
QMessageBox {
    background-color: #F3F6FA;
}
QMessageBox QLabel {
    color: #152536;
    min-width: 280px;
}
"""


def configure_dialog(dialog: QDialog, width=560, height=480):
    dialog.setModal(True)
    dialog.setMinimumSize(440, 360)
    dialog.resize(width, height)
    dialog.setSizeGripEnabled(True)
    dialog.setStyleSheet(DIALOG_QSS)


def show_validation(parent, text):
    box = QMessageBox(QMessageBox.Icon.Warning, "Vérification", text, parent=parent)
    box.setStyleSheet(DIALOG_QSS)
    box.exec()


def prepare_form(form):
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
    form.setHorizontalSpacing(18)
    form.setVerticalSpacing(12)
    form.setFieldGrowthPolicy(
        QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
    )
