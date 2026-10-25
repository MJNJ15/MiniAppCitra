# ️ MiniAppCitra

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0.0-white?logo=opencv&logoColor=white)](https://opencv.org/)

---

## 📖 Deskripsi Singkat (About)

**MiniAppCitra** adalah aplikasi desktop edukatif yang dirancang untuk memvisualisasikan dan mengimplementasikan berbagai algoritma pengolahan citra secara *real-time*. Proyek ini dikembangkan sebagai alat bantu pembelajaran untuk mata kuliah Pengolahan Citra Digital di tingkat universitas, memungkinkan mahasiswa untuk memahami konsep transformasi piksel, filtering, konvolusi, dan transformasi geometrik melalui antarmuka grafis yang interaktif.

Aplikasi ini menyelesaikan masalah umum dalam pembelajaran pengolahan citra, yaitu kesulitan memvisualisasikan efek dari berbagai algoritma secara langsung. Dengan dukungan fitur webcam *real-time*, pengguna dapat melihat hasil pengolahan citra secara instan tanpa perlu memuat ulang gambar, sehingga proses eksplorasi dan eksperimen menjadi lebih cepat dan intuitif.

---

## ✨ Fitur Utama (Key Features)

### 🎨 15 Metode Pengolahan Citra
- **Transformasi Titik Piksel:** Thresholding, Thresholding Double, Grayscale, Negative, Brightness, Contrast
- **Filtering & Konvolusi:** Noise (Gaussian & Salt-Pepper), Edge Detection (Canny & Sobel), Histogram Equalization, Emboss, Sharpening, Smoothing, Custom Convolution 3x3
- **Transformasi Geometrik:** Mirroring (Horizontal/Vertical/Both), Rotation (0°-360°)

### Webcam Real-Time
- Pengolahan citra langsung dari kamera webcam tanpa perlu memuat file
- Mode *raw feed* untuk melihat video mentah di panel kiri
- Ganti metode secara dinamis tanpa menghentikan webcam

### 📊 Histogram Real-Time
- Visualisasi distribusi intensitas piksel secara *live*
- Update otomatis setiap 5 frame untuk performa optimal
- Mendukung citra berwarna (RGB) dan grayscale

### Antarmuka Intuitif
- Panel input dinamis yang berubah sesuai metode yang dipilih
- Tombol Reset untuk mengembalikan aplikasi ke kondisi awal
- Status bar informatif yang menampilkan resolusi citra dan progres pemrosesan
- Desain modern dengan Qt Fusion Style

### 💾 Manajemen File
- Buka citra dari berbagai format (JPG, PNG, BMP)
- Simpan hasil pengolahan ke format yang diinginkan
- Error handling yang komprehensif

---

## 🛠️ Tech Stack / Teknologi

| Komponen | Teknologi | Versi Minimum | Fungsi |
|----------|-----------|---------------|--------|
| **Bahasa Pemrograman** | Python | 3.10+ | Logika aplikasi dan pemrosesan data |
| **GUI Framework** | PySide6 (Qt for Python) | 6.5.0+ | Antarmuka pengguna desktop |
| **Image Processing** | OpenCV | 4.8.0+ | Operasi pengolahan citra dan akses webcam |
| **Array Manipulation** | NumPy | 1.24.0+ | Manipulasi matriks piksel dan perhitungan numerik |
| **Visualization** | Matplotlib | 3.7.0+ | Render histogram embedded di Qt |
| **Threading** | QThread (PySide6) | - | Pemrosesan webcam di background tanpa freeze UI |

---

## 📁 Struktur Direktori (Project Structure)
```
pengolahan_citra/
│
├── main.py # Entry point aplikasi
├── requirements.txt # Daftar dependensi Python
├── README.md # Dokumentasi proyek (file ini)
├── LICENSE # Informasi lisensi
│
├── ui/ # Modul antarmuka pengguna
│ ├── init.py
│ ├── main_window.py # Window utama & layout
│ ├── image_panel.py # Panel gambar (QLabel + auto-scale)
│ ├── method_panel.py # Panel pilihan metode (15 radio buttons)
│ ├── control_panel.py # Panel kontrol (Proses, Webcam, Reset, Input)
│ └── histogram_widget.py # Widget histogram (Matplotlib embedded)
│
├── processors/ # Modul logika pengolahan citra
│ ├── init.py
│ ├── base_processor.py # Kelas abstrak dasar untuk semua processor
│ ├── thresholding.py # Thresholding & Double Thresholding
│ ├── grayscale.py # Konversi ke grayscale
│ ├── negative.py # Inversi warna (negative)
│ ├── brightness.py # Penyesuaian kecerahan
│ ├── contrast.py # Penyesuaian kontras
│ ├── noise.py # Injeksi noise (Gaussian, Salt & Pepper)
│ ├── edge_detection.py # Deteksi tepi (Canny, Sobel)
│ ├── equalization.py # Histogram Equalization
│ ├── emboss.py # Filter emboss
│ ├── sharpening.py # Filter penajaman
│ ├── smoothing.py # Filter penghalusan (blur)
│ ├── convolution.py # Konvolusi kustom 3x3
│ ├── mirroring.py # Pencerminkan citra
│ └── rotation.py # Rotasi citra
│
└── utils/ # Modul utilitas
├── init.py
├── image_utils.py # Konversi cv2 ↔ QPixmap (BGR ↔ RGB)
├── constants.py # Konstanta global & konfigurasi
└── webcam_worker.py # QThread untuk pembacaan webcam real-time
```

---

## 📦 Prasyarat & Instalasi (Prerequisites & Installation)

### Prasyarat Sistem
- **Python 3.10** atau lebih baru ([Download Python](https://www.python.org/downloads/))
- **Webcam** (opsional, untuk fitur real-time)
- **Git** (opsional, untuk cloning repositori)

### Langkah Instalasi

#### 1. Clone Repositori
```bash
git clone https://github.com/MJNJ15/MiniAppCitra.git
cd MiniAppCitra
```

#### 2. Buat Virtual Environmen (Direkomendasikan)
# Windows
```bash
python -m venv venv
venv\Scripts\activate
```

# Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

#### 4. Verifikasi Instalasi
```bash
python -c "import cv2, PySide6, numpy, matplotlib; print('Semua dependensi terinstal dengan baik!')"
```

---

## 🚀 Cara Penggunaan (Usage)

### Menjalankan Aplikasi
```bash
python main.py
```

### Alur Kerja Dasar

#### Mode 1: Pengolahan Citra dari File
1. Klik tombol 📂 Buka di toolbar
2. Pilih file gambar (JPG, PNG, atau BMP)
3. Pilih metode pengolahan dari panel METODE (kiri bawah)
4. Sesuaikan parameter di panel INPUT NILAI (kanan bawah)
5. Klik tombol ▶ Proses untuk melihat hasil di panel kanan
6. Klik 💾 Simpan untuk menyimpan citra hasil

#### Mode 2: Pengolahan Citra Real-Time (Webcam)
1. Klik tombol 📷 Webcam untuk mengaktifkan kamera
2. Panel kiri akan menampilkan video mentah secara real-time
3. Pilih metode pengolahan dari panel METODE
4. Sesuaikan parameter di panel INPUT NILAI
5. Klik ▶ Proses untuk menerapkan efek secara live di panel kanan
6. Ganti metode kapan saja tanpa perlu mematikan webcam
7. Klik ⏹ Stop Webcam untuk menghentikan kamera

#### Mode 3: Reset Aplikasi
- Klik tombol **Reset** untuk:
    - Menghapus pilihan metode
    - Mengosongkan panel input
    - Menghentikan proses (jika webcam aktif, webcam tetap menyala dalam mode raw)

### Contoh Penggunaan Metode
| Metode | Parameter | Deskripsi |
|--------|-----------|-----------|
| Thresholding | Threshold: 128 | Mengubah citra menjadi biner (hitam-putih) |
| Edge Detection | Metode: Canny | Mendeteksi tepi objek dalam citra |
| Noise | Tipe: Gaussian, Amount: 0.3 | Menambahkan derau untuk simulasi gangguan |
| Smoothing | Tipe: Gaussian, Kernel: 5 | Menghaluskan citra untuk mengurangi noise |
| Rotation | Sudut: 45° | Memutar citra sebesar 45 derajat |