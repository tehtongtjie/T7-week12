# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Nama Kelas]
# ============================================================
# chart_widget.py — Widget Matplotlib yang tertanam di PySide6
# ============================================================

import matplotlib
matplotlib.use("Agg")  # Backend non-interaktif agar aman di PySide6

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy


# Palet warna konsisten untuk seluruh dashboard
COLORS = ["#4F8EF7", "#F7754F", "#4FD18E", "#F7C84F",
          "#A54FF7", "#F74FA5", "#4FF7F0", "#F7A54F"]

DARK_BG  = "#1A1D2E"
PANEL_BG = "#252840"
TEXT_COL = "#E8EAF6"
GRID_COL = "#2E3250"


def _style_axes(ax, title: str = ""):
    """Terapkan tema gelap konsisten ke sumbu Matplotlib."""
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COL)
    ax.grid(color=GRID_COL, linewidth=0.5, alpha=0.6)
    if title:
        ax.set_title(title, color=TEXT_COL, fontsize=10, fontweight="bold", pad=8)
    ax.title.set_color(TEXT_COL)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)


class ChartWidget(QWidget):
    """
    Widget tunggal yang memuat FigureCanvas Matplotlib.
    Mendukung berbagai jenis chart yang dapat diperbarui secara dinamis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Buat Figure dan Canvas
        self.figure = Figure(facecolor=DARK_BG, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def _clear(self):
        """Bersihkan figure sebelum menggambar ulang."""
        self.figure.clear()

    def plot_bar_branch(self, df: pd.DataFrame):
        """Bar chart: Total Pendapatan per Cabang."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        grouped = df.groupby("Branch")["Total"].sum().reset_index()
        bars = ax.bar(grouped["Branch"], grouped["Total"],
                      color=COLORS[:len(grouped)], width=0.5, edgecolor=DARK_BG, linewidth=1.2)

        # Label nilai di atas bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 50,
                    f"${height:,.0f}", ha="center", va="bottom",
                    color=TEXT_COL, fontsize=8, fontweight="bold")

        _style_axes(ax, "Total Pendapatan per Cabang")
        ax.set_xlabel("Cabang", fontsize=8)
        ax.set_ylabel("Total (USD)", fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.canvas.draw()

    def plot_pie_product(self, df: pd.DataFrame):
        """Pie chart: Distribusi Penjualan per Lini Produk."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        grouped = df.groupby("Product line")["Total"].sum()
        wedges, texts, autotexts = ax.pie(
            grouped.values,
            labels=None,
            autopct="%1.1f%%",
            colors=COLORS[:len(grouped)],
            startangle=140,
            wedgeprops={"edgecolor": DARK_BG, "linewidth": 1.5},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_color(DARK_BG)
            at.set_fontsize(7.5)
            at.set_fontweight("bold")

        ax.legend(
            wedges, grouped.index,
            loc="upper left", bbox_to_anchor=(-0.15, 1.15),
            fontsize=7, labelcolor=TEXT_COL,
            framealpha=0, handlelength=1,
        )
        ax.set_facecolor(PANEL_BG)
        ax.set_title("Distribusi Penjualan per Lini Produk",
                     color=TEXT_COL, fontsize=10, fontweight="bold", pad=8)
        self.figure.set_facecolor(DARK_BG)
        self.canvas.draw()

    def plot_line_trend(self, df: pd.DataFrame):
        """Line chart: Tren Pendapatan Harian."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty or "Date" not in df.columns:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        trend = df.groupby(df["Date"].dt.date)["Total"].sum().reset_index()
        trend.columns = ["Date", "Total"]
        trend = trend.sort_values("Date")

        ax.plot(trend["Date"], trend["Total"],
                color=COLORS[0], linewidth=2, marker="o",
                markersize=3, markerfacecolor=COLORS[1])
        ax.fill_between(trend["Date"], trend["Total"],
                        alpha=0.15, color=COLORS[0])

        _style_axes(ax, "Tren Pendapatan Harian")
        ax.set_xlabel("Tanggal", fontsize=8)
        ax.set_ylabel("Total (USD)", fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=7)
        self.canvas.draw()

    def plot_bar_payment(self, df: pd.DataFrame):
        """Horizontal bar chart: Distribusi Metode Pembayaran."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        grouped = df.groupby("Payment")["Total"].sum().sort_values()
        bars = ax.barh(grouped.index, grouped.values,
                       color=COLORS[2:5], edgecolor=DARK_BG, linewidth=1.2, height=0.5)

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 100, bar.get_y() + bar.get_height() / 2,
                    f"${width:,.0f}", va="center", color=TEXT_COL, fontsize=8)

        _style_axes(ax, "Total per Metode Pembayaran")
        ax.set_xlabel("Total (USD)", fontsize=8)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.canvas.draw()

    def plot_scatter_rating(self, df: pd.DataFrame):
        """Scatter chart: Hubungan Total vs Rating."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        scatter = ax.scatter(
            df["Rating"], df["Total"],
            c=COLORS[0], alpha=0.55, s=20, edgecolors="none"
        )
        # Garis tren
        z = np.polyfit(df["Rating"].dropna(), df["Total"].dropna(), 1)
        p = np.poly1d(z)
        x_line = np.linspace(df["Rating"].min(), df["Rating"].max(), 100)
        ax.plot(x_line, p(x_line), color=COLORS[1], linewidth=1.5, linestyle="--")

        _style_axes(ax, "Hubungan Rating vs Total Pembelian")
        ax.set_xlabel("Rating", fontsize=8)
        ax.set_ylabel("Total (USD)", fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.canvas.draw()

    def plot_bar_gender(self, df: pd.DataFrame):
        """Grouped bar chart: Pendapatan berdasarkan Gender & Cabang."""
        self._clear()
        ax = self.figure.add_subplot(111)
        if df.empty:
            ax.text(0.5, 0.5, "Tidak ada data", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_COL)
            self.canvas.draw()
            return

        pivot = df.pivot_table(values="Total", index="Branch",
                               columns="Gender", aggfunc="sum", fill_value=0)
        x = np.arange(len(pivot.index))
        width = 0.35
        for i, (col, color) in enumerate(zip(pivot.columns, [COLORS[0], COLORS[3]])):
            offset = (i - 0.5) * width
            bars = ax.bar(x + offset, pivot[col], width, label=col,
                          color=color, edgecolor=DARK_BG, linewidth=1)

        ax.set_xticks(x)
        ax.set_xticklabels(pivot.index, color=TEXT_COL, fontsize=8)
        ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0)
        _style_axes(ax, "Pendapatan per Cabang & Gender")
        ax.set_xlabel("Cabang", fontsize=8)
        ax.set_ylabel("Total (USD)", fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.canvas.draw()

    def save_to_png(self, filepath: str):
        """Simpan chart aktif ke file PNG."""
        self.figure.savefig(filepath, dpi=150, bbox_inches="tight",
                            facecolor=DARK_BG, edgecolor="none")
