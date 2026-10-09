# Mini Project Pengolahan Citra Digital: OCR Nomor Ijazah dan Deteksi Tanda Tangan

Program ini menjalankan dua tugas utama:

1. Membaca nomor ijazah dari gambar menggunakan OCR (Tesseract).
2. Memperkirakan apakah area gambar tanda tangan berisi goresan/tinta tanda tangan (`PRESENT`) atau tidak (`ABSENT`).
3. Membandingkan metode enhancement berdasarkan Character Error Rate (CER), jika teks nomor ijazah yang benar (ground truth) disediakan.

> **Penting:** gambar di folder `input/Nomor_Ijazah/` dan `input/Tanda_Tangan/` harus berupa crop area yang relevan. Program ini tidak otomatis memotong area dari ijazah penuh. Deteksi tanda tangan berbasis rasio tinta, bukan verifikasi keaslian tanda tangan.

## 1. Struktur Folder

Pastikan susunan proyek seperti berikut:

```text
mini_project_integrasi_ijazah/
├── main.py
├── requirements.txt
├── input/
│   ├── Nomor_Ijazah/
│   │   ├── nomor_ijazah_1.jpg
│   │   └── nomor_ijazah_2.jpg
│   └── Tanda_Tangan/
│       ├── tanda_tangan_1.jpg
│       └── tanda_tangan_2.jpg
└── output/                       # dibuat otomatis saat program berjalan
    ├── nomor_ijazah/
    ├── tanda_tangan/
    ├── hasil_ocr_cer.csv
    ├── hasil_deteksi_tanda_tangan.csv
    └── ringkasan_cer_per_metode.csv
```

Nama file gambar bebas. Format yang didukung: JPG, JPEG, PNG, BMP, TIF, dan TIFF. Letakkan gambar langsung di dalam folder masing-masing, bukan di subfolder tambahan.

## 2. Persyaratan

- Python 3.9 atau lebih baru disarankan.
- Tesseract OCR harus diinstal terpisah dari Python.
- Terminal PowerShell atau terminal VS Code.

### Instal Tesseract OCR di Windows

1. Instal Tesseract OCR untuk Windows.
2. Jika program tidak menemukannya secara otomatis, catat lokasi `tesseract.exe`. Lokasi yang umum adalah:

   ```text
   C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

3. Jika Tesseract terpasang di lokasi lain, gunakan argumen `--tesseract-path` saat menjalankan program (lihat contoh di bawah).

## 3. Instalasi Library Python

Buka VS Code, pilih **File → Open Folder**, lalu buka folder proyek yang berisi `main.py`.

Buka terminal (**Terminal → New Terminal**) dan pastikan terminal berada di folder proyek. Jalankan:

```powershell
python --version
```

Kemudian instal dependensi:

```powershell
pip install -r requirements.txt
```

Jika perintah `python` tidak dikenali, coba:

```powershell
py --version
py -m pip install -r requirements.txt
```

## 4. Menyiapkan Gambar Input

- Masukkan crop yang hanya berisi nomor ijazah ke `input/Nomor_Ijazah/`.
- Masukkan crop area tanda tangan yang ingin diperiksa ke `input/Tanda_Tangan/`.
- Untuk deteksi tanda tangan yang lebih baik, crop area tanda tangan sedekat mungkin, tetapi jangan sampai memotong goresan tanda tangan.
- Hindari memasukkan seluruh halaman ijazah ke folder tanda tangan karena teks, foto, stempel, dan elemen lain dapat dianggap sebagai tinta.

## 5. Menjalankan Program

### A. Menjalankan tanpa menghitung CER

```powershell
python main.py
```

Program akan menjalankan OCR dan deteksi tanda tangan. Kolom CER akan kosong karena teks acuan belum diberikan.

### B. Menjalankan dengan satu nomor acuan

Jika semua gambar nomor ijazah yang diuji memiliki nomor yang sama, gunakan:

```powershell
python main.py --ground-truth "571012022000056"
```

Ganti angka tersebut dengan nomor ijazah yang benar untuk gambar yang diuji. Jangan gunakan contoh nomor ini jika tidak sesuai dengan gambar input.

### C. Jika setiap gambar memiliki nomor berbeda

Buat file `ground_truth.csv` di folder proyek dengan isi seperti berikut:

```csv
filename,ground_truth
nomor_ijazah_1.jpg,571012022000056
nomor_ijazah_2.jpg,571012022000123
```

Ganti nama file dan nomor contoh sesuai gambar masing-masing, lalu jalankan:

```powershell
python main.py --ground-truth-csv ground_truth.csv
```

Nama pada kolom `filename` harus sama persis dengan nama file di `input/Nomor_Ijazah/`.

### D. Menentukan lokasi Tesseract secara manual

Jika Tesseract tidak ditemukan otomatis:

```powershell
python main.py --tesseract-path "C:\Program Files\Tesseract-OCR\tesseract.exe" --ground-truth "NOMOR_IJAZAH_YANG_BENAR"
```

Sesuaikan lokasi `tesseract.exe` dan teks acuan.

### E. Memilih metode threshold untuk deteksi tanda tangan

Metode default adalah Otsu. Untuk adaptive threshold:

```powershell
python main.py --threshold adaptive
```

Untuk mengubah ambang rasio tinta:

```powershell
python main.py --min-ink-ratio 0.015
```

Ambang ini perlu disesuaikan dan dievaluasi pada crop yang digunakan. Jangan menganggap nilai default selalu optimal.

## 6. Memahami Hasil

Semua hasil disimpan ke folder `output/`.

| File | Isi |
|---|---|
| `hasil_ocr_cer.csv` | Hasil OCR setiap gambar dengan metode `original`, `clahe`, dan `contrast_stretch`, termasuk CER jika ground truth tersedia. |
| `ringkasan_cer_per_metode.csv` | Rata-rata CER per metode enhancement. |
| `hasil_deteksi_tanda_tangan.csv` | Status `PRESENT`/`ABSENT`, rasio tinta, dan parameter threshold. |
| `nomor_ijazah/` | Gambar yang diproses untuk OCR. |
| `tanda_tangan/` | Hasil thresholding dan morphology untuk pemeriksaan visual. |

### Menentukan enhancement terbaik dengan CER

- **CER (Character Error Rate)** mengukur proporsi kesalahan karakter OCR dibandingkan teks acuan.
- **CER lebih rendah berarti lebih baik**; CER `0.0` atau `0%` berarti teks OCR sama dengan teks acuan setelah normalisasi.
- Bandingkan nilai `average_cer_percent` dalam `ringkasan_cer_per_metode.csv`.
- Metode dengan CER rata-rata terendah pada kumpulan gambar pengujian adalah metode terbaik untuk kumpulan tersebut. Hasil bisa berbeda untuk kumpulan gambar lain.
- Jika ground truth tidak diberikan, CER tidak dihitung sehingga metode terbaik belum bisa ditentukan secara objektif.

## 7. Metode yang Digunakan

1. **Grayscale:** gambar nomor diubah menjadi citra keabuan.
2. **Enhancement:** tiga versi dibandingkan: gambar asli (`original`), CLAHE, dan contrast stretching.
3. **Resize:** gambar diperbesar 3 kali dengan interpolasi bicubic sebelum OCR.
4. **OCR Tesseract:** pengenalan karakter menggunakan konfigurasi satu baris teks (`--psm 7`) dan whitelist huruf/angka serta `/` dan `-`.
5. **Evaluasi CER:** hasil OCR dibandingkan dengan ground truth menggunakan jarak edit karakter.
6. **Deteksi tanda tangan:** grayscale, Gaussian blur, threshold Otsu atau adaptive, operasi morphology, lalu hitung rasio piksel tinta untuk menghasilkan `PRESENT` atau `ABSENT`.

Deteksi berbasis rasio tinta adalah baseline sederhana. Ia dapat keliru jika crop berisi stempel, teks, garis, atau latar yang bertekstur. Untuk evaluasi akademik, cocokkan hasil dengan label manual dan laporkan keterbatasannya.

## 8. Troubleshooting

**`Tidak ada gambar di input\Nomor_Ijazah`**
- Pastikan folder bernama persis `Nomor_Ijazah` (huruf besar/kecil sebaiknya disamakan).
- Pastikan gambar berada langsung di folder tersebut dan memiliki ekstensi yang didukung.

**`Tesseract OCR belum ditemukan`**
- Instal Tesseract OCR.
- Jalankan ulang dengan `--tesseract-path` ke lokasi `tesseract.exe`.

**`pytesseract belum ada` atau error modul `cv2`**
- Jalankan `pip install -r requirements.txt` pada environment Python yang digunakan untuk menjalankan `main.py`.

**CER kosong**
- Jalankan dengan `--ground-truth` jika semua nomor sama, atau `--ground-truth-csv` jika nomornya berbeda.

**Deteksi tanda tangan salah**
- Periksa apakah crop hanya mencakup area tanda tangan.
- Bandingkan file threshold dan morphology di `output/tanda_tangan/`.
- Uji nilai `--min-ink-ratio` yang berbeda dan validasi hasil secara manual.

## 9. Contoh Alur Singkat

```powershell
cd "C:\path\ke\mini_project_integrasi_ijazah"
pip install -r requirements.txt
python main.py --ground-truth "NOMOR_IJAZAH_YANG_BENAR"
```

Pastikan gambar input sudah diletakkan pada folder yang benar sebelum menjalankan perintah.
