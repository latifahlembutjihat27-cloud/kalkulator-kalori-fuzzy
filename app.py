
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# KONFIGURASI WEBSITE
# ==========================================

st.set_page_config(
    page_title="Kalkulator Kalori Pintar",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 KALKULATOR KALORI PINTAR")
st.write(
    "Sistem Penentuan Kebutuhan Kalori Harian "
    "Menggunakan Metode Fuzzy Mamdani"
)

st.divider()

# ==========================================
# FUNGSI KEANGGOTAAN FUZZY
# ==========================================

def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    hasil = np.zeros_like(x)

    if a != b:
        mask = (x >= a) & (x <= b)
        hasil[mask] = (x[mask] - a) / (b - a)

    if b != c:
        mask = (x >= b) & (x <= c)
        hasil[mask] = (c - x[mask]) / (c - b)

    hasil[x == b] = 1

    return np.clip(hasil, 0, 1)


def trapmf(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    hasil = np.zeros_like(x)

    if a == b:
        hasil[x <= b] = 1
    else:
        mask = (x >= a) & (x < b)
        hasil[mask] = (x[mask] - a) / (b - a)

    hasil[(x >= b) & (x <= c)] = 1

    if c == d:
        hasil[x >= c] = 1
    else:
        mask = (x > c) & (x <= d)
        hasil[mask] = (d - x[mask]) / (d - c)

    return np.clip(hasil, 0, 1)


# ==========================================
# VARIABEL FUZZY
# ==========================================

# Berat badan (kg)
x_berat = np.linspace(30, 120, 500)

berat_ringan = trapmf(x_berat, 30, 30, 45, 60)
berat_normal = trimf(x_berat, 50, 70, 90)
berat_berat = trapmf(x_berat, 80, 100, 120, 120)

# Aktivitas fisik (faktor aktivitas)
x_aktivitas = np.linspace(1.2, 2.0, 500)

aktivitas_rendah = trapmf(
    x_aktivitas, 1.2, 1.2, 1.35, 1.5
)
aktivitas_sedang = trimf(
    x_aktivitas, 1.4, 1.6, 1.8
)
aktivitas_tinggi = trapmf(
    x_aktivitas, 1.7, 1.85, 2.0, 2.0
)

# Output kebutuhan kalori (kkal)
x_kalori = np.linspace(1000, 4000, 1000)

kalori_rendah = trapmf(
    x_kalori, 1000, 1000, 1500, 2100
)
kalori_sedang = trimf(
    x_kalori, 1800, 2500, 3200
)
kalori_tinggi = trapmf(
    x_kalori, 2800, 3500, 4000, 4000
)


# ==========================================
# ATURAN IF-THEN FUZZY MAMDANI
# ==========================================

aturan_fuzzy = [
    ("Ringan", "Rendah", "Rendah"),
    ("Ringan", "Sedang", "Sedang"),
    ("Ringan", "Tinggi", "Tinggi"),

    ("Normal", "Rendah", "Sedang"),
    ("Normal", "Sedang", "Sedang"),
    ("Normal", "Tinggi", "Tinggi"),

    ("Berat", "Rendah", "Rendah"),
    ("Berat", "Sedang", "Sedang"),
    ("Berat", "Tinggi", "Tinggi")
]


# ==========================================
# PROSES FUZZY MAMDANI
# ==========================================

def proses_mamdani(berat, aktivitas):

    # Fuzzifikasi berat
    mu_berat = {
        "Ringan": float(trapmf(
            np.array([berat]), 30, 30, 45, 60
        )[0]),
        "Normal": float(trimf(
            np.array([berat]), 50, 70, 90
        )[0]),
        "Berat": float(trapmf(
            np.array([berat]), 80, 100, 120, 120
        )[0])
    }

    # Fuzzifikasi aktivitas
    mu_aktivitas = {
        "Rendah": float(trapmf(
            np.array([aktivitas]), 1.2, 1.2, 1.35, 1.5
        )[0]),
        "Sedang": float(trimf(
            np.array([aktivitas]), 1.4, 1.6, 1.8
        )[0]),
        "Tinggi": float(trapmf(
            np.array([aktivitas]), 1.7, 1.85, 2.0, 2.0
        )[0])
    }

    # Inferensi dan agregasi
    hasil_agregasi = np.zeros_like(x_kalori)
    hasil_aturan = []

    output_fuzzy = {
        "Rendah": kalori_rendah,
        "Sedang": kalori_sedang,
        "Tinggi": kalori_tinggi
    }

    for no, (b, a, k) in enumerate(aturan_fuzzy, start=1):

        alpha = min(mu_berat[b], mu_aktivitas[a])

        hasil_implikasi = np.minimum(
            alpha, output_fuzzy[k]
        )

        hasil_agregasi = np.maximum(
            hasil_agregasi, hasil_implikasi
        )

        hasil_aturan.append({
            "Aturan": f"R{no}",
            "IF": f"Berat {b} AND Aktivitas {a}",
            "THEN": f"Kalori {k}",
            "Alpha": alpha
        })

    # Defuzzifikasi metode Centroid
    penyebut = np.sum(hasil_agregasi)

    if penyebut == 0:
        return None, mu_berat, mu_aktivitas, hasil_agregasi, hasil_aturan

    hasil_akhir = (
        np.sum(x_kalori * hasil_agregasi) / penyebut
    )

    return (
        hasil_akhir,
        mu_berat,
        mu_aktivitas,
        hasil_agregasi,
        hasil_aturan
    )


# ==========================================
# INPUT PENGGUNA
# ==========================================

st.subheader("📋 Masukkan Data Pengguna")

kolom1, kolom2 = st.columns(2)

with kolom1:
    berat = st.number_input(
        "Berat Badan (kg)",
        min_value=30.0,
        max_value=120.0,
        value=65.0,
        step=1.0
    )

with kolom2:
    aktivitas_pilihan = st.selectbox(
        "Tingkat Aktivitas Fisik",
        [
            "Rendah (1.3)",
            "Sedang (1.6)",
            "Tinggi (1.9)"
        ]
    )

aktivitas = float(
    aktivitas_pilihan.split("(")[1].replace(")", "")
)

if st.button("Hitung Kebutuhan Kalori", type="primary"):

    hasil, mu_berat, mu_aktivitas, agregasi, hasil_aturan = (
        proses_mamdani(berat, aktivitas)
    )

    if hasil is None:
        st.error(
            "Data tidak menghasilkan aturan fuzzy aktif. "
            "Periksa kembali rentang fungsi keanggotaan."
        )

    else:
        st.divider()

        # ======================================
        # HASIL PERHITUNGAN
        # ======================================

        st.subheader("📊 Hasil Perhitungan")

        st.metric(
            "Estimasi Kebutuhan Kalori",
            f"{hasil:.2f} kkal/hari"
        )

        st.info(
            "Hasil ini merupakan estimasi dari model fuzzy "
            "berdasarkan berat badan dan tingkat aktivitas "
            "yang dimasukkan."
        )

        # ======================================
        # HASIL FUZZIFIKASI
        # ======================================

        st.subheader("1. Hasil Fuzzifikasi")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Derajat Keanggotaan Berat Badan**")
            for nama, nilai in mu_berat.items():
                st.write(f"{nama}: {nilai:.3f}")

        with col2:
            st.write("**Derajat Keanggotaan Aktivitas**")
            for nama, nilai in mu_aktivitas.items():
                st.write(f"{nama}: {nilai:.3f}")

        # ======================================
        # ATURAN IF-THEN
        # ======================================

        st.subheader("2. Aturan IF-THEN")

        st.write(
            "Nilai Alpha merupakan hasil operasi MIN "
            "dari derajat keanggotaan kedua input."
        )

        st.dataframe(
            hasil_aturan,
            use_container_width=True,
            hide_index=True
        )

        # ======================================
        # GRAFIK KEANGGOTAAN BERAT
        # ======================================

        st.subheader("3. Grafik Fungsi Keanggotaan Berat Badan")

        fig1, ax1 = plt.subplots(figsize=(9, 4))

        ax1.plot(x_berat, berat_ringan, label="Ringan")
        ax1.plot(x_berat, berat_normal, label="Normal")
        ax1.plot(x_berat, berat_berat, label="Berat")

        ax1.set_xlabel("Berat Badan (kg)")
        ax1.set_ylabel("Derajat Keanggotaan")
        ax1.set_ylim(0, 1.1)
        ax1.set_title("Fungsi Keanggotaan Berat Badan")
        ax1.legend()
        ax1.grid(True)

        st.pyplot(fig1)
        plt.close(fig1)

        # ======================================
        # GRAFIK KEANGGOTAAN AKTIVITAS
        # ======================================

        st.subheader("4. Grafik Fungsi Keanggotaan Aktivitas")

        fig2, ax2 = plt.subplots(figsize=(9, 4))

        ax2.plot(
            x_aktivitas, aktivitas_rendah,
            label="Rendah"
        )
        ax2.plot(
            x_aktivitas, aktivitas_sedang,
            label="Sedang"
        )
        ax2.plot(
            x_aktivitas, aktivitas_tinggi,
            label="Tinggi"
        )

        ax2.set_xlabel("Faktor Aktivitas")
        ax2.set_ylabel("Derajat Keanggotaan")
        ax2.set_ylim(0, 1.1)
        ax2.set_title("Fungsi Keanggotaan Aktivitas Fisik")
        ax2.legend()
        ax2.grid(True)

        st.pyplot(fig2)
        plt.close(fig2)

        # ======================================
        # GRAFIK OUTPUT KALORI
        # ======================================

        st.subheader("5. Grafik Fungsi Keanggotaan Kalori")

        fig3, ax3 = plt.subplots(figsize=(9, 4))

        ax3.plot(
            x_kalori, kalori_rendah,
            label="Kalori Rendah"
        )
        ax3.plot(
            x_kalori, kalori_sedang,
            label="Kalori Sedang"
        )
        ax3.plot(
            x_kalori, kalori_tinggi,
            label="Kalori Tinggi"
        )

        ax3.set_xlabel("Kebutuhan Kalori (kkal)")
        ax3.set_ylabel("Derajat Keanggotaan")
        ax3.set_ylim(0, 1.1)
        ax3.set_title("Fungsi Keanggotaan Output Kalori")
        ax3.legend()
        ax3.grid(True)

        st.pyplot(fig3)
        plt.close(fig3)

        # ======================================
        # GRAFIK HASIL INFERENSI
        # ======================================

        st.subheader("6. Grafik Inferensi dan Defuzzifikasi")

        fig4, ax4 = plt.subplots(figsize=(9, 4))

        ax4.plot(
            x_kalori, kalori_rendah,
            "--", label="Kalori Rendah"
        )
        ax4.plot(
            x_kalori, kalori_sedang,
            "--", label="Kalori Sedang"
        )
        ax4.plot(
            x_kalori, kalori_tinggi,
            "--", label="Kalori Tinggi"
        )

        ax4.fill_between(
            x_kalori,
            agregasi,
            alpha=0.3,
            label="Hasil Agregasi Mamdani"
        )

        ax4.axvline(
            hasil,
            linestyle=":",
            label=f"Centroid = {hasil:.2f} kkal"
        )

        ax4.set_xlabel("Kebutuhan Kalori (kkal)")
        ax4.set_ylabel("Derajat Keanggotaan")
        ax4.set_ylim(0, 1.1)
        ax4.set_title("Hasil Inferensi dan Defuzzifikasi")
        ax4.legend()
        ax4.grid(True)

        st.pyplot(fig4)
        plt.close(fig4)

        st.success(
            "Perhitungan Fuzzy Mamdani berhasil dilakukan!"
        )

# ==========================================
# INFORMASI METODE
# ==========================================

st.divider()

with st.expander("ℹ️ Tentang Metode Fuzzy Mamdani"):
    st.write("""
    Sistem ini menggunakan empat tahapan:

    1. **Fuzzifikasi:** Mengubah input angka menjadi derajat keanggotaan fuzzy.
    2. **Inferensi:** Memproses aturan IF-THEN menggunakan operator MIN.
    3. **Agregasi:** Menggabungkan seluruh hasil aturan menggunakan operator MAX.
    4. **Defuzzifikasi:** Mengubah hasil fuzzy menjadi angka menggunakan metode Centroid.
    """)
