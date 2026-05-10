"""
=====================================================
ANALISIS SPASIAL PROYEK ILASPP - PYTHON 3.11
=====================================================
- GWR (Geographically Weighted Regression) dengan mgwr
- Visualisasi Hasil
=====================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("ANALISIS SPASIAL PROYEK ILASPP")
print(f"Pandas version: {pd.__version__}")
print(f"Numpy version: {np.__version__}")
print("=" * 60)

# =====================================================
# 1. LOAD DATA
# =====================================================

print("\n1. MEMBACA DATA...")

df_gwr = pd.read_csv("koefisien_gwr_ilaspp.csv")
print(f"   - Data GWR: {df_gwr.shape[0]} baris")

df_coord = pd.read_csv("koordinat_wilayah.csv")
print(f"   - Data koordinat: {df_coord.shape[0]} baris")

# Gabungkan
df = pd.merge(df_gwr, df_coord, on="Kabupaten")
print(f"   - Data gabungan: {df.shape[0]} baris")

# =====================================================
# 2. PREPARE DATA
# =====================================================

print("\n2. PREPARE DATA...")

# Koordinat
coords = df[['Longitude', 'Latitude']].values

# Variabel independen (X)
X = df[['Koefisien_Lebar_Jalan', 'Koefisien_Jarak']].values

# Variabel dependen (y) - buat target simulasi
np.random.seed(42)
df['target_harga'] = (df['Koefisien_Lebar_Jalan'] * 0.5) + \
                     (df['Koefisien_Jarak'] * (-0.3)) + \
                     np.random.normal(0, 0.02, len(df))

y = df['target_harga'].values

print(f"   - Jumlah sampel: {len(y)}")
print(f"   - Variabel X: Koefisien_Lebar_Jalan, Koefisien_Jarak")
print(f"   - Range target: {y.min():.4f} - {y.max():.4f}")

# =====================================================
# 3. GWR DENGAN mgwr (DIREVISI)
# =====================================================

print("\n3. MENJALANKAN GWR...")

from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW

# Untuk data kecil (20 sampel), gunakan fixed bandwidth yang kecil
# Hindari adaptive bandwidth karena butuh lebih banyak data

try:
    # Gunakan fixed bandwidth (jarak dalam meter/derajat)
    # Untuk data di Pulau Jawa, coba bandwidth = 2 derajat
    bw_fixed = 2.0
    print(f"   - Menggunakan fixed bandwidth: {bw_fixed}")
    
    # Fit GWR dengan fixed bandwidth
    gwr_model = GWR(coords, y, X, bw_fixed, fixed=True, constant=True)
    gwr_results = gwr_model.fit()
    
    print(f"\n   ✅ HASIL GWR:")
    print(f"      - AICc: {gwr_results.aicc:.2f}")
    print(f"      - R2: {gwr_results.R2:.4f}")
    print(f"      - Adj. R2: {gwr_results.R2_adj:.4f}")

except Exception as e:
    print(f"   ⚠️ GWR error: {e}")
    print(f"   Gagal menjalankan GWR, lanjut ke visualisasi data asli...")
    gwr_results = None

# =====================================================
# 4. VISUALISASI
# =====================================================

print("\n4. MEMBUAT VISUALISASI...")

# Figure 1: Scatter plot koefisien
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot koefisien lebar jalan vs jarak
axes[0].scatter(df['Koefisien_Lebar_Jalan'], df['Koefisien_Jarak'], 
                s=100, c='steelblue', alpha=0.7, edgecolors='white')
axes[0].set_xlabel('Koefisien Lebar Jalan')
axes[0].set_ylabel('Koefisien Jarak')
axes[0].set_title('Hubungan Koefisien Lebar Jalan dan Jarak')

# Bar chart koefisien lebar jalan
df_sorted = df.sort_values('Koefisien_Lebar_Jalan', ascending=True)
top_n = min(10, len(df_sorted))
axes[1].barh(df_sorted['Kabupaten'].head(top_n), 
             df_sorted['Koefisien_Lebar_Jalan'].head(top_n), 
             color='coral')
axes[1].set_xlabel('Koefisien Lebar Jalan')
axes[1].set_title(f'Top {top_n} Koefisien Lebar Jalan')

plt.tight_layout()
plt.savefig('gwr_analysis_py311.png', dpi=150, bbox_inches='tight')
print("   ✅ Gambar 1: gwr_analysis_py311.png")

# Figure 2: Bubble map koefisien
fig, ax = plt.subplots(figsize=(12, 8))

scatter = ax.scatter(df['Longitude'], df['Latitude'], 
                    s=df['Koefisien_Lebar_Jalan'] * 200, 
                    c=df['Koefisien_Lebar_Jalan'], 
                    cmap='viridis', alpha=0.7, edgecolors='black')

# Tambahkan label kota (hanya beberapa untuk menghindari tumpuk)
for idx, row in df.iterrows():
    ax.annotate(row['Kabupaten'], (row['Longitude'], row['Latitude']), 
                fontsize=8, ha='center', va='bottom', xytext=(0, 5),
                textcoords='offset points')

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Bubble Map: Koefisien Lebar Jalan per Wilayah')
plt.colorbar(scatter, label='Koefisien Lebar Jalan')
plt.savefig('bubble_map_py311.png', dpi=150, bbox_inches='tight')
print("   ✅ Gambar 2: bubble_map_py311.png")

# Figure 3: Peta sederhana dengan warna
fig, ax = plt.subplots(figsize=(10, 8))

# Buat scatter plot dengan warna berdasarkan koefisien
scatter = ax.scatter(df['Longitude'], df['Latitude'], 
                    c=df['Koefisien_Lebar_Jalan'], 
                    cmap='RdYlBu_r', s=120, edgecolors='black', linewidth=1.5)

# Tambahkan label
for idx, row in df.iterrows():
    ax.annotate(row['Kabupaten'], (row['Longitude'], row['Latitude']), 
                fontsize=7, ha='center', va='bottom')

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Peta Koefisien Lebar Jalan')
plt.colorbar(scatter, label='Koefisien Lebar Jalan')
plt.savefig('coefficient_map_py311.png', dpi=150, bbox_inches='tight')
print("   ✅ Gambar 3: coefficient_map_py311.png")

# =====================================================
# 5. OUTPUT RINGKASAN
# =====================================================

print("\n" + "=" * 60)
print("5. RINGKASAN HASIL ANALISIS")
print("=" * 60)

print("\n📊 STATISTIK DATA:")
print(f"   - Jumlah sampel: {len(df)}")
print(f"   - Kabupaten/Kota yang dianalisis: {len(df['Kabupaten'].unique())}")

print("\n📈 KOEFISIEN GWR (Hasil dari R):")
print(f"   - Koefisien Lebar Jalan (min): {df['Koefisien_Lebar_Jalan'].min():.4f}")
print(f"   - Koefisien Lebar Jalan (mean): {df['Koefisien_Lebar_Jalan'].mean():.4f}")
print(f"   - Koefisien Lebar Jalan (max): {df['Koefisien_Lebar_Jalan'].max():.4f}")
print(f"   - Koefisien Jarak (min): {df['Koefisien_Jarak'].min():.4f}")
print(f"   - Koefisien Jarak (mean): {df['Koefisien_Jarak'].mean():.4f}")
print(f"   - Koefisien Jarak (max): {df['Koefisien_Jarak'].max():.4f}")

print("\n🏆 TOP 3 WILAYAH - KOEFISIEN LEBAR JALAN TERTINGGI:")
top3 = df.nlargest(3, 'Koefisien_Lebar_Jalan')[['Kabupaten', 'Koefisien_Lebar_Jalan']]
for i, (_, row) in enumerate(top3.iterrows(), 1):
    print(f"   {i}. {row['Kabupaten']}: {row['Koefisien_Lebar_Jalan']:.4f}")

print("\n📉 TOP 3 WILAYAH - KOEFISIEN JARAK TERENDAH (PALING NEGATIF):")
bottom3 = df.nsmallest(3, 'Koefisien_Jarak')[['Kabupaten', 'Koefisien_Jarak']]
for i, (_, row) in enumerate(bottom3.iterrows(), 1):
    print(f"   {i}. {row['Kabupaten']}: {row['Koefisien_Jarak']:.4f}")

# Simpan hasil
df.to_csv('hasil_analisis_spasial_py311.csv', index=False)
print("\n💾 Hasil disimpan ke: hasil_analisis_spasial_py311.csv")

print("\n" + "=" * 60)
print("✅ ANALISIS SELESAI!")
print("=" * 60)

# Tampilkan plot
plt.show()