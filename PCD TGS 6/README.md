1. Clone repository
Download atau clone repository dari GitHub, kemudian buka folder project menggunakan Visual Studio Code atau terminal.

2. Install library yang dibutuhkan
Jalankan perintah berikut pada terminal:
pip install opencv-python numpy pandas

3. Siapkan dataset
Letakkan gambar yang akan diuji ke dalam folder data/.
Gambar yang digunakan merupakan area tanda tangan rektor yang sudah di-crop dari citra ijazah.

4. Jalankan proses pengolahan citra
Jalankan program:

python signature_detection.py

Program akan melakukan proses grayscale, Global Thresholding, Otsu Thresholding, Adaptive Thresholding, Opening, Closing, serta menghitung jumlah piksel foreground.

5. Jalankan proses klasifikasi

Setelah proses pengolahan citra selesai, jalankan:

python signature_classification.py

Program akan menentukan apakah tanda tangan terdeteksi sebagai SIGNATURE PRESENT atau SIGNATURE ABSENT.

6. Lihat hasil

Hasil pengolahan citra dan segmentasi terdapat pada folder results/, sedangkan hasil klasifikasi terdapat pada:

results/classification/

Data hasil perhitungan segmentasi disimpan dalam segmentation_results.csv, sedangkan hasil klasifikasi disimpan dalam classification_results.csv.