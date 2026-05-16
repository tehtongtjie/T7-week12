# ============================================================
# Nama  : [Nama Mahasiswa]
# NIM   : [NIM Mahasiswa]
# Kelas : [Nama Kelas]
# ============================================================
# data_loader.py — Modul untuk memuat dan memproses dataset
# Sumber dataset: Supermarket Sales Dataset (Kaggle)
# URL: https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales
# ============================================================

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta


def generate_supermarket_data(n: int = 200) -> pd.DataFrame:
    """
    Generate realistic supermarket sales data jika file CSV tidak tersedia.
    Kolom mengikuti struktur dataset Kaggle Supermarket Sales.

    Kolom utama:
      - Invoice ID   : ID unik setiap transaksi
      - Branch       : Cabang toko (A / B / C)
      - City         : Kota lokasi cabang
      - Customer type: Member atau Normal
      - Gender       : Male / Female
      - Product line : Kategori produk
      - Unit price   : Harga satuan (USD)
      - Quantity     : Jumlah unit yang dibeli
      - Tax 5%       : Pajak 5% dari subtotal
      - Total        : Total pembayaran termasuk pajak
      - Date         : Tanggal transaksi (Jan–Mar 2019)
      - Time         : Jam transaksi
      - Payment      : Metode pembayaran
      - cogs         : Cost of goods sold
      - gross income : Keuntungan kotor
      - Rating       : Rating kepuasan pelanggan (1–10)
    """
    random.seed(42)
    np.random.seed(42)

    branches = {"A": "Yangon", "B": "Mandalay", "C": "Naypyitaw"}
    product_lines = [
        "Health and beauty",
        "Electronic accessories",
        "Home and lifestyle",
        "Sports and travel",
        "Food and beverages",
        "Fashion accessories",
    ]
    payments = ["Ewallet", "Cash", "Credit card"]
    customer_types = ["Member", "Normal"]
    genders = ["Male", "Female"]

    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 3, 30)
    date_range = (end_date - start_date).days

    records = []
    for i in range(n):
        branch = random.choice(list(branches.keys()))
        city = branches[branch]
        ctype = random.choice(customer_types)
        gender = random.choice(genders)
        product = random.choice(product_lines)
        unit_price = round(random.uniform(10.0, 99.99), 2)
        quantity = random.randint(1, 10)
        subtotal = unit_price * quantity
        tax = round(subtotal * 0.05, 4)
        total = round(subtotal + tax, 2)
        cogs = round(subtotal, 2)
        gross_income = round(tax, 4)
        rating = round(random.uniform(4.0, 10.0), 1)
        txn_date = start_date + timedelta(days=random.randint(0, date_range))
        txn_time = f"{random.randint(10, 20):02d}:{random.randint(0, 59):02d}"
        payment = random.choice(payments)
        invoice_id = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

        records.append(
            {
                "Invoice ID": invoice_id,
                "Branch": branch,
                "City": city,
                "Customer type": ctype,
                "Gender": gender,
                "Product line": product,
                "Unit price": unit_price,
                "Quantity": quantity,
                "Tax 5%": tax,
                "Total": total,
                "Date": txn_date.strftime("%m/%d/%Y"),
                "Time": txn_time,
                "Payment": payment,
                "cogs": cogs,
                "gross income": gross_income,
                "Rating": rating,
            }
        )

    return pd.DataFrame(records)


def load_data(csv_path: str = None) -> pd.DataFrame:
    """
    Muat data dari file CSV jika ada, atau generate data sintetis.
    Mengembalikan DataFrame yang sudah dibersihkan dan siap digunakan.
    """
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = generate_supermarket_data(200)

    # Pastikan kolom numerik bertipe float
    numeric_cols = ["Unit price", "Quantity", "Tax 5%", "Total",
                    "cogs", "gross income", "Rating"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parse tanggal
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


def get_summary(df: pd.DataFrame) -> dict:
    """Hitung ringkasan statistik utama dari DataFrame."""
    return {
        "Total Transaksi": len(df),
        "Total Pendapatan": f"${df['Total'].sum():,.2f}",
        "Rata-rata Total": f"${df['Total'].mean():,.2f}",
        "Rata-rata Rating": f"{df['Rating'].mean():.2f}",
        "Cabang Terbanyak": df["Branch"].value_counts().idxmax() if len(df) > 0 else "-",
        "Produk Terlaris": df["Product line"].value_counts().idxmax() if len(df) > 0 else "-",
    }
