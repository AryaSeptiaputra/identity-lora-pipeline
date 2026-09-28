# identity-lora-pipeline

Persiapan dataset untuk fine-tuning LoRA identitas, tiga tahap berurutan. Notebook 01
(modul 001) mendeteksi manusia pada foto mentah per identitas (YOLOv8n, kelas `person`),
memilih box dengan confidence tertinggi jika ada beberapa `person`, lalu memotong (crop)
region tersebut dengan padding menjadi gambar tubuh penuh siap dipakai tahap berikutnya.
Notebook 02 (modul 002) membaca hasil notebook 01, mendeteksi wajah (InsightFace
`buffalo_sc`, CPU), memilih bbox dengan confidence tertinggi jika ada beberapa wajah,
lalu memotong region wajah dengan padding. Notebook 03 (modul 004) membaca hasil
notebook 01 dan 02, lalu memberi caption teks ke tiap gambar dengan model JoyCaption
(VLM), disimpan sebagai file `.txt` bersebelahan.

Deteksi upper body dan lower body (DWPose/`rtmlib`, sempat ada di rancangan
002/003) **sudah dihapus total** dari notebook 02 — lihat rancangan 004. Status
permanen atau sementaranya masih titik periksa terbuka (13/14) di
`docs/keputusan-produk.md`, belum dijawab Arya.

Rancangan lengkap: `docs/rancangan/001a_2026-09-26_mvp-deteksi-manusia-dan-cropping.md`,
`docs/rancangan/002a_2026-09-26_mvp-deteksi-wajah-tubuh-dan-cropping.md`,
`docs/rancangan/003a_2026-09-26_mvp-revisi-dwpose-gpu.md`,
`docs/rancangan/004a_2026-09-28_dev-revisi-deteksi-dan-captioning.md` (mendokumentasikan
retroaktif revisi notebook 00–02 dan penambahan notebook 03), dan
`docs/keputusan-produk.md`.

## Struktur folder

```
identity-lora-pipeline/
├── notebooks/
│   ├── 00_pipeline_errors.ipynb                # definisi error pipeline, dimuat
│   │                                              01, 02, dan 03 lewat %run
│   ├── 01_human_detection_and_cropping.ipynb   # modul 001: config, deteksi,
│   │                                              validasi, cropping, orkestrasi
│   ├── 02_face_detection_and_cropping.ipynb    # modul 002: config, deteksi wajah
│   │                                              (InsightFace, CPU), cropping,
│   │                                              orkestrasi
│   └── 03_image_captioning.ipynb               # modul 004: config, load model
│                                                  JoyCaption, generate & simpan
│                                                  caption, orkestrasi
├── data/
│   ├── raw/<identitas>/                # foto asli per identitas, isi Anda sendiri,
│   │                                      tidak diubah oleh pipeline
│   ├── cropped/<identitas>/            # hasil crop tubuh penuh notebook 01, juga
│   │                                      input notebook 02 dan 03 (caption `.txt`
│   │                                      ditulis bersebelahan di sini oleh notebook 03)
│   └── face/<identitas>/               # hasil crop wajah notebook 02, juga input
│                                          notebook 03 (caption `.txt` bersebelahan)
├── tests/notebooks/
│   ├── test_pipeline_errors.py               # test notebook 00
│   ├── test_human_detection_and_cropping.py  # test notebook 01, mock model
│   ├── test_face_detection_and_cropping.py   # test notebook 02, mock model
│   └── test_image_captioning.py              # test notebook 03, mock model VLM
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
`yolov8n.pt` diunduh otomatis oleh package `ultralytics`; bobot `buffalo_sc` diunduh
otomatis oleh package `insightface` ke `~/.insightface/models/`; bobot JoyCaption
(`fancyfeast/llama-joycaption-beta-one-hf-llava`) diunduh otomatis oleh package
`transformers` saat notebook 03 pertama kali dijalankan (butuh koneksi internet sekali
per bobot).

Notebook 00 dan 01, serta seluruh notebook 02 (deteksi wajah CPU, InsightFace),
berjalan di CPU tanpa GPU. Notebook 03 memuat model JoyCaption lewat
`device_map="auto"` (`accelerate`) tanpa verifikasi eksplisit ketersediaan GPU di
kode saat ini — kebijakan GPU untuk notebook 03 masih titik periksa terbuka (15) di
`docs/keputusan-produk.md`.

## Menjalankan pipeline

Jalankan notebook secara berurutan — notebook 02 membaca output notebook 01, dan
notebook 03 membaca output notebook 01 dan 02, jadi notebook sebelumnya harus selesai
lebih dulu untuk identitas yang sama.

1. Letakkan foto mentah tiap identitas di `data/raw/<nama-identitas>/`.
2. Jalankan `notebooks/01_human_detection_and_cropping.ipynb` dari awal sampai akhir
   (notebook `00_pipeline_errors.ipynb` dimuat otomatis, tidak perlu dijalankan sendiri).
   Tiap bagian fungsi punya sel runner di bawahnya yang menampilkan `DISPLAY_LIMIT` (5)
   data pertama.
3. Hasil crop tubuh penuh tersimpan di `data/cropped/<nama-identitas>/`, dengan nama file
   diturunkan dari nama file asal (`<nama_asli>_person.jpg`) — menjalankan ulang pipeline
   pada data yang sama akan menimpa file lama, bukan menduplikasi (K5).
4. Foto yang tidak menghasilkan deteksi `person` sama sekali, atau hasil crop-nya di
   bawah ukuran minimum, dilewati dan dicatat ke log (bukan error); kalau ada lebih dari
   satu box `person`, box dengan confidence tertinggi dipilih otomatis — periksa output
   sel untuk melihat foto mana yang terlewat.
5. Setelah notebook 01 selesai, jalankan
   `notebooks/02_face_detection_and_cropping.ipynb` dari awal sampai akhir. Wajah
   terdeteksi diproses dengan aturan pemilihan dan pelewatan yang sama seperti butir 4,
   hasil crop tersimpan di `data/face/<nama-identitas>/` (nama file
   `<nama_asli>_face.jpg`; re-run aman, menimpa bukan menduplikasi).
6. Setelah notebook 01 dan/atau 02 selesai, jalankan
   `notebooks/03_image_captioning.ipynb` dari awal sampai akhir untuk memberi caption
   pada gambar di `data/cropped/` dan `data/face/`. Caption disimpan sebagai file `.txt`
   bersebelahan gambar (nama sama, stem sama), diproses berkelompok
   (`CAPTION_BATCH_SIZE`).

Ambang confidence deteksi (`CONF_THRESHOLD`, `FACE_DET_THRESH`, sel Konfigurasi tiap
notebook) dan ukuran minimum crop (`MIN_SIDE_PX`) adalah nilai awal sementara; kalibrasi
ulang setelah melihat hasil pada data asli.

## Test

```bash
pytest tests/
```

Notebook diuji lewat `testbook` (menjalankan sel definisi notebook di kernel Jupyter
sungguhan, tanpa memindah kodenya ke modul `.py`, sesuai keputusan K6/K16). Sel runner
yang memanggil model sungguhan (`tag: manual-run`, termasuk semua sel runner
"define -> demonstrate") tidak dieksekusi oleh test — deteksi dan captioning diuji
dengan `ultralytics.YOLO`, `insightface.app.FaceAnalysis`, dan model VLM JoyCaption
(`AutoProcessor`/`LlavaForConditionalGeneration`) yang di-mock. Test tidak menjalankan
pipeline pada data sungguhan atau memerlukan GPU; itu dilakukan Arya sendiri di luar
test ini.

## Lisensi

- Package `ultralytics` (YOLOv8, kelas `person`, notebook 01) berlisensi AGPL-3.0 secara
  default.
- Model pack `buffalo_sc` (InsightFace, notebook 02) berlisensi non-commercial research
  only; kode package `insightface` sendiri berlisensi MIT.
- Model JoyCaption (`fancyfeast/llama-joycaption-beta-one-hf-llava`, notebook 03) —
  lisensinya belum ditinjau di dokumen ini, lihat `docs/keputusan-produk.md`.

Pipeline ini dipakai internal saja, tidak didistribusikan atau dijual ke pihak lain.
Kalau model bisnis LoRA hasil pipeline ini berubah menjadi komersial, lisensi di atas
perlu ditinjau ulang.
