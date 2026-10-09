import cv2
import matplotlib.pyplot as plt
from pathlib import Path


# ==========================================================
# KONFIGURASI FOLDER
# ==========================================================

# Folder gambar asli yang SUDAH di-crop
folder_input = Path("CitraIjazah")

# Folder hasil enhancement
folder_brightness = Path("hasil/brightness")
folder_contrast = Path("hasil/contrast_stretching")
folder_equalization = Path("hasil/histogram_equalization")

# Folder untuk menyimpan hasil histogram
folder_histogram = Path("hasil/histogram")


# Membuat folder histogram jika belum ada
folder_histogram.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# MENCARI SEMUA GAMBAR ASLI
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
# INFORMASI PROGRAM
# ==========================================================

print("=" * 70)
print("HISTOGRAM CITRA NOMOR IJAZAH")
print("=" * 70)

print()
print(f"Folder input  : {folder_input}")
print(f"Jumlah gambar : {len(daftar_gambar)}")
print(f"Output        : {folder_histogram}")


# ==========================================================
# PROSES SEMUA GAMBAR
# ==========================================================

for nomor, file_gambar in enumerate(
    daftar_gambar,
    start=1
):

    print()
    print("-" * 70)
    print(
        f"[{nomor}/{len(daftar_gambar)}] "
        f"{file_gambar.name}"
    )
    print("-" * 70)


    # ======================================================
    # NAMA FILE
    # ======================================================

    nama = file_gambar.stem


    # ======================================================
    # MEMBACA CITRA ASLI
    # ======================================================

    gambar_asli = cv2.imread(
        str(file_gambar)
    )

    if gambar_asli is None:

        print("Gambar asli gagal dibaca.")
        continue


    # ======================================================
    # KONVERSI CITRA ASLI KE GRAYSCALE
    # ======================================================

    original = cv2.cvtColor(
        gambar_asli,
        cv2.COLOR_BGR2GRAY
    )


    # ======================================================
    # MEMBACA HASIL BRIGHTNESS
    # ======================================================

    path_brightness = (
        folder_brightness
        / f"{nama}_brightness.jpg"
    )

    brightness = cv2.imread(
        str(path_brightness),
        cv2.IMREAD_GRAYSCALE
    )


    # ======================================================
    # MEMBACA HASIL CONTRAST STRETCHING
    # ======================================================

    path_contrast = (
        folder_contrast
        / f"{nama}_contrast.jpg"
    )

    contrast = cv2.imread(
        str(path_contrast),
        cv2.IMREAD_GRAYSCALE
    )


    # ======================================================
    # MEMBACA HASIL HISTOGRAM EQUALIZATION
    # ======================================================

    path_equalization = (
        folder_equalization
        / f"{nama}_equalization.jpg"
    )

    equalization = cv2.imread(
        str(path_equalization),
        cv2.IMREAD_GRAYSCALE
    )


    # ======================================================
    # CEK HASIL ENHANCEMENT
    # ======================================================

    if brightness is None:

        print(
            "Hasil brightness tidak ditemukan:"
        )

        print(path_brightness)

        continue


    if contrast is None:

        print(
            "Hasil contrast stretching "
            "tidak ditemukan:"
        )

        print(path_contrast)

        continue


    if equalization is None:

        print(
            "Hasil histogram equalization "
            "tidak ditemukan:"
        )

        print(path_equalization)

        continue


    # ======================================================
    # MEMBUAT HISTOGRAM
    # ======================================================

    plt.figure(figsize=(14, 10))


    # ------------------------------------------------------
    # 1. HISTOGRAM CITRA ASLI
    # ------------------------------------------------------

    plt.subplot(2, 2, 1)

    plt.hist(
        original.ravel(),
        bins=256,
        range=[0, 256]
    )

    plt.title(
        "Histogram Sebelum Enhancement"
    )

    plt.xlabel(
        "Intensitas Piksel"
    )

    plt.ylabel(
        "Jumlah Piksel"
    )


    # ------------------------------------------------------
    # 2. HISTOGRAM BRIGHTNESS
    # ------------------------------------------------------

    plt.subplot(2, 2, 2)

    plt.hist(
        brightness.ravel(),
        bins=256,
        range=[0, 256]
    )

    plt.title(
        "Histogram Brightness Adjustment"
    )

    plt.xlabel(
        "Intensitas Piksel"
    )

    plt.ylabel(
        "Jumlah Piksel"
    )


    # ------------------------------------------------------
    # 3. HISTOGRAM CONTRAST STRETCHING
    # ------------------------------------------------------

    plt.subplot(2, 2, 3)

    plt.hist(
        contrast.ravel(),
        bins=256,
        range=[0, 256]
    )

    plt.title(
        "Histogram Contrast Stretching"
    )

    plt.xlabel(
        "Intensitas Piksel"
    )

    plt.ylabel(
        "Jumlah Piksel"
    )


    # ------------------------------------------------------
    # 4. HISTOGRAM EQUALIZATION
    # ------------------------------------------------------

    plt.subplot(2, 2, 4)

    plt.hist(
        equalization.ravel(),
        bins=256,
        range=[0, 256]
    )

    plt.title(
        "Histogram Equalization"
    )

    plt.xlabel(
        "Intensitas Piksel"
    )

    plt.ylabel(
        "Jumlah Piksel"
    )


    # ======================================================
    # JUDUL UTAMA
    # ======================================================

    plt.suptitle(
        f"Perbandingan Histogram - {nama}",
        fontsize=14
    )


    plt.tight_layout()


    # ======================================================
    # SIMPAN HASIL HISTOGRAM
    # ======================================================

    path_output = (
        folder_histogram
        / f"{nama}_histogram.png"
    )

    plt.savefig(
        str(path_output),
        dpi=150,
        bbox_inches="tight"
    )


    # Tampilkan histogram
    plt.show()

    # Tutup figure
    plt.close()


    # ======================================================
    # INFORMASI STATISTIK
    # ======================================================

    print(
        f"Original             : "
        f"mean={original.mean():.2f}, "
        f"std={original.std():.2f}"
    )

    print(
        f"Brightness            : "
        f"mean={brightness.mean():.2f}, "
        f"std={brightness.std():.2f}"
    )

    print(
        f"Contrast Stretching   : "
        f"mean={contrast.mean():.2f}, "
        f"std={contrast.std():.2f}"
    )

    print(
        f"Histogram Equalization: "
        f"mean={equalization.mean():.2f}, "
        f"std={equalization.std():.2f}"
    )

    print(
        f"Hasil disimpan: {path_output}"
    )


# ==========================================================
# SELESAI
# ==========================================================

print()
print("=" * 70)
print("PROSES HISTOGRAM SELESAI")
print("=" * 70)

print()
print("Semua histogram tersimpan di:")
print(folder_histogram)