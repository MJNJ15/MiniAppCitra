# 📘 Penjelasan Kode Aplikasi — MiniAppCitra

> Dokumen ini menjelaskan proyek secara umum dan teknis berdasarkan kondisi kode terakhir
> (branch fitur-ui-modern). Diuji pada **Python 3.13 · PySide6 6.11 · OpenCV 5.0 · NumPy 2.x**.

---

## Daftar Isi

1. [Ide Proyek](#1-ide-proyek)
2. [Alur Proyek](#2-alur-proyek)
3. [Alur Kode Program](#3-alur-kode-program)
4. [Alur Kode Fungsi](#4-alur-kode-fungsi)
5. [Library / Dependency yang Digunakan](#5-library--dependency-yang-digunakan)
6. [Penjelasan Metode Secara Teori](#6-penjelasan-metode-secara-teori)
7. [Dokumentasi Library / Dependency / Fungsi](#7-dokumentasi-library--dependency--fungsi)

---

## 1. Ide Proyek

**MiniAppCitra** adalah aplikasi desktop edukatif untuk **Pengolahan Citra Digital**. Ide utamanya:

- **Visualisasi langsung**: mahasiswa sering kesulitan membayangkan efek algoritma (thresholding, edge detection, blur, dsb.). Aplikasi ini menampilkan hasil secara instan, baik dari file gambar maupun langsung dari webcam.
- **Eksperimen cepat**: karena memakai webcam *real-time*, pengguna bisa mengubah metode/parameter dan langsung melihat perubahannya tanpa memuat ulang gambar.
- **Pembelajaran bertingkat**: 15 metode dikelompokkan ke 3 kategori besar — transformasi titik piksel, filtering/konvolusi, dan transformasi geometrik — sehingga konsep kuliah (piksel, kernel, histogram, geometri) bisa dipraktikkan satu per satu.
- **Dua mode pemilihan**: mode **Tunggal** (satu metode) dan **Multiple** (hingga 5 metode yang diterapkan berurutan), agar pengguna memahami bagaimana hasil suatu metode menjadi masukan metode berikutnya.

---

## 2. Alur Proyek

Alur penggunaan dari sudut pandang pengguna:

```
Buka aplikasi (python main.py)
        │
        ▼
┌─ Pilih sumber citra ──────────────────────────────┐
│ A. 📂 Buka gambar (JPG/PNG/BMP)                  │
│ B. 📷 Aktifkan Webcam (panel kiri = raw feed)    │
└──────────────────────┬───────────────────────────┘
                       ▼
┌─ Pilih metode (panel METODE) ─────────────────────┐
│ Mode TUNGGAL : satu metode                        │
│ Mode MULTIPLE : centang ≥1 (maks 5), urutan klik  │
└──────────────────────┬───────────────────────────┘
                       ▼
        Panel INPUT NILAI menyesuaikan metode
        (spinbox / slider / combo / kernel 3x3)
                       ▼
              Klik ▶ PROSES
                       ▼
┌──────────────────────┴───────────────────────────┐
│ Statis : proses rantai → panel kanan + histogram  │
│ Webcam : processor dikirim ke worker → live       │
└──────────────────────┬───────────────────────────┘
                       ▼
   Lihat hasil + histogram (nilai & jumlah piksel)
                       ▼
   💾 Simpan hasil  |  📸 Ambil Foto (webcam → simpan hasil proses ke file)
                       ▼
   🔄 Reset → kembali ke kondisi awal
```

Titik-titik kunci alur:

- Pemilihan metode **membangun ulang** panel input sesuai parameter metode tersebut.
- Tombol **Proses** bersifat cerdas: jika webcam aktif, metode diterapkan di thread worker secara live; jika tidak, citra statis diproses.
- **Histogram** selalu mengikuti citra yang tampil: raw di panel kiri, hasil di panel kanan.

---

## 3. Alur Kode Program

### 3.1 Arsitektur lapisan

```
main.py  →  ui/  ⇄  processors/ , utils/
```

| Lapisan | File | Peran |
|---|---|---|
| Entry point | `main.py` | Membuat `QApplication`, menerapkan style/protema, menjalankan `MainWindow` |
| UI | `ui/main_window.py` | Orkestrator: merangkai panel, menerima sinyal, memutuskan alur proses |
| UI | `ui/method_panel.py` | Pemilihan metode (Tunggal/Multiple) |
| UI | `ui/control_panel.py` | Tombol aksi + panel input parameter dinamis |
| UI | `ui/image_panel.py` | Menampilkan citra (resize otomatis) + histogram |
| UI | `ui/histogram_widget.py` | Render histogram QPainter cepat |
| UI | `ui/styles.py` | Tema gelap (QSS) |
| Logika | `processors/` | 15 kelas algoritma, semua mewarisi `BaseProcessor` |
| Utilitas | `utils/image_utils.py` | Konversi OpenCV → QPixmap |
| Utilitas | `utils/constants.py` | Konstanta format file & ukuran jendela |
| Utilitas | `utils/webcam_worker.py` | QThread pembaca webcam real-time |

### 3.2 Alur event / sinyal (signal-driven)

```
MethodPanel.methods_changed ──► ControlPanel.update_methods()
        (membangun widget input per metode)

ControlPanel.process_requested ──► MainWindow._on_process_requested()
        │
        ├─ webcam aktif → workers.set_processors(rantai) → live
        └─ statis      → _process_static_image(rantai) → panel kanan

WebcamWorker.frame_raw_ready ──► panel kiri (raw)
WebcamWorker.frame_processed_ready ──► panel kanan (hasil)
WebcamWorker.hist_raw_ready / hist_processed_ready
        ──► disimpan → QTimer 120ms → _flush_hist_updates() → render
```

### 3.3 Alur webcam (thread)

1. `_start_webcam()` membuat `WebcamWorker` dan menghubungkan sinyal.
2. Worker `run()` membuka `cv2.VideoCapture(0)`, lalu loop:
   - baca frame → kirim `frame_raw_ready` + histogram (tiap 3 frame);
   - jika ada rantai processor → proses berurutan → kirim `frame_processed_ready` + histogram.
3. `stop()` menghentikan loop dan menunggu thread selesai.

### 3.4 Alur pemrosesan statis

1. `_on_process_requested` memvalidasi semua nama metode di `self.processors`.
2. `_process_static_image` menyalin `original_image_np`, lalu untuk tiap metode:
   `result = processor.process(result, **params)`.
3. Hasil akhir ditampilkan di panel kanan + histogram.

---

## 4. Alur Kode Fungsi

### 4.1 `main.py`

| Fungsi | Alur |
|---|---|
| `main()` | Atur kebijakan High-DPI → `QApplication` → `setStyle("Fusion")` → `apply_app_style(app)` → buat & tampilkan `MainWindow` → `sys.exit(app.exec())` |

### 4.2 `ui/main_window.py`

| Fungsi | Alur |
|---|---|
| `__init__` | Inisialisasi state (`original_image_np`, `result_image_np`, state webcam & histogram, tabel processor) → `_init_ui` → `_create_toolbar` → `_connect_signals` |
| `_init_ui` | Layout vertikal: dua panel gambar (kiri/kanan) + dua panel kontrol (metode/input) |
| `_connect_signals` | Menghubungkan sinyal MethodPanel & ControlPanel ke handler |
| `_start_webcam` | Bersihkan pilihan, buat worker, hubungkan sinyal, mulai timer histogram 120 ms, `start()` |
| `_on_process_requested` | Validasi → cabang webcam (set_processors) atau statis |
| `_process_static_image` | Loop rantai processor → tampilkan hasil + histogram |
| `_on_snapshot_requested` | Jika tidak ada processor aktif → notifikasi; jika ada → ambil `snapshot_processed()` → dialog simpan → `cv2.imwrite` |
| `_on_reset_requested` | Bersihkan pilihan/input; saat webcam: bersihkan processor & hasil; statis: bersihkan semua panel |
| `open_image` / `save_image` | Dialog buka/simpan file via `QFileDialog` |
| `closeEvent` | Hentikan webcam sebelum aplikasi ditutup |

### 4.3 `utils/webcam_worker.py`

| Fungsi | Alur |
|---|---|
| `run()` | Buka kamera → loop baca frame → `_emit_raw` & `_emit_processed` → release kamera → sinyal `stopped_signal` |
| `_emit_raw` | Kirim `frame_raw_ready` (+ histogram tiap 3 frame) |
| `_emit_processed` | Jika ada `_active_processors` → proses berantai → simpan `_last_processed_frame` → kirim hasil + histogram |
| `set_processors` / `clear_processor` | Atur / kosongkan rantai processor |
| `snapshot_processed` | Kembalikan salinan frame hasil terakhir |
| `_compute_histogram` | `cv2.calcHist` per channel → `(256, 3)` atau `(256,)` |

### 4.4 `ui/control_panel.py`

| Fungsi | Alur |
|---|---|
| `update_methods` | Bersihkan layout input → untuk tiap metode terpilih buat `QGroupBox` bernomor + widget parameternya |
| `_build_group_inputs` | Percabangan nama metode → spinbox/slider/combo/kernel 3x3 |
| `_add_spinbox` / `_add_doublespinbox` / `_add_slider` / `_add_combobox` | Bangun satu baris input dan daftarkan ke `widgets` entry |
| `_on_process_clicked` | Kumpulkan parameter dari semua group → emit `process_requested` (list dict) |
| `set_webcam_state` | Ubah teks/warna tombol Webcam + visibilitas "Ambil Foto" |
| `_styled_button` | Buat tombol berwarna dengan state hover/pressed |

### 4.5 `ui/method_panel.py`

| Fungsi | Alur |
|---|---|
| `_on_mode_toggled` | Jika mode berubah → `clear_selection()` + atur eksklusivitas QButtonGroup |
| `_on_method_toggled` | Mode Multiple: tambah/hapus dari `_selected_order` (batas MAX_METHODS, nomor urut); Tunggal: ganti pilihan |
| `_refresh_labels` | Beri nomor urut pada label metode terpilih |
| `_emit_selection` | Emit `methods_changed` berisi daftar terurut |
| `clear_selection` | Uncheck semua (lewat non-eksklusif sementara) → emit kosong |

### 4.6 `ui/image_panel.py` & `ui/histogram_widget.py`

- `set_image(pixmap, smooth)`: simpan pixmap → `_update_scaled_image()` (Smooth untuk statis, Fast untuk webcam).
- `HistogramWidget`: `update_histogram_counts(counts)` hanya menyimpan data + `update()`. `paintEvent` menggambar sumbu X (nilai piksel 0–255), sumbu Y (jumlah piksel), dan batang; jika histogram **sparse** (<10% bin terisi, mis. citra biner) otomatis memakai **skala log10** agar lonjakan terlihat.

### 4.7 `utils/image_utils.py`

- `cv2_to_qpixmap(img)`: BGR→RGB, `QImage` (RGB888 / Grayscale8), lalu `QPixmap.fromImage(q_img.copy())` — `copy()` penting agar memori tidak diikat array NumPy.

---

## 5. Library / Dependency yang Digunakan

### `requirements.txt` (kondisi akhir)

```
PySide6>=6.5.0
opencv-python>=4.8.0
numpy>=1.24.0
```

> **Catatan:** `matplotlib` **telah dihapus** — histogram kini dirender dengan QPainter (jauh lebih cepat untuk real-time).

### Ringkasan library

| Library | Versi | Bagian yang dipakai |
|---|---|---|
| **PySide6** | ≥6.5 | `QtWidgets` (QMainWindow, QWidget, QLabel, QPushButton, QGroupBox, QSpinBox, QSlider, QComboBox, QFileDialog, QScrollArea, QButtonGroup, QMessageBox, QToolBar), `QtCore` (Qt, Signal, QThread, QTimer), `QtGui` (QImage, QPixmap, QPainter, QColor, QFont); QSS untuk tema |
| **OpenCV (opencv-python)** | ≥4.8 (diuji 5.0) | I/O (`imread`, `imwrite`, `VideoCapture`), transformasi (`cvtColor`, `threshold`, `flip`, `warpAffine`), filtering (`GaussianBlur`, `blur`, `medianBlur`, `filter2D`, `Canny`, `Sobel`, `equalizeHist`, `bitwise_not`, `add`), analisis (`calcHist`) |
| **NumPy** | ≥1.24 | Array BGR, `where`, `clip`, `astype`, `histogram`, `random.normal/randint`, `stack` |
| **stdlib** | - | `abc` (ABC), `os`, `time`, `sys` |

---

## 6. Penjelasan Metode Secara Teori

Semua processor mewarisi `BaseProcessor` dan mengimplementasikan `process(image, **kwargs)`. Citra direpresentasikan sebagai array NumPy **BGR** (OpenCV).

### 6.1 Transformasi titik piksel

| Metode | Teori | Implementasi |
|---|---|---|
| **Grayscale** | Kombinasi bobot saluran R,G,B (OpenCV: 0.299R+0.587G+0.114B) | `cv2.cvtColor(BGR2GRAY)` |
| **Negative** | Inversi intensitas: `s = 255 - r` | `cv2.bitwise_not` |
| **Thresholding** | Binerisasi: piksel `< T` → 0, `≥ T` → 255 | `cv2.threshold(..., THRESH_BINARY)` |
| **Thresholding Double** | Rentang: piksel pada `[t1, t2]` → 255, di luar → 0 | `np.where((gray>=t1)&(gray<=t2), 255, 0)` |
| **Brightness** | Penambahan konstan: `s = r + b`, clipping [0,255] | `cv2.add(image, value)` (auto-clip) |
| **Contrast** | Perenggangan seputar nilai 128: `s = f*(r-128)+128` | `np.clip(f*(img-128)+128, 0, 255)` |

### 6.2 Filtering & konvolusi

| Metode | Teori | Implementasi |
|---|---|---|
| **Noise Gaussian** | Tambah derau berdistribusi normal `N(0, σ)`, σ = amount×50 | `np.random.normal(0, sigma, shape)` + clip |
| **Noise Salt & Pepper** | Acak piksel jadi putih (salt) / hitam (pepper) sesuai amount | `np.random.randint` koordinat → set 255 / 0 |
| **Edge Detection Canny** | Multi-tahap: Gaussian blur → gradien Sobel → non-maximum suppression → hysteresis threshold (100/200) | `cv2.Canny(gray, 100, 200)` |
| **Edge Detection Sobel** | Perkiraan gradien orde-1: `Gx` (Sobel X) / `Gy` (Sobel Y); besaran tepi | `cv2.Sobel(gray, CV_64F, 1|0, ...)` → `np.absolute` |
| **Histogram Equalization** | Ratakan distribusi tingkat keabuan agar kontras meningkat | `cv2.equalizeHist(gray)` |
| **Emboss** | Kernel asimetris (±2/±1) memberi efek timbul 3D; hasil digeser +128 agar terlihat | `cv2.filter2D` + clip(+128) |
| **Sharpening** | Kernel pusat tinggi (5) dengan tetangga negatif → pertegas tepi | `cv2.filter2D(image, -1, [[0,-1,0],[-1,5,-1],[0,-1,0]])` |
| **Smoothing** | Penghalusan (blur): Average (rata-rata), Gaussian (bobot normal), Median (median lokal) — mengurangi noise | `cv2.blur` / `GaussianBlur` / `medianBlur` dengan kernel ganjil |
| **Convolution 3x3** | Konvolusi kernel kustom apa pun yang dimasukkan pengguna | `cv2.filter2D(image, -1, kernel)` |

### 6.3 Transformasi geometrik

| Metode | Teori | Implementasi |
|---|---|---|
| **Mirroring** | Membalikkan citra: Horizontal (flipCode=1), Vertical (0), Both (-1) | `cv2.flip(image, code)` |
| **Rotation** | Rotasi sudut θ sekitar pusat; bounding box baru dihitung agar tidak terpotong; area kosong diisi putih | `cv2.getRotationMatrix2D` → `cv2.warpAffine(..., borderValue=(255,255,255))` |

### 6.4 Histogram

- Histogram menghitung frekuensi tiap nilai piksel (0–255) per saluran.
- Citra biner/tepi hanya memuat sedikit nilai → dengan skala linear mayoritas plot kosong; aplikasi ini mendeteksi histogram **sparse** dan otomatis menggambar dalam **skala log10(1+x)**.
- Sumbu X = nilai piksel, sumbu Y = jumlah piksel (format ringkas `150k`).

---

## 7. Dokumentasi Library / Dependency / Fungsi

### 7.0 Tautan dokumentasi resmi

| Topik | Tautan |
|---|---|
| Repositori proyek (GitHub) | https://github.com/MJNJ15/MiniAppCitra |
| Dokumentasi Python | https://docs.python.org/3/ |
| PySide6 — Qt for Python | https://doc.qt.io/qtforpython-6/ |
| PySide6.QtWidgets (widget) | https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html |
| PySide6.QtCore (QThread, Signal, QTimer) | https://doc.qt.io/qtforpython-6/PySide6/QtCore/index.html |
| PySide6.QtGui (QPainter, QImage, QPixmap) | https://doc.qt.io/qtforpython-6/PySide6/QtGui/index.html |
| Qt Style Sheets (QSS) — referensi properti | https://doc.qt.io/qt-6/stylesheet-reference.html |
| Tutorial PySide6 (Qt for Python) | https://doc.qt.io/qtforpython-6/tutorials/index.html |
| OpenCV — tutorial Python | https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html |
| OpenCV — cv2.calcHist (histogram) | https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html |
| OpenCV — cv2.threshold (thresholding) | https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html |
| OpenCV — cv2.Canny (edge detection) | https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html |
| OpenCV — cv2.Sobel (gradien) | https://docs.opencv.org/4.x/d5/d0f/tutorial_py_gradients.html |
| OpenCV — cv2.filter2D (smoothing/konvolusi) | https://docs.opencv.org/4.x/d4/dbd/tutorial_py_filtering.html |
| OpenCV — transformasi geometrik (warpAffine, flip) | https://docs.opencv.org/4.x/da/d54/tutorial_py_geometric_transformations.html |
| OpenCV — cv2.equalizeHist | https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html |
| OpenCV — modul video (VideoCapture) | https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html |
| NumPy — dokumentasi resmi | https://numpy.org/doc/stable/ |
| NumPy — numpy.histogram | https://numpy.org/doc/stable/reference/generated/numpy.histogram.html |
| NumPy — numpy.clip | https://numpy.org/doc/stable/reference/generated/numpy.clip.html |
| NumPy — numpy.random (noise) | https://numpy.org/doc/stable/reference/random/index.html |

> **Catatan:** tautan OpenCV di atas memakai versi 4.x (stabil & banyak dipakai); perilaku API yang dipakai kode ini juga kompatibel dengan OpenCV 5.x, kecuali `cv2.calcHist` yang di 5.x mengembalikan array 1D (kode sudah menyesuaikan dengan `.ravel()`).

### 7.1 Dokumentasi library

#### PySide6 (Qt for Python)

| Nama | Deskripsi | Catatan |
|---|---|---|
| `QApplication` | Obyek aplikasi; media stylesheet global | `setStyle("Fusion")`, `setStyleSheet(...)` |
| `QMainWindow` | Jendela utama dengan menu/toolbar/statusbar | - |
| `QThread` | Thread terpisah untuk pekerjaan latar | `WebcamWorker(QThread)` |
| `Signal` | Mekanisme komunikasi antar-objek Qt | **Pakai `Signal(object)` untuk membawa list/dict** (Signal(list) gagal di PySide6) |
| `QTimer` | Timer berulang untuk throttling render histogram | interval 120 ms |
| `QPainter` | Menggambar kustom di widget | dipakai histogram |
| `QPixmap`/`QImage` | Representasi gambar Qt | QImage aman lintas-thread |
| `QFileDialog` | Dialog buka/simpan file | - |
| `QButtonGroup` | Kelompok checkbox/radio eksklusif | **Eksklusif menolak `setChecked(False)` saat sinyal diblokir** → nonaktifkan sementara |
| QSS | Stylesheet Qt untuk tema | `ui/styles.py` |

#### OpenCV

| Fungsi | Deskripsi |
|---|---|
| `imread` / `imwrite` | Baca/tulis citra |
| `VideoCapture` | Buka kamera (index 0) |
| `cvtColor` | Ubah ruang warna |
| `threshold` | Binerisasi |
| `Canny`, `Sobel` | Deteksi tepi |
| `GaussianBlur`, `blur`, `medianBlur` | Penghalusan |
| `filter2D` | Konvolusi dengan kernel |
| `warpAffine`, `getRotationMatrix2D` | Transformasi affine |
| `flip` | Pencerminan |
| `equalizeHist` | Pemerataan histogram |
| `calcHist` | Hitung histogram per channel (di OpenCV 5.x hasilnya array 1D → pakai `.ravel()`) |

#### NumPy

| Nama | Deskripsi |
|---|---|
| `np.ndarray` | Representasi citra `(H, W, 3)` / `(H, W)` |
| `np.where` | Seleksi bersyarat (Double Thresholding) |
| `np.clip` | Batasi nilai ke [0,255] |
| `np.histogram` | Histogram berbasis NumPy (mode statis) |
| `np.random.normal / randint` | Bangkitkan noise |

### 7.2 Dokumentasi fungsi internal (per modul)

#### `main.py`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `main()` | - | None | Menjalankan aplikasi |

#### `ui/main_window.py` — kelas `MainWindow`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `_init_ui()` | - | None | Susun layout utama |
| `_create_toolbar()` | - | None | Toolbar Buka/Simpan |
| `_connect_signals()` | - | None | Hubungkan sinyal panel |
| `_on_webcam_toggle()` | - | None | Mulai/hentikan webcam |
| `_start_webcam()` | - | None | Inisialisasi worker + timer histogram |
| `_stop_webcam()` | - | None | Hentikan worker |
| `_on_webcam_frame_raw_ready(pixmap)` | QPixmap | None | Tampilkan feed di panel kiri |
| `_on_webcam_frame_processed_ready(pixmap)` | QPixmap | None | Tampilkan hasil di panel kanan |
| `_on_webcam_hist_raw_ready(hist)` | ndarray | None | Simpan data histogram raw |
| `_on_webcam_hist_processed_ready(hist)` | ndarray | None | Simpan data histogram hasil |
| `_flush_hist_updates()` | - | None | Render histogram tertunda (throttle) |
| `_on_webcam_error(message)` | str | None | Pesan error + stop webcam |
| `_on_webcam_started()` / `_on_webcam_stopped()` | - | None | Update state/UI saat webcam mulai/berhenti |
| `_on_snapshot_requested()` | - | None | Simpan frame hasil proses ke file (notifikasi jika belum ada proses) |
| `_on_process_requested(params_list)` | list[dict] | None | Kirim rantai ke webcam / proses statis |
| `_process_static_image(params_list)` | list[dict] | None | Terapkan rantai ke citra statis |
| `_on_reset_requested()` | - | None | Bersihkan semua state |
| `open_image()` | - | None | Dialog buka citra |
| `save_image()` | - | None | Dialog simpan hasil |
| `closeEvent(event)` | QCloseEvent | None | Bersihkan webcam saat tutup |

#### `utils/webcam_worker.py` — kelas `WebcamWorker`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `run()` | - | None | Loop utama baca frame |
| `stop()` | - | None | Hentikan loop & tunggu thread |
| `set_processors(processors)` | list[(processor, params)] | None | Set rantai processor |
| `clear_processor()` | - | None | Kosongkan rantai |
| `snapshot_processed()` | - | ndarray/None | Frame hasil proses terakhir (salinan) |
| `_compute_histogram(image)` (static) | ndarray | ndarray | Histogram `(256,3)`/`(256,)` |

#### `ui/control_panel.py` — kelas `ControlPanel`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `update_methods(methods)` | list[(nama, default)] | None | Bangun panel input per metode |
| `_build_group_inputs(layout, name, defaults, entry)` | - | None | Isi satu group input |
| `_add_spinbox(...)` / `_add_doublespinbox(...)` / `_add_slider(...)` / `_add_combobox(...)` | (layout, widgets, key, label, rentang, default) | None | Tambah satu baris input |
| `_on_process_clicked()` | - | None | Kumpulkan parameter → emit |
| `set_webcam_state(active)` | bool | None | Update UI tombol webcam |
| `clear_inputs()` | - | None | Kosongkan panel input |
| `_styled_button(text, base, hover, pressed, disabled)` (static) | str × 5 | QPushButton | Tombol berwarna modern |

#### `ui/method_panel.py` — kelas `MethodPanel`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `_on_mode_toggled(checked)` | bool | None | Ganti mode Tunggal/Multiple |
| `_on_method_toggled(checked)` | bool | None | Kelola pilihan & urutan |
| `_refresh_labels()` | - | None | Nomor urut pada label |
| `_emit_selection()` | - | None | Emit `methods_changed` |
| `clear_selection()` | - | None | Bersihkan semua pilihan |

#### `ui/image_panel.py` — kelas `ImagePanel`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `set_image(pixmap, smooth=True)` | QPixmap, bool | None | Tampilkan gambar (halus/cepat) |
| `update_histogram(image_np)` | ndarray | None | Teruskan ke widget histogram |
| `update_histogram_counts(counts)` | ndarray | None | Teruskan data histogram siap pakai |
| `clear()` | - | None | Reset panel |
| `resizeEvent(event)` | QResizeEvent | None | Re-scale gambar saat resize |

#### `ui/histogram_widget.py` — kelas `HistogramWidget`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `update_histogram(image_np)` | ndarray | None | Hitung & render (mode statis) |
| `update_histogram_counts(counts)` | ndarray | None | Render data histogram langsung |
| `clear()` | - | None | Kosongkan grafik |
| `paintEvent(event)` | QPaintEvent | None | Gambar sumbu + batang (skala log utk sparse) |

#### `utils/image_utils.py`

| Fungsi | Parameter | Kembalian | Deskripsi |
|---|---|---|---|
| `cv2_to_qpixmap(cv_img)` | ndarray (BGR) | QPixmap | Konversi untuk ditampilkan di Qt |

#### `processors/` — kelas turunan `BaseProcessor`

Semua memiliki `process(image, **kwargs) -> ndarray`:

| Kelas | Parameter penting (kwargs) |
|---|---|
| `ThresholdingProcessor` | `threshold` (default 128) |
| `DoubleThresholdingProcessor` | `t1`, `t2` |
| `GrayscaleProcessor` | - |
| `NegativeProcessor` | - |
| `BrightnessProcessor` | `value` (-100..100) |
| `ContrastProcessor` | `factor` (0.5..3.0) |
| `NoiseProcessor` | `type` (Gaussian/Salt & Pepper), `amount` |
| `EdgeDetectionProcessor` | `edge_method` (Canny/Sobel X/Sobel Y) |
| `EqualizationProcessor` | - |
| `EmbossProcessor` | - |
| `SharpeningProcessor` | - |
| `SmoothingProcessor` | `type` (Gaussian/Average/Median), `kernel_size` |
| `ConvolutionProcessor` | `kernel` (list 3x3) |
| `MirroringProcessor` | `direction` (Horizontal/Vertical/Both) |
| `RotationProcessor` | `angle` (0..360) |

---

## Lampiran: Catatan Teknis Penting

- **Sinyal berisi koleksi Python** → deklarasikan `Signal(object)` (PySide6 menolak `Signal(list)`).
- **QButtonGroup eksklusif** → `setChecked(False)` tidak berlaku saat sinyal diblokir; nonaktifkan eksklusivitas sementara.
- **OpenCV 5.x** → `cv2.calcHist` mengembalikan array 1D; gunakan `.ravel()`.
- **Matplotlib dihapus** → histogram memakai QPainter; perbandingan lama ±140 ms vs ±13 ms per update.
- **Throttle histogram** → hitung di worker (tiap 3 frame), render di UI tiap 120 ms.
