# ️ MiniAppCitra

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0.0-white?logo=opencv&logoColor=white)](https://opencv.org/)

---

## 📖 Deskripsi Singkat (About)

**MiniAppCitra** adalah aplikasi desktop edukatif yang memvisualisasikan dan mengimplementasikan berbagai algoritma pengolahan citra secara *real-time*. Proyek ini dikembangkan sebagai alat bantu pembelajaran untuk mata kuliah Pengolahan Citra Digital, memungkinkan mahasiswa memahami konsep transformasi piksel, filtering, konvolusi, dan transformasi geometrik melalui antarmuka grafis interaktif.

Aplikasi ini menyelesaikan masalah umum dalam pembelajaran: kesulitan memvisualisasikan efek berbagai algoritma secara langsung. Dengan dukungan webcam *real-time*, hasil pengolahan terlihat instan tanpa perlu memuat ulang gambar, sehingga eksplorasi menjadi lebih cepat dan intuitif.

> Diuji pada Python 3.13 · PySide6 6.11 · OpenCV 5.0 · NumPy 2.x

---

## ✨ Fitur Utama (Key Features)

### 🎨 15 Metode Pengolahan Citra
- **Transformasi Titik Piksel:** Thresholding, Thresholding Double, Grayscale, Negative, Brightness, Contrast
- **Filtering & Konvolusi:** Noise (Gaussian & Salt-Pepper), Edge Detection (Canny & Sobel), Histogram Equalization, Emboss, Sharpening, Smoothing, Custom Convolution 3x3
- **Transformasi Geometrik:** Mirroring (Horizontal/Vertical/Both), Rotation (0°-360°)

### 🔀 Mode Pemilihan Metode
- **Tunggal** — satu metode dengan satu panel parameter (perilaku klasik)
- **Multiple** — pilih hingga **5 metode sekaligus**; hasil diterapkan **berurutan sesuai urutan klik** (output metode pertama menjadi input metode berikutnya), tersedia di mode statis maupun webcam

### 📷 Webcam Real-Time
- Pengolahan citra langsung dari kamera tanpa perlu memuat file
- Mode *raw feed* di panel kiri; ganti metode secara dinamis tanpa menghentikan webcam
- **Histogram real-time** di kedua panel dengan sumbu berlabel (nilai piksel 0–255 & jumlah piksel) serta skala log otomatis untuk citra biner/tepi agar lonjakan terlihat

### 📸 Ambil Foto
- Simpan **hasil pemrosesan** webcam langsung ke file (PNG/JPG/BMP)
- Menampilkan notifikasi jika belum ada pemrosesan aktif

### 🎨 Antarmuka Modern
- Tema gelap kustom berbasis Qt Style Sheets (QSS), tombol berperan dengan state *hover/pressed*
- Panel input dinamis (spinbox/slider/combo/kernel 3x3) per metode terpilih
- Status bar informatif (resolusi citra, progres, konfirmasi simpan)

### 💾 Manajemen File
- Buka citra (JPG, PNG, BMP) dan simpan hasil pengolahan
- Error handling yang komprehensif

---

## 🛠️ Tech Stack / Teknologi

| Komponen | Teknologi | Versi Minimum | Fungsi |
|----------|-----------|---------------|--------|
| **Bahasa Pemrograman** | Python | 3.10+ | Logika aplikasi dan pemrosesan data |
| **GUI Framework** | PySide6 (Qt for Python) | 6.5.0+ | Antarmuka pengguna desktop |
| **Image Processing** | OpenCV | 4.8.0+ | Operasi pengolahan citra dan akses webcam |
| **Array Manipulation** | NumPy | 1.24.0+ | Manipulasi matriks piksel dan perhitungan numerik |
| **Rendering Histogram** | QPainter (Qt) | - | Render histogram real-time berperforma tinggi (tanpa Matplotlib) |
| **Threading** | QThread (PySide6) | - | Pemrosesan webcam di background tanpa freeze UI |

---

## 📁 Struktur Direktori (Project Structure)

```
MiniAppCitra/
│
├── main.py                  # Entry point aplikasi
├── requirements.txt         # Daftar dependensi Python
├── README.md                # Dokumentasi proyek (file ini)
├── LICENSE                  # Informasi lisensi
│
├── ui/                      # Modul antarmuka pengguna
│   ├── main_window.py       # Window utama, layout & orkestrasi
│   ├── image_panel.py       # Panel gambar (QLabel + auto-scale + histogram)
│   ├── method_panel.py      # Panel pilihan metode (Tunggal/Multiple)
│   ├── control_panel.py     # Panel kontrol (Proses, Webcam, Ambil Foto, Reset, Input)
│   ├── histogram_widget.py  # Widget histogram QPainter (real-time)
│   └── styles.py            # Tema modern gelap (QSS)
│
├── processors/              # Modul logika pengolahan citra
│   ├── __init__.py
│   ├── base_processor.py    # Kelas abstrak dasar untuk semua processor
│   ├── thresholding.py      # Thresholding & Double Thresholding
│   ├── grayscale.py         # Konversi ke grayscale
│   ├── negative.py          # Inversi warna (negative)
│   ├── brightness.py        # Penyesuaian kecerahan
│   ├── contrast.py          # Penyesuaian kontras
│   ├── noise.py             # Injeksi noise (Gaussian, Salt & Pepper)
│   ├── edge_detection.py    # Deteksi tepi (Canny, Sobel)
│   ├── equalization.py      # Histogram Equalization
│   ├── emboss.py            # Filter emboss
│   ├── sharpening.py        # Filter penajaman
│   ├── smoothing.py         # Filter penghalusan (blur)
│   ├── convolution.py       # Konvolusi kustom 3x3
│   ├── mirroring.py         # Pencerminan citra
│   └── rotation.py          # Rotasi citra
│
└── utils/                   # Modul utilitas
    ├── __init__.py
    ├── image_utils.py       # Konversi cv2 → QPixmap (BGR → RGB)
    ├── constants.py         # Konstanta global & konfigurasi
    └── webcam_worker.py     # QThread untuk pembacaan webcam real-time
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

#### 2. Buat Virtual Environment (Direkomendasikan)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
```

#### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

#### 4. Verifikasi Instalasi
```bash
python -c "import cv2, PySide6, numpy; print('Semua dependensi terinstal dengan baik!')"
```

---

## 🚀 Cara Penggunaan (Usage)

### Menjalankan Aplikasi
```bash
python main.py
```

### Mode 1: Pengolahan Citra dari File
1. Klik tombol 📂 Buka di toolbar
2. Pilih file gambar (JPG, PNG, atau BMP)
3. Pilih metode (mode **Tunggal** atau **Multiple**) dari panel METODE
4. Sesuaikan parameter di panel INPUT NILAI
5. Klik tombol ▶ Proses — hasil tampil di panel kanan beserta histogramnya
6. Klik 💾 Simpan untuk menyimpan citra hasil

### Mode 2: Pengolahan Citra Real-Time (Webcam)
1. Klik tombol 📷 Webcam; panel kiri menampilkan video mentah + histogram real-time
2. Pilih metode (Tunggal/Multiple), sesuaikan parameter, klik ▶ Proses — hasil diterapkan live di panel kanan
3. Tombol 📸 Ambil Foto muncul; klik untuk menyimpan **frame hasil proses** ke file (muncul notifikasi bila belum ada pemrosesan aktif)
4. Klik ⏹ Stop Webcam untuk menghentikan kamera

### Mode 3: Reset Aplikasi
- Klik **Reset**: menghapus pilihan metode, mengosongkan input & hasil; saat webcam aktif, webcam tetap menyala dalam mode raw

### Contoh Penggunaan Metode
| Metode | Parameter | Deskripsi |
|--------|-----------|-----------|
| Thresholding | Threshold: 128 | Mengubah citra menjadi biner (hitam-putih) |
| Edge Detection | Metode: Canny | Mendeteksi tepi objek dalam citra |
| Noise | Tipe: Gaussian, Amount: 0.3 | Menambahkan derau untuk simulasi gangguan |
| Smoothing | Tipe: Gaussian, Kernel: 5 | Menghaluskan citra untuk mengurangi noise |
| Rotation | Sudut: 45° | Memutar citra sebesar 45 derajat |
| Grayscale → Thresholding | (rantai mode Multiple) | Contoh rantai dua metode yang diterapkan berurutan |
