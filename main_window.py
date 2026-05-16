# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Nama Kelas]
# ============================================================
# main_window.py — Jendela utama Dashboard Visualisasi Data
# Dataset  : Supermarket Sales Dataset
# Sumber   : https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales
# ============================================================

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QFrame,
    QFileDialog, QStatusBar, QScrollArea, QGridLayout,
    QSizePolicy, QTabWidget,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

import pandas as pd

from data_loader import load_data, get_summary
from chart_widget import ChartWidget

# ─── Konstanta warna ──────────────────────────────────────
C_BG      = "#0F1117"
C_PANEL   = "#1A1D2E"
C_CARD    = "#252840"
C_ACCENT  = "#4F8EF7"
C_ACCENT2 = "#F7754F"
C_TEXT    = "#E8EAF6"
C_MUTED   = "#8B8FA8"
C_BORDER  = "#2E3250"
C_SUCCESS = "#4FD18E"
C_WARN    = "#F7C84F"

# ─── Style Sheet Global ───────────────────────────────────
QSS = f"""
/* Window & panel utama */
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Display", Helvetica, Arial, sans-serif;
    font-size: 13px;
}}

/* Tab Bar */
QTabWidget::pane {{
    border: 1px solid {C_BORDER};
    background: {C_PANEL};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {C_CARD};
    color: {C_MUTED};
    padding: 8px 20px;
    margin-right: 2px;
    border-radius: 4px 4px 0 0;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {C_PANEL};
    color: {C_ACCENT};
    border-bottom: 2px solid {C_ACCENT};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    color: {C_TEXT};
    background: {C_PANEL};
}}

/* ComboBox */
QComboBox {{
    background-color: {C_CARD};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 28px;
}}
QComboBox:hover {{ border-color: {C_ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {C_CARD};
    color: {C_TEXT};
    selection-background-color: {C_ACCENT};
    border: 1px solid {C_BORDER};
}}

/* Tombol */
QPushButton {{
    background-color: {C_ACCENT};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: 600;
    min-height: 32px;
}}
QPushButton:hover    {{ background-color: #6CA3FF; }}
QPushButton:pressed  {{ background-color: #3A6FD4; }}
QPushButton#btnRefresh {{
    background-color: {C_CARD};
    color: {C_ACCENT};
    border: 1px solid {C_ACCENT};
}}
QPushButton#btnRefresh:hover {{ background-color: {C_ACCENT}; color: white; }}
QPushButton#btnExport {{
    background-color: {C_CARD};
    color: {C_SUCCESS};
    border: 1px solid {C_SUCCESS};
}}
QPushButton#btnExport:hover {{ background-color: {C_SUCCESS}; color: {C_BG}; }}

/* QTableWidget */
QTableWidget {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    gridline-color: {C_BORDER};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    font-size: 12px;
    selection-background-color: {C_ACCENT};
    selection-color: white;
}}
QTableWidget::item {{ padding: 4px 8px; }}
QHeaderView::section {{
    background-color: {C_CARD};
    color: {C_ACCENT};
    padding: 6px 8px;
    border: none;
    border-bottom: 2px solid {C_BORDER};
    font-weight: bold;
    font-size: 11px;
}}
QTableWidget::item:alternate {{ background-color: {C_CARD}; }}

/* Scroll bar */
QScrollBar:vertical, QScrollBar:horizontal {{
    background: {C_PANEL};
    width: 8px; height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {C_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}

/* Status bar */
QStatusBar {{
    background: {C_PANEL};
    color: {C_MUTED};
    font-size: 11px;
    border-top: 1px solid {C_BORDER};
}}

/* Label */
QLabel#lblTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {C_TEXT};
}}
QLabel#lblSubtitle {{
    font-size: 12px;
    color: {C_MUTED};
}}

/* Card ringkasan */
QFrame#summaryCard {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 8px;
}}

/* Splitter handle */
QSplitter::handle {{
    background: {C_BORDER};
    width: 2px; height: 2px;
}}
"""


def _make_card(label: str, value: str, color: str = C_ACCENT) -> QFrame:
    """Buat widget kartu ringkasan statistik."""
    card = QFrame()
    card.setObjectName("summaryCard")
    card.setFixedHeight(90)
    layout = QVBoxLayout(card)
    layout.setSpacing(4)

    lbl = QLabel(label)
    lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; font-weight: 500;")
    lbl.setAlignment(Qt.AlignCenter)

    val = QLabel(value)
    val.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 700;")
    val.setAlignment(Qt.AlignCenter)

    layout.addWidget(lbl)
    layout.addWidget(val)
    return card


class MainWindow(QMainWindow):
    """Jendela utama Dashboard Visualisasi Supermarket Sales."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Supermarket Sales Dashboard")
        self.setMinimumSize(1200, 750)

        # Muat data
        self.df_all = load_data()   # Semua data
        self.df     = self.df_all.copy()  # Data yang sedang ditampilkan

        # Terapkan stylesheet
        self.setStyleSheet(QSS)

        # Buat UI
        self._build_ui()

        # Isi tabel dan chart awal
        self._refresh_all()

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status = sb
        self._update_status()

    # ──────────────────────────────────────────────────────
    # Pembangunan UI
    # ──────────────────────────────────────────────────────

    def _build_ui(self):
        """Bangun struktur layout utama dashboard."""
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 8)
        root.setSpacing(10)

        # ── Header ──
        root.addLayout(self._build_header())

        # ── Kartu Ringkasan ──
        self.summary_grid = QGridLayout()
        self.summary_grid.setSpacing(10)
        root.addLayout(self.summary_grid)

        # ── Tab area ──
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, stretch=1)

        # Tab 1: Tabel Data
        self.tabs.addTab(self._build_table_tab(), "📋  Data Mentah")

        # Tab 2: Chart
        self.tabs.addTab(self._build_chart_tab(), "📈  Visualisasi")

    def _build_header(self) -> QHBoxLayout:
        """Bangun area header dengan judul, filter, dan tombol aksi."""
        hbox = QHBoxLayout()
        hbox.setSpacing(12)

        # Judul
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Supermarket Sales Dashboard")
        lbl_title.setObjectName("lblTitle")
        lbl_sub = QLabel("Dataset: Kaggle — Supermarket Sales Dataset | 200 Transaksi")
        lbl_sub.setObjectName("lblSubtitle")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        hbox.addLayout(title_box)
        hbox.addStretch()

        # Filter: Cabang
        hbox.addWidget(QLabel("Cabang:"))
        self.cmb_branch = QComboBox()
        self.cmb_branch.setFixedWidth(110)
        self.cmb_branch.addItem("Semua")
        for b in sorted(self.df_all["Branch"].unique()):
            self.cmb_branch.addItem(b)
        self.cmb_branch.currentTextChanged.connect(self._on_filter_changed)
        hbox.addWidget(self.cmb_branch)

        # Filter: Kategori Produk
        hbox.addWidget(QLabel("Produk:"))
        self.cmb_product = QComboBox()
        self.cmb_product.setFixedWidth(170)
        self.cmb_product.addItem("Semua")
        for p in sorted(self.df_all["Product line"].unique()):
            self.cmb_product.addItem(p)
        self.cmb_product.currentTextChanged.connect(self._on_filter_changed)
        hbox.addWidget(self.cmb_product)

        # Filter: Metode Pembayaran
        hbox.addWidget(QLabel("Pembayaran:"))
        self.cmb_payment = QComboBox()
        self.cmb_payment.setFixedWidth(120)
        self.cmb_payment.addItem("Semua")
        for py in sorted(self.df_all["Payment"].unique()):
            self.cmb_payment.addItem(py)
        self.cmb_payment.currentTextChanged.connect(self._on_filter_changed)
        hbox.addWidget(self.cmb_payment)

        # Tombol Refresh
        btn_refresh = QPushButton("⟳  Refresh")
        btn_refresh.setObjectName("btnRefresh")
        btn_refresh.setFixedWidth(100)
        btn_refresh.clicked.connect(self._on_refresh)
        hbox.addWidget(btn_refresh)

        return hbox

    def _build_table_tab(self) -> QWidget:
        """Tab tabel data mentah dengan QTableWidget."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(6)

        # Info baris
        self.lbl_row_count = QLabel()
        self.lbl_row_count.setStyleSheet(f"color: {C_MUTED}; font-size: 11px;")
        layout.addWidget(self.lbl_row_count)

        # Tabel
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        return container

    def _build_chart_tab(self) -> QWidget:
        """Tab visualisasi dengan dua baris chart (2×3 grid)."""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 8, 0, 0)
        main_layout.setSpacing(8)

        # Toolbar pilihan chart + tombol export
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Pilih Chart:"))

        self.cmb_chart_top = QComboBox()
        self.cmb_chart_top.setFixedWidth(220)
        self.cmb_chart_top.addItems([
            "Pendapatan per Cabang (Bar)",
            "Tren Harian (Line)",
            "Rating vs Total (Scatter)",
            "Per Cabang & Gender (Grouped Bar)",
        ])
        self.cmb_chart_top.currentIndexChanged.connect(self._update_top_chart)
        toolbar.addWidget(self.cmb_chart_top)

        toolbar.addSpacing(20)
        toolbar.addWidget(QLabel("Chart 2:"))

        self.cmb_chart_bot = QComboBox()
        self.cmb_chart_bot.setFixedWidth(220)
        self.cmb_chart_bot.addItems([
            "Distribusi Produk (Pie)",
            "Metode Pembayaran (Bar)",
        ])
        self.cmb_chart_bot.setCurrentIndex(0)
        self.cmb_chart_bot.currentIndexChanged.connect(self._update_bot_chart)
        toolbar.addWidget(self.cmb_chart_bot)

        toolbar.addStretch()

        btn_export = QPushButton("💾  Export PNG")
        btn_export.setObjectName("btnExport")
        btn_export.setFixedWidth(130)
        btn_export.clicked.connect(self._export_chart)
        toolbar.addWidget(btn_export)

        main_layout.addLayout(toolbar)

        # Dua chart berdampingan
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.chart_top = ChartWidget()
        self.chart_bot = ChartWidget()

        splitter.addWidget(self.chart_top)
        splitter.addWidget(self.chart_bot)
        splitter.setSizes([600, 600])

        main_layout.addWidget(splitter, stretch=1)

        return container

    # ──────────────────────────────────────────────────────
    # Logika Data & Update
    # ──────────────────────────────────────────────────────

    def _apply_filter(self):
        """Terapkan filter cabang, produk, dan pembayaran ke df."""
        df = self.df_all.copy()

        branch = self.cmb_branch.currentText()
        if branch != "Semua":
            df = df[df["Branch"] == branch]

        product = self.cmb_product.currentText()
        if product != "Semua":
            df = df[df["Product line"] == product]

        payment = self.cmb_payment.currentText()
        if payment != "Semua":
            df = df[df["Payment"] == payment]

        self.df = df

    def _refresh_all(self):
        """Refresh tabel, ringkasan, dan semua chart."""
        self._fill_table()
        self._fill_summary()
        self._update_top_chart()
        self._update_bot_chart()

    def _fill_summary(self):
        """Perbarui kartu ringkasan statistik."""
        # Hapus kartu lama
        while self.summary_grid.count():
            item = self.summary_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        summary = get_summary(self.df)
        labels = list(summary.keys())
        values = list(summary.values())
        colors = [C_ACCENT, C_SUCCESS, C_ACCENT2, C_WARN, C_TEXT, C_MUTED]

        for i, (lbl, val) in enumerate(zip(labels, values)):
            card = _make_card(lbl, str(val), colors[i % len(colors)])
            self.summary_grid.addWidget(card, 0, i)

    def _fill_table(self):
        """Isi QTableWidget dengan data yang sudah difilter."""
        df = self.df.reset_index(drop=True)

        # Kolom yang ditampilkan
        show_cols = [
            "Invoice ID", "Branch", "City", "Customer type",
            "Gender", "Product line", "Unit price", "Quantity",
            "Total", "Payment", "Rating",
        ]
        show_cols = [c for c in show_cols if c in df.columns]
        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(show_cols))
        self.table.setHorizontalHeaderLabels(show_cols)

        for row_idx, row in df.iterrows():
            for col_idx, col in enumerate(show_cols):
                val = row[col]
                if isinstance(val, float):
                    text = f"{val:.2f}" if col in ("Unit price", "Total", "Rating") else str(val)
                elif hasattr(val, "strftime"):
                    text = val.strftime("%Y-%m-%d")
                else:
                    text = str(val)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.lbl_row_count.setText(
            f"Menampilkan {len(df)} dari {len(self.df_all)} baris"
        )

    def _update_top_chart(self):
        """Gambar ulang chart atas sesuai pilihan ComboBox."""
        idx = self.cmb_chart_top.currentIndex()
        if   idx == 0: self.chart_top.plot_bar_branch(self.df)
        elif idx == 1: self.chart_top.plot_line_trend(self.df)
        elif idx == 2: self.chart_top.plot_scatter_rating(self.df)
        elif idx == 3: self.chart_top.plot_bar_gender(self.df)

    def _update_bot_chart(self):
        """Gambar ulang chart bawah sesuai pilihan ComboBox."""
        idx = self.cmb_chart_bot.currentIndex()
        if   idx == 0: self.chart_bot.plot_pie_product(self.df)
        elif idx == 1: self.chart_bot.plot_bar_payment(self.df)

    # ──────────────────────────────────────────────────────
    # Slot / Handler
    # ──────────────────────────────────────────────────────

    def _on_filter_changed(self):
        """Dipanggil saat nilai ComboBox filter berubah."""
        self._apply_filter()
        self._refresh_all()
        self._update_status()

    def _on_refresh(self):
        """Reset semua filter lalu refresh."""
        self.cmb_branch.setCurrentIndex(0)
        self.cmb_product.setCurrentIndex(0)
        self.cmb_payment.setCurrentIndex(0)
        self._apply_filter()
        self._refresh_all()
        self._update_status("Data di-refresh.")

    def _export_chart(self):
        """Simpan chart aktif (tab kiri) ke file PNG."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Chart", "chart_export.png",
            "PNG Image (*.png);;All Files (*)"
        )
        if path:
            self.chart_top.save_to_png(path)
            self._status.showMessage(f"Chart disimpan ke: {path}", 5000)

    def _update_status(self, msg: str = ""):
        """Perbarui teks status bar."""
        base = (
            f"Total data: {len(self.df_all)} baris  |  "
            f"Ditampilkan: {len(self.df)} baris  |  "
            f"Filter: Cabang={self.cmb_branch.currentText()}  "
            f"Produk={self.cmb_product.currentText()}  "
            f"Pembayaran={self.cmb_payment.currentText()}"
        )
        full = f"{base}  {'— ' + msg if msg else ''}"
        self._status.showMessage(full)
