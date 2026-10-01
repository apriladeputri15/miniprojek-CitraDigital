import cv2
import numpy as np
from pathlib import Path
import csv


INPUT_DIR = Path("data")
OUTPUT_DIR = Path("results")

GLOBAL_THRESHOLD = 180


def crop_signature_area(image):
    """
    Gambar input sudah merupakan hasil crop
    area tanda tangan kepala sekolah.

    Jadi gambar langsung digunakan sebagai ROI.
    """
    return image.copy()


def convert_grayscale(image):
    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


def global_threshold(gray):

    _, result = cv2.threshold(
        gray,
        GLOBAL_THRESHOLD,
        255,
        cv2.THRESH_BINARY_INV
    )

    return result, GLOBAL_THRESHOLD


def otsu_threshold(gray):

    threshold_value, result = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV +
        cv2.THRESH_OTSU
    )

    return result, threshold_value


def adaptive_threshold(gray):

    result = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        11
    )

    return result


def morphological_opening(binary):

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    return cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )


def morphological_closing(binary):

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    return cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )


def count_foreground(binary):

    return cv2.countNonZero(binary)


def calculate_foreground_ratio(binary):

    total = (
        binary.shape[0] *
        binary.shape[1]
    )

    foreground = count_foreground(
        binary
    )

    return foreground / total


def save_image(path, image):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(path),
        image
    )


def process_image(image_path):

    print(
        f"\nMemproses: {image_path.name}"
    )

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        print("Gambar tidak dapat dibaca.")

        return []


    # ========================================================
    # 1. CROP / ROI
    # ========================================================
    #
    # Input sudah berupa hasil crop tanda tangan.
    # Jadi digunakan langsung sebagai ROI.
    # ========================================================

    roi = crop_signature_area(
        image
    )

    result_dir = (
        OUTPUT_DIR /
        image_path.stem
    )

    save_image(
        result_dir / "01_roi.png",
        roi
    )


    # ========================================================
    # 2. GRAYSCALE
    # ========================================================

    gray = convert_grayscale(
        roi
    )

    save_image(
        result_dir / "02_grayscale.png",
        gray
    )


    # ========================================================
    # 3. GLOBAL THRESHOLD
    # ========================================================

    global_result, global_value = (
        global_threshold(gray)
    )

    save_image(
        result_dir /
        "03_global_threshold.png",
        global_result
    )


    # ========================================================
    # 4. OTSU THRESHOLD
    # ========================================================

    otsu_result, otsu_value = (
        otsu_threshold(gray)
    )

    save_image(
        result_dir /
        "04_otsu_threshold.png",
        otsu_result
    )


    # ========================================================
    # 5. ADAPTIVE THRESHOLD
    # ========================================================

    adaptive_result = (
        adaptive_threshold(gray)
    )

    save_image(
        result_dir /
        "05_adaptive_threshold.png",
        adaptive_result
    )


    # ========================================================
    # 6. MORPHOLOGY - GLOBAL
    # ========================================================

    global_opening = (
        morphological_opening(
            global_result
        )
    )

    global_closing = (
        morphological_closing(
            global_opening
        )
    )

    save_image(
        result_dir /
        "06_global_opening.png",
        global_opening
    )

    save_image(
        result_dir /
        "07_global_closing.png",
        global_closing
    )


    # ========================================================
    # 7. MORPHOLOGY - OTSU
    # ========================================================

    otsu_opening = (
        morphological_opening(
            otsu_result
        )
    )

    otsu_closing = (
        morphological_closing(
            otsu_opening
        )
    )

    save_image(
        result_dir /
        "08_otsu_opening.png",
        otsu_opening
    )

    save_image(
        result_dir /
        "09_otsu_closing.png",
        otsu_closing
    )


    # ========================================================
    # 8. MORPHOLOGY - ADAPTIVE
    # ========================================================

    adaptive_opening = (
        morphological_opening(
            adaptive_result
        )
    )

    adaptive_closing = (
        morphological_closing(
            adaptive_opening
        )
    )

    save_image(
        result_dir /
        "10_adaptive_opening.png",
        adaptive_opening
    )

    save_image(
        result_dir /
        "11_adaptive_closing.png",
        adaptive_closing
    )


    # ========================================================
    # 9. HITUNG FOREGROUND PIXEL
    # ========================================================

    results = []


    # Global
    results.append({

        "image": image_path.name,

        "method": "Global",

        "threshold": global_value,

        "foreground_before":
            count_foreground(
                global_result
            ),

        "foreground_after_opening":
            count_foreground(
                global_opening
            ),

        "foreground_after_closing":
            count_foreground(
                global_closing
            ),

        "foreground_ratio":
            round(
                calculate_foreground_ratio(
                    global_closing
                ),
                6
            )

    })


    # Otsu
    results.append({

        "image": image_path.name,

        "method": "Otsu",

        "threshold":
            round(
                float(otsu_value),
                2
            ),

        "foreground_before":
            count_foreground(
                otsu_result
            ),

        "foreground_after_opening":
            count_foreground(
                otsu_opening
            ),

        "foreground_after_closing":
            count_foreground(
                otsu_closing
            ),

        "foreground_ratio":
            round(
                calculate_foreground_ratio(
                    otsu_closing
                ),
                6
            )

    })


    # Adaptive
    results.append({

        "image": image_path.name,

        "method": "Adaptive",

        "threshold": "Local",

        "foreground_before":
            count_foreground(
                adaptive_result
            ),

        "foreground_after_opening":
            count_foreground(
                adaptive_opening
            ),

        "foreground_after_closing":
            count_foreground(
                adaptive_closing
            ),

        "foreground_ratio":
            round(
                calculate_foreground_ratio(
                    adaptive_closing
                ),
                6
            )

    })


    # ========================================================
    # 10. TAMPILKAN HASIL
    # ========================================================

    for result in results:

        print(
            f"\nMetode: {result['method']}"
        )

        print(
            f"Threshold: "
            f"{result['threshold']}"
        )

        print(
            f"Foreground sebelum morphology: "
            f"{result['foreground_before']}"
        )

        print(
            f"Foreground setelah opening: "
            f"{result['foreground_after_opening']}"
        )

        print(
            f"Foreground setelah closing: "
            f"{result['foreground_after_closing']}"
        )

        print(
            f"Foreground ratio: "
            f"{result['foreground_ratio']:.4f}"
        )


    return results


def main():

    print("=" * 70)

    print(
        "MINI PROJECT - SEGMENTASI TANDA TANGAN"
    )

    print("=" * 70)

    print(
        "\nDataset yang digunakan:"
    )

    print(
        "Citra sudah berupa crop area "
        "tanda tangan kepala sekolah."
    )

    print(
        "\nTahapan:"
    )

    print(
        "1. Gunakan crop sebagai ROI"
    )

    print(
        "2. Grayscale"
    )

    print(
        "3. Global Threshold"
    )

    print(
        "4. Otsu Threshold"
    )

    print(
        "5. Adaptive Threshold"
    )

    print(
        "6. Opening"
    )

    print(
        "7. Closing"
    )

    print(
        "8. Hitung foreground pixel"
    )


    # --------------------------------------------------------
    # Cari gambar
    # --------------------------------------------------------

    extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.bmp",
        "*.webp"
    ]

    image_files = []

    for extension in extensions:

        image_files.extend(
            INPUT_DIR.glob(extension)
        )

    image_files = sorted(
        image_files
    )


    if not image_files:

        print(
            "\nTidak ada gambar di folder data."
        )

        return


    print(
        f"\nJumlah gambar: "
        f"{len(image_files)}"
    )


    all_results = []


    for image_path in image_files:

        results = process_image(
            image_path
        )

        all_results.extend(
            results
        )


    # ========================================================
    # SIMPAN CSV
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    csv_path = (
        OUTPUT_DIR /
        "segmentation_results.csv"
    )

    fieldnames = [

        "image",
        "method",
        "threshold",
        "foreground_before",
        "foreground_after_opening",
        "foreground_after_closing",
        "foreground_ratio"

    ]

    with open(
        csv_path,
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
            all_results
        )


    print(
        "\n" + "=" * 70
    )

    print(
        "SELESAI"
    )

    print(
        "=" * 70
    )

    print(
        f"\nHasil tersimpan di:"
    )

    print(
        f"{OUTPUT_DIR}"
    )

    print(
        f"\nTabel:"
    )

    print(
        f"{csv_path}"
    )

    print(
        "\nBelum ada klasifikasi "
        "SIGNATURE PRESENT/ABSENT."
    )


if __name__ == "__main__":

    main()