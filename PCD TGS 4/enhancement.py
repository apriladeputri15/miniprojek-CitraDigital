import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ==========================================================
# KONFIGURASI FOLDER
# ==========================================================

# Gambar di folder ini SUDAH di-crop
folder_input = Path("CitraIjazah")

# Folder hasil enhancement
folder_brightness = Path("hasil/brightness")
folder_contrast = Path("hasil/contrast_stretching")
folder_equalization = Path("hasil/histogram_equalization")
folder_perbandingan = Path("hasil/perbandingan")


# Membuat folder output jika belum ada
folder_brightness.mkdir(parents=True, exist_ok=True)
folder_contrast.mkdir(parents=True, exist_ok=True)
folder_equalization.mkdir(parents=True, exist_ok=True)
folder_perbandingan.mkdir(parents=True, exist_ok=True)


# ==========================================================
# PARAMETER BRIGHTNESS
# ==========================================================

# Nilai positif = lebih terang
# Nilai negatif = lebih gelap

BRIGHTNESS_VALUE = 20


# ==========================================================
# 1. BRIGHTNESS ADJUSTMENT
# ==========================================================

def brightness_adjustment(gray, beta=20):

    hasil = cv2.convertScaleAbs(
        gray,
        alpha=1.0,
        beta=beta
    )

    return hasil


# ==========================================================
# 2. CONTRAST STRETCHING
# ==========================================================

def contrast_stretching(gray):

    # Nilai intensitas minimum
    min_val = np.min(gray)

    # Nilai intensitas maksimum
    max_val = np.max(gray)

    # Jika semua piksel memiliki nilai yang sama
    if max_val == min_val:
        return gray.copy()

    # Contrast stretching
    hasil = (
        (gray.astype(np.float32) - min_val)
        * 255
        / (max_val - min_val)
    )

    # Memastikan nilai berada pada 0-255
    hasil = np.clip(hasil, 0, 255)

    return hasil.astype(np.uint8)


# ==========================================================
# 3. HISTOGRAM EQUALIZATION
# ==========================================================

def histogram_equalization(gray):

    hasil = cv2.equalizeHist(gray)

    return hasil


# ==========================================================
# MENCARI SEMUA GAMBAR
# ==========================================================

daftar_gambar = sorted(
    list(folder_input.glob("*.jpg"))
    + list(folder_input.glob("*.jpeg"))
    + list(folder_input.glob("*.png"))
    + list(folder_input.glob("*.bmp"))
)


# ==========================================================
# CEK GAMBAR
# ==========================================================

if not daftar_gambar:

    print("Tidak ditemukan gambar di folder:")
    print(folder_input)

    exit()


# ==========================================================
# PROSES ENHANCEMENT
# ==========================================================

print("=" * 70)
print("ENHANCEMENT NOMOR IJAZAH")
print("=" * 70)

print()
print(f"Folder input  : {folder_input}")
print(f"Jumlah gambar : {len(daftar_gambar)}")


for nomor, file_gambar in enumerate(daftar_gambar, start=1):

    print()
    print("-" * 70)
    print(f"[{nomor}/{len(daftar_gambar)}] {file_gambar.name}")
    print("-" * 70)


    # ======================================================
    # MEMBACA GAMBAR
    # ======================================================

    gambar = cv2.imread(str(file_gambar))

    if gambar is None:

        print("Gambar gagal dibaca.")
        continue


    # ======================================================
    # MENGUBAH KE GRAYSCALE
    # ======================================================

    gray = cv2.cvtColor(
        gambar,
        cv2.COLOR_BGR2GRAY
    )


    # ======================================================
    # BRIGHTNESS ADJUSTMENT
    # ======================================================

    hasil_brightness = brightness_adjustment(
        gray,
        BRIGHTNESS_VALUE
    )


    # ======================================================
    # CONTRAST STRETCHING
    # ======================================================

    hasil_contrast = contrast_stretching(gray)


    # ======================================================
    # HISTOGRAM EQUALIZATION
    # ======================================================

    hasil_equalization = histogram_equalization(gray)


    # ======================================================
    # NAMA FILE
    # ======================================================

    nama = file_gambar.stem


    # ======================================================
    # SIMPAN HASIL BRIGHTNESS
    # ======================================================

    path_brightness = (
        folder_brightness /
        f"{nama}_brightness.jpg"
    )

    cv2.imwrite(
        str(path_brightness),
        hasil_brightness
    )


    # ======================================================
    # SIMPAN HASIL CONTRAST STRETCHING
    # ======================================================

    path_contrast = (
        folder_contrast /
        f"{nama}_contrast.jpg"
    )

    cv2.imwrite(
        str(path_contrast),
        hasil_contrast
    )


    # ======================================================
    # SIMPAN HASIL HISTOGRAM EQUALIZATION
    # ======================================================

    path_equalization = (
        folder_equalization /
        f"{nama}_equalization.jpg"
    )

    cv2.imwrite(
        str(path_equalization),
        hasil_equalization
    )


    # ======================================================
    # PERBANDINGAN CITRA
    # ======================================================

    plt.figure(figsize=(14, 8))


    # ------------------------------------------------------
    # CITRA ASLI
    # ------------------------------------------------------

    plt.subplot(2, 2, 1)

    plt.imshow(
        gray,
        cmap="gray"
    )

    plt.title("Sebelum Enhancement")
    plt.axis("off")


    # ------------------------------------------------------
    # BRIGHTNESS
    # ------------------------------------------------------

    plt.subplot(2, 2, 2)

    plt.imshow(
        hasil_brightness,
        cmap="gray"
    )

    plt.title("Brightness Adjustment")
    plt.axis("off")


    # ------------------------------------------------------
    # CONTRAST STRETCHING
    # ------------------------------------------------------

    plt.subplot(2, 2, 3)

    plt.imshow(
        hasil_contrast,
        cmap="gray"
    )

    plt.title("Contrast Stretching")
    plt.axis("off")


    # ------------------------------------------------------
    # HISTOGRAM EQUALIZATION
    # ------------------------------------------------------

    plt.subplot(2, 2, 4)

    plt.imshow(
        hasil_equalization,
        cmap="gray"
    )

    plt.title("Histogram Equalization")
    plt.axis("off")


    plt.suptitle(
        f"Perbandingan Enhancement - {nama}",
        fontsize=14
    )

    plt.tight_layout()


    # Simpan gambar perbandingan
    path_perbandingan = (
        folder_perbandingan /
        f"{nama}_perbandingan.png"
    )

    plt.savefig(
        str(path_perbandingan),
        dpi=150
    )

    plt.close()


    # ======================================================
    # INFORMASI STATISTIK SEDERHANA
    # ======================================================

    print(
        f"Original             : "
        f"mean={np.mean(gray):.2f}, "
        f"std={np.std(gray):.2f}"
    )

    print(
        f"Brightness            : "
        f"mean={np.mean(hasil_brightness):.2f}, "
        f"std={np.std(hasil_brightness):.2f}"
    )

    print(
        f"Contrast Stretching   : "
        f"mean={np.mean(hasil_contrast):.2f}, "
        f"std={np.std(hasil_contrast):.2f}"
    )

    print(
        f"Histogram Equalization: "
        f"mean={np.mean(hasil_equalization):.2f}, "
        f"std={np.std(hasil_equalization):.2f}"
    )


# ==========================================================
# SELESAI
# ==========================================================

print()
print("=" * 70)
print("PROSES ENHANCEMENT SELESAI")
print("=" * 70)

print()
print("Hasil tersimpan di:")

print(f"- {folder_brightness}")
print(f"- {folder_contrast}")
print(f"- {folder_equalization}")
print(f"- {folder_perbandingan}")