"""
=====================================================
KRIGING + PETA ADMINISTRASI JAWA TIMUR
Dengan Download Shapefile Otomatis
=====================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykrige.ok import OrdinaryKriging
import geopandas as gpd
import warnings
import os
import requests
import zipfile
from io import BytesIO

warnings.filterwarnings('ignore')

# =====================================================
# 1. DOWNLOAD SHAPEFILE BATAS WILAYAH
# =====================================================

print("=" * 60)
print("1. DOWNLOAD SHAPEFILE BATAS PROVINSI/KABUPATEN")
print("=" * 60)

# Gunakan dataset dari GitHub (GeoJSON Indonesia)
# Sumber: https://github.com/chmdznr/indonesia-geojson
# Atau alternatif dari idn-area-boundary

# Opsi A: Download batas provinsi (ukuran lebih kecil)
print("\nMengunduh data batas provinsi Indonesia...")
province_url = "https://raw.githubusercontent.com/fityannugroho/idn-area-boundary/main/data/provinces.geojson"

try:
    gdf_provinsi = gpd.read_file(province_url)
    print(f"✅ Data provinsi berhasil diunduh: {len(gdf_provinsi)} provinsi")
    
    # Filter untuk Jawa Timur
    jatim = gdf_provinsi[gdf_provinsi['name'] == 'Jawa Timur']
    print(f"✅ Batas Provinsi Jawa Timur ditemukan")
    
except Exception as e:
    print(f"⚠️ Gagal download dari primary source: {e}")
    print("Mencoba source alternatif...")
    
    # Opsi B: Gunakan data dari repositori lain
    backup_url = "https://raw.githubusercontent.com/alfiannisaa/indonesia-geojson/main/geojson/provinces.json"
    try:
        gdf_provinsi = gpd.read_file(backup_url)
        jatim = gdf_provinsi[gdf_provinsi['name'] == 'Jawa Timur']
    except:
        print("Membuat bounding box sebagai fallback...")
        # Fallback: bounding box area Jawa Timur
        from shapely.geometry import box
        jatim = gpd.GeoDataFrame(
            {'geometry': [box(110, -9, 115, -6)], 'name': ['Jawa Timur (Bounding Box)']},
            crs='EPSG:4326'
        )

# =====================================================
# 2. LOAD DATA SAMPEL
# =====================================================

print("\n" + "=" * 60)
print("2. MEMBACA DATA SAMPEL")
print("=" * 60)

# Baca data koefisien GWR
df = pd.read_csv("koefisien_gwr_ilaspp.csv")
df_coord = pd.read_csv("koordinat_wilayah.csv")
df = pd.merge(df, df_coord, on="Kabupaten")

# Buat target untuk Kriging
np.random.seed(42)
df['target_harga'] = (df['Koefisien_Lebar_Jalan'] * 50) + \
                     (df['Koefisien_Jarak'] * 30) + \
                     np.random.normal(0, 5, len(df))

print(f"✅ Data siap: {len(df)} titik sampel")

# =====================================================
# 3. KRIGING INTERPOLATION
# =====================================================

print("\n" + "=" * 60)
print("3. MENJALANKAN KRIGING")
print("=" * 60)

x = df['Longitude'].values
y = df['Latitude'].values
z = df['target_harga'].values

# Grid untuk interpolasi
grid_lon = np.linspace(x.min() - 0.5, x.max() + 0.5, 150)
grid_lat = np.linspace(y.min() - 0.5, y.max() + 0.5, 150)

print(f"Grid size: {len(grid_lon)} x {len(grid_lat)} = {len(grid_lon) * len(grid_lat)} titik")

# Ordinary Kriging
OK = OrdinaryKriging(x, y, z, variogram_model='linear', verbose=False)
z_grid, ss_grid = OK.execute('grid', grid_lon, grid_lat)

print("✅ Kriging selesai")

# =====================================================
# 4. PLOT DENGAN BATAS WILAYAH
# =====================================================

print("\n" + "=" * 60)
print("4. MEMBUAT VISUALISASI")
print("=" * 60)

fig, ax = plt.subplots(figsize=(14, 10))

# Plot hasil Kriging
im = ax.imshow(z_grid, 
               extent=[grid_lon.min(), grid_lon.max(), 
                       grid_lat.min(), grid_lat.max()],
               origin='lower', 
               cmap='RdYlBu_r', 
               alpha=0.75)

# Overlay batas provinsi/kabupaten (jika ada)
try:
    # Plot batas wilayah (polygon outline)
    jatim.boundary.plot(ax=ax, edgecolor='black', linewidth=1.5, alpha=0.8)
    print("✅ Batas wilayah berhasil ditambahkan")
except:
    print("⚠️ Tidak dapat menampilkan batas wilayah")

# Plot titik sampel
ax.scatter(x, y, c='black', s=60, edgecolors='white', 
           linewidth=1.5, label='Titik Sampel', zorder=5)

# Tambahkan label kota
for idx, row in df.iterrows():
    ax.annotate(row['Kabupaten'], (row['Longitude'], row['Latitude']),
                fontsize=7, ha='center', va='bottom', 
                xytext=(0, 5), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# Setting plot
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.set_title('Kriging Interpolation - Prediksi Harga Tanah\n(Overlay dengan Batas Provinsi Jawa Timur)', 
            fontsize=14, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Prediksi Harga (Juta/m²)', fontsize=10)

# Legend
ax.legend(loc='upper right')

# Grid
ax.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('kriging_with_administrative_boundary.png', dpi=150, bbox_inches='tight')
print("\n✅ Peta tersimpan: kriging_with_administrative_boundary.png")

plt.show()

# =====================================================
# 5. RINGKASAN HASIL
# =====================================================

print("\n" + "=" * 60)
print("5. RINGKASAN HASIL")
print("=" * 60)

print(f"\n📊 Statistik Prediksi Kriging:")
print(f"   - Minimum: {np.nanmin(z_grid):.2f} Juta/m²")
print(f"   - Maksimum: {np.nanmax(z_grid):.2f} Juta/m²")
print(f"   - Rata-rata: {np.nanmean(z_grid):.2f} Juta/m²")

print(f"\n📈 Titik Sampel (n={len(df)}):")
print(f"   - Kisaran harga: {df['target_harga'].min():.2f} - {df['target_harga'].max():.2f} Juta/m²")

print("\n" + "=" * 60)
print("✅ ANALISIS SELESAI!")
print("=" * 60)