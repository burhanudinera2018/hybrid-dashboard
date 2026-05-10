"""
EXPORT HASIL KRIGING KE CSV UNTUK DASHBOARD
"""

import pandas as pd
import numpy as np
from pykrige.ok import OrdinaryKriging
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv("koefisien_gwr_ilaspp.csv")
df_coord = pd.read_csv("koordinat_wilayah.csv")
df = pd.merge(df, df_coord, on="Kabupaten")

# Target untuk Kriging
np.random.seed(42)
df['target_harga'] = (df['Koefisien_Lebar_Jalan'] * 50) + \
                     (df['Koefisien_Jarak'] * 30) + \
                     np.random.normal(0, 5, len(df))

# Koordinat
x = df['Longitude'].values
y = df['Latitude'].values
z = df['target_harga'].values

# Grid
grid_lon = np.linspace(x.min() - 0.5, x.max() + 0.5, 50)
grid_lat = np.linspace(y.min() - 0.5, y.max() + 0.5, 50)

# Kriging
OK = OrdinaryKriging(x, y, z, variogram_model='linear', verbose=False)
z_grid, ss_grid = OK.execute('grid', grid_lon, grid_lat)

# Konversi ke DataFrame
lon_mesh, lat_mesh = np.meshgrid(grid_lon, grid_lat)
kriging_df = pd.DataFrame({
    'longitude': lon_mesh.flatten(),
    'latitude': lat_mesh.flatten(),
    'prediksi': z_grid.flatten(),
    'variance': ss_grid.flatten()
})

# Filter nilai valid (bukan NaN)
kriging_df = kriging_df.dropna()

# Simpan ke CSV
kriging_df.to_csv('kriging_results.csv', index=False)
print(f"✅ Hasil Kriging tersimpan: {len(kriging_df)} titik grid")
print("   File: kriging_results.csv")