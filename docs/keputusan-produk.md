# Keputusan Produk

Produk: Deteksi Manusia, Wajah, dan Bagian Tubuh & Cropping untuk Persiapan Data Identitas
Jenis: Data pipeline (persiapan dataset untuk fine-tuning LoRA identitas)
Fase: MVP
Data: tingkat 0 — belum ada foto identitas asli; pengujian dengan data sungguhan dilakukan Arya sendiri, di luar cakupan rancangan ini; mode data rahasia: tidak aktif
Status: siap dikerjakan
Diperbarui: 2026-09-26

## Ringkasan
Pipeline ini mengubah foto mentah per identitas (`data/raw/<identitas>/`) menjadi crop siap pakai untuk tahap alignment LoRA berikutnya, dalam dua tahap berurutan. Tahap 1 (modul 001, notebook 0) mendeteksi manusia (YOLOv8n, kelas `person`), memvalidasi tepat satu orang per foto, dan memotong tubuh penuh ke `data/cropped/<identitas>/`. Tahap 2 (modul 002, notebook 1) membaca hasil tahap 1, mendeteksi wajah (InsightFace `buffalo_sc`, CPU) serta upper body dan lower body (DWPose via `rtmlib`, GPU wajib — direvisi dari YOLOv8n-pose CPU, lihat rancangan 003), lalu memotong masing-masing ke `data/face/<identitas>/`, `data/upper_body/<identitas>/`, `data/lower_body/<identitas>/`. Dipakai secara internal oleh Arya dan pink-chan; kode inti tetap satu notebook per tahap, pengujian dengan data sungguhan dilakukan Arya sendiri.

## Titik periksa
1. [Subjek] Bagaimana pipeline memilih bounding box saat satu foto berisi lebih dari satu orang?
   a. Satu box per foto, area terbesar — cocok untuk foto identitas solo, tapi bisa salah pilih kalau orang di latar tampak lebih besar dari subjek asli.
   b. Satu box per foto, confidence tertinggi — lebih tahan ke sudut kamera ganjil, tapi bisa salah pilih kalau orang di latar terdeteksi lebih yakin.
   c. Simpan semua box seperti draft lama — tidak ada data hilang, tapi mencemari dataset identitas dengan foto orang lain.
   d. Cakupan MVP disederhanakan: pipeline hanya menerima foto berisi 1 orang. Tepat 1 box → diproses; 0 box → lewati & log; >1 box → dianggap di luar cakupan, lewati & log peringatan (tidak ada pemilihan otomatis). ✓ 2026-09-26

2. [Lisensi] Ultralytics YOLOv8 berlisensi AGPL-3.0 secara default — bagaimana status pemakaian pipeline ini?
   a. Dipakai internal saja, tidak didistribusikan atau dijual ke klien lain (Usulan) — kewajiban copyleft AGPL kemungkinan besar tidak berlaku, tapi tetap dicatat sebagai risiko kalau rencana bisnis berubah. ✓ 2026-09-26
   b. Akan ditawarkan sebagai layanan/produk ke pihak lain — perlu Enterprise License Ultralytics berbayar, menambah biaya ke rancangan.
   c. Belum tahu model bisnisnya — keputusan ditunda, masuk "Belum pasti".

3. [DataUji] Data pengganti apa yang dipakai untuk menguji pipeline sebelum foto identitas asli tersedia?
   a. Gambar demo resmi Ultralytics: `bus.jpg` (banyak orang) dan `zidane.jpg` (dua orang) — sumber resmi dan legal, cukup untuk kasus satu-orang dan banyak-orang, tapi tidak mirip foto potret identitas asli.
   b. Arya menyiapkan beberapa foto pribadi non-rahasia sendiri — lebih mirip data asli, tapi butuh disiapkan dulu.
   c. Tunda pengujian sampai foto identitas asli datang — paling akurat, tapi MVP tidak bisa dipastikan berjalan lebih dulu.
   d. Pengujian dengan data sungguhan dilakukan Arya sendiri, di luar cakupan rancangan dan pekerjaan pink-chan. Codebase hanya divalidasi secara statis/impor (struktur benar, modul bisa diimpor), tanpa menjalankan pipeline sungguhan sebagai gate MVP. ✓ 2026-09-26

4. [Struktur] Kode inti (deteksi, validasi jumlah deteksi, cropping) langsung dipisah jadi modul Python sejak MVP, atau tetap di satu notebook dulu?
   a. Modul Python (`shared`, `detect`, `crop`) dipanggil dari notebook untuk orkestrasi dan demo — notebook alignment berikutnya bisa memakai ulang tanpa menyalin kode, dengan sedikit lebih banyak file di MVP pertama.
   b. Semua kode tetap di satu notebook dulu, dipisah nanti di fase Dev — paling cepat dibangun sekarang, tapi berisiko disalin manual saat notebook berikutnya dibuat. ✓ 2026-09-26

5. [SumberInput] Modul 002 (deteksi wajah/upper/lower) menerima gambar dari mana: hasil modul 001 atau langsung dari foto mentah?
   a. `data/cropped/<identitas>/` — hasil modul 001 (Usulan) — reuse validasi "1 orang" dan gambar yang sudah bersih dari modul 001, tapi menambah dependency wajib modul 001 dijalankan lebih dulu. ✓ 2026-09-26
   b. `data/raw/<identitas>/` — independen dari modul 001 — tidak perlu modul 001 selesai dulu, tapi mengulang logika validasi "tepat 1 orang" dan berisiko background/orang lain yang seharusnya sudah tersaring modul 001.

6. [LisensiWajah] Model pack `buffalo_sc` (InsightFace) berlisensi non-commercial research only — bagaimana status pemakaian di pipeline ini?
   a. Dipakai internal saja untuk riset/persiapan data, konsisten dengan keputusan AGPL di modul 001 (Usulan) — sejalan dengan keputusan Arya sebelumnya, tapi risiko tetap ada kalau LoRA hasil pipeline ini nanti dipakai/dijual komersial, karena data latihnya "diproses" oleh model non-commercial. ✓ 2026-09-26
   b. Ganti model deteksi wajah lain yang lisensinya lebih aman untuk kemungkinan komersial (mis. RetinaFace) — menghilangkan risiko lisensi, tapi menyimpang dari permintaan eksplisit Arya memakai `buffalo_sc`.
   c. Belum tahu model bisnis akhir — ditunda, masuk "Belum pasti"; pipeline tetap dibangun dengan `buffalo_sc` untuk fase MVP ini.

7. [CakupanJenis] Kalau salah satu jenis deteksi gagal untuk satu foto (misal wajah terdeteksi tapi pose tidak, atau sebaliknya), bagaimana?
   a. Independen per jenis: simpan crop yang berhasil, lewati & log jenis yang gagal (Usulan) — lebih banyak data terselamatkan, tapi bisa menghasilkan set crop tidak lengkap per foto. ✓ 2026-09-26
   b. Semua jenis harus berhasil dulu; kalau satu jenis gagal, seluruh foto dilewati untuk ketiga jenis — set crop selalu lengkap (triplet), tapi lebih banyak foto terbuang total.

8. [Keypoint] Bagaimana bbox upper/lower body dianggap valid kalau sebagian keypoint confidence-nya rendah/tidak terdeteksi?
   a. Minimal 1 titik anchor grup (bahu untuk upper, pinggul untuk lower) + minimal 2 titik total di grup itu lolos ambang confidence, baru bbox dihitung; kalau kurang → lewati jenis itu & log (Usulan) — menjaga kualitas box, tapi foto dengan pose miring/badan terpotong bisa banyak melewati upper atau lower. ✓ 2026-09-26
   b. Bbox dihitung dari titik apa pun yang tersedia di grup itu (minimal 1 titik saja) — lebih banyak foto terproses, tapi box bisa sangat kecil/tidak representatif kalau hanya 1 titik yang terdeteksi.

9. [PaketDW] (rancangan 003) Paket implementasi mana yang dipakai untuk DWPose?
   a. `rtmlib` (Wholebody class) (Usulan) — wrapper ringan onnxruntime-only (tanpa mmcv/mmdet/mmpose/torch), satu API `device="cpu"/"cuda"`, direkomendasikan resmi oleh `open-mmlab/mmpose`, label kematangan "Naik" (bukan "Umum"). ✓ 2026-09-26
   b. DWPose resmi (`IDEA-Research/DWPose`) + `mmpose`/`mmdet`/`mmcv` — kontrol penuh atas detector+pose, tapi instalasi jauh lebih berat dan berisiko konflik versi antar paket OpenMMLab.
   c. `controlnet_aux` (Hugging Face) `DWposeDetector` — didukung organisasi besar, tapi menambah dependency `torch`/`diffusers` yang tidak relevan untuk pipeline data sederhana ini.

10. [DeviceGPU] (rancangan 003) Kalau GPU/CUDA tidak tersedia saat notebook dijalankan, bagaimana?
    a. GPU dengan fallback otomatis ke CPU (Usulan red-chan) — onnxruntime otomatis pakai CPUExecutionProvider kalau CUDAExecutionProvider tidak terdeteksi, pipeline tetap jalan (lebih lambat) tanpa error.
    b. GPU wajib, gagal keras (raise error) kalau CUDA tidak tersedia — kode wajib memverifikasi eksplisit `onnxruntime.get_available_providers()` mengandung `CUDAExecutionProvider` sebelum/saat memuat model, dan melempar error jelas (`GPUNotAvailableError`) kalau tidak ada; TIDAK boleh diam-diam jatuh ke CPU. ✓ 2026-09-26 — **koreksi Arya, menolak usulan red-chan (a)**

11. [ModulLain] (rancangan 003) Apakah deteksi manusia (K1, modul 001) dan deteksi wajah (K8) juga dipindah ke GPU?
    a. Tidak, tetap CPU seperti sebelumnya (Usulan) — hanya K9 (pose/DWPose) yang pakai GPU sesuai permintaan eksplisit Arya, K1/K8 tidak disentuh. ✓ 2026-09-26
    b. Ya, pindahkan juga ke GPU (`ctx_id=0` InsightFace, device eksplisit YOLOv8n) — performa GPU konsisten di seluruh modul, tapi memperluas cakupan revisi di luar permintaan eksplisit Arya.

12. [CakupanKP] (rancangan 003) 133 keypoint DWPose mencakup wajah (68 titik) dan tangan (42 titik) tambahan — dipakai atau diabaikan?
    a. Diabaikan sepenuhnya, hanya 17 titik body (indeks 0-16) yang dipakai (Usulan) — cakupan modul 002 tidak berubah, tidak tumpang tindih dengan K8. ✓ 2026-09-26
    b. Titik wajah/tangan dipakai untuk sesuatu (misal crop tangan terpisah) — menambah cakupan baru (D2) yang belum diminta Arya, perlu rancangan tambahan.

## Bentrokan
| Bentrokan | Cara rancangan menghindarinya |
|---|---|
| Cakupan MVP (hanya 1 orang per foto, titik periksa 1) vs foto identitas asli yang mungkin memuat lebih dari 1 orang | Foto dengan >1 box dilewati dan dicatat sebagai peringatan, tidak diproses otomatis; volume foto yang berhasil diproses tergantung kurasi awal foto oleh Arya |
| Ambang confidence tetap (0.5) vs variasi pose/jarak kamera foto identitas asli yang belum diketahui | Ambang ditandai (sementara), dikalibrasi ulang oleh Arya sendiri setelah menjalankan pipeline pada data asli |
| Tanda berhasil MVP berbasis validasi statis (impor & struktur kode) vs belum ada bukti pipeline benar-benar berjalan pada gambar sungguhan | Diterima sebagai keputusan Arya (titik periksa 3); Arya yang menjalankan dan memvalidasi dengan data miliknya sendiri setelah kode selesai |
| Modul 002 bergantung pada output modul 001 (dependency antar notebook) | Urutan eksekusi dicatat di README: notebook 0 harus dijalankan sampai selesai sebelum notebook 1 (titik periksa 5) |
| Lisensi model `buffalo_sc` (non-commercial research only) vs kemungkinan model bisnis LoRA komersial di masa depan | Dipakai internal saja untuk fase ini (titik periksa 6); ditinjau ulang kalau model bisnis berubah, sama seperti AGPL modul 001 |
| Folder output baru `data/face/`, `data/upper_body/`, `data/lower_body/` vs `data/cropped/` yang sudah dipakai modul 001 sebagai output dan kini juga jadi input modul 002 | Folder output modul 002 sengaja tidak bersarang di bawah `data/cropped/`, dipisah di level yang sama (K13) |
| Cakupan independen per jenis deteksi (K12) vs kebutuhan triplet lengkap (face+upper+lower) untuk training LoRA berikutnya | Diterima sebagai keputusan Arya (titik periksa 7); pencocokan triplet didorong ke fase Dev kalau dibutuhkan (lihat Ditunda) |
| GPU wajib (K9 revisi rancangan 003, titik periksa 10) vs D4 tanda berhasil MVP (validasi statis/impor saja, tidak menjalankan model sungguhan) | Definisi fungsi tidak memanggil model sehingga validasi statis pink-chan tetap lolos tanpa GPU; hanya sel runner (manual-run) dan pemakaian sungguhan yang melempar `GPUNotAvailableError` kalau dijalankan tanpa CUDA — diterima sebagai konsekuensi sadar keputusan Arya, bukan bug |
| `onnxruntime` (dipakai K8, InsightFace) vs `onnxruntime-gpu` (dipakai K9 revisi, `rtmlib`) — dua paket berbagi nama modul `onnxruntime`, berisiko konflik binari kalau dua-duanya terpasang | requirements.txt hanya memasang SATU paket (`onnxruntime-gpu`), yang tetap menyediakan `CPUExecutionProvider` untuk K8 |

## Asumsi
- Foto identitas asli, pada cakupan MVP ini, sudah dikurasi berisi satu orang dominan per foto (bukan foto grup) — sesuai keputusan titik periksa 1.
- Modul 001 (YOLOv8n, K1) dan deteksi wajah modul 002 (`buffalo_sc`, K8) tetap diasumsikan berjalan di CPU tanpa GPU khusus (`ctx_id=-1` untuk InsightFace) — TIDAK diubah oleh rancangan 003 (titik periksa 11).
- Deteksi pose modul 002 (K9, direvisi rancangan 003) sekarang MEWAJIBKAN GPU (CUDA) tersedia di mesin tempat notebook benar-benar dijalankan — berbeda dari asumsi lama "tidak ada GPU sama sekali"; kalau tidak ada GPU, pipeline sengaja gagal keras (`GPUNotAvailableError`), bukan berjalan lebih lambat di CPU (titik periksa 10, koreksi Arya terhadap usulan awal red-chan).
- Pipeline dijalankan manual per identitas lewat notebook, belum ada penjadwalan otomatis.
- Nama "red-chan" dan "pink-chan" pada draft notebook adalah nama identitas uji coba, bukan data rahasia klien.
- Pipeline dipakai internal saja (tidak didistribusikan/dijual) — sesuai keputusan titik periksa 2 dan 6; kalau model bisnis berubah, lisensi AGPL-3.0 (YOLOv8n) maupun lisensi non-commercial `buffalo_sc` perlu ditinjau ulang.
- Foto input modul 002 sudah tervalidasi berisi 1 orang oleh modul 001 — modul 002 tidak mengulang pemilihan subjek, hanya mewarisi invarian itu (titik periksa 5).
- Tujuan crop upper/lower body adalah data latih LoRA per-region (bukan riset pose presisi), sehingga bbox sederhana dari keypoint sudah cukup untuk fase MVP ini; `mode="balanced"` DWPose dipilih dengan pertimbangan yang sama.

## Belum pasti
- Profil foto identitas asli: jumlah foto per identitas, resolusi, dan seberapa konsisten kurasi "satu orang per foto" bisa dijaga.
- Ketersediaan GPU di lingkungan produksi nanti untuk modul 001/K8 (baru relevan kalau volume identitas membesar di fase Dev/Production); untuk K9 (pose), GPU sudah menjadi kebutuhan wajib sejak rancangan 003.
- Hasil pengujian nyata oleh Arya pada data sungguhan — belum ada saat rancangan ini disetujui, karena sengaja di luar cakupan MVP.
- Apakah tahap training LoRA berikutnya membutuhkan set crop lengkap (face+upper+lower) per foto, atau cukup menerima crop yang independen — belum diputuskan, di luar cakupan modul 002.
- Versi CUDA/driver GPU di mesin tempat Arya akhirnya menjalankan notebook — menentukan versi `onnxruntime-gpu` yang kompatibel; red-chan tidak bisa memastikan versi ini dari rancangan, dicatat sebagai pemeriksaan teknis untuk pink-chan/Arya.
- Lisensi bobot model DWPose (file weight, bukan kode) belum ditemukan pernyataan eksplisit terpisah seperti `buffalo_sc`; kode DWPose dan `rtmlib` terkonfirmasi Apache-2.0, tapi bobot belum 100% terverifikasi terpisah — ditinjau ulang kalau model bisnis pipeline ini berubah menjadi komersial.

## Ditunda
| Topik | Ditunda sampai |
|---|---|
| Penanganan foto berisi lebih dari 1 orang (pemilihan subjek utama atau multi-crop) | Fase Dev, kalau Arya memutuskan memperluas cakupan |
| Face alignment / normalisasi ukuran & rasio crop | Notebook berikutnya dalam pipeline (tahap alignment) |
| Deduplikasi foto & quality filtering (blur, wajah tertutup, dsb.) | Fase Dev, setelah foto identitas asli tersedia |
| Pemisahan kode notebook menjadi modul Python (`shared`, `detect`, `crop`) | Fase Dev — MVP ini sengaja tetap satu notebook per tahap (titik periksa 4) |
| Pengujian pipeline dengan data sungguhan | Dikerjakan Arya sendiri setelah pink-chan menyelesaikan codebase; bukan gate MVP |
| Pencatatan status per gambar (`storage/`), lanjut-dari-kegagalan, penjadwalan otomatis | Fase Dev/Production |
| Manifest/pencocokan triplet crop (face+upper+lower) per foto per identitas | Fase Dev, kalau training LoRA berikutnya butuh set lengkap (lihat titik periksa 7) |
| Kalibrasi ambang modul 002 (`det_thresh`, `POSE_CONF_THRESHOLD`, `KEYPOINT_CONF_THRESHOLD`, `MIN_SIDE_PX`) pada data asli | Dilakukan Arya sendiri, sama seperti modul 001 |
| Pemakaian 116 keypoint tambahan DWPose (feet/wajah/tangan) untuk kebutuhan lain | Fase Dev, kalau Arya memutuskan memperluas cakupan (titik periksa 12) |
| Pemindahan modul 001 (K1) dan deteksi wajah (K8) ke GPU | Fase Dev, kalau Arya memutuskan memperluas cakupan (titik periksa 11) |

---
<!-- Bagian teknis — dibaca pink-chan -->

## Gambaran sistem

**Struktur folder (konseptual)** — letak dan penamaan file persis ditentukan pink-chan, mengikuti bentuk ini:
```
identity-lora-pipeline/
├── notebooks/
│   ├── 0_human_detection_and_cropping.ipynb   ← modul 001: config, HumanDetector,
│   │                                              validasi jumlah deteksi, Cropper, orkestrasi
│   └── 1_face_upper_lower_detection_and_cropping.ipynb  ← modul 002: config, deteksi
│                                              wajah (K8), deteksi pose (K9, DWPose GPU),
│                                              kelompok keypoint (K10, K11), Cropper (reuse),
│                                              orkestrasi
├── data/
│   ├── raw/<identitas>/         ← foto asli per identitas, disediakan Arya, tidak diubah
│   ├── cropped/<identitas>/     ← hasil crop tubuh penuh modul 001; input modul 002
│   ├── face/<identitas>/        ← hasil crop wajah modul 002 (K13)
│   ├── upper_body/<identitas>/  ← hasil crop upper body modul 002 (K13)
│   └── lower_body/<identitas>/  ← hasil crop lower body modul 002 (K13)
├── requirements.txt             ← ultralytics, opencv-python-headless, numpy, insightface,
│                                    onnxruntime-gpu, rtmlib, dst. (K9 revisi rancangan 003)
└── README.md                    ← cara menjalankan kedua notebook secara berurutan, letak data,
                                     kebutuhan GPU/CUDA wajib untuk notebook 1 (K9)
```
Bobot model (`yolov8n.pt`) memakai cache unduhan bawaan `ultralytics`; bobot `buffalo_sc` memakai cache unduhan bawaan `insightface` (`~/.insightface/models/`); bobot DWPose (`rtmlib`) diunduh otomatis dari mirror OpenMMLab/HuggingFace saat pertama dipakai dan dicache oleh `rtmlib` sendiri — tidak perlu folder khusus untuk fase ini. `yolov8n-pose.pt` tidak lagi dipakai (diganti DWPose, K9 revisi rancangan 003). Tidak ada `.env` karena tidak ada kredensial atau API key yang dipakai (model dan data seluruhnya lokal).

| Bagian | Tugasnya | Terhubung ke |
|---|---|---|
| Notebook 0 (K6) | Berisi seluruh kode inti modul 001: deteksi manusia, validasi jumlah deteksi, cropping, orkestrasi | Baca `[data/raw/<identitas>]`; tulis `[data/cropped/<identitas>]` |
| Config notebook 0 | Menyimpan path `data/raw`, `data/cropped`, path/nama bobot model, ambang confidence, padding, ambang ukuran minimum crop | Dibaca semua sel/fungsi lain di notebook 0 |
| `HumanDetector` (K1) | Membungkus YOLOv8n, memfilter kelas `person`, mengembalikan daftar bounding box + confidence untuk satu gambar | Menerima path gambar dari orkestrasi; mengirim daftar box ke validasi jumlah deteksi |
| Validasi jumlah deteksi (K2) | Memastikan tepat satu box `person` per gambar. 0 box → lewati & catat log. >1 box → lewati & catat log peringatan (di luar cakupan MVP), tidak dipilih otomatis | Menerima daftar box dari `HumanDetector`; kalau tepat 1, kirim box itu ke `Cropper` |
| `Cropper` (K3, K4) | Memotong region sesuai box + padding rasio; menolak dan mencatat crop yang sisinya di bawah ukuran minimum; menyimpan file hasil | Menerima box dari validasi jumlah deteksi; membaca gambar asli dari `[data/raw/<identitas>]`; menulis ke `[data/cropped/<identitas>]` |
| `[data/raw/<identitas>]` | Folder foto mentah per identitas, tidak pernah diubah oleh pipeline | Dibaca orkestrasi notebook 0 dan `Cropper` |
| `[data/cropped/<identitas>]` | Folder hasil crop tubuh penuh modul 001; **juga jadi input modul 002** | Ditulis `Cropper` (modul 001); dibaca orkestrasi notebook 1 (modul 002) |
| Notebook 1 (K16) | Berisi seluruh kode inti modul 002: config, deteksi wajah, deteksi pose, pengelompokan keypoint, Cropper (reuse pola modul 001), orkestrasi | Baca `[data/cropped/<identitas>]`; tulis `[data/face/<identitas>]`, `[data/upper_body/<identitas>]`, `[data/lower_body/<identitas>]` |
| Config notebook 1 | Menyimpan path input/output, nama model (`buffalo_sc`, `rtmlib.Wholebody`), `POSE_DEVICE="cuda"` (wajib), `POSE_MODE`, `KEYPOINT_CONF_THRESHOLD`, `det_thresh`, padding, ukuran minimum crop | Dibaca semua sel/fungsi lain di notebook 1 |
| Deteksi wajah (K8) | Membungkus `FaceAnalysis(name="buffalo_sc", allowed_modules=["detection"])`; mengembalikan bbox wajah; memvalidasi tepat 1 wajah; tetap CPU (`ctx_id=-1`), tidak diubah rancangan 003 | Menerima gambar dari `[data/cropped/<identitas>]`; mengirim bbox valid ke `Cropper` |
| Deteksi pose (K9, direvisi rancangan 003) | Membungkus `rtmlib.Wholebody` (DWPose); **sebelum memuat model, memverifikasi `onnxruntime.get_available_providers()` memuat `CUDAExecutionProvider`, lempar `GPUNotAvailableError` kalau tidak ada** (GPU wajib, tidak fallback CPU); mengembalikan 133 keypoint whole-body per orang (`keypoints`, `scores` terpisah); memvalidasi tepat 1 orang | Menerima gambar dari `[data/cropped/<identitas>]`; mengirim keypoint valid (subset 0-16) ke pengelompokan keypoint |
| Pengelompokan keypoint & bbox (K10, K11) | Mengambil subset indeks 0-16 dari 133 keypoint DWPose (116 titik feet/wajah/tangan diabaikan, titik periksa 12); membagi jadi grup upper/lower; menghitung bbox tiap grup dari titik yang lolos ambang; menolak grup dengan keypoint tidak cukup | Menerima keypoint dari deteksi pose; mengirim bbox upper/lower yang valid ke `Cropper` |
| `Cropper` notebook 1 (K14, K15) | Memotong region sesuai bbox (wajah/upper/lower) + padding; menolak crop di bawah ukuran minimum; menyimpan file, nama diturunkan dari nama asal | Menerima bbox dari deteksi wajah atau pengelompokan keypoint; menulis ke folder output masing-masing |
| `[data/face/<identitas>]` | Folder hasil crop wajah, siap dipakai tahap berikutnya | Ditulis `Cropper` notebook 1 |
| `[data/upper_body/<identitas>]` | Folder hasil crop upper body, siap dipakai tahap berikutnya | Ditulis `Cropper` notebook 1 |
| `[data/lower_body/<identitas>]` | Folder hasil crop lower body, siap dipakai tahap berikutnya | Ditulis `Cropper` notebook 1 |

## Keputusan
| # | Keputusan | Rancangan | Alasan | Label |
|---|---|---|---|---|
| D1 | Pengguna | Arya dan pink-chan (internal, developer); tidak ada pengguna akhir eksternal | Notebook dan kode adalah alat kerja persiapan data, bukan produk yang dipakai orang lain — asumsi | — |
| D2 | Cakupan | **Modul 001:** deteksi manusia + validasi tepat-satu-box + cropping, dari `data/raw/<identitas>/` ke `data/cropped/<identitas>/`, hanya foto berisi 1 orang. **Modul 002 (baru):** deteksi wajah (K8) serta upper/lower body dari keypoint pose (K9–K11), dan cropping masing-masing, dari `data/cropped/<identitas>/` ke `data/face/`, `data/upper_body/`, `data/lower_body/` — independen per jenis deteksi (K12) | Modul 001 disederhanakan sesuai keputusan Arya di titik periksa 1; modul 002 memperluas pipeline sesuai permintaan Arya (deteksi face/upper/lower), tanpa mengubah cakupan modul 001. Face alignment, dedup, filtering, multi-subjek, manifest triplet, dan training LoRA sengaja tidak dikerjakan (lihat Ditunda) | — |
| D3 | Sumber data | Folder lokal per identitas disediakan Arya; foto identitas asli belum ada (tingkat 0). **Modul 001** membaca `data/raw/<identitas>/`; **modul 002** membaca output modul 001 (`data/cropped/<identitas>/`), bukan raw langsung (titik periksa 5). Penyediaan dan pengujian data sungguhan **di luar cakupan rancangan dan pekerjaan pink-chan** — dilakukan Arya sendiri setelah kode selesai | Keputusan Arya di titik periksa 3 (berlaku untuk seluruh pipeline) dan titik periksa 5 (sumber input modul 002): fokus pekerjaan pink-chan adalah codebase, bukan data uji; modul 002 sengaja dibuat bergantung pada modul 001 supaya invarian "1 orang per foto" tidak perlu diulang | — |
| D4 | Tanda berhasil | Modul bisa diimpor tanpa error, seluruh kelas/fungsi (kedua notebook) ada dan sesuai rancangan di sini; **tidak** disyaratkan menjalankan pipeline pada gambar sungguhan sebagai gate MVP. Definisi fungsi K9 (DWPose, GPU wajib) tidak memanggil model saat diimpor, sehingga validasi statis tetap lolos tanpa GPU; `GPUNotAvailableError` hanya muncul kalau sel runner atau pemakaian sungguhan benar-benar dijalankan tanpa CUDA | Keputusan Arya di titik periksa 3: validasi statis/impor saja, pengujian nyata dilakukan Arya sendiri di luar rancangan ini; berlaku juga untuk modul 002 dan revisi K9 rancangan 003 | — |
| K1 | Model deteksi | YOLOv8n pretrained COCO via package `ultralytics`; filter kelas `person` (id 0); ambang confidence 0.5 (sementara — belum dikalibrasi pada data asli) | Sesuai permintaan prompt; nilai ambang mengikuti draft yang sudah dicoba. Lisensi AGPL-3.0 — dipakai internal saja sesuai keputusan Arya di titik periksa 2. Tetap CPU, tidak diubah rancangan 003 (titik periksa 11) | Umum [S1, S2] |
| K2 | Validasi jumlah deteksi (bukan pemilihan subjek) | Setiap gambar diharapkan menghasilkan **tepat satu** box `person`. 0 box → lewati, catat log. **>1 box → dianggap di luar cakupan MVP, lewati, catat log sebagai peringatan** — tidak ada logika memilih satu box otomatis dari banyak box | Keputusan Arya di titik periksa 1: cakupan MVP disederhanakan menjadi "hanya foto 1 orang", menggantikan usulan heuristik area terbesar/confidence tertinggi dan draft lama yang meng-crop semua deteksi | — |
| K3 | Validasi ukuran minimum crop | Tolak dan catat (skip) crop yang sisi terpanjangnya di bawah ambang piksel awal (nilai sementara, dikalibrasi Arya sendiri nanti) | Mencegah crop terlalu kecil/blur ikut menjadi data training — pengetahuan umum persiapan dataset gambar | Umum |
| K4 | Padding crop | Rasio padding 0.1 di semua sisi, dipertahankan dari draft; belum menyeragamkan aspek rasio (square/rectangle) | Dipertahankan karena sudah pernah dicoba dan cukup untuk MVP; penyeragaman rasio didorong ke tahap alignment berikutnya | — |
| K5 | Re-run aman | Nama file hasil crop diturunkan dari nama file gambar asal (bukan penomoran acak), sehingga menjalankan ulang pipeline pada data yang sama menimpa file lama, bukan menduplikasi | Mengikuti aturan wajib pipeline data: tahap harus bisa dijalankan ulang tanpa merusak — pengetahuan umum | Umum |
| K6 | Struktur proyek | Struktur **folder** dirancang sekarang (lihat diagram di atas: `notebooks/`, `data/raw/`, `data/cropped/`, `requirements.txt`, `README.md`). Struktur **kode** tetap satu notebook untuk fase ini — `HumanDetector`, validasi jumlah deteksi, `Cropper`, dan orkestrasi semua ditulis di dalam notebook yang sama, tidak dipecah jadi file `.py` | Keputusan Arya di titik periksa 4: kecepatan membangun MVP lebih diutamakan; pemisahan ke modul Python ditunda ke fase Dev | — |
| K7 | Sumber input modul 002 | Modul 002 membaca gambar dari `data/cropped/<identitas>/` (hasil modul 001), bukan `data/raw/` | Keputusan Arya di titik periksa 5: reuse invarian "tepat 1 orang" yang sudah divalidasi modul 001, gambar lebih bersih dari background/orang lain | — |
| K8 | Deteksi wajah | `insightface.app.FaceAnalysis(name="buffalo_sc", allowed_modules=["detection"])`, `ctx_id=-1` (CPU), `det_thresh=0.5` (sementara). `allowed_modules=["detection"]` membatasi hanya memuat model deteksi SCRFD-500MF, tidak memuat model recognition MBF@WebFace600K yang tidak dipakai. Validasi tepat 1 wajah per gambar (gaya sama dengan K2): 0 wajah → lewati+log info; >1 wajah → lewati+log peringatan, di luar cakupan. Tetap CPU, tidak diubah rancangan 003 (titik periksa 11) | Sesuai permintaan prompt Arya. Lisensi model `buffalo_sc`: **non-commercial research only** (berbeda dari lisensi kode `insightface` yang MIT) — dipakai internal saja sesuai keputusan Arya di titik periksa 6 | Naik [S4, S5] |
| K9 | Deteksi pose — **direvisi rancangan 003** | `rtmlib.Wholebody` (DWPose), `mode="balanced"`, `backend="onnxruntime"`, `device="cuda"`. **GPU wajib**: sebelum/saat memuat model, kode memverifikasi `onnxruntime.get_available_providers()` memuat `CUDAExecutionProvider`; kalau tidak ada, lempar `GPUNotAvailableError` (gagal keras, TIDAK fallback diam-diam ke CPU — ini koreksi Arya terhadap usulan awal red-chan yang mengusulkan fallback otomatis, titik periksa 10). Output: 133 keypoint whole-body per orang, `keypoints` (N,133,2) dan `scores` (N,133) sebagai dua array terpisah; hanya subset indeks 0-16 (17 body) yang dipakai (K10). Validasi tepat 1 orang per gambar (gaya sama dengan K2). Requirements.txt: tambah `rtmlib`; ganti `onnxruntime==1.30.0` → `onnxruntime-gpu` (SATU paket saja, tetap menyediakan `CPUExecutionProvider` untuk K8); `ultralytics` tetap ada (dipakai K1); bobot `yolov8n-pose.pt` tidak lagi dipakai | Permintaan Arya (rancangan 003): ganti model deteksi upper/lower body ke DWPose, runtime GPU. `rtmlib` dipilih sebagai wrapper (ringan, tanpa mmcv/mmpose/mmdet/torch, direkomendasikan resmi oleh `open-mmlab/mmpose`, titik periksa 9). GPU wajib (bukan fallback) adalah koreksi eksplisit Arya di titik periksa 10 | Naik [S8, S9, S10, S12] |
| K10 | Kelompok keypoint & bbox — **direvisi rancangan 003** | Upper body = indeks 0–10 (nose, left/right eye, left/right ear, left/right shoulder, left/right elbow, left/right wrist). Lower body = indeks 11–16 (left/right hip, left/right knee, left/right ankle) — indeks TIDAK berubah dari rancangan 002 karena 17 body pertama COCO-WholeBody (output DWPose) urutannya identik dengan COCO 17-keypoint standar. 116 keypoint sisanya (6 feet, 68 face, 42 hand, indeks 17-132) sengaja diabaikan sepenuhnya (titik periksa 12, menghindari tumpang tindih dengan K8). Bbox tiap grup = `min/max(x, y)` dari titik yang lolos ambang confidence keypoint dalam grup itu, lalu padding (K14) | Pembagian di garis pinggul mengikuti konvensi umum "upper garment vs lower garment" pada dataset crop tubuh untuk kebutuhan LoRA per-region — pengetahuan umum computer vision; subset 0-16 dan pengabaian feet/face/hand mengikuti skema resmi COCO-WholeBody dan keputusan Arya titik periksa 12 rancangan 003 | — [S10, S11] |
| K11 | Penanganan keypoint tidak lengkap | Grup (upper/lower) dianggap valid untuk di-crop kalau: (a) minimal satu titik "anchor" grup itu lolos ambang (bahu kiri/kanan untuk upper, pinggul kiri/kanan untuk lower), **dan** (b) minimal 2 titik total dari grup itu lolos ambang `KEYPOINT_CONF_THRESHOLD=0.5`. Aturan TIDAK berubah dari rancangan 002; hanya sumber array keypoint yang berubah — `rtmlib` mengembalikan `keypoints` (x,y) dan `scores` (confidence) sebagai dua array terpisah (bukan satu array `(17,3)` gabungan seperti Ultralytics dulu), sehingga titik "lolos ambang" digabung dari kedua array berdasarkan indeks yang sama sebelum aturan anchor+min-2-titik diterapkan. Kalau tidak terpenuhi → lewati jenis itu untuk gambar tersebut, catat log info, jenis lain tetap diproses (lihat K12) | Keputusan Arya di titik periksa 8 rancangan 002 (aturan tidak diubah); cara membaca sumber data disesuaikan ke API `rtmlib` (rancangan 003) | — |
| K12 | Cakupan per jenis deteksi | Independen: satu gambar bisa menghasilkan 0–3 crop (face/upper/lower). Kalau satu jenis gagal (0 deteksi, >1 deteksi, atau keypoint tidak cukup), jenis itu dilewati+log, jenis lain yang berhasil tetap disimpan. Tidak mensyaratkan ketiga jenis berhasil bersamaan | Keputusan Arya di titik periksa 7: lebih banyak data terselamatkan; risiko crop tidak berpasangan (triplet tidak lengkap) diterima dan didorong ke Ditunda kalau perlu dirapikan nanti | — |
| K13 | Struktur folder output modul 002 | `data/face/<identitas>/`, `data/upper_body/<identitas>/`, `data/lower_body/<identitas>/` — sengaja **bukan** bersarang di bawah `data/cropped/` (yang sudah dipakai modul 001 sebagai output dan kini menjadi input modul 002) | Menghindari ambiguitas "cropped di dalam cropped"; folder output baru dipisah di level yang sama dengan `data/cropped/` | — |
| K14 | Padding & ukuran minimum crop modul 002 | Reuse nilai dari K3/K4: `PADDING_RATIO=0.1`, `MIN_SIDE_PX=64` (sementara, sama-sama menunggu kalibrasi Arya). Fungsi crop+padding+validasi ukuran (bentuk `BoundingBox` yang sama seperti modul 001) dipakai ulang untuk ketiga jenis bbox — hanya sumber bbox-nya berbeda (langsung dari deteksi wajah, atau dihitung dari keypoint di K10) | Konsistensi dengan modul 001; menghindari duplikasi logika crop | Umum (pengetahuan umum) |
| K15 | Re-run aman modul 002 | Nama file hasil crop diturunkan dari nama file sumber: `<nama_asli>_face.jpg`, `<nama_asli>_upper.jpg`, `<nama_asli>_lower.jpg` | Sama seperti K5: menjalankan ulang pipeline menimpa, bukan menduplikasi — pengetahuan umum pipeline data | Umum |
| K16 | Struktur kode modul 002 | Notebook baru `notebooks/1_face_upper_lower_detection_and_cropping.ipynb`, seluruh kode functional (config sebagai konstanta, error class per kegagalan — termasuk `GPUNotAvailableError` baru untuk K9, logger, tanpa OOP) ditulis di notebook yang sama, tidak dipecah jadi file `.py` | Konsisten K6: kecepatan MVP diutamakan; pemisahan modul ditunda ke fase Dev untuk seluruh pipeline sekaligus | — |

## Desain UI/UX
Tidak berlaku. Modul-modul ini tidak punya antarmuka untuk pengguna akhir; notebook adalah alat kerja developer (Arya/pink-chan), dijalankan langsung sebagai kode, bukan disajikan sebagai produk dengan tampilan.

## Model data
Tidak berlaku. Hasil pipeline disimpan sebagai file gambar di sistem berkas (`data/raw/<identitas>/`, `data/cropped/<identitas>/`, `data/face/<identitas>/`, `data/upper_body/<identitas>/`, `data/lower_body/<identitas>/`), bukan sebagai data terstruktur di basis data. Tidak ada skema tabel atau ERD yang perlu dirancang di fase ini.

## Sumber
| # | Sumber | Tingkat | Tanggal | Dipakai untuk |
|---|---|---|---|---|
| S1 | Ultralytics Docs — Explore YOLOv8 (docs.ultralytics.com/models/yolov8) | 1 · dokumentasi resmi | dibaca 2026-09-26 | Konfirmasi model YOLOv8n, kelas `person`, cara pakai via package `ultralytics` (K1); dasar lisensi AGPL yang diwarisi K9 lama |
| S2 | Ultralytics — AGPL-3.0 Open Source License (ultralytics.com/legal/agpl-3-0-software-license) dan `ultralytics/ultralytics` file `LICENSE` di GitHub | 1 · halaman lisensi resmi dan repository resmi terverifikasi | dibaca 2026-09-26 | Dasar titik periksa 2: lisensi AGPL-3.0 default paket `ultralytics`, alternatif Enterprise License; masih berlaku untuk K1 (deteksi manusia modul 001, tidak diubah rancangan 003) |
| S3 | GitHub `ultralytics/assets` (repository resmi terverifikasi, berisi `bus.jpg`, `zidane.jpg`) | 1 · repository resmi | dibaca 2026-09-26 | Diusulkan sebagai data pengganti untuk uji mekanik pipeline; tidak dipakai karena Arya memilih menguji sendiri (titik periksa 3), disimpan sebagai catatan riset |
| S4 | GitHub `deepinsight/insightface`, `model_zoo/README.md` (repository resmi terverifikasi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K8 dan titik periksa 6: lisensi `buffalo_sc` "non-commercial research purposes only"; spesifikasi model (SCRFD-500MF + MBF@WebFace600K, tanpa alignment, 16MB) |
| S5 | GitHub `deepinsight/insightface`, `README.md` dan `python-package/README.md` (repository resmi terverifikasi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K8: lisensi kode MIT, cara pakai `FaceAnalysis(name=..., allowed_modules=...)`, `app.prepare(ctx_id=...)`, `app.get(image)` mengembalikan `bbox`/`kps`/`embedding`, dependency `onnxruntime` |
| S6 | GitHub `ultralytics/ultralytics`, `docs/en/tasks/pose.md` (repository resmi terverifikasi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K9 lama (YOLOv8n-pose, sudah diganti rancangan 003): cara load `YOLO("yolov8n-pose.pt")`, struktur output `result.keypoints.xy` / `.xyn` / `.data` — disimpan sebagai riwayat riset |
| S7 | GitHub `ultralytics/ultralytics`, `ultralytics/cfg/datasets/coco-pose.yaml` (file konfigurasi resmi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K10 (skema 17 keypoint COCO body): `kpt_shape: [17, 3]`, `flip_idx`, konfirmasi nama & urutan 17 keypoint COCO — masih berlaku karena urutan 17 body pertama COCO-WholeBody identik |
| S8 | GitHub `Tau-J/rtmlib` (repository resmi, direkomendasikan `open-mmlab/mmpose`) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K9 revisi: cara pakai `rtmlib.Wholebody`, parameter `mode`/`backend`/`device`, output `keypoints`/`scores` terpisah, dependency (numpy, opencv, onnxruntime; opsional onnxruntime-gpu/openvino/tensorrt) |
| S9 | PyPI `rtmlib` (pypi.org/project/rtmlib) | 1 · indeks paket resmi | dibaca 2026-09-26 | Dasar K9 revisi: versi 0.0.16 (rilis 2026-08-04, dalam 12 bulan terakhir), lisensi Apache-2.0, dependency `Python>=3.10` |
| S10 | GitHub `IDEA-Research/DWPose`, branch `onnx`, `README.md` + `LICENSE` (repository resmi paper ICCV 2023) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K9/K10 revisi: skema 133 keypoint whole-body (17 body + 6 feet + 68 face + 42 hand); lisensi Apache-2.0 (atribusi IDEA 2023 & OpenMMLab 2018-2020); versi resmi non-`rtmlib` butuh detector YOLOX terpisah (dipakai sebagai perbandingan alternatif yang ditolak) |
| S11 | GitHub `jin-s13/COCO-WholeBody` (repository resmi dataset ECCV 2020) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K10 revisi: komposisi resmi 133 keypoint (17 body + 6 feet + 68 face + 42 hand), dasar keputusan subset indeks 0-16 tetap identik dengan COCO 17-keypoint |
| S12 | GitHub `open-mmlab/mmpose`, `projects/rtmpose` (repository resmi OpenMMLab) | 1 · repository resmi | dibaca 2026-09-26 | Dasar titik periksa 9: `rtmlib` direkomendasikan resmi oleh mmpose sebagai cara inferensi RTMPose/DWPose tanpa mmcv/mmpose/mmdet — dasar syarat "dipakai luas" untuk label kematangan Naik |

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-09-26 | Rancangan pertama ditulis (usulan) | Permintaan Arya: bangun modul deteksi manusia (YOLOv8n) + cropping, struktur proyek awal |
| 2026-09-26 | Empat titik periksa dijawab Arya; D2–D4, K2, K6 disesuaikan; status menjadi siap dikerjakan | Arya menyederhanakan cakupan (hanya 1 orang/foto), memindahkan tanggung jawab pengujian ke dirinya sendiri, dan menahan kode dalam satu notebook untuk MVP |
| 2026-09-26 | Rancangan 002 ditambahkan: K7–K16 baru, D2/D3 diperluas secara aditif (K1–K6 modul 001 tidak diubah), empat titik periksa baru (5–8) dijawab Arya mengikuti usulan | Permintaan Arya: tambahkan modul deteksi wajah (InsightFace `buffalo_sc`), upper body dan lower body (YOLOv8n-pose) serta cropping-nya, sebagai lanjutan pipeline setelah modul 001 |
| 2026-09-26 | Rancangan 003: K9 direvisi in-place (model deteksi pose upper/lower body: YOLOv8n-pose CPU → DWPose via `rtmlib`, GPU) dan K10 (sumber keypoint: subset 0-16 dari 133 keypoint DWPose, 116 titik lain diabaikan); K11 aturan tidak berubah, hanya sumber datanya. K7, K8, K12–K16 tidak berubah. Empat titik periksa baru (9–12) dijawab Arya. **Titik periksa 10 (device GPU): Arya MENOLAK usulan awal red-chan (GPU dengan fallback otomatis ke CPU) dan mengoreksi ke GPU wajib** — kode harus memverifikasi eksplisit `onnxruntime.get_available_providers()` mengandung `CUDAExecutionProvider` dan melempar `GPUNotAvailableError` (gagal keras) kalau tidak ada, tidak boleh diam-diam jatuh ke CPU. requirements.txt diperbarui: tambah `rtmlib`, ganti `onnxruntime` → `onnxruntime-gpu` (satu paket) | Permintaan Arya: ganti model deteksi upper/lower body ke DWPose dengan runtime GPU (rancangan 003), termasuk koreksi eksplisit soal kebijakan device GPU |
