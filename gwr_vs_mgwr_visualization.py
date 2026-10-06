"""
=====================================================
VISUALISASI PERBEDAAN GWR vs MGWR
=====================================================
Ilustrasi bagaimana MGWR mengakomodasi bandwidth berbeda
untuk setiap variabel, sementara GWR memaksa satu bandwidth kompromi.
=====================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# =====================================================
# PANEL KIRI: GWR (Single Bandwidth untuk semua variabel)
# =====================================================

ax1 = axes[0]
ax1.set_title('GWR (Geographically Weighted Regression)\nSatu Bandwidth untuk SEMUA Variabel', 
              fontsize=12, fontweight='bold', pad=15)

# Gambar area penelitian (pulau)
x = np.linspace(0, 10, 100)
y = np.linspace(0, 10, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)  # landscape sederhana

# Plot peta dasar
ax1.imshow(Z, extent=[0, 10, 0, 10], origin='lower', cmap='terrain', alpha=0.3)

# Bandwidth tunggal (lingkaran besar yang sama untuk semua variabel)
bandwidth_gwr = 3.5
for cx in [2, 5, 8]:
    for cy in [2, 5, 8]:
        circle = plt.Circle((cx, cy), bandwidth_gwr, 
                           color='red', fill=False, linewidth=2, linestyle='--', alpha=0.7)
        ax1.add_patch(circle)
        ax1.plot(cx, cy, 'ro', markersize=8)

# Anotasi
ax1.annotate('Bandwidth SAMA\nuntuk Lebar Jalan & Jarak', 
             xy=(5, 7), xytext=(6, 8.5),
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=9, ha='center', color='red')

ax1.set_xlabel('Longitude', fontsize=10)
ax1.set_ylabel('Latitude', fontsize=10)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)

# Legend untuk GWR
gwr_legend_elements = [
    mpatches.Patch(facecolor='none', edgecolor='red', linestyle='--', label=f'Bandwidth GWR = {bandwidth_gwr} (sama untuk semua)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Titik Sampel')
]
ax1.legend(handles=gwr_legend_elements, loc='lower right', fontsize=8)

# Keterangan
ax1.text(0.5, -0.12, 'Kelebihan: Sederhana | Kekurangan: Tidak fleksibel untuk variabel dengan skala berbeda', 
         transform=ax1.transAxes, fontsize=9, ha='center', style='italic', color='gray')

# =====================================================
# PANEL KANAN: MGWR (Multiscale GWR - Bandwidth berbeda per variabel)
# =====================================================

ax2 = axes[1]
ax2.set_title('MGWR (Multiscale GWR)\nBandwidth BERBEDA untuk Setiap Variabel', 
              fontsize=12, fontweight='bold', pad=15)

# Plot peta dasar
ax2.imshow(Z, extent=[0, 10, 0, 10], origin='lower', cmap='terrain', alpha=0.3)

# Titik sampel yang sama
for cx in [2, 5, 8]:
    for cy in [2, 5, 8]:
        ax2.plot(cx, cy, 'bo', markersize=8)

# Bandwidth KECIL untuk Lebar Jalan (variasi lokal cepat)
bandwidth_lebar = 1.2
for cx in [2, 5, 8]:
    for cy in [2, 5, 8]:
        circle_small = plt.Circle((cx, cy), bandwidth_lebar, 
                                  color='green', fill=False, linewidth=2, linestyle='-', alpha=0.8)
        ax2.add_patch(circle_small)

# Bandwidth BESAR untuk Jarak ke Pusat (variasi global)
bandwidth_jarak = 4.5
for cx in [2, 5, 8]:
    for cy in [2, 5, 8]:
        circle_large = plt.Circle((cx, cy), bandwidth_jarak, 
                                  color='orange', fill=False, linewidth=2, linestyle=':', alpha=0.8)
        ax2.add_patch(circle_large)

# Anotasi untuk bandwidth berbeda
ax2.annotate('Bandwidth KECIL\n(untuk Lebar Jalan)\nperubahan cepat', 
             xy=(3, 3), xytext=(1, 1),
             arrowprops=dict(arrowstyle='->', color='green'),
             fontsize=8, ha='center', color='green')

ax2.annotate('Bandwidth BESAR\n(untuk Jarak ke Pusat)\nperubahan lambat', 
             xy=(5, 7), xytext=(7, 8.5),
             arrowprops=dict(arrowstyle='->', color='orange'),
             fontsize=8, ha='center', color='orange')

ax2.set_xlabel('Longitude', fontsize=10)
ax2.set_ylabel('Latitude', fontsize=10)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)

# Legend untuk MGWR
mgwr_legend_elements = [
    mpatches.Patch(facecolor='none', edgecolor='green', linestyle='-', label='Bandwidth KECIL (Lebar Jalan - Variasi Lokal)'),
    mpatches.Patch(facecolor='none', edgecolor='orange', linestyle=':', label='Bandwidth BESAR (Jarak ke Pusat - Variasi Global)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Titik Sampel')
]
ax2.legend(handles=mgwr_legend_elements, loc='lower right', fontsize=8)

# Keterangan
ax2.text(0.5, -0.12, 'Kelebihan: Setiap variabel punya skala sendiri | Lebih akurat & fleksibel', 
         transform=ax2.transAxes, fontsize=9, ha='center', style='italic', color='gray')

# =====================================================
# FOOTER GLOBAL
# =====================================================

plt.suptitle('Perbandingan GWR vs MGWR dalam Menangkap Heterogenitas Spasial', 
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('gwr_vs_mgwr_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("📊 INTERPRETASI VISUALISASI")
print("="*60)
print("\n🔵 GWR (Kiri) - Satu Bandwidth untuk Semua:")
print("   • Semua variabel dipaksa menggunakan bandwidth yang sama (lingkaran merah putus-putus)")
print("   • Kelemahan: Tidak bisa membedakan mana variabel yang bervariasi cepat vs lambat")
print("   • Akibat: Model bisa over-smoothing untuk variabel lokal atau under-smoothing untuk variabel global")
print("\n🟢 MGWR (Kanan) - Bandwidth Berbeda per Variabel:")
print("   • Variabel lokal (Lebar Jalan): bandwidth kecil (lingkaran hijau solid) → berubah cepat")
print("   • Variabel global (Jarak ke Pusat): bandwidth besar (lingkaran oranye titik-titik) → berubah lambat")
print("   • Keunggulan: Setiap variabel diestimasi pada skala spasial yang paling tepat")
print("\n📈 Implikasi untuk ILASPP:")
print("   • Lebar jalan → prioritas kebijakan LOKAL (per blok/RT)")
print("   • Jarak ke pusat kota → prioritas kebijakan GLOBAL (per kecamatan/kota)")
print("="*60)