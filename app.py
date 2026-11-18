import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Kalkulator Kalori Pintar - Fuzzy Mamdani",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Styling CSS Kustom untuk Tampilan Modern
st.markdown("""
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
""", unsafe_allow_html=True)

# 3. Fungsi Sistem Logika Fuzzy Mamdani
def buat_sistem_fuzzy():
    umur = ctrl.Antecedent(np.arange(0, 81, 1), 'umur')
    imt = ctrl.Antecedent(np.arange(10, 35, 0.5), 'imt')
    aktivitas = ctrl.Antecedent(np.arange(0, 11, 0.5), 'aktivitas')
    kalori = ctrl.Consequent(np.arange(1000, 3501, 50), 'kalori')

    # Fungsi Keanggotaan Umur
    umur['muda'] = fuzz.trapmf(umur.universe, [0, 0, 25, 40])
    umur['parubaya'] = fuzz.trimf(umur.universe, [35, 40, 60])
    umur['tua'] = fuzz.trimf(umur.universe, [55, 60, 70])
    umur['sangat_tua'] = fuzz.trapmf(umur.universe, [65, 70, 80, 80])

    # Fungsi Keanggotaan IMT
    imt['sangat_kurus'] = fuzz.trapmf(imt.universe, [10, 10, 16.5, 17])
    imt['kurus'] = fuzz.trapmf(imt.universe, [16.5, 17, 18, 18.5])
    imt['normal'] = fuzz.trapmf(imt.universe, [18, 18.5, 24.5, 25])
    imt['gemuk'] = fuzz.trapmf(imt.universe, [24.5, 25, 26.5, 27])
    imt['sangat_gemuk'] = fuzz.trapmf(imt.universe, [26.5, 27, 35, 35])

    # Fungsi Keanggotaan Aktivitas Fisik
    aktivitas['istirahat'] = fuzz.trapmf(aktivitas.universe, [0, 0, 2, 4])
    aktivitas['ringan'] = fuzz.trimf(aktivitas.universe, [3, 4, 5])
    aktivitas['sedang'] = fuzz.trimf(aktivitas.universe, [4, 6, 8])
    aktivitas['berat'] = fuzz.trimf(aktivitas.universe, [7, 8, 9])
    aktivitas['sangat_berat'] = fuzz.trapmf(aktivitas.universe, [8, 10, 10, 10])

    # Fungsi Keanggotaan Output Kalori
    kalori['rendah'] = fuzz.trapmf(kalori.universe, [1000, 1000, 1400, 1700])
    kalori['sedang'] = fuzz.trimf(kalori.universe, [1500, 2000, 2500])
    kalori['tinggi'] = fuzz.trapmf(kalori.universe, [2200, 2600, 3500, 3500])

    # Basis Aturan (Rule Base)
    rule1 = ctrl.Rule(imt['sangat_kurus'] | imt['kurus'], kalori['tinggi'])
    rule2 = ctrl.Rule(imt['normal'] & (aktivitas['istirahat'] | aktivitas['ringan']), kalori['sedang'])
    rule3 = ctrl.Rule(imt['normal'] & (aktivitas['sedang'] | aktivitas['berat'] | aktivitas['sangat_berat']), kalori['tinggi'])
    rule4 = ctrl.Rule((imt['gemuk'] | imt['sangat_gemuk']) & (umur['tua'] | umur['sangat_tua']), kalori['rendah'])
    rule5 = ctrl.Rule((imt['gemuk'] | imt['sangat_gemuk']) & (aktivitas['istirahat'] | aktivitas['ringan']), kalori['rendah'])
    rule6 = ctrl.Rule((imt['gemuk'] | imt['sangat_gemuk']) & (aktivitas['sedang'] | aktivitas['berat'] | aktivitas['sangat_berat']), kalori['sedang'])
    rule7 = ctrl.Rule((umur['tua'] | umur['sangat_tua']) & imt['normal'], kalori['rendah'])

    sistem_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
    simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)
    
    return simulasi, umur, imt, aktivitas, kalori

def hitung_kalori(input_umur, berat_badan, tinggi_badan_cm, input_aktivitas, jenis_kelamin):
    simulasi, _, _, _, _ = buat_sistem_fuzzy()
    
    tinggi_m = tinggi_badan_cm / 100.0
    nilai_imt = berat_badan / (tinggi_m ** 2)
    
    simulasi.input['umur'] = input_umur
    simulasi.input['imt'] = np.clip(nilai_imt, 10, 34.5)
    simulasi.input['aktivitas'] = input_aktivitas
    
    simulasi.compute()
    hasil_kalori = simulasi.output['kalori']
    
    if jenis_kelamin == "Laki-laki":
        hasil_kalori *= 1.05
    else:
        hasil_kalori *= 0.95
        
    return round(hasil_kalori, 2), round(nilai_imt, 2)

def gambar_grafik_himpunan(input_umur=None, nilai_imt=None, input_aktivitas=None):
    _, umur, imt, aktivitas, _ = buat_sistem_fuzzy()
    fig, axes = plt.subplots(3, 1, figsize=(8, 10))
    
    # 1. Grafik Umur
    for label in umur.terms:
        axes[0].plot(umur.universe, umur[label].mf, label=label.replace('_', ' ').title())
    if input_umur is not None:
        axes[0].axvline(x=input_umur, color='red', linestyle='--', linewidth=2, label=f'Input: {input_umur} Thn')
    axes[0].set_title('Himpunan Fuzzy Variabel Umur')
    axes[0].set_xlabel('Umur (Tahun)')
    axes[0].set_ylabel('Keanggotaan')
    axes[0].legend(loc='upper right', fontsize=8)
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # 2. Grafik IMT
    for label in imt.terms:
        axes[1].plot(imt.universe, imt[label].mf, label=label.replace('_', ' ').title())
    if nilai_imt is not None:
        axes[1].axvline(x=nilai_imt, color='red', linestyle='--', linewidth=2, label=f'Input IMT: {nilai_imt}')
    axes[1].set_title('Himpunan Fuzzy Variabel Indeks Massa Tubuh (IMT)')
    axes[1].set_xlabel('IMT (kg/m²)')
    axes[1].set_ylabel('Keanggotaan')
    axes[1].legend(loc='upper right', fontsize=8)
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # 3. Grafik Aktivitas Fisik
    for label in aktivitas.terms:
        axes[2].plot(aktivitas.universe, aktivitas[label].mf, label=label.replace('_', ' ').title())
    if input_aktivitas is not None:
        axes[2].axvline(x=input_aktivitas, color='red', linestyle='--', linewidth=2, label=f'Input: {input_aktivitas}')
    axes[2].set_title('Himpunan Fuzzy Variabel Aktivitas Fisik')
    axes[2].set_xlabel('Skor Aktivitas (0 - 10)')
    axes[2].set_ylabel('Keanggotaan')
    axes[2].legend(loc='upper right', fontsize=8)
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    return fig

# 4. Header Tampilan Web
st.markdown("<h1 style='text-align: center; color: #2d3436;'>🥗 Smart Calorie Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #636e72; font-size: 16px;'>Sistem Penentuan Kebutuhan Kalori Harian Menggunakan Metode Logika Fuzzy Mamdani</p>", unsafe_allow_html=True)
st.markdown("---")

# 5. Sidebar Input Pengguna
with st.sidebar:
    st.header("⚙️ Panel Pengguna")
    st.markdown("Masukkan data diri fisik Anda.")

    gender = st.selectbox("👤 Jenis Kelamin", options=["Laki-laki", "Perempuan"])
    berat = st.number_input("⚖️ Berat Badan (kg)", min_value=30.0, max_value=150.0, value=60.0, step=0.5)
    tinggi = st.number_input("📏 Tinggi Badan (cm)", min_value=100.0, max_value=220.0, value=165.0, step=0.5)
    usia = st.number_input("🎂 Usia (Tahun)", min_value=1, max_value=80, value=25, step=1)
    
    # Skor Aktivitas 0 - 10 sesuai semesta pembicaraan fungsi fuzzy
    aktivitas_skor = st.slider("🏃‍♂️ Skor Aktivitas Fisik (0 - 10)", min_value=0.0, max_value=10.0, value=5.0, step=0.5, 
                               help="0-2: Istirahat, 3-4: Ringan, 5-6: Sedang, 7-8: Berat, 9-10: Sangat Berat")

    st.write("")
    hitung = st.button("Hitung Kebutuhan Kalori")

# 6. Konten Utama & Tampilan Hasil
col1, col2 = st.columns([1.2, 1] if hitung else [1, 0.001])

with col1:
    if hitung:
        hasil_kalori, nilai_imt = hitung_kalori(usia, berat, tinggi, aktivitas_skor, gender)

        # Kartu Hasil Kalori
        st.markdown(f"""
            <div class="result-card">
                <p style="font-size: 16px; margin: 0; text-transform: uppercase; letter-spacing: 1px;">Estimasi Kebutuhan Kalori Harian</p>
                <h2>{hasil_kalori} kkal</h2>
                <p style="font-size: 13px; margin-top: 5px; opacity: 0.9;">IMT Terhitung: {nilai_imt} kg/m² ({gender})</p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.success("✨ **Analisis Berhasil!** Inferensi dan Defuzzifikasi Fuzzy Mamdani selesai diproses.")
    else:
        st.info("👈 Silakan lengkapi data parameter di **Panel Pengguna sebelah kiri**, lalu klik tombol **'Hitung Kebutuhan Kalori'**.")
        st.markdown("### 📌 Informasi Sistem")
        st.write("Aplikasi ini menggunakan metode **Logika Fuzzy Mamdani** dengan variabel Umur, Indeks Massa Tubuh (IMT), dan Aktivitas Fisik untuk memberikan rekomendasi kalori harian yang presisi.")

# Kolom Samping untuk Ringkasan Parameter
if hitung:
    with col2:
        st.markdown("### 📊 Ringkasan Parameter")
        st.metric(label="Indeks Massa Tubuh (IMT)", value=f"{nilai_imt} kg/m²")
        st.metric(label="Usia", value=f"{usia} Tahun")
        st.metric(label="Skor Aktivitas", value=f"{aktivitas_skor} / 10")

# 7. Menampilkan Diagram Himpunan Fuzzy di Bagian Bawah
if hitung:
    st.markdown("---")
    st.markdown("### 📈 Diagram Himpunan Fuzzy & Posisi Input Anda")
    st.info("Garis putus-putus berwarna merah pada grafik di bawah ini menunjukkan titik posisi data input Anda pada masing-masing domain himpunan fuzzy.")
    
    # Memanggil fungsi pembuat grafik dan merendernya di Streamlit
    fig = gambar_grafik_himpunan(input_umur=usia, nilai_imt=nilai_imt, input_aktivitas=aktivitas_skor)
    st.pyplot(fig)
