# 001b · MVP · Deteksi manusia dan cropping identitas

Status: disetujui 2026-09-26
Dari: docs/rancangan/001a_2026-09-26_mvp-deteksi-manusia-dan-cropping.md
Kondisi kode: Project baru. Belum ada struktur folder apa pun selain `.claude/` dan `docs/`.
Satu-satunya kode yang ada adalah `00_name_file.ipynb` di root — draft percobaan lama
berisi `HumanDetector`, `Cropper`, `process_identity` yang **belum** sesuai rancangan
final (masih meng-crop *semua* box terdeteksi per gambar, bukan memvalidasi tepat-1-box;
mengasumsikan `data/raw`/`data/cropped` langsung di root tanpa struktur project). File ini
dipindah dan ditulis ulang di Langkah 1, bukan disalin apa adanya.

## Peta keputusan → kode

| Keputusan | Folder / file | Class / fungsi utama | Peran (writer-code) |
|---|---|---|---|
| K6 Struktur proyek | Root project: `notebooks/`, `data/raw/<identitas>/`, `data/cropped/<identitas>/`, `requirements.txt`, `README.md`, `.gitignore` | — | Struktur project (Bagian 1) — template `structure-pipeline.md` disederhanakan sesuai K6: tanpa `app/`, karena kode inti sengaja tetap satu notebook di fase ini. Satu `requirements.txt` saja (koreksi Arya) — lihat catatan dependency di bawah |
| Config (sel notebook, bagian dari K6) | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Konfigurasi" | Konstanta `RAW_DIR`, `CROPPED_DIR`, `MODEL_WEIGHTS`, `CONF_THRESHOLD`, `PADDING_RATIO`, `MIN_SIDE_PX` | Bukan `Settings`/`.env` — rancangan menyatakan eksplisit tidak ada kredensial, config cukup sel notebook |
| K1 Model deteksi | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Deteksi" | `BoundingBox` (dataclass), `HumanDetector.detect` | Pengakses luar (memanggil model YOLOv8n via `ultralytics`) |
| K2 Validasi jumlah deteksi | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Validasi" | `validate_single_detection(boxes) -> BoundingBox` (raise `NoDetectionError` / `MultipleDetectionError`) | Pemeriksa (`validate_`) |
| K3 Validasi ukuran minimum crop | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Cropping" | `Cropper._is_large_enough` | Pemeriksa, sub-proses dari `Cropper.crop` |
| K4 Padding crop | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Cropping" | `Cropper.crop` | Pengubah bentuk (memotong array gambar di memori, tanpa I/O) |
| K5 Re-run aman (nama file dari nama asal) | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Cropping" | `build_crop_filename(source_path)` | Pembantu |
| Orkestrasi per identitas (D2) | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Orkestrasi" | `process_identity(identity_dir, detector, cropper)`, `run_pipeline(identities)` | Proses / sub-proses |
| Error milik pipeline (2.6) | `notebooks/0_human_detection_and_cropping.ipynb` — sel "Error" | `NoDetectionError`, `MultipleDetectionError`, `CropTooSmallError` | Definisi error, ditangkap di `process_identity` untuk log lewati/log peringatan |

## Langkah

| # | Yang dibangun | File disentuh | Test | Gate (dari rencana-evaluasi) | Bergantung pada |
|---|---|---|---|---|---|
| 1 | **Memulai project**: struktur folder MVP (`notebooks/`, `data/raw/`, `data/cropped/` dengan `.gitkeep`), `requirements.txt` (tunggal, termasuk `pytest`+`testbook`), `README.md`, `.gitignore`; pindahkan `00_name_file.ipynb` → `notebooks/0_human_detection_and_cropping.ipynb` dan tulis ulang isinya sesuai K1–K6 (config sel, `BoundingBox`, `HumanDetector`, error pipeline, `validate_single_detection`, `Cropper` + `build_crop_filename`, `process_identity`/`run_pipeline`); hapus `00_name_file.ipynb` dari root setelah dipindah | Baru: `notebooks/0_human_detection_and_cropping.ipynb`, `requirements.txt`, `README.md`, `.gitignore`, `data/raw/.gitkeep`, `data/cropped/.gitkeep`, `tests/notebooks/test_human_detection_and_cropping.py`. Dihapus: `00_name_file.ipynb` | `tests/notebooks/test_human_detection_and_cropping.py` memuat sel-sel notebook lewat `testbook` (tanpa memindah logika ke modul `.py`, sesuai K6) dan menguji tiap fungsi terpisah dengan `ultralytics.YOLO` di-mock (tidak mengunduh/memanggil model sungguhan) serta gambar sintetis kecil di `tmp_path` (bukan data asli): <br>• `HumanDetector.detect` meneruskan hasil mock apa adanya (K1) <br>• `validate_single_detection`: lolos pada 1 box, `NoDetectionError` pada 0 box, `MultipleDetectionError` pada >1 box (K2) <br>• `Cropper.crop` menerapkan `PADDING_RATIO` dan menolak (`CropTooSmallError`) crop di bawah `MIN_SIDE_PX` (K3, K4) <br>• `build_crop_filename` menghasilkan nama dari file asal; menjalankan `process_identity` dua kali pada data sama menimpa file yang sama, bukan menduplikasi (K5) <br>• `process_identity` pada folder identitas sintetis (2 gambar valid, 1 gambar 0-box, 1 gambar >1-box via mock): jumlah file keluaran benar, 2 gambar bermasalah tercatat di log bukan dilempar sebagai error tak tertangani <br>• satu test smoke mengeksekusi seluruh notebook end-to-end (`testbook`/`nbclient`) dengan mock+data sintetis — memenuhi D4 "bisa diimpor/dijalankan tanpa error", bukan menjalankan pipeline pada data sungguhan | Tidak ada `docs/rencana-evaluasi.md` untuk rancangan ini; D4 sudah menetapkan tanda berhasil = validasi statis/impor lulus test di atas, bukan menjalankan pipeline pada data sungguhan (bukan gate MVP) | — (langkah pertama) |

## Tidak dibangun di rencana ini

- Pemilihan subjek utama otomatis saat >1 box (ditolak di titik periksa 1; foto >1 box tetap dilewati + log peringatan).
- Face alignment, deduplikasi, quality filtering — ditunda ke pipeline/notebook berikutnya.
- Pemisahan kode inti ke modul `.py` (`app/shared`, `app/detect`, `app/crop`) — sengaja ditunda ke fase Dev (K6, titik periksa 4).
- `config.py` + `.env`/`.env.example` — tidak ada kredensial atau API key yang dipakai; config cukup sel notebook per K6.
- Penyediaan folder `data/raw/<identitas>/` berisi foto sungguhan, dan pengujian pipeline pada data sungguhan — di luar cakupan pekerjaan pink-chan (D3, D4); dilakukan Arya sendiri setelah Langkah 1 selesai.
- Kalibrasi ulang `CONF_THRESHOLD` (0.5) dan `MIN_SIDE_PX` (64, nilai awal sesuai anjuran K3) berdasarkan data asli — dilakukan Arya.
- Pencatatan status per gambar (`storage/`), lanjut-dari-kegagalan, penjadwalan otomatis — fase Dev/Production.

## Risiko teknis

- **Kode tidak bisa diuji lewat pytest biasa** karena K6 mengharuskan seluruh logika tetap di satu notebook (tidak ada modul `.py` untuk di-import langsung). Mitigasi: pakai `testbook` untuk menjalankan sel/fungsi notebook secara terisolasi di test — tidak melanggar K6 karena kode sumber tetap satu-satunya di notebook, `testbook` hanya membaca dan mengeksekusinya saat test.
- **Dependency dev (`pytest`, `testbook`) digabung ke `requirements.txt`, bukan `requirements-dev.txt` terpisah** (koreksi Arya). Diterima karena project ini tidak punya lingkungan produksi yang berjalan terus-menerus terpisah dari lingkungan Arya/pink-chan mengembangkan — satu-satunya "produksi" adalah notebook yang dijalankan manual di komputer yang sama; tidak ada konflik dependency dev vs prod untuk dihindari di fase MVP ini.
- `ultralytics.YOLO(weights)` di `HumanDetector.__init__` akan mencoba mengunduh `yolov8n.pt` saat notebook benar-benar dijalankan pertama kali (butuh koneksi internet) — di luar cakupan test Langkah 1 (di-mock), tapi Arya perlu koneksi internet sekali saat menjalankan notebook sungguhan nanti.
- `CONF_THRESHOLD = 0.5` dan `MIN_SIDE_PX = 64` adalah nilai sementara dari rancangan (K1, K3), belum dikalibrasi pada data asli — dicatat sebagai konstanta bernama jelas di sel config supaya mudah diubah Arya, bukan angka tersebar di kode.
- Lisensi AGPL-3.0 paket `ultralytics` (K1) — dipakai internal saja sesuai keputusan Arya; tidak mempengaruhi struktur kode, hanya dicatat ulang di `README.md`.

## Koreksi selama putaran

- Tidak ada `requirements-dev.txt` terpisah — `pytest` dan `testbook` digabung ke satu `requirements.txt` (koreksi Arya saat menyetujui, lihat Risiko teknis).
- Nama file kode berbahasa Inggris: notebook `0_deteksi_manusia_dan_cropping.ipynb` → `0_human_detection_and_cropping.ipynb`, test `test_deteksi_manusia_dan_cropping.py` → `test_human_detection_and_cropping.py` (koreksi Arya saat menyetujui). Dokumen rancangan (`001a`, `001b`, `docs/keputusan-produk.md`) tetap Bahasa Indonesia.
