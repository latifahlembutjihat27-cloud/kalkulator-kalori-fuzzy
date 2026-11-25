
import streamlit as st
import numpy as np
import pandas as pd

# =====================================
# 1. KONFIGURASI HALAMAN
# =====================================

st.set_page_config(
    page_title="Kalkulator Kalori Pintar",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 KALKULATOR KALORI PINTAR")
st.caption("Sistem Penentuan Kebutuhan Kalori Harian")
st.write("Metode Logika Fuzzy Mamdani")

# =====================================
# 2. FUNGSI KEANGGOTAAN
# =====================================

def trimf(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif x < b:
        return (x-a)/(b-a)
    else:
        return (c-x)/(c-b)


def trapmf(x, a, b, c, d):
    if x < a or x > d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif x < b:
        return (x-a)/(b-a)
    else:
        return (d-x)/(d-c)


# =====================================
# 3. FUZZIFIKASI BERAT BADAN
# =====================================

def fuzzy_berat(x):
    return {
        "Ringan": trapmf(x, 30, 30, 45, 60),
        "Normal": trimf(x, 50, 70, 90),
        "Berat": trapmf(x, 80, 100, 120, 120)
    }


# =====================================
# 4. FUZZIFIKASI AKTIVITAS
# =====================================

def fuzzy_aktivitas(x):
    return {
        "Rendah": trapmf(x, 1.2, 1.2, 1.35, 1.5),
        "Sedang": trimf(x, 1.4, 1.6, 1.8),
        "Tinggi": trapmf(x, 1.7, 1.85, 2.0, 2.0)
    }


# =====================================
# 5. FUNGSI KEANGGOTAAN OUTPUT
# =====================================

def fuzzy_kalori(x):
    return {
        "Rendah": np.array([
            trapmf(v, 1000, 1000, 1500, 2100)
            for v in x
        ]),
        "Sedang": np.array([
            trimf(v, 1800, 2500, 3200)
            for v in x
        ]),
        "Tinggi": np.array([
            trapmf(v, 2800, 3500, 4000, 4000)
            for v in x
        ])
    }


# =====================================
# 6. BASIS ATURAN IF-THEN
# =====================================

aturan_fuzzy = [
    ("R1", "Ringan", "Rendah", "Rendah"),
    ("R2", "Ringan", "Sedang", "Sedang"),
    ("R3", "Ringan", "Tinggi", "Tinggi"),

    ("R4", "Normal", "Rendah", "Sedang"),
    ("R5", "Normal", "Sedang", "Sedang"),
    ("R6", "Normal", "Tinggi", "Tinggi"),

    ("R7", "Berat", "Rendah", "Rendah"),
    ("R8", "Berat", "Sedang", "Sedang"),
    ("R9", "Berat", "Tinggi", "Tinggi")
]


# =====================================
# 7. PROSES INFERENSI MAMDANI
# =====================================

def proses_mamdani(berat, aktivitas):

    # Fuzzifikasi
    derajat_berat = fuzzy_berat(berat)
    derajat_aktivitas = fuzzy_aktivitas(aktivitas)

    # Rentang output
    x = np.arange(1000, 4001, 1)

    fungsi_output = fuzzy_kalori(x)

    hasil_agregasi = np.zeros(len(x))

    hasil_aturan = []

    # Evaluasi aturan IF-THEN
    for kode, b, a, output in aturan_fuzzy:

        # Operator AND menggunakan MIN
        alpha = min(
            derajat_berat[b],
            derajat_aktivitas[a]
        )

        hasil_aturan.append({
            "Aturan": kode,
            "IF Berat": b,
            "AND Aktivitas": a,
            "THEN Kalori": output,
            "Alpha": alpha
        })

        # Implikasi Mamdani
        hasil_potong = np.minimum(
            alpha,
            fungsi_output[output]
        )

        # Agregasi menggunakan MAX
        hasil_agregasi = np.maximum(
            hasil_agregasi,
            hasil_potong
        )

    # Defuzzifikasi Centroid
    total = np.sum(hasil_agregasi)

    if total == 0:
        return None, derajat_berat, derajat_aktivitas, hasil_aturan

    kalori = np.sum(
        x * hasil_agregasi
    ) / total

    return kalori, derajat_berat, derajat_aktivitas, hasil_aturan


# =====================================
# 8. TAMPILAN INPUT
# =====================================

st.subheader("📝 Input Data Pengguna")

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
    pilihan = {
        "Rendah": 1.3,
        "Sedang": 1.6,
        "Tinggi": 1.9
    }

    aktivitas_pilih = st.selectbox(
        "Tingkat Aktivitas Fisik",
        list(pilihan.keys())
    )

aktivitas = pilihan[aktivitas_pilih]

# =====================================
# 9. TOMBOL HITUNG
# =====================================

if st.button("Hitung Kebutuhan Kalori", type="primary"):

    kalori, db, da, aturan = proses_mamdani(
        berat,
        aktivitas
    )

    if kalori is None:
        st.error("Perhitungan tidak dapat dilakukan.")

    else:
        st.success("Perhitungan berhasil!")

        # Hasil akhir
        st.subheader("📊 Hasil Kebutuhan Kalori")

        st.metric(
            "Estimasi Kalori Harian",
            f"{kalori:,.0f} kkal/hari"
        )

        st.divider()

        # =================================
        # 10. HASIL FUZZIFIKASI
        # =================================

        st.subheader("1. Hasil Fuzzifikasi")

        c1, c2 = st.columns(2)

        with c1:
            st.write("Berat Badan")
            st.json(db)

        with c2:
            st.write("Aktivitas Fisik")
            st.json(da)

        st.divider()

        # =================================
        # 11. TABEL ATURAN IF-THEN
        # =================================

        st.subheader("2. Aturan IF-THEN Mamdani")

        df_aturan = pd.DataFrame(aturan)

        st.dataframe(
            df_aturan,
            use_container_width=True,
            hide_index=True
        )

        # =================================
        # 12. ATURAN YANG AKTIF
        # =================================

        st.subheader("3. Aturan Fuzzy yang Aktif")

        aktif = [
            r for r in aturan
            if r["Alpha"] > 0
        ]

        if aktif:
            st.dataframe(
                pd.DataFrame(aktif),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Tidak ada aturan yang aktif.")

        st.divider()

        # =================================
        # 13. DEFUZZIFIKASI
        # =================================

        st.subheader("4. Defuzzifikasi")

        st.write(
            "Metode yang digunakan: Centroid"
        )

        st.metric(
            "Nilai akhir",
            f"{kalori:,.2f} kkal/hari"
        )

        st.caption(
            "Hasil merupakan estimasi dari parameter "
            "dan aturan fuzzy yang digunakan."
        )

# =====================================
# 14. TAMPILAN BASIS ATURAN
# =====================================

with st.expander("Lihat Seluruh Basis Aturan Fuzzy"):
    st.write("Daftar sembilan aturan IF-THEN:")

    for kode, b, a, output in aturan_fuzzy:
        st.write(
            f"{kode}: IF Berat {b} AND Aktivitas {a} "
            f"THEN Kalori {output}"
        )

st.divider()

st.caption(
    "Kalkulator Kalori Pintar | Metode Fuzzy Mamdani"
)
