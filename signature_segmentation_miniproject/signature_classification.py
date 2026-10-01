import csv
from pathlib import Path

import cv2


# ============================================================
# KONFIGURASI
# ============================================================

# Hasil dari tahap 1
RESULTS_DIR = Path("results")

# Folder untuk menyimpan hasil tahap 2
CLASSIFICATION_DIR = RESULTS_DIR / "classification"

# Metode yang digunakan untuk klasifikasi
# Kita gunakan hasil Otsu + closing
METHOD = "Otsu"

# ============================================================
# ATURAN SEMENTARA
# ============================================================
#
# Nilai ini HARUS disesuaikan berdasarkan hasil
# foreground_ratio dari tahap 1.
#
# Contoh:
#
# foreground_ratio >= 0.05
#       -> SIGNATURE PRESENT
#
# foreground_ratio < 0.05
#       -> SIGNATURE ABSENT
#
# JANGAN langsung menganggap 0.05 sebagai nilai final.
# Lihat segmentation_results.csv terlebih dahulu.
#
SIGNATURE_THRESHOLD = 0.05


# ============================================================
# 1. BACA HASIL TAHAP 1
# ============================================================

def read_segmentation_results():

    csv_path = RESULTS_DIR / "segmentation_results.csv"

    if not csv_path.exists():

        print("ERROR:")
        print(
            "File segmentation_results.csv tidak ditemukan."
        )

        print(
            "Jalankan terlebih dahulu:"
        )

        print(
            "python signature_detection.py"
        )

        return []

    with open(
        csv_path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    return rows


# ============================================================
# 2. AMBIL HASIL METODE YANG DIPILIH
# ============================================================

def select_method(rows):

    selected = []

    for row in rows:

        if row["method"] == METHOD:

            selected.append(row)

    return selected


# ============================================================
# 3. BUAT ATURAN KLASIFIKASI
# ============================================================

def classify_signature(foreground_ratio):

    if foreground_ratio >= SIGNATURE_THRESHOLD:

        return "SIGNATURE PRESENT"

    else:

        return "SIGNATURE ABSENT"


# ============================================================
# 4. KLASIFIKASI SEMUA CITRA
# ============================================================

def classify_images(rows):

    results = []

    for row in rows:

        ratio = float(
            row["foreground_ratio"]
        )

        prediction = classify_signature(
            ratio
        )

        result = {

            "image": row["image"],

            "method": row["method"],

            "threshold": row["threshold"],

            "foreground_pixels": row[
                "foreground_after_closing"
            ],

            "foreground_ratio": ratio,

            "prediction": prediction

        }

        results.append(result)

    return results


# ============================================================
# 5. SIMPAN HASIL KLASIFIKASI
# ============================================================

def save_classification_results(results):

    CLASSIFICATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        CLASSIFICATION_DIR /
        "classification_results.csv"
    )

    fieldnames = [

        "image",

        "method",

        "threshold",

        "foreground_pixels",

        "foreground_ratio",

        "prediction"

    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            results
        )

    return output_file


# ============================================================
# 6. BUAT GAMBAR HASIL KLASIFIKASI
# ============================================================

def create_classification_preview(
    results
):

    for result in results:

        image_name = Path(
            result["image"]
        ).stem

        # Folder hasil tahap 1
        image_result_dir = (
            RESULTS_DIR /
            image_name
        )

        # Hasil morphology Otsu
        image_path = (
            image_result_dir /
            "09_otsu_closing.png"
        )

        if not image_path.exists():

            print(
                f"Hasil Otsu tidak ditemukan: "
                f"{image_path}"
            )

            continue

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            continue

        # --------------------------------
        # Teks hasil
        # --------------------------------

        prediction = result[
            "prediction"
        ]

        ratio = result[
            "foreground_ratio"
        ]

        text1 = prediction

        text2 = (
            f"Foreground Ratio: "
            f"{ratio:.4f}"
        )

        # --------------------------------
        # Tulisan pada gambar
        # --------------------------------

        if prediction == "SIGNATURE PRESENT":

            text_color = (
                0,
                180,
                0
            )

        else:

            text_color = (
                0,
                0,
                255
            )

        cv2.putText(

            image,

            text1,

            (10, 30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            text_color,

            2,

            cv2.LINE_AA

        )

        cv2.putText(

            image,

            text2,

            (10, 60),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (0, 0, 0),

            2,

            cv2.LINE_AA

        )

        # --------------------------------
        # Simpan
        # --------------------------------

        output_path = (
            CLASSIFICATION_DIR /
            f"{image_name}_classification.png"
        )

        cv2.imwrite(
            str(output_path),
            image
        )


# ============================================================
# 7. TAMPILKAN HASIL
# ============================================================

def display_results(results):

    print()
    print("=" * 75)

    print(
        "HASIL KLASIFIKASI TANDA TANGAN"
    )

    print("=" * 75)

    print()

    print(
        f"{'Citra':35} "
        f"{'Ratio':10} "
        f"Hasil"
    )

    print("-" * 75)

    for result in results:

        image = result["image"]

        ratio = result[
            "foreground_ratio"
        ]

        prediction = result[
            "prediction"
        ]

        print(
            f"{image:35} "
            f"{ratio:<10.4f} "
            f"{prediction}"
        )

    print("-" * 75)

    print(
        f"\nBatas klasifikasi: "
        f"{SIGNATURE_THRESHOLD}"
    )


# ============================================================
# 8. MAIN
# ============================================================

def main():

    print("=" * 75)

    print(
        "TAHAP 2 - KLASIFIKASI KEBERADAAN TANDA TANGAN"
    )

    print("=" * 75)

    print()

    print(
        "Metode yang digunakan : Otsu"
    )

    print(
        "Karakteristik          : Foreground Ratio"
    )

    print(
        "Aturan                 :"
    )

    print(
        f"Ratio >= "
        f"{SIGNATURE_THRESHOLD}"
        f" -> SIGNATURE PRESENT"
    )

    print(
        f"Ratio < "
        f"{SIGNATURE_THRESHOLD}"
        f" -> SIGNATURE ABSENT"
    )

    # --------------------------------------------------------
    # Baca hasil tahap 1
    # --------------------------------------------------------

    rows = read_segmentation_results()

    if not rows:

        return

    # --------------------------------------------------------
    # Pilih Otsu
    # --------------------------------------------------------

    selected_rows = select_method(
        rows
    )

    if not selected_rows:

        print(
            "\nTidak ditemukan hasil metode Otsu."
        )

        return

    # --------------------------------------------------------
    # Klasifikasi
    # --------------------------------------------------------

    results = classify_images(
        selected_rows
    )

    # --------------------------------------------------------
    # Simpan CSV
    # --------------------------------------------------------

    output_file = (
        save_classification_results(
            results
        )
    )

    # --------------------------------------------------------
    # Buat preview
    # --------------------------------------------------------

    create_classification_preview(
        results
    )

    # --------------------------------------------------------
    # Tampilkan
    # --------------------------------------------------------

    display_results(
        results
    )

    # --------------------------------------------------------
    # Selesai
    # --------------------------------------------------------

    print()

    print(
        "Hasil klasifikasi:"
    )

    print(
        output_file
    )

    print()

    print(
        "Preview:"
    )

    print(
        CLASSIFICATION_DIR
    )

    print()

    print(
        "PENTING:"
    )

    print(
        "Nilai threshold klasifikasi masih perlu"
    )

    print(
        "divalidasi menggunakan citra yang benar-benar"
    )

    print(
        "memiliki dan tidak memiliki tanda tangan."
    )


if __name__ == "__main__":

    main()