import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

def buat_sistem_fuzzy():
    # 1. Definisi Semesta Pembicaraan (Input & Output)
    umur = ctrl.Antecedent(np.arange(0, 81, 1), 'umur')
    imt = ctrl.Antecedent(np.arange(10, 35, 0.5), 'imt')
    aktivitas = ctrl.Antecedent(np.arange(0, 11, 0.5), 'aktivitas')
    kalori = ctrl.Consequent(np.arange(1000, 3501, 50), 'kalori')

    # 2. Fungsi Keanggotaan Variabel Umur (Sesuai rujukan jurnal)[cite: 1]
    umur['muda'] = fuzz.trapmf(umur.universe, [0, 0, 25, 40])
    umur['parubaya'] = fuzz.trimf(umur.universe, [35, 40, 60])
    umur['tua'] = fuzz.trimf(umur.universe, [55, 60, 70])
    umur['sangat_tua'] = fuzz.trapmf(umur.universe, [65, 70, 80, 80])

    # 3. Fungsi Keanggotaan Variabel Berat Badan / IMT (Sesuai rujukan jurnal)[cite: 1]
    imt['sangat_kurus'] = fuzz.trapmf(imt.universe, [10, 10, 16.5, 17])
    imt['kurus'] = fuzz.trapmf(imt.universe, [16.5, 17, 18, 18.5])
    imt['normal'] = fuzz.trapmf(imt.universe, [18, 18.5, 24.5, 25])
    imt['gemuk'] = fuzz.trapmf(imt.universe, [24.5, 25, 26.5, 27])
    imt['sangat_gemuk'] = fuzz.trapmf(imt.universe, [26.5, 27, 35, 35])

    # 4. Fungsi Keanggotaan Variabel Aktivitas Fisik (Sesuai rujukan jurnal)[cite: 1]
    aktivitas['istirahat'] = fuzz.trapmf(aktivitas.universe, [0, 0, 2, 4])
    aktivitas['ringan'] = fuzz.trimf(aktivitas.universe, [3, 4, 5])
    aktivitas['sedang'] = fuzz.trimf(aktivitas.universe, [4, 6, 8])
    aktivitas['berat'] = fuzz.trimf(aktivitas.universe, [7, 8, 9])
    aktivitas['sangat_berat'] = fuzz.trapmf(aktivitas.universe, [8, 10, 10, 10])

    # 5. Fungsi Keanggotaan Output Kalori (kkal)
    kalori['rendah'] = fuzz.trapmf(kalori.universe, [1000, 1000, 1400, 1700])
    kalori['sedang'] = fuzz.trimf(kalori.universe, [1500, 2000, 2500])
    kalori['tinggi'] = fuzz.trapmf(kalori.universe, [2200, 2600, 3500, 3500])

    # 6. Basis Aturan (Rule Base) Mamdani
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
    
    # Menghitung IMT dari Berat Badan (kg) dan Tinggi Badan (meter)[cite: 1]
    tinggi_m = tinggi_badan_cm / 100.0
    nilai_imt = berat_badan / (tinggi_m ** 2)
    
    # Memasukkan nilai ke sistem fuzzy
    simulasi.input['umur'] = input_umur
    simulasi.input['imt'] = np.clip(nilai_imt, 10, 34.5)
    simulasi.input['aktivitas'] = input_aktivitas
    
    # Proses Inferensi & Defuzzifikasi Mamdani
    simulasi.compute()
    hasil_kalori = simulasi.output['kalori']
    
    # Penyesuaian faktor jenis kelamin
    if jenis_kelamin == "Laki-laki":
        hasil_kalori *= 1.05
    else:
        hasil_kalori *= 0.95
        
    return round(hasil_kalori, 2), round(nilai_imt, 2)

def gambar_grafik_himpunan(input_umur=None, nilai_imt=None, input_aktivitas=None):
    _, umur, imt, aktivitas, _ = buat_sistem_fuzzy()
    fig, axes = plt.subplots(3, 1, figsize=(7, 9))
    
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

    # 2. Grafik IMT (Berat Badan)
    for label in imt.terms:
        axes[1].plot(imt.universe, imt[label].mf, label=label.replace('_', ' ').title())
    if nilai_imt is not None:
        axes[1].axvline(x=nilai_imt, color='red', linestyle='--', linewidth=2, label=f'Input IMT: {nilai_imt}')
    axes[1].set_title('Himpunan Fuzzy Variabel Berat Badan (IMT)')
    axes[1].set_xlabel('Indeks Massa Tubuh (IMT)')
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
