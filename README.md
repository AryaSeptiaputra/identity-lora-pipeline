# identity-lora-pipeline

Persiapan dataset untuk fine-tuning LoRA identitas, dua tahap berurutan. Modul 001
mendeteksi manusia pada foto mentah per identitas (YOLOv8n, kelas `person`), memvalidasi
bahwa setiap foto berisi tepat satu orang, lalu memotong (crop) region tersebut dengan
padding menjadi gambar tubuh penuh siap dipakai tahap berikutnya. Modul 002 membaca hasil
modul 001, mendeteksi wajah (InsightFace `buffalo_sc`) serta upper body dan lower body
(YOLOv8n-pose, dari 17 keypoint COCO), lalu memotong masing-masing menjadi crop siap
dipakai tahap alignment LoRA berikutnya.

Rancangan lengkap: `docs/rancangan/001a_2026-09-26_mvp-deteksi-manusia-dan-cropping.md`,
`docs/rancangan/002a_2026-09-26_mvp-deteksi-wajah-tubuh-dan-cropping.md`, dan
`docs/keputusan-produk.md`.

## Struktur folder

```
identity-lora-pipeline/
├── notebooks/
│   ├── 00_pipeline_errors.ipynb                       # definisi error pipeline, dimuat
│   │                                                     01 & 02 lewat %run
│   ├── 01_human_detection_and_cropping.ipynb          # modul 001: config, deteksi,
│   │                                                     validasi, cropping, orkestrasi
│   └── 02_face_upper_lower_body_detection_and_cropping.ipynb  # modul 002: config,
│                                                          deteksi wajah, deteksi pose,
│                                                          kelompok keypoint, cropping,
│                                                          orkestrasi
├── data/
│   ├── raw/<identitas>/                        # foto asli per identitas, isi Anda
│   │                                              sendiri, tidak diubah oleh pipeline
│   ├── cropped/<identitas>/                     # hasil crop tubuh penuh modul 001,
│   │                                              juga jadi input modul 002
│   ├── face/<identitas>/                        # hasil crop wajah modul 002
│   ├── upper_body/<identitas>/                  # hasil crop upper body modul 002
│   └── lower_body/<identitas>/                  # hasil crop lower body modul 002
├── tests/notebooks/
│   ├── test_pipeline_errors.py                          # test notebook 00
│   ├── test_human_detection_and_cropping.py             # test notebook 01, mock model
│   └── test_face_upper_lower_body_detection_and_cropping.py  # test notebook 02, mock model
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
(`yolov8n.pt`, `yolov8n-pose.pt`) diunduh otomatis oleh package `ultralytics`, dan bobot
`buffalo_sc` diunduh otomatis oleh package `insightface` ke `~/.insightface/models/`,
saat notebook pertama kali dijalankan (butuh koneksi internet sekali per bobot).

## Menjalankan pipeline

Jalankan notebook secara berurutan — modul 002 membaca output modul 001, jadi modul 001
harus selesai lebih dulu untuk identitas yang sama.

1. Letakkan foto mentah tiap identitas di `data/raw/<nama-identitas>/`.
2. Jalankan `notebooks/01_human_detection_and_cropping.ipynb` dari awal sampai akhir
   (notebook `00_pipeline_errors.ipynb` dimuat otomatis, tidak perlu dijalankan sendiri).
   Tiap bagian fungsi punya sel runner di bawahnya yang menampilkan `DISPLAY_LIMIT` (5)
   data pertama.
3. Hasil crop tubuh penuh tersimpan di `data/cropped/<nama-identitas>/`, dengan nama file
   diturunkan dari nama file asal (`<nama_asli>_person.jpg`) — menjalankan ulang pipeline
   pada data yang sama akan menimpa file lama, bukan menduplikasi (K5).
4. Foto yang tidak menghasilkan tepat satu deteksi `person`, atau hasil crop-nya di
   bawah ukuran minimum, dilewati dan dicatat ke log (bukan error) — periksa output sel
   untuk melihat foto mana yang terlewat.
5. Setelah modul 001 selesai, jalankan
   `notebooks/02_face_upper_lower_body_detection_and_cropping.ipynb` dari awal sampai
   akhir. Wajah, upper body, dan lower body diproses independen per gambar — satu foto
   bisa menghasilkan 0 sampai 3 crop, tersimpan masing-masing di
   `data/face/<nama-identitas>/`, `data/upper_body/<nama-identitas>/`, dan
   `data/lower_body/<nama-identitas>/` (nama file `<nama_asli>_face.jpg`,
   `<nama_asli>_upper.jpg`, `<nama_asli>_lower.jpg`; re-run aman, menimpa bukan
   menduplikasi).

Ambang confidence deteksi (`CONF_THRESHOLD`, `FACE_DET_THRESH`, `POSE_CONF_THRESHOLD`,
`KEYPOINT_CONF_THRESHOLD`, sel Konfigurasi tiap notebook) dan ukuran minimum crop
(`MIN_SIDE_PX`) adalah nilai awal sementara; kalibrasi ulang setelah melihat hasil pada
data asli.

## Test

```bash
pytest tests/
```

Notebook diuji lewat `testbook` (menjalankan sel definisi notebook di kernel Jupyter
sungguhan, tanpa memindah kodenya ke modul `.py`, sesuai keputusan K6/K16). Sel runner
yang memanggil model sungguhan (`tag: manual-run`, termasuk semua sel runner
"define -> demonstrate") tidak dieksekusi oleh test — deteksi diuji dengan
`ultralytics.YOLO` dan `insightface.app.FaceAnalysis` yang di-mock. Test tidak
menjalankan pipeline pada data sungguhan; itu dilakukan Arya sendiri di luar test ini.

## Lisensi

- Package `ultralytics` (YOLOv8, YOLOv8n-pose) berlisensi AGPL-3.0 secara default.
- Model pack `buffalo_sc` (InsightFace) berlisensi non-commercial research only; kode
  package `insightface` sendiri berlisensi MIT.

Pipeline ini dipakai internal saja, tidak didistribusikan atau dijual ke pihak lain.
Kalau model bisnis LoRA hasil pipeline ini berubah menjadi komersial, kedua lisensi di
atas perlu ditinjau ulang.
