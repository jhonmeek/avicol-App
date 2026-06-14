"""Point d'entrée de l'application Avicole Pro."""

import os
import sys
import traceback
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

from main_window import ProfessionalMainWindow
from app_paths import data_dir, ensure_user_directories


class AvicoleSplashScreen(QSplashScreen):
    """Écran de démarrage aligné sur l'identité institutionnelle."""

    def __init__(self):
        pixmap = QPixmap(720, 430)
        pixmap.fill(Qt.GlobalColor.transparent)
        self._draw(pixmap)
        super().__init__(pixmap)

    @staticmethod
    def _draw(pixmap):
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        background = QLinearGradient(0, 0, 720, 430)
        background.setColorAt(0, QColor("#081B2D"))
        background.setColorAt(1, QColor("#123B5D"))
        painter.fillRect(pixmap.rect(), background)

        painter.fillRect(0, 0, 8, 430, QColor("#C9A227"))

        painter.setBrush(QColor("#C9A227"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(58, 62, 64, 64, 12, 12)

        painter.setPen(QColor("#0B1F33"))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(58, 62, 64, 64, Qt.AlignmentFlag.AlignCenter, "AP")

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 29, QFont.Weight.Bold))
        painter.drawText(58, 184, "AVICOLE PRO")

        painter.setPen(QColor("#C8D6E3"))
        painter.setFont(QFont("Segoe UI", 13))
        painter.drawText(60, 220, "Système intégré de gestion avicole")

        painter.setPen(QColor("#8FA7BA"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(
            60,
            330,
            "Pilotage  •  Traçabilité  •  Performance  •  Rapports",
        )

        painter.setPen(QColor("#C9A227"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        painter.drawText(60, 382, "INITIALISATION SÉCURISÉE")

        painter.setPen(QColor("#8FA7BA"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(622, 382, "v3.1")
        painter.end()


def ensure_directories():
    return ensure_user_directories()


def install_exception_handler():
    def handle_exception(exc_type, exc_value, exc_traceback):
        log_path = data_dir() / "logs" / "crash.log"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}]\n")
            traceback.print_exception(
                exc_type, exc_value, exc_traceback, file=log
            )
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Avicole Pro")
    app.setOrganizationName("Avicole Pro")
    app.setApplicationDisplayName("Avicole Pro")
    app.setFont(QFont("Segoe UI", 10))

    ensure_directories()
    install_exception_handler()

    splash = AvicoleSplashScreen()
    splash.show()
    app.processEvents()

    window = ProfessionalMainWindow()

    def reveal_window():
        window.showMaximized()
        splash.finish(window)
        if os.environ.get("AVICOLE_SMOKE_TEST") == "1":
            QTimer.singleShot(1200, app.quit)

    QTimer.singleShot(650, reveal_window)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
