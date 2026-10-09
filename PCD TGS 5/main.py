import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pytesseract
import os
import re


# ============================================================
# 1. KONFIGURASI
# ============================================================

# Folder tempat 9 gambar berada
INPUT_FOLDER = r"citra"

# Lokasi Tesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Nomor ijazah yang benar
GROUND_TRUTH = "571012022000056"


# ============================================================
# 2. FOLDER HASIL
# ============================================================

FOLDER_HASIL = r"hasil"
FOLDER_FILTER = r"hasil\filter"
FOLDER_HISTOGRAM = r"hasil\histogram"
FOLDER_OCR = r"hasil\ocr"

os.makedirs(FOLDER_HASIL, exist_ok=True)
os.makedirs(FOLDER_FILTER, exist_ok=True)
os.makedirs(FOLDER_HISTOGRAM, exist_ok=True)
os.makedirs(FOLDER_OCR, exist_ok=True)


# ============================================================
# 3. MENCARI SEMUA GAMBAR
# ============================================================

daftar_file = []

for nama_file in os.listdir(INPUT_FOLDER):

    if nama_file.lower().endswith((".jpg", ".jpeg")):

        daftar_file.append(
            os.path.join(
                INPUT_FOLDER,
                nama_file
            )
        )


# Urutkan berdasarkan nama
daftar_file.sort()


# ============================================================
# 4. CEK GAMBAR
# ============================================================

print("=" * 100)
print("FILTERING, NOISE REDUCTION, SHARPENING DAN OCR")
print("=" * 100)

print(
    f"\nJumlah gambar ditemukan: {len(daftar_file)}"
)


if len(daftar_file) == 0:

    print("\n❌ Tidak ada gambar ditemukan!")

    print("\nPastikan struktur folder seperti:")
    print("citra/")
    print("├── 01_HighQuality_Enhanced.jpg")
    print("├── 02_LowContrast.jpg")
    print("├── 03_Blurred.jpg")
    print("├── 04_HighNoise.jpg")
    print("├── 05_LowResolution_Upsampled.jpg")
    print("├── 06_Faded_Underexposed.jpg")
    print("├── 07_ColorShift_WarmTint.jpg")
    print("├── 08_JPEGCompression_Artifacts.jpg")
    print("└── 09_CombinedDegradation.jpg")

    exit()


# ============================================================
# 5. TAMPILKAN DAFTAR GAMBAR
# ============================================================

print("\nDaftar gambar:")

for i, file_path in enumerate(
    daftar_file,
    start=1
):

    print(
        f"{i}. {os.path.basename(file_path)}"
    )


# ============================================================
# 6. FUNGSI NORMALISASI OCR
# ============================================================

def normalisasi_ocr(teks):

    """
    Mengambil angka dari hasil OCR.

    Contoh:

    OCR:
    NOMORIJAZAH571012022000056

    Hasil:
    571012022000056
    """

    # Ubah ke huruf besar
    teks = teks.upper()

    # Ambil semua kelompok angka
    angka = re.findall(
        r"\d+",
        teks
    )

    # Gabungkan semua angka
    hasil = "".join(
        angka
    )

    return hasil


# ============================================================
# 7. FUNGSI HITUNG KARAKTER BENAR
# ============================================================

def hitung_karakter_benar(
    ground_truth,
    hasil_ocr
):

    """
    Membandingkan karakter berdasarkan posisi.

    Contoh:

    Ground Truth : 571012022000056
    OCR          : 571012022000056

    Karakter benar = 15
    """

    jumlah_dibandingkan = min(
        len(ground_truth),
        len(hasil_ocr)
    )

    benar = 0

    for i in range(
        jumlah_dibandingkan
    ):

        if ground_truth[i] == hasil_ocr[i]:

            benar += 1

    return benar


# ============================================================
# 8. DATA UNTUK MENYIMPAN HASIL
# ============================================================

semua_hasil = []


# ============================================================
# 9. PROSES SEMUA GAMBAR
# ============================================================

for nomor_gambar, file_path in enumerate(
    daftar_file,
    start=1
):

    nama_file = os.path.basename(
        file_path
    )

    nama_gambar = os.path.splitext(
        nama_file
    )[0]


    print("\n")
    print("=" * 100)

    print(
        f"GAMBAR {nomor_gambar}: {nama_file}"
    )

    print("=" * 100)


    # ========================================================
    # BACA CITRA
    # ========================================================

    image = cv2.imread(
        file_path
    )


    if image is None:

        print(
            "❌ Gagal membaca:",
            file_path
        )

        continue


    print(
        "Ukuran citra:",
        image.shape
    )


    # ========================================================
    # GRAYSCALE
    # ========================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    # ========================================================
    # 10. FILTERING
    # ========================================================

    # --------------------------------------------------------
    # Original
    # --------------------------------------------------------

    original = gray.copy()


    # --------------------------------------------------------
    # Mean Filter
    # --------------------------------------------------------

    mean_filter = cv2.blur(
        gray,
        (5, 5)
    )


    # --------------------------------------------------------
    # Median Filter
    # --------------------------------------------------------

    median_filter = cv2.medianBlur(
        gray,
        5
    )


    # --------------------------------------------------------
    # Gaussian Filter
    # --------------------------------------------------------

    gaussian_filter = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )


    # --------------------------------------------------------
    # Sharpening
    # --------------------------------------------------------

    kernel_sharpen = np.array([
        [0, -1,  0],
        [-1, 5, -1],
        [0, -1,  0]
    ])


    sharpening = cv2.filter2D(
        gray,
        -1,
        kernel_sharpen
    )


    # ========================================================
    # 11. SIMPAN SEMUA METODE
    # ========================================================

    hasil_filter = {

        "Original":
            original,

        "Mean Filter":
            mean_filter,

        "Median Filter":
            median_filter,

        "Gaussian Filter":
            gaussian_filter,

        "Sharpening":
            sharpening
    }


    # ========================================================
    # 12. FOLDER PER GAMBAR
    # ========================================================

    folder_gambar_filter = os.path.join(
        FOLDER_FILTER,
        nama_gambar
    )

    folder_gambar_histogram = os.path.join(
        FOLDER_HISTOGRAM,
        nama_gambar
    )

    folder_gambar_ocr = os.path.join(
        FOLDER_OCR,
        nama_gambar
    )


    os.makedirs(
        folder_gambar_filter,
        exist_ok=True
    )

    os.makedirs(
        folder_gambar_histogram,
        exist_ok=True
    )

    os.makedirs(
        folder_gambar_ocr,
        exist_ok=True
    )


    # ========================================================
    # 13. SIMPAN HASIL FILTER
    # ========================================================

    for nama_metode, citra in hasil_filter.items():

        nama_metode_file = (
            nama_metode
            .lower()
            .replace(" ", "_")
            + ".jpg"
        )

        output_path = os.path.join(
            folder_gambar_filter,
            nama_metode_file
        )

        cv2.imwrite(
            output_path,
            citra
        )


    # ========================================================
    # 14. PERBANDINGAN CITRA
    # ========================================================

    plt.figure(
        figsize=(15, 8)
    )


    for i, (
        nama_metode,
        citra
    ) in enumerate(
        hasil_filter.items()
    ):

        plt.subplot(
            2,
            3,
            i + 1
        )

        plt.imshow(
            citra,
            cmap="gray"
        )

        plt.title(
            nama_metode
        )

        plt.axis("off")


    plt.suptitle(
        "Perbandingan Filtering - " + nama_file,
        fontsize=16
    )

    plt.tight_layout()


    plt.savefig(
        os.path.join(
            folder_gambar_filter,
            "perbandingan.jpg"
        ),
        dpi=300
    )

    plt.close()


    # ========================================================
    # 15. HISTOGRAM
    # ========================================================

    plt.figure(
        figsize=(15, 8)
    )


    for i, (
        nama_metode,
        citra
    ) in enumerate(
        hasil_filter.items()
    ):

        plt.subplot(
            2,
            3,
            i + 1
        )

        plt.hist(
            citra.ravel(),
            bins=256,
            range=(0, 256)
        )

        plt.title(
            nama_metode
        )

        plt.xlabel(
            "Intensitas"
        )

        plt.ylabel(
            "Jumlah Piksel"
        )


    plt.suptitle(
        "Histogram - " + nama_file,
        fontsize=16
    )

    plt.tight_layout()


    plt.savefig(
        os.path.join(
            folder_gambar_histogram,
            "histogram.jpg"
        ),
        dpi=300
    )

    plt.close()


    # ========================================================
    # 16. OCR SETIAP METODE
    # ========================================================

    for nama_metode, citra in hasil_filter.items():

        # ----------------------------------------------------
        # THRESHOLD OTSU
        # ----------------------------------------------------

        _, binary = cv2.threshold(
            citra,
            0,
            255,
            cv2.THRESH_BINARY +
            cv2.THRESH_OTSU
        )


        # ----------------------------------------------------
        # SIMPAN CITRA UNTUK OCR
        # ----------------------------------------------------

        nama_ocr_file = (
            nama_metode
            .lower()
            .replace(" ", "_")
            + "_ocr.jpg"
        )


        cv2.imwrite(
            os.path.join(
                folder_gambar_ocr,
                nama_ocr_file
            ),
            binary
        )


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        teks = pytesseract.image_to_string(
            binary,
            config="--psm 7"
        )


        # ----------------------------------------------------
        # NORMALISASI OCR
        # ----------------------------------------------------

        teks_bersih = normalisasi_ocr(
            teks
        )


        # ----------------------------------------------------
        # HITUNG KARAKTER BENAR
        # ----------------------------------------------------

        karakter_benar = hitung_karakter_benar(
            GROUND_TRUTH,
            teks_bersih
        )


        # ----------------------------------------------------
        # HITUNG AKURASI
        # ----------------------------------------------------

        if len(GROUND_TRUTH) > 0:

            akurasi = (
                karakter_benar /
                len(GROUND_TRUTH)
            ) * 100

        else:

            akurasi = 0


        # ----------------------------------------------------
        # SIMPAN HASIL
        # ----------------------------------------------------

        semua_hasil.append({

            "Gambar":
                nama_file,

            "Metode":
                nama_metode,

            "Hasil OCR":
                teks_bersih,

            "Karakter Benar":
                karakter_benar,

            "Akurasi (%)":
                round(
                    akurasi,
                    2
                )
        })


        # ----------------------------------------------------
        # TAMPILKAN HASIL DI TERMINAL
        # ----------------------------------------------------

        print(
            f"{nama_metode:15} | "
            f"OCR: {teks_bersih:20} | "
            f"Benar: {karakter_benar:2} | "
            f"Akurasi: {akurasi:6.2f}%"
        )


# ============================================================
# 17. DATAFRAME
# ============================================================

df = pd.DataFrame(
    semua_hasil
)


# ============================================================
# 18. TAMPILKAN HASIL OCR
# ============================================================

print("\n")

print("=" * 110)
print("HASIL OCR SEMUA GAMBAR")
print("=" * 110)


print(
    df.to_string(
        index=False
    )
)


# ============================================================
# 19. SIMPAN HASIL KE EXCEL
# ============================================================

try:

    df.to_excel(
        r"hasil\hasil_ocr.xlsx",
        index=False
    )

    print(
        "\n✓ Excel berhasil dibuat:"
    )

    print(
        "  hasil\\hasil_ocr.xlsx"
    )

except ImportError:

    print(
        "\n❌ Gagal membuat Excel."
    )

    print(
        "Install openpyxl dengan:"
    )

    print(
        "python -m pip install openpyxl"
    )


# ============================================================
# 20. SIMPAN HASIL KE CSV
# ============================================================

df.to_csv(
    r"hasil\hasil_ocr.csv",
    index=False
)


print(
    "✓ CSV berhasil dibuat:"
)

print(
    "  hasil\\hasil_ocr.csv"
)


# ============================================================
# 21. RATA-RATA AKURASI SETIAP METODE
# ============================================================

print("\n")

print("=" * 80)
print("RATA-RATA AKURASI SETIAP METODE")
print("=" * 80)


rata_rata = (
    df
    .groupby(
        "Metode"
    )["Akurasi (%)"]
    .mean()
    .reset_index()
)


# Urutkan dari akurasi tertinggi
rata_rata = rata_rata.sort_values(
    "Akurasi (%)",
    ascending=False
)


print(
    rata_rata.to_string(
        index=False
    )
)


# ============================================================
# 22. SIMPAN RATA-RATA
# ============================================================

try:

    rata_rata.to_excel(
        r"hasil\rata_rata_akurasi.xlsx",
        index=False
    )

    print(
        "\n✓ Rata-rata berhasil disimpan:"
    )

    print(
        "  hasil\\rata_rata_akurasi.xlsx"
    )

except ImportError:

    print(
        "\n⚠ File rata-rata Excel tidak dibuat karena openpyxl belum terinstall."
    )


# ============================================================
# 23. GRAFIK AKURASI
# ============================================================

plt.figure(
    figsize=(10, 6)
)


plt.bar(
    rata_rata["Metode"],
    rata_rata["Akurasi (%)"]
)


plt.xlabel(
    "Metode"
)

plt.ylabel(
    "Rata-rata Akurasi (%)"
)

plt.title(
    "Perbandingan Rata-rata Akurasi OCR"
)

plt.xticks(
    rotation=20
)

plt.ylim(
    0,
    100
)

plt.tight_layout()


plt.savefig(
    r"hasil\perbandingan_akurasi.jpg",
    dpi=300
)


# Tampilkan grafik
plt.show()


# ============================================================
# 24. SELESAI
# ============================================================

print("\n")

print("=" * 100)
print("PROSES SELESAI")
print("=" * 100)


print(
    f"\nJumlah gambar diproses: {len(daftar_file)}"
)


print(
    f"Jumlah hasil OCR: {len(df)}"
)


print(
    f"\nGround Truth: {GROUND_TRUTH}"
)


print("\nFile hasil:")

print(
    "✓ hasil\\hasil_ocr.xlsx"
)

print(
    "✓ hasil\\hasil_ocr.csv"
)

print(
    "✓ hasil\\rata_rata_akurasi.xlsx"
)

print(
    "✓ hasil\\perbandingan_akurasi.jpg"
)


print(
    "\n✓ Semua gambar berhasil diproses."
)