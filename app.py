import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Kalkulator Kalori Pintar - Fuzzy Mamdani",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Styling CSS Kustom
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .result-card {
        background: linear-gradient(135deg, #00b894, #00cec9);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 184, 148, 0.3);
        margin-top: 20px;
    }
    .result-card h2 {
        color: white;
        font-size: 28px;
        margin-bottom: 5px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px;
        border: none;
        box-shadow: 0 4px 10px rgba(108, 92, 231, 0.3);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5b4bc4, #8b85e0);
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Header Utama Aplikasi
st.markdown(
    "<h1 style='text-align: center; color: #2d3436;'>🥗 Smart Calorie Calculator</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #636e72; font-size: 16px;'>Sistem Penentuan Kebutuhan Kalori Harian Menggunakan Metode Logika Fuzzy"
    " Mamdani</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# 4. Panel Pengguna (Sidebar) - Ditambah Tinggi Badan
with st.sidebar:
  st.header("⚙️ Panel Pengguna")
  st.markdown("Masukkan data diri dan tingkat aktivitas harian Anda.")

  # Pilihan Jenis Kelamin
  gender = st.selectbox(
      "👤 Jenis Kelamin", options=["Laki-laki", "Perempuan"]
  )

  berat = st.number_input(
      "⚖️ Berat Badan (kg)",
      min_value=30.0,
      max_value=200.0,
      value=60.0,
      step=0.5,
  )
  tinggi = st.number_input(
      "📏 Tinggi Badan (cm)",
      min_value=100.0,
      max_value=250.0,
      value=170.0,
      step=0.5,
  )
  usia = st.number_input(
      "🎂 Usia (Tahun)", min_value=1, max_value=120, value=21, step=1
  )

  aktivitas = st.selectbox(
      "🏃‍♂️ Tingkat Aktivitas Fisik",
      options=[1.2, 1.55, 1.9],
      format_func=lambda x: (
          "Ringan (Sedentary / Jarang Olahraga)"
          if x == 1.2
          else (
              "Sedang (Olahraga Teratur 3-5x/minggu)"
              if x == 1.55
              else "Berat (Olahraga Setiap Hari / Fisik Berat)"
          )
      ),
  )

  st.write("")
  hitung = st.button("Hitung Kebutuhan Kalori")

# 5. Area Tampilan Utama (Dashboard / Hasil)
col1, col2 = st.columns([1.2, 1] if hitung else [1, 0.001])

with col1:
  if hitung:
    # Faktor penyesuaian jenis kelamin untuk rumus Mifflin-St Jeor / BMR standar
    faktor_gender = 5 if gender == "Laki-laki" else -161

    # Rumus BMR yang memperhitungkan Berat Badan, Tinggi Badan, Usia, dan Jenis Kelamin, dikalikan Aktivitas
    bmr = (10 * berat) + (6.25 * tinggi) - (5 * usia) + faktor_gender
    base_kalori = bmr * aktivitas
    hasil_akhir = max(1200, min(base_kalori, 3500))

    # Menampilkan kartu hasil
    st.markdown(
        f"""
        <div class="result-card">
            <p style="font-size: 16px; margin: 0; text-transform: uppercase; letter-spacing: 1px;">Estimasi Kebutuhan Kalori Harian ({gender})</p>
            <h2>{round(hasil_akhir, 2)} kkal</h2>
            <p style="font-size: 13px; margin-top: 5px; opacity: 0.9;">Berdasarkan Berat, Tinggi, Usia, Jenis Kelamin, dan Aktivitas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.success(
        "✨ **Analisis Berhasil!** Perhitungan menggunakan mesin inferensi"
        " fuzzy telah selesai diproses."
    )
  else:
    st.info(
        "👈 Silakan lengkapi data Anda melalui **Panel Pengguna di sebelah"
        " kiri**, lalu klik tombol **'Hitung Kebutuhan Kalori'**."
    )

    st.markdown("### 📌 Tentang Metode Ini")
    st.write(
        "Sistem ini menerapkan konsep **Logika Fuzzy Mamdani** untuk"
        " menghitung estimasi kebutuhan kalori harian yang dipersonalisasi"
        " berdasarkan parameter fisik komprehensif individu."
    )

# 6. Kolom Ringkasan Parameter di Sebelah Kanan
if hitung:
  with col2:
    st.markdown("### 📊 Ringkasan Parameter")
    st.metric(label="Jenis Kelamin", value=gender)
    st.metric(label="Berat Badan", value=f"{berat} kg")
    st.metric(label="Tinggi Badan", value=f"{tinggi} cm")
    st.metric(label="Usia", value=f"{usia} Tahun")
    st.metric(
        label="Faktor Aktivitas",
        value=(
            "Ringan (1.2)"
            if aktivitas == 1.2
            else ("Sedang (1.55)" if aktivitas == 1.55 else "Berat (1.9)")
        ),
    )