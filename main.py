# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Nama Kelas]
# ============================================================
# main.py — Entry point aplikasi Dashboard Supermarket Sales
# Jalankan: python main.py
# ============================================================

import sys
import os

# Pastikan direktori proyek ada di sys.path
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from main_window import MainWindow


def main():
    """Inisialisasi dan jalankan aplikasi PySide6."""
    # Aktifkan high-DPI scaling agar tampilan tajam di monitor 4K
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Supermarket Sales Dashboard")
    app.setOrganizationName("Tugas6-VisualisasiData")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
