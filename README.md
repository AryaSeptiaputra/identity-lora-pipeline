# identity-lora-pipeline

Persiapan dataset untuk fine-tuning LoRA identitas. Modul MVP ini mendeteksi manusia
pada foto mentah per identitas (YOLOv8n, kelas `person`), memvalidasi bahwa setiap foto
berisi tepat satu orang, lalu memotong (crop) region tersebut dengan padding menjadi
gambar identitas siap dipakai tahap alignment berikutnya.

Rancangan lengkap: `docs/rancangan/001a_2026-09-26_mvp-deteksi-manusia-dan-cropping.md`
dan `docs/keputusan-produk.md`.

## Struktur folder

```
identity-lora-pipeline/
├── notebooks/
│   ├── 00_pipeline_errors.ipynb                # definisi error pipeline, dimuat 01 lewat %run
│   └── 01_human_detection_and_cropping.ipynb   # config, deteksi, validasi, cropping,
│                                                 orkestrasi — satu notebook (K6)
├── data/
│   ├── raw/<identitas>/                        # foto asli per identitas, isi Anda
│   │                                             sendiri, tidak diubah oleh pipeline
│   └── cropped/<identitas>/                     # hasil crop, ditulis notebook
├── tests/notebooks/
│   └── test_human_detection_and_cropping.py     # test lewat testbook, mock model
├── requirements.txt
└── README.md
```

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tidak ada `.env` — tidak ada kredensial atau API key yang dipakai. Bobot model
(`yolov8n.pt`) diunduh otomatis oleh package `ultralytics` saat notebook pertama kali
dijalankan (butuh koneksi internet sekali).

## Menjalankan pipeline

1. Letakkan foto mentah tiap identitas di `data/raw/<nama-identitas>/`.
2. Jalankan `notebooks/01_human_detection_and_cropping.ipynb` dari awal sampai akhir
   (notebook `00_pipeline_errors.ipynb` dimuat otomatis, tidak perlu dijalankan sendiri).
   Tiap bagian fungsi punya sel runner di bawahnya yang menampilkan `DISPLAY_LIMIT` (5)
   data pertama.
3. Hasil crop tersimpan di `data/cropped/<nama-identitas>/`, dengan nama file diturunkan
   dari nama file asal (`<nama_asli>_person.jpg`) — menjalankan ulang pipeline pada data
   yang sama akan menimpa file lama, bukan menduplikasi (K5).
4. Foto yang tidak menghasilkan tepat satu deteksi `person`, atau hasil crop-nya di
   bawah ukuran minimum, dilewati dan dicatat ke log (bukan error) — periksa output sel
   untuk melihat foto mana yang terlewat.

Ambang confidence deteksi (`CONF_THRESHOLD`, sel Konfigurasi) dan ukuran minimum crop
(`MIN_SIDE_PX`) adalah nilai awal sementara; kalibrasi ulang setelah melihat hasil pada
data asli.

## Test

```bash
pytest tests/
```

Notebook diuji lewat `testbook` (menjalankan sel definisi notebook di kernel Jupyter
sungguhan, tanpa memindah kodenya ke modul `.py`, sesuai keputusan K6). Sel runner yang memanggil
model YOLOv8n sungguhan (`tag: manual-run`) tidak dieksekusi oleh test —
deteksi diuji dengan `ultralytics.YOLO` yang di-mock. Test tidak menjalankan pipeline
pada data sungguhan; itu dilakukan Arya sendiri di luar test ini.

## Lisensi

Package `ultralytics` (YOLOv8) berlisensi AGPL-3.0 secara default. Pipeline ini dipakai
internal saja, tidak didistribusikan atau dijual ke pihak lain.
