import argparse
import csv
import re
import shutil
from pathlib import Path

import cv2
import numpy as np

try:
    import pytesseract
except ImportError:
    pytesseract = None

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
METHODS = ("original", "clahe", "contrast_stretch")


def norm(text):
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


def calculate_cer(reference, hypothesis):
    """CER = (substitusi + penghapusan + penyisipan) / jumlah karakter referensi."""
    ref, hyp = norm(reference), norm(hypothesis)
    if not ref:
        return None
    prev = list(range(len(hyp) + 1))
    for i, a in enumerate(ref, 1):
        cur = [i]
        for j, b in enumerate(hyp, 1):
            cur.append(min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (a != b)))
        prev = cur
    return prev[-1] / len(ref)


def enhance(gray, method):
    if method == "original":
        return gray.copy()
    if method == "clahe":
        return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    low, high = np.percentile(gray, (2, 98))
    if high <= low:
        return gray.copy()
    out = (gray.astype(np.float32) - low) * 255.0 / (high - low)
    return np.clip(out, 0, 255).astype(np.uint8)


def image_files(folder):
    folder = Path(folder)
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS) if folder.exists() else []


def load_ground_truth_csv(path):
    result = {}
    if not path:
        return result
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"filename", "ground_truth"}.issubset(reader.fieldnames):
            raise ValueError("CSV ground truth wajib memiliki kolom filename,ground_truth")
        for row in reader:
            result[Path(row["filename"]).name] = row["ground_truth"].strip()
    return result


def setup_tesseract(path):
    if pytesseract is None:
        raise RuntimeError("pytesseract belum ada. Jalankan pip install -r requirements.txt")
    if path:
        pytesseract.pytesseract.tesseract_cmd = path
    elif shutil.which("tesseract") is None:
        default = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        if Path(default).exists():
            pytesseract.pytesseract.tesseract_cmd = default
        else:
            raise RuntimeError(
                'Tesseract OCR belum ditemukan. Instal Tesseract, atau tambahkan '
                '--tesseract-path "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"'
            )


def ocr(gray):
    enlarged = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    config = "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-"
    return pytesseract.image_to_string(enlarged, config=config).strip(), enlarged


def detect_signature(image, threshold="otsu", min_ink_ratio=0.015):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    if threshold == "otsu":
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        block = min(31, min(gray.shape) if min(gray.shape) % 2 else min(gray.shape) - 1)
        block = max(3, block)
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) if block < 3 else (None, cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, 10))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
    ratio = float(np.count_nonzero(cleaned)) / cleaned.size
    return ("PRESENT" if ratio >= min_ink_ratio else "ABSENT"), ratio, binary, cleaned


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="OCR nomor ijazah + deteksi tanda tangan.")
    parser.add_argument("--input-dir", default="input", help="Folder input yang berisi Nomor_Ijazah dan Tanda_Tangan")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--ground-truth", default="", help="Nomor ijazah acuan jika semua gambar memakai nomor sama")
    parser.add_argument("--ground-truth-csv", default="", help="CSV dengan kolom filename,ground_truth untuk nomor berbeda")
    parser.add_argument("--tesseract-path", default="", help="Lokasi tesseract.exe jika tidak terdeteksi otomatis")
    parser.add_argument("--threshold", choices=["otsu", "adaptive"], default="otsu")
    parser.add_argument("--min-ink-ratio", type=float, default=0.015)
    args = parser.parse_args()

    root = Path(args.input_dir)
    number_dir = root / "Nomor_Ijazah"
    signature_dir = root / "Tanda_Tangan"
    out = Path(args.output_dir)
    number_out, signature_out = out / "nomor_ijazah", out / "tanda_tangan"
    number_out.mkdir(parents=True, exist_ok=True)
    signature_out.mkdir(parents=True, exist_ok=True)

    numbers = image_files(number_dir)
    signatures = image_files(signature_dir)
    if not numbers:
        raise SystemExit(f"Tidak ada gambar di {number_dir}. Masukkan gambar crop nomor ijazah ke folder tersebut.")
    if not signatures:
        print(f"PERINGATAN: tidak ada gambar tanda tangan di {signature_dir}.")

    try:
        setup_tesseract(args.tesseract_path)
        truth_map = load_ground_truth_csv(args.ground_truth_csv)
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        raise SystemExit(str(e))

    ocr_rows = []
    for path in numbers:
        img = cv2.imread(str(path))
        if img is None:
            print("Gambar gagal dibaca:", path)
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gt = truth_map.get(path.name, args.ground_truth.strip())
        for method in METHODS:
            processed = enhance(gray, method)
            text, enlarged = ocr(processed)
            score = calculate_cer(gt, text) if gt else None
            cv2.imwrite(str(number_out / f"{path.stem}_{method}.png"), enlarged)
            ocr_rows.append({
                "filename": path.name, "method": method, "ocr_result": text,
                "ground_truth": gt, "cer": "" if score is None else round(score, 6),
                "cer_percent": "" if score is None else round(score * 100, 2)
            })
    write_csv(out / "hasil_ocr_cer.csv", ocr_rows,
              ["filename", "method", "ocr_result", "ground_truth", "cer", "cer_percent"])

    signature_rows = []
    for path in signatures:
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            print("Gambar gagal dibaca:", path)
            continue
        status, ratio, binary, cleaned = detect_signature(img, args.threshold, args.min_ink_ratio)
        cv2.imwrite(str(signature_out / f"{path.stem}_threshold.png"), binary)
        cv2.imwrite(str(signature_out / f"{path.stem}_morphology.png"), cleaned)
        signature_rows.append({
            "filename": path.name, "status": status, "ink_ratio": round(ratio, 6),
            "threshold": args.threshold, "min_ink_ratio": args.min_ink_ratio
        })
    write_csv(out / "hasil_deteksi_tanda_tangan.csv", signature_rows,
              ["filename", "status", "ink_ratio", "threshold", "min_ink_ratio"])

    summary = []
    for method in METHODS:
        vals = [float(r["cer"]) for r in ocr_rows if r["method"] == method and r["cer"] != ""]
        summary.append({
            "method": method, "average_cer": "" if not vals else round(sum(vals) / len(vals), 6),
            "average_cer_percent": "" if not vals else round(sum(vals) / len(vals) * 100, 2),
            "images_evaluated": len(vals)
        })
    write_csv(out / "ringkasan_cer_per_metode.csv", summary,
              ["method", "average_cer", "average_cer_percent", "images_evaluated"])

    print("\\n=== RINGKASAN ===")
    print("Gambar nomor ijazah diproses:", len(numbers))
    print("Gambar tanda tangan diproses:", len(signature_rows))
    print("Hasil OCR:", out / "hasil_ocr_cer.csv")
    print("Hasil deteksi tanda tangan:", out / "hasil_deteksi_tanda_tangan.csv")
    print("Ringkasan CER:", out / "ringkasan_cer_per_metode.csv")
    valid = [r for r in summary if r["average_cer"] != ""]
    if valid:
        best = min(valid, key=lambda r: float(r["average_cer"]))
        print(f"Metode dengan CER rata-rata terendah: {best['method']} ({best['average_cer_percent']}%)")
    else:
        print("CER belum dihitung. Tambahkan --ground-truth atau --ground-truth-csv.")
    for r in signature_rows:
        print(f"Tanda tangan {r['filename']}: {r['status']} (rasio tinta={r['ink_ratio']})")
    print("Catatan: deteksi tanda tangan berdasarkan rasio tinta; periksa hasil visual.")


if __name__ == "__main__":
    main()
