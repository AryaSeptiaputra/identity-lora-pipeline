# 003b · MVP · Revisi deteksi pose ke DWPose (rtmlib) dengan GPU wajib

Status: disetujui 2026-09-27
Dari: docs/rancangan/003a_2026-09-26_mvp-revisi-dwpose-gpu.md
Kondisi kode: Project sudah ada (modul 001 dan 002 selesai, 001b/002b keduanya
`selesai`). `notebooks/00_pipeline_errors.ipynb` berisi error pipeline bersama, dimuat
`%run` oleh notebook 01 dan 02. `notebooks/02_face_upper_lower_body_detection_and_cropping.ipynb`
saat ini mendeteksi upper/lower body dengan `YOLO("yolov8n-pose.pt")` (`ultralytics`,
CPU) di sel `## 5. Deteksi pose (K9)` — ini yang direvisi rancangan 003. Sel
`## 6. Kelompok keypoint & bbox (K10, K11)` (konstanta `UPPER_KEYPOINT_INDICES` dkk.
dan `derive_body_part_bbox`) serta sel `## 7. Cropping` dan `## 8. Orkestrasi`
memakai array keypoint berbentuk `(17, 3)` — bentuk ini **tidak berubah**, jadi tidak
disentuh langkah ini, hanya cara array itu dihasilkan (di dalam `detect_pose`) yang
berubah. Modul 001 (`01_human_detection_and_cropping.ipynb`) dan deteksi wajah (K8,
sel `## 4. Deteksi wajah` di notebook 02) tidak disentuh sama sekali.

## Peta keputusan → kode

| Keputusan | Folder / file | Class / fungsi utama | Peran (writer-code) |
|---|---|---|---|
| K9 (error baru) | `notebooks/00_pipeline_errors.ipynb` — `## 1. Error pipeline` | `GPUNotAvailableError` | Definisi error (2.6); error K9 lain (`PoseDetectionError`, `NoPersonPoseDetectedError`, `MultiplePersonPoseDetectedError`) reuse yang sudah ada, tidak didefinisikan ulang |
| Config notebook 02 (K9) | `notebooks/02_...ipynb` — `## 2. Konfigurasi` | Hapus `POSE_MODEL_WEIGHTS`, `POSE_CONF_THRESHOLD`; tambah `POSE_MODE = "balanced"`, `POSE_DEVICE = "cuda"` | Konstanta config sel notebook (bukan `Settings`/`.env`, sama seperti sebelumnya) |
| K9 Deteksi pose — DWPose GPU wajib | `notebooks/02_...ipynb` — `## 1. Import dan logger`, `## 5. Deteksi pose (K9)` | `import onnxruntime as ort`, `from rtmlib import Wholebody`; `load_pose_detector(mode: str, device: str) -> Wholebody` (verifikasi `ort.get_available_providers()` sebelum construct, raise `GPUNotAvailableError`); `detect_pose(model: Wholebody, image: np.ndarray) -> list[np.ndarray]` (gabung `keypoints`+`scores`, subset 17 titik body pertama, kembalikan bentuk `(17, 3)` sama seperti sebelumnya) | `load_pose_detector` pembentuk (raise `GPUNotAvailableError`, gagal keras, tidak fallback CPU); `detect_pose` pengakses luar (bungkus panggilan model, raise `PoseDetectionError`) |
| K9 validasi jumlah orang (tidak berubah) | sel yang sama (`## 5`) | `validate_single_person_pose(people) -> np.ndarray` | Pemeriksa — logika dan nama identik, tidak disentuh |
| K10 subset 17 dari 133 keypoint | di dalam `detect_pose` (`## 5`), bukan sel `## 6` | Sub-proses privat `_body17_from_wholebody(keypoints, scores) -> np.ndarray` (nama indikatif, boleh berubah kecil saat coding) | Pengubah bentuk — dipanggil `detect_pose`, tidak dipanggil dari luar |
| K10 kelompok keypoint & bbox (tidak berubah) | `notebooks/02_...ipynb` — `## 6. Kelompok keypoint & bbox (K10, K11)` | `UPPER_KEYPOINT_INDICES`, `LOWER_KEYPOINT_INDICES`, `UPPER_ANCHOR_INDICES`, `LOWER_ANCHOR_INDICES`, `derive_body_part_bbox` | Tidak diubah sama sekali — bentuk `(17, 3)` yang diterima identik dengan sebelumnya |
| Orkestrasi (wiring ke K9 baru) | `notebooks/02_...ipynb` — `## 8. Orkestrasi per identitas (K12)` | `process_image`, `process_identity`, `run_pipeline` — parameter `pose_conf_threshold` dihapus dari tanda tangan; panggilan `detect_pose(pose_model, image_path, pose_conf_threshold)` menjadi `detect_pose(pose_model, image)` (memakai `image` yang sudah dibaca `_read_image`, bukan membaca ulang dari path) | Proses — peran tidak berubah, hanya parameter yang menyesuaikan sumber deteksi baru |
| Dependency (K9) | `requirements.txt` | Tambah `rtmlib`; ganti `onnxruntime==1.30.0` → `onnxruntime-gpu` (satu paket, tetap menyediakan `CPUExecutionProvider` untuk K8); `ultralytics` tetap ada (K1, modul 001) meski import-nya dihapus dari notebook 02 | — |

## Langkah

| # | Yang dibangun | File disentuh | Test | Gate (dari rencana-evaluasi) | Bergantung pada |
|---|---|---|---|---|---|
| 1 | Error pipeline baru untuk K9 revisi: tambah `GPUNotAvailableError` ke `00_pipeline_errors.ipynb` dan daftar nama error yang divalidasi | `notebooks/00_pipeline_errors.ipynb` (tambah 1 class); `tests/notebooks/test_pipeline_errors.py` (tambah `"GPUNotAvailableError"` ke `PIPELINE_ERROR_NAMES`) | `pytest tests/notebooks/test_pipeline_errors.py` — lulus | Tidak ada `docs/rencana-evaluasi.md` untuk rancangan ini (revisi model deteksi, bukan fase Dev evaluasi retrieval); gate cukup lulus test, sama seperti 001b/002b | — (langkah pertama) |
| 2 | Revisi K9 (deteksi pose → `rtmlib.Wholebody`, verifikasi GPU wajib, subset 17 dari 133 keypoint di dalam `detect_pose`) dan penyesuaian wiring orkestrasi (K12) yang memanggilnya; perbarui dependency dan `README.md` | Edit: `notebooks/02_face_upper_lower_body_detection_and_cropping.ipynb` (sel `## 1`, `## 2`, `## 5` ditulis ulang; sel runner `## 5` disesuaikan; sel `## 8` disesuaikan tanda tangan `process_image`/`process_identity`/`run_pipeline`); `requirements.txt` (tambah `rtmlib`, ganti `onnxruntime` → `onnxruntime-gpu`); `tests/notebooks/test_face_upper_lower_body_detection_and_cropping.py` (ganti test `load_pose_detector`/`detect_pose` yang mock `YOLO` menjadi mock `rtmlib.Wholebody`; tambah test `GPUNotAvailableError` lewat `onnxruntime.get_available_providers` yang di-mock dengan/tanpa `CUDAExecutionProvider`; sesuaikan pemanggilan `process_image`/`process_identity` di test yang ada — hapus argumen `pose_conf_threshold`); `README.md` (ganti sebutan "YOLOv8n-pose" → DWPose/`rtmlib`, tambah catatan GPU/CUDA wajib untuk notebook 02, hapus `POSE_CONF_THRESHOLD` dari daftar ambang) | `pytest tests/notebooks/test_face_upper_lower_body_detection_and_cropping.py tests/notebooks/test_pipeline_errors.py` — lulus, dengan `rtmlib.Wholebody` dan `onnxruntime.get_available_providers` di-mock (tanpa GPU sungguhan, tanpa mengunduh bobot DWPose) | Sama seperti langkah 1 — D4 tetap berlaku: definisi fungsi tidak memanggil model saat diimpor, sel `manual-run` sengaja tidak dieksekusi test dan akan raise `GPUNotAvailableError` kalau dijalankan tanpa CUDA (konsekuensi sadar titik periksa 10) | Langkah 1 (butuh `GPUNotAvailableError` sudah ada) |

## Tidak dibangun di rencana ini

- Pemindahan K1 (modul 001) dan K8 (deteksi wajah) ke GPU — ditolak eksplisit di titik periksa 11.
- Pemakaian 116 keypoint tambahan DWPose (feet/wajah/tangan) — ditolak eksplisit di titik periksa 12.
- Kalibrasi ambang (`KEYPOINT_CONF_THRESHOLD`, `MIN_SIDE_PX`, dll.) pada data asli — dilakukan Arya sendiri.
- Pengujian pipeline pada foto identitas sungguhan, termasuk verifikasi GPU/CUDA sungguhan berjalan — di luar cakupan pekerjaan pink-chan (D3, D4); dilakukan Arya di mesin dengan GPU, memakai sel runner (`tag: manual-run`) notebook 02.

## Risiko teknis

- **`detect_pose` berubah tanda tangan**: dari `(model, image_path, conf_threshold)` menjadi `(model, image)`. Ini konsekuensi teknis memakai API `rtmlib` (`wholebody(image)` menerima array gambar, bukan path, dan pseudocode K9 di 003a tidak menyebutkan parameter ambang confidence person-level pada pemanggilan `Wholebody`) — bukan perubahan keputusan produk. Akibatnya `POSE_CONF_THRESHOLD` (dulu dipakai sebagai `conf=` YOLO) dihapus dari config; `KEYPOINT_CONF_THRESHOLD` (K11, ambang per-keypoint) tidak berubah. Kalau ternyata `rtmlib.Wholebody` di versi yang terinstal nyata mengekspos parameter ambang person-level yang relevan, itu akan dilaporkan sebagai penyesuaian implementasi kecil, bukan keputusan baru.
- **Penggabungan `keypoints` (N,133,2) + `scores` (N,133) jadi array (17,3) per orang** dilakukan di dalam `detect_pose`, supaya `validate_single_person_pose`, `UPPER_KEYPOINT_INDICES`/`LOWER_KEYPOINT_INDICES`/`derive_body_part_bbox` (K10, K11) tidak perlu disentuh sama sekali — sesuai catatan 003a "K11 aturan tidak berubah, hanya sumber array keypoint/scores yang berbeda".
- **Bobot model DWPose diunduh otomatis oleh `rtmlib`** saat pertama dipakai (sama seperti `yolov8n-pose.pt`/`buffalo_sc` sebelumnya) — hanya terjadi di sel `manual-run`, tidak dieksekusi test.
- **Test tidak bisa memverifikasi GPU sungguhan** (mesin pink-chan kemungkinan tidak punya CUDA — dikonfirmasi sebagai konsekuensi sadar di 003a). Test memvalidasi logika verifikasi provider dengan `onnxruntime.get_available_providers` di-mock (dengan dan tanpa `"CUDAExecutionProvider"`), bukan menjalankan inferensi DWPose sungguhan.
- **Environment ini memakai Python 3.11.15** — memenuhi syarat `rtmlib` (`Python>=3.10` per S9 di `docs/keputusan-produk.md`), menjawab pemeriksaan teknis yang dicatat "Belum pasti" di 003a/keputusan-produk.
- **Versi persis `rtmlib` dan `onnxruntime-gpu`** dikunci (`==`) saat `pip install` benar-benar dijalankan di Langkah 2, bukan ditebak di rencana ini — kalau versi tertentu gagal terinstal atau konflik dengan `numpy==2.5.3`/`opencv-python-headless==5.0.0.93` yang sudah dipakai, dilaporkan dan disesuaikan pin di langkah itu, tanpa mengubah keputusan K9.
- **`ultralytics` tetap di `requirements.txt`** (dipakai K1, modul 001) walau baris `from ultralytics import YOLO` dihapus dari notebook 02 — hanya notebook 02 yang tidak lagi memakainya.
