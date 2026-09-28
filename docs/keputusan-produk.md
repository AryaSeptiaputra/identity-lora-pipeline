# Keputusan Produk

Produk: Deteksi Manusia, Wajah, dan Bagian Tubuh & Cropping untuk Persiapan Data Identitas
Jenis: Data pipeline (persiapan dataset untuk fine-tuning LoRA identitas)
Fase: Dev
Data: tingkat 0 — belum ada foto identitas asli; pengujian dengan data sungguhan dilakukan Arya sendiri, di luar cakupan rancangan ini; mode data rahasia: tidak aktif
Status: siap dikerjakan
Diperbarui: 2026-09-28

## Ringkasan
Pipeline ini mengubah foto mentah per identitas (`data/raw/<identitas>/`) menjadi crop dan caption siap pakai untuk tahap training LoRA berikutnya, dalam tiga tahap berurutan. Notebook 01 (modul 001) mendeteksi manusia (YOLOv8n, kelas `person`) dan memotong tubuh penuh ke `data/cropped/<identitas>/`. Notebook 02 (modul 002) membaca hasil notebook 01, mendeteksi wajah (InsightFace `buffalo_sc`, CPU), dan memotong ke `data/face/<identitas>/`. Notebook 03 (modul 004, baru) membaca hasil notebook 01 dan 02, lalu memberi caption teks ke masing-masing gambar dengan model JoyCaption (VLM), disimpan sebagai file `.txt` bersebelahan. Definisi error pipeline dipisah ke notebook 00, dimuat oleh 01/02/03 lewat `%run`. Dipakai secara internal oleh Arya dan pink-chan; pengujian dengan data sungguhan dilakukan Arya sendiri.

**Perubahan besar sejak rancangan 003 (dicatat detail di rancangan 004):** deteksi upper body dan lower body (DWPose/`rtmlib`, K9–K12) **dihapus total** dari notebook 02 — notebook itu sekarang hanya mendeteksi dan memotong wajah. Validasi jumlah deteksi di notebook 01 dan 02 tidak lagi melewati foto yang berisi lebih dari satu box/wajah; keduanya sekarang **memilih otomatis** box/bbox dengan confidence tertinggi. Beberapa nilai ambang berubah. Notebook 03 (captioning) adalah kemampuan baru yang belum pernah dirancang sebelumnya.

## Titik periksa
1. [Subjek] Bagaimana pipeline memilih bounding box saat satu foto berisi lebih dari satu orang?
   a. Satu box per foto, area terbesar — cocok untuk foto identitas solo, tapi bisa salah pilih kalau orang di latar tampak lebih besar dari subjek asli.
   b. Satu box per foto, confidence tertinggi — lebih tahan ke sudut kamera ganjil, tapi bisa salah pilih kalau orang di latar terdeteksi lebih yakin.
   c. Simpan semua box seperti draft lama — tidak ada data hilang, tapi mencemari dataset identitas dengan foto orang lain.
   d. Cakupan MVP disederhanakan: pipeline hanya menerima foto berisi 1 orang. Tepat 1 box → diproses; 0 box → lewati & log; >1 box → dianggap di luar cakupan, lewati & log peringatan (tidak ada pemilihan otomatis). ✓ 2026-09-26 — **catatan rancangan 004: kode saat ini sudah menyimpang dari pilihan ini, lihat titik periksa 13**

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
   b. Semua kode tetap di satu notebook dulu, dipisah nanti di fase Dev — paling cepat dibangun sekarang, tapi berisiko disalin manual saat notebook berikutnya dibuat. ✓ 2026-09-26 — **catatan rancangan 004: definisi error (bukan seluruh kode) sudah dipisah ke notebook `00_pipeline_errors.ipynb`, dimuat lewat `%run`; sisanya (deteksi, crop, orkestrasi) tetap satu notebook per tahap seperti semula**

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
   — **catatan rancangan 004: jenis "pose/upper/lower" sudah tidak ada lagi di kode (dihapus), jadi keputusan ini kini hanya relevan untuk kombinasi wajah vs tubuh penuh**

8. [Keypoint] Bagaimana bbox upper/lower body dianggap valid kalau sebagian keypoint confidence-nya rendah/tidak terdeteksi?
   a. Minimal 1 titik anchor grup (bahu untuk upper, pinggul untuk lower) + minimal 2 titik total di grup itu lolos ambang confidence, baru bbox dihitung; kalau kurang → lewati jenis itu & log (Usulan) — menjaga kualitas box, tapi foto dengan pose miring/badan terpotong bisa banyak melewati upper atau lower. ✓ 2026-09-26 — **tidak lagi berlaku, kode upper/lower dihapus (rancangan 004)**
   b. Bbox dihitung dari titik apa pun yang tersedia di grup itu (minimal 1 titik saja) — lebih banyak foto terproses, tapi box bisa sangat kecil/tidak representatif kalau hanya 1 titik yang terdeteksi.

9. [PaketDW] (rancangan 003) Paket implementasi mana yang dipakai untuk DWPose?
   a. `rtmlib` (Wholebody class) (Usulan) — wrapper ringan onnxruntime-only (tanpa mmcv/mmdet/mmpose/torch), satu API `device="cpu"/"cuda"`, direkomendasikan resmi oleh `open-mmlab/mmpose`, label kematangan "Naik" (bukan "Umum"). ✓ 2026-09-26 — **tidak lagi relevan, deteksi pose dihapus dari kode (rancangan 004)**
   b. DWPose resmi (`IDEA-Research/DWPose`) + `mmpose`/`mmdet`/`mmcv` — kontrol penuh atas detector+pose, tapi instalasi jauh lebih berat dan berisiko konflik versi antar paket OpenMMLab.
   c. `controlnet_aux` (Hugging Face) `DWposeDetector` — didukung organisasi besar, tapi menambah dependency `torch`/`diffusers` yang tidak relevan untuk pipeline data sederhana ini.

10. [DeviceGPU] (rancangan 003) Kalau GPU/CUDA tidak tersedia saat notebook dijalankan, bagaimana?
    a. GPU dengan fallback otomatis ke CPU (Usulan red-chan) — onnxruntime otomatis pakai CPUExecutionProvider kalau CUDAExecutionProvider tidak terdeteksi, pipeline tetap jalan (lebih lambat) tanpa error.
    b. GPU wajib, gagal keras (raise error) kalau CUDA tidak tersedia — kode wajib memverifikasi eksplisit `onnxruntime.get_available_providers()` mengandung `CUDAExecutionProvider` sebelum/saat memuat model, dan melempar error jelas (`GPUNotAvailableError`) kalau tidak ada; TIDAK boleh diam-diam jatuh ke CPU. ✓ 2026-09-26 — **koreksi Arya, menolak usulan red-chan (a)** — **catatan rancangan 004: kode yang memakai pola ini (K9/DWPose) sudah dihapus; kelas `GPUNotAvailableError` masih ada di notebook 00 tapi tidak dipakai kode manapun saat ini. Notebook 03 (JoyCaption) memakai `device_map="auto"` tanpa verifikasi eksplisit seperti ini — lihat titik periksa 15**

11. [ModulLain] (rancangan 003) Apakah deteksi manusia (K1, modul 001) dan deteksi wajah (K8) juga dipindah ke GPU?
    a. Tidak, tetap CPU seperti sebelumnya (Usulan) — hanya K9 (pose/DWPose) yang pakai GPU sesuai permintaan eksplisit Arya, K1/K8 tidak disentuh. ✓ 2026-09-26
    b. Ya, pindahkan juga ke GPU (`ctx_id=0` InsightFace, device eksplisit YOLOv8n) — performa GPU konsisten di seluruh modul, tapi memperluas cakupan revisi di luar permintaan eksplisit Arya.

12. [CakupanKP] (rancangan 003) 133 keypoint DWPose mencakup wajah (68 titik) dan tangan (42 titik) tambahan — dipakai atau diabaikan?
    a. Diabaikan sepenuhnya, hanya 17 titik body (indeks 0-16) yang dipakai (Usulan) — cakupan modul 002 tidak berubah, tidak tumpang tindih dengan K8. ✓ 2026-09-26 — **tidak lagi relevan, seluruh deteksi keypoint dihapus (rancangan 004)**
    b. Titik wajah/tangan dipakai untuk sesuatu (misal crop tangan terpisah) — menambah cakupan baru (D2) yang belum diminta Arya, perlu rancangan tambahan.

13. **(baru, rancangan 004)** [PilihBox] Kode notebook 01 dan 02 saat ini memilih otomatis box/bbox dengan confidence tertinggi ketika ada lebih dari satu deteksi — ini bertentangan dengan titik periksa 1 (opsi d, disetujui) dan K8 (validasi wajah "di luar cakupan kalau >1"). Bagaimana status seharusnya?
    a. Ratifikasi: terima "pilih confidence tertinggi" sebagai keputusan final baru untuk K2 dan K8, menggantikan aturan skip-kalau->1 (Usulan berdasarkan kode yang sudah berjalan) — dokumentasi tinggal disesuaikan ke kode, tapi mewarisi risiko yang sama dengan opsi (b) yang dulu ditolak Arya di titik periksa 1: salah pilih kalau ada orang/wajah lain dengan confidence lebih tinggi di background.
    b. Kembalikan kode ke aturan lama (skip & log kalau >1 box/wajah, tidak dipilih otomatis) — konsisten dengan keputusan awal Arya, tapi perlu pink-chan mengubah kode notebook 01 dan 02 lagi.

14. **(baru, rancangan 004)** [CakupanTubuh] Deteksi upper body dan lower body (DWPose, K9–K12) sudah dihapus total dari notebook 02 dan folder `data/upper_body/`, `data/lower_body/` sudah tidak ada di working tree — apakah ini permanen di luar cakupan pipeline, atau akan dibangun ulang nanti?
    a. Permanen di luar cakupan untuk saat ini; pipeline fokus pada tubuh penuh + wajah + caption (Usulan berdasarkan kode saat ini) — README dan bagian "Gambaran sistem" di dokumen ini perlu dianggap final seperti ini, tapi kalau nanti dibutuhkan lagi harus dirancang ulang dari nol (K9–K12 tidak bisa langsung dipakai lagi karena rtmlib/DWPose sudah tidak dipasang).
    b. Direncanakan dibangun kembali di notebook terpisah pada rancangan berikutnya — cakupan tetap seperti rancangan 002/003, hanya ditunda sementara; requirements.txt dan dependency `rtmlib`/`onnxruntime-gpu` tetap dipertahankan.

15. **(baru, rancangan 004)** [GPUCaption] Notebook 03 (JoyCaption) memakai `device_map="auto"` (dari `accelerate`) tanpa verifikasi eksplisit CUDA tersedia — berbeda dari pola K9 lama (`GPUNotAvailableError` gagal keras). Kalau tidak ada GPU, `device_map="auto"` bisa diam-diam menempatkan model di CPU (sangat lambat untuk VLM) alih-alih gagal. Bagaimana kebijakannya?
    a. Ikuti pola yang sama seperti K9 lama: verifikasi eksplisit `torch.cuda.is_available()` sebelum memuat model, gagal keras dengan pesan jelas kalau tidak ada GPU (Usulan, konsisten dengan preferensi Arya di titik periksa 10) — perilaku konsisten di seluruh pipeline, tapi perlu pink-chan menambah pemeriksaan di notebook 03.
    b. Biarkan `device_map="auto"` menangani sendiri (fallback diam-diam ke CPU kalau perlu) — tidak ada perubahan kode, tapi berisiko notebook 03 "menggantung" berjalan sangat lambat di CPU tanpa peringatan jelas.

## Bentrokan
| Bentrokan | Cara rancangan menghindarinya |
|---|---|
| Cakupan MVP (hanya 1 orang per foto, titik periksa 1) vs foto identitas asli yang mungkin memuat lebih dari 1 orang | Foto dengan >1 box dilewati dan dicatat sebagai peringatan, tidak diproses otomatis; volume foto yang berhasil diproses tergantung kurasi awal foto oleh Arya — **catatan rancangan 004: kode saat ini sudah menyimpang, lihat titik periksa 13** |
| Ambang confidence tetap (kini 0.7 untuk manusia, 0.5 untuk wajah) vs variasi pose/jarak kamera foto identitas asli yang belum diketahui | Ambang ditandai (sementara), dikalibrasi ulang oleh Arya sendiri setelah menjalankan pipeline pada data asli |
| Tanda berhasil MVP berbasis validasi statis (impor & struktur kode) vs belum ada bukti pipeline benar-benar berjalan pada gambar sungguhan | Diterima sebagai keputusan Arya (titik periksa 3); Arya yang menjalankan dan memvalidasi dengan data miliknya sendiri setelah kode selesai |
| Modul 002 bergantung pada output modul 001 (dependency antar notebook) | Urutan eksekusi dicatat di README: notebook 01 harus dijalankan sampai selesai sebelum notebook 02, dan notebook 02 sebelum notebook 03 (titik periksa 5) |
| Lisensi model `buffalo_sc` (non-commercial research only) vs kemungkinan model bisnis LoRA komersial di masa depan | Dipakai internal saja untuk fase ini (titik periksa 6); ditinjau ulang kalau model bisnis berubah, sama seperti AGPL modul 001 |
| Folder output baru `data/face/` vs `data/cropped/` yang sudah dipakai modul 001 sebagai output dan kini juga jadi input modul 002 | Folder output modul 002 sengaja tidak bersarang di bawah `data/cropped/`, dipisah di level yang sama (K13) |
| Cakupan independen per jenis deteksi (K12) vs kebutuhan triplet lengkap (face+upper+lower) untuk training LoRA berikutnya | Tidak lagi relevan sepenuhnya — jenis "upper/lower" sudah dihapus dari kode (rancangan 004); pencocokan face vs tubuh penuh tetap didorong ke fase Dev kalau dibutuhkan (lihat Ditunda) |
| GPU wajib (K9 revisi rancangan 003) vs D4 tanda berhasil MVP (validasi statis/impor saja, tidak menjalankan model sungguhan) | Tidak lagi relevan — kode K9 (DWPose, GPU wajib) sudah dihapus dari notebook 02 (rancangan 004); kelas `GPUNotAvailableError` masih ada di notebook 00 tapi tidak dipanggil kode manapun saat ini |
| `onnxruntime` (dipakai K8, InsightFace) vs `onnxruntime-gpu` (dulu dipakai K9, `rtmlib`) — dua paket berbagi nama modul `onnxruntime`, berisiko konflik binari kalau dua-duanya terpasang | Catatan ini kini kurang relevan karena `rtmlib`/DWPose sudah dihapus dari kode; `requirements.txt` perlu ditinjau ulang pink-chan apakah `rtmlib`/`onnxruntime-gpu` masih perlu dipertahankan (lihat titik periksa 14) |
| **(baru, rancangan 004)** Kode saat ini (K2, K8: pilih confidence tertinggi otomatis) menyimpang dari keputusan Arya yang sudah disetujui (titik periksa 1 opsi d, K8: skip kalau >1) | Dicatat sebagai titik periksa 13 untuk diratifikasi atau dikembalikan; **belum dianggap keputusan final** sampai Arya menjawab |
| **(baru, rancangan 004)** `README.md` masih menjelaskan struktur lama (nama file notebook 02 dengan "upper_lower_body", folder `data/upper_body/`, `data/lower_body/`, GPU wajib untuk notebook 02) yang sudah tidak sesuai dengan kode aktual | Dicatat di sini sebagai temuan; **README belum diperbarui oleh red-chan** (di luar daftar file yang boleh ditulis red-chan) — perlu pink-chan atau Arya memperbarui README mengikuti isi dokumen ini setelah titik periksa 13/14 dijawab |
| **(baru, rancangan 004)** Notebook 03 (captioning) tidak punya penanganan error per gambar (tidak ada try/except untuk gambar rusak/tidak terbaca) seperti pola K2/K8 di notebook 01/02 | Diterima sebagai kondisi kode saat ini; didorong ke Ditunda sebagai perbaikan robustness fase Dev lanjutan, bukan pemblokir dokumentasi ini |

## Asumsi
- Foto identitas asli, pada cakupan MVP ini, sudah dikurasi berisi satu orang dominan per foto (bukan foto grup) — sesuai keputusan titik periksa 1, meski kode saat ini (titik periksa 13) tidak lagi menegakkan asumsi ini secara ketat karena otomatis memilih box confidence tertinggi kalau kurasi meleset.
- Modul 001 (YOLOv8n, K1) dan deteksi wajah modul 002 (`buffalo_sc`, K8) tetap diasumsikan berjalan di CPU tanpa GPU khusus (`ctx_id=-1` untuk InsightFace).
- Pipeline dijalankan manual per identitas lewat notebook, belum ada penjadwalan otomatis.
- Nama "red-chan" dan "pink-chan" pada draft notebook adalah nama identitas uji coba, bukan data rahasia klien.
- Pipeline dipakai internal saja (tidak didistribusikan/dijual) — sesuai keputusan titik periksa 2 dan 6; kalau model bisnis berubah, lisensi AGPL-3.0 (YOLOv8n), lisensi non-commercial `buffalo_sc`, maupun lisensi Meta Llama (JoyCaption, berbasis Llama) perlu ditinjau ulang.
- Foto input modul 002 sudah tervalidasi berisi 1 orang oleh modul 001 — modul 002 tidak mengulang pemilihan subjek, hanya mewarisi invarian itu (titik periksa 5).
- **(baru, rancangan 004)** Prompt captioning notebook 03 sengaja tidak mendeskripsikan fitur wajah permanen (bentuk mata/hidung/bibir/rahang), tone kulit, atau bentuk tubuh — asumsinya, atribut identitas itu harus dipelajari LoRA dari gambar langsung, bukan diverbalkan di caption, supaya tidak "terkunci" ke kata-kata caption saat training.
- **(baru, rancangan 004)** Trigger word `<nama>` di notebook 03 adalah placeholder yang diasumsikan akan diganti Arya dengan nama identitas sungguhan sebelum dipakai untuk training — belum ada mekanisme otomatis mengganti `<nama>` per identitas di kode saat ini.

## Belum pasti
- Profil foto identitas asli: jumlah foto per identitas, resolusi, dan seberapa konsisten kurasi "satu orang per foto" bisa dijaga.
- Ketersediaan GPU di lingkungan produksi nanti untuk modul 001/K8 (baru relevan kalau volume identitas membesar di fase Dev/Production).
- Hasil pengujian nyata oleh Arya pada data sungguhan — belum ada saat rancangan ini disetujui, karena sengaja di luar cakupan MVP.
- Apakah tahap training LoRA berikutnya membutuhkan set crop lengkap (face+tubuh penuh) per foto, atau cukup menerima crop yang independen — belum diputuskan.
- Versi CUDA/driver GPU di mesin tempat Arya akhirnya menjalankan notebook — relevan untuk notebook 03 (JoyCaption, butuh GPU praktis meski tidak divalidasi eksplisit, lihat titik periksa 15).
- **(baru, rancangan 004)** Apakah pengurangan cakupan (upper/lower body dihapus) bersifat permanen atau sementara — lihat titik periksa 14; sampai dijawab, dokumen ini menganggapnya sebagai kondisi kode saat ini, bukan keputusan final.
- **(baru, rancangan 004)** Lisensi bobot model JoyCaption (`fancyfeast/llama-joycaption-beta-one-hf-llava`, berbasis Meta Llama) — repository resminya menyertakan `LLAMA_LICENSE`, tunduk pada Llama Community License Meta (termasuk syarat izin tambahan kalau MAU pengguna bulanan produk melampaui ambang tertentu); belum diverifikasi detail penuh apakah ada klausul yang membatasi pemakaian internal seperti ini.
- **(baru, rancangan 004)** Apakah `requirements.txt` masih menyertakan `rtmlib`/`onnxruntime-gpu` walau kode DWPose sudah dihapus — perlu diperiksa pink-chan, karena mempengaruhi Bentrokan konflik paket `onnxruntime` yang dicatat di rancangan 003.

## Ditunda
| Topik | Ditunda sampai |
|---|---|
| Penanganan foto berisi lebih dari 1 orang (pemilihan subjek utama secara sengaja, bukan default confidence tertinggi tanpa disadari) | Dijawab lewat titik periksa 13 |
| Face alignment / normalisasi ukuran & rasio crop | Notebook berikutnya dalam pipeline (tahap alignment/training) |
| Deduplikasi foto & quality filtering (blur, wajah tertutup, dsb.) | Fase Dev, setelah foto identitas asli tersedia |
| Pengujian pipeline dengan data sungguhan | Dikerjakan Arya sendiri setelah pink-chan menyelesaikan codebase; bukan gate MVP |
| Pencatatan status per gambar (`storage/`), lanjut-dari-kegagalan, penjadwalan otomatis | Fase Dev/Production |
| Manifest/pencocokan pasangan crop (face + tubuh penuh + caption) per foto per identitas | Fase Dev, kalau training LoRA berikutnya butuh set lengkap |
| Kalibrasi ambang (`CONF_THRESHOLD`, `FACE_DET_THRESH`, `MIN_SIDE_PX`, `PADDING_RATIO`) pada data asli | Dilakukan Arya sendiri |
| Pembangunan kembali deteksi upper/lower body, kalau dibutuhkan | Dijawab lewat titik periksa 14 |
| Verifikasi GPU eksplisit untuk notebook 03 (JoyCaption) | Dijawab lewat titik periksa 15 |
| Penanganan error per gambar di notebook 03 (gambar rusak/tidak terbaca, retry) | Fase Dev lanjutan, perbaikan robustness |
| Mengganti trigger word `<nama>` otomatis per identitas di notebook 03 | Fase Dev lanjutan, kalau proses jadi tidak manual lagi |
| Pembaruan `README.md` mengikuti kondisi kode terbaru | Setelah titik periksa 13 dan 14 dijawab Arya |

---
<!-- Bagian teknis — dibaca pink-chan -->

## Gambaran sistem

**Struktur folder (kondisi kode saat ini, dikonfirmasi dari notebook)** — letak dan penamaan file lain di luar ini ditentukan pink-chan:
```
identity-lora-pipeline/
├── notebooks/
│   ├── 00_pipeline_errors.ipynb              ← kelas error pipeline, dimuat 01/02/03
│   │                                            lewat %run (K17, baru rancangan 004)
│   ├── 01_human_detection_and_cropping.ipynb ← modul 001: config, deteksi (K1, functional),
│   │                                            validasi+pilih box confidence tertinggi (K2
│   │                                            revisi), Cropper (K3, K4 revisi), orkestrasi
│   ├── 02_face_detection_and_cropping.ipynb  ← modul 002 (dipersempit rancangan 004):
│   │                                            HANYA deteksi wajah (K8 revisi) + cropping
│   │                                            (K14 revisi); deteksi pose/upper/lower body
│   │                                            (K9–K12 lama) SUDAH DIHAPUS dari notebook ini
│   └── 03_image_captioning.ipynb             ← modul baru (rancangan 004): caption gambar
│                                                dengan JoyCaption (K19–K23)
├── data/
│   ├── raw/<identitas>/         ← foto asli per identitas, disediakan Arya, tidak diubah
│   ├── cropped/<identitas>/     ← hasil crop tubuh penuh modul 001; input modul 002 & 03;
│   │                               setelah notebook 03 juga berisi file `.txt` caption
│   │                               bersebelahan (nama sama, stem sama)
│   └── face/<identitas>/        ← hasil crop wajah modul 002 (K13); input modul 03; setelah
│                                   notebook 03 juga berisi file `.txt` caption bersebelahan
│   (folder `data/upper_body/`, `data/lower_body/` TIDAK ADA lagi di kode/working tree
│    saat ini — dihasilkan dulu oleh K9–K13 lama yang sudah dihapus, rancangan 004)
├── requirements.txt             ← ultralytics, opencv-python-headless, numpy, insightface,
│                                    onnxruntime(-gpu), transformers, torch, accelerate, dst.
│                                    (isi persis perlu ditinjau ulang pink-chan, titik periksa 14)
└── README.md                    ← BELUM diperbarui mengikuti kondisi kode saat ini
                                     (lihat Bentrokan)
```
Bobot model (`yolov8n.pt`) memakai cache unduhan bawaan `ultralytics`; bobot `buffalo_sc` memakai cache unduhan bawaan `insightface` (`~/.insightface/models/`); bobot JoyCaption (`fancyfeast/llama-joycaption-beta-one-hf-llava`) diunduh otomatis oleh `transformers` dari Hugging Face Hub saat notebook 03 pertama dijalankan, dan dicache di cache bawaan Hugging Face. Tidak ada `.env` karena tidak ada kredensial atau API key yang dipakai (model dan data seluruhnya lokal/publik).

| Bagian | Tugasnya | Terhubung ke |
|---|---|---|
| Notebook 00 (K17, baru) | Berisi seluruh kelas error pipeline (`ImageReadError`, `DetectionError`, `NoDetectionError`, `MultipleDetectionError`, `CropTooSmallError`, `CropSaveError`, `FaceDetectionError`, `NoFaceDetectedError`, `MultipleFaceDetectedError`, `PoseDetectionError`, `NoPersonPoseDetectedError`, `MultiplePersonPoseDetectedError`, `InsufficientKeypointsError`, `GPUNotAvailableError`) | Dimuat oleh notebook 01, 02, 03 lewat `%run`; sebagian kelas (pose/keypoint/GPU) sudah tidak dipakai kode manapun saat ini (peninggalan K9–K12 lama) |
| Notebook 01 (K1–K6, direvisi) | Deteksi manusia (fungsi murni, bukan kelas), memilih box confidence tertinggi (K2 revisi), cropping+padding (K3, K4 revisi), orkestrasi per identitas | Baca `[data/raw/<identitas>]`; tulis `[data/cropped/<identitas>]` |
| Config notebook 01 | `CONF_THRESHOLD=0.7`, `PADDING_RATIO=0.2`, `MIN_SIDE_PX=256`, `DISPLAY_LIMIT=5` | Dibaca semua sel/fungsi lain di notebook 01 |
| `detect_humans` / `load_detector` (K1) | Fungsi (bukan kelas `HumanDetector` lagi) membungkus YOLOv8n, memfilter kelas `person`, mengembalikan daftar bounding box + confidence | Menerima path gambar; mengirim daftar box ke `validate_single_detection` |
| `validate_single_detection` (K2, **direvisi menyimpang dari titik periksa 1**) | 0 box → `NoDetectionError`, dilewati & dicatat. **>1 box → otomatis memilih box dengan confidence tertinggi (bukan lagi dilewati sebagai di luar cakupan)** | Menerima daftar box; mengirim satu box terpilih ke `crop_with_padding` |
| `crop_with_padding` / `save_crop` (K3, K4) | Memotong region sesuai box + padding 0.2; menolak dan mencatat crop yang sisinya di bawah 256px; menyimpan file hasil | Menerima box terpilih; membaca gambar dari `[data/raw/<identitas>]`; menulis ke `[data/cropped/<identitas>]` |
| `[data/raw/<identitas>]` | Folder foto mentah per identitas, tidak pernah diubah oleh pipeline | Dibaca orkestrasi notebook 01 |
| `[data/cropped/<identitas>]` | Folder hasil crop tubuh penuh modul 001; input modul 002 dan modul 03 | Ditulis notebook 01; dibaca notebook 02 dan notebook 03; setelah notebook 03 juga berisi `.txt` caption |
| Notebook 02 (K8, K13–K16, **dipersempit rancangan 004**) | HANYA deteksi wajah + cropping wajah. Deteksi pose/upper body/lower body (K9–K12 lama) tidak ada lagi di notebook ini | Baca `[data/cropped/<identitas>]`; tulis `[data/face/<identitas>]` |
| Config notebook 02 | `FACE_MODEL_NAME="buffalo_sc"`, `FACE_DET_THRESH=0.5`, `PADDING_RATIO=0.7` (khusus wajah, terpisah dari K3/K4), `MIN_SIDE_PX=64` | Dibaca semua sel/fungsi lain di notebook 02 |
| `detect_faces` / `validate_single_face` (K8, **direvisi menyimpang seperti K2**) | Membungkus `FaceAnalysis(name="buffalo_sc", allowed_modules=["detection"])`, `ctx_id=-1` (CPU). 0 wajah → `NoFaceDetectedError`, dilewati. **>1 wajah → otomatis memilih bbox confidence tertinggi (bukan lagi dilewati)** | Menerima gambar dari `[data/cropped/<identitas>]`; mengirim bbox terpilih ke `crop_with_padding` |
| `crop_with_padding` / `save_crop` notebook 02 (K14 revisi) | Memotong region wajah + padding 0.7; menolak crop kosong/di bawah 64px; menyimpan file, nama `<asal>_face.jpg` (K15, hanya suffix `_face` tersisa) | Menerima bbox terpilih; menulis ke `[data/face/<identitas>]` |
| `[data/face/<identitas>]` | Folder hasil crop wajah; input modul 03; setelah notebook 03 juga berisi `.txt` caption | Ditulis notebook 02; dibaca notebook 03 |
| Notebook 03 (K18–K23, **baru, rancangan 004**) | Membaca gambar dari `[data/cropped/<identitas>]` dan `[data/face/<identitas>]`, menghasilkan caption teks dengan JoyCaption per batch, menambahkan trigger word, menyimpan `.txt` bersebelahan gambar | Baca `[data/cropped/<identitas>]`, `[data/face/<identitas>]`; tulis file `.txt` di folder yang sama |
| Config notebook 03 | `MODEL_NAME="fancyfeast/llama-joycaption-beta-one-hf-llava"`, `TEMP=0.7`, `PROMPT` (4 bagian tetap, K20), `TRIGGER_WORD="<nama>"`, `CAPTION_IMAGE_LIMIT=5`, `CAPTION_BATCH_SIZE=2` | Dibaca semua sel/fungsi lain di notebook 03 |
| `load_vlm_model` (K19) | Memuat `AutoProcessor` + `LlavaForConditionalGeneration` JoyCaption, `torch_dtype=bfloat16`, `device_map="auto"` — **tidak ada verifikasi GPU eksplisit** (lihat titik periksa 15) | Dipanggil `run_captioning` |
| `generate_captions` (K19, K22) | Menjalankan satu forward pass `model.generate` untuk satu batch gambar sekaligus (bukan satu-satu), memakai prompt tetap dan `temperature` | Menerima daftar path gambar; mengembalikan daftar `ImageCaption` |
| `caption_images` (K22) | Membagi daftar gambar jadi batch ukuran `CAPTION_BATCH_SIZE`, memanggil `generate_captions` per batch, menyimpan dan mem-post-process tiap caption | Dipanggil `run_captioning`; memanggil `save_caption`, `post_process_caption` |
| `save_caption` / `post_process_caption` (K21, K23) | Menyimpan caption sebagai `.txt` (nama = stem gambar), menambahkan `TRIGGER_WORD` di awal secara idempoten | Menulis file `.txt` bersebelahan gambar sumber |
| `run_captioning` | Orkestrasi: memuat model sekali, memproses maksimal `cropped_limit`/`face_limit` gambar dari `data/cropped/` dan `data/face/` | Membaca `[data/cropped/<identitas>]`, `[data/face/<identitas>]`; menulis `.txt` di folder yang sama |

## Keputusan
| # | Keputusan | Rancangan | Alasan | Label |
|---|---|---|---|---|
| D1 | Pengguna | Arya dan pink-chan (internal, developer); tidak ada pengguna akhir eksternal | Notebook dan kode adalah alat kerja persiapan data, bukan produk yang dipakai orang lain — asumsi | — |
| D2 | Cakupan | **Modul 001 (notebook 01):** deteksi manusia + cropping tubuh penuh, dari `data/raw/` ke `data/cropped/`. **Modul 002 (notebook 02, dipersempit rancangan 004):** HANYA deteksi wajah + cropping, dari `data/cropped/` ke `data/face/` — upper/lower body dihapus dari cakupan aktif. **Modul baru (notebook 03, rancangan 004):** captioning gambar dari `data/cropped/` dan `data/face/`, output `.txt` bersebelahan | Modul 001 dan 002 disederhanakan/direvisi mengikuti kode aktual (lihat titik periksa 13, 14); modul captioning menambah kemampuan baru sesuai kode yang sudah ada. Face alignment, dedup, filtering, multi-subjek disengaja, manifest triplet, dan training LoRA sengaja tidak dikerjakan (lihat Ditunda) | — |
| D3 | Sumber data | Folder lokal per identitas disediakan Arya; foto identitas asli belum ada (tingkat 0). **Modul 001** membaca `data/raw/<identitas>/`; **modul 002** membaca output modul 001; **modul 03** membaca output modul 001 dan 002. Penyediaan dan pengujian data sungguhan **di luar cakupan rancangan dan pekerjaan pink-chan** | Keputusan Arya di titik periksa 3 dan 5 | — |
| D4 | Tanda berhasil | Modul bisa diimpor tanpa error, seluruh fungsi (keempat notebook) ada dan sesuai kode aktual di sini; **tidak** disyaratkan menjalankan pipeline pada gambar sungguhan sebagai gate MVP | Keputusan Arya di titik periksa 3; berlaku juga untuk notebook 00 dan 03 | — |
| K1 | Model deteksi manusia | YOLOv8n pretrained COCO via package `ultralytics`; filter kelas `person` (id 0); **ambang confidence 0.7 (diubah dari 0.5, rancangan 004, sementara — belum dikalibrasi pada data asli)** | Nilai ambang dinaikkan mengikuti kode aktual; alasan detail perubahan tidak tercatat sebelum rancangan 004, dicatat sebagai temuan dokumentasi. Lisensi AGPL-3.0 — dipakai internal saja (titik periksa 2). Tetap CPU | Umum [S1, S2] |
| K2 | Validasi jumlah deteksi manusia — **direvisi rancangan 004, menyimpang dari titik periksa 1** | 0 box → `NoDetectionError`, dilewati, catat log. **>1 box → sekarang OTOMATIS memilih box dengan confidence tertinggi** (`max(boxes, key=confidence)`), BUKAN lagi "dilewati sebagai di luar cakupan" seperti keputusan Arya semula | Perilaku kode saat ini menyimpang dari keputusan Arya yang sudah disetujui (titik periksa 1 opsi d). Dicatat sebagai temuan, **belum diratifikasi** — lihat titik periksa 13 | — |
| K3 | Validasi ukuran minimum crop tubuh penuh | `MIN_SIDE_PX=256` (eksplisit, sebelumnya tidak tertulis angkanya di dokumen; nilai sementara, dikalibrasi Arya nanti) | Mencegah crop terlalu kecil/blur ikut menjadi data training — pengetahuan umum persiapan dataset gambar | Umum |
| K4 | Padding crop tubuh penuh | `PADDING_RATIO=0.2` (diubah dari 0.1, rancangan 004) di semua sisi | Nilai diperbesar mengikuti kode aktual; alasan detail tidak tercatat sebelum rancangan 004 | — |
| K5 | Re-run aman | Nama file hasil crop diturunkan dari nama file gambar asal (`<asal>_person.jpg`), sehingga menjalankan ulang pipeline pada data yang sama menimpa file lama, bukan menduplikasi | Mengikuti aturan wajib pipeline data — pengetahuan umum. Tidak berubah | Umum |
| K6 | Struktur proyek dan kode modul 001 — **direvisi rancangan 004** | Struktur folder tidak berubah secara prinsip (lihat diagram). **Struktur kode: bukan lagi kelas `HumanDetector`, sekarang fungsi murni** (`load_detector`, `detect_humans`, `validate_single_detection`, `crop_with_padding`, dst.), sesuai gaya functional. Definisi error dipisah ke notebook 00 (K17) | Refactor ke functional style (ditemukan dari commit `38e8f3c`); pemisahan error notebook untuk dipakai bersama tiga notebook (K17) | — |
| K7 | Sumber input modul 002 | Modul 002 membaca gambar dari `data/cropped/<identitas>/` (hasil modul 001), bukan `data/raw/` | Keputusan Arya di titik periksa 5: reuse invarian "tepat 1 orang" yang sudah divalidasi modul 001. Tidak berubah | — |
| K8 | Deteksi wajah — **direvisi rancangan 004, menyimpang dari keputusan asli** | `insightface.app.FaceAnalysis(name="buffalo_sc", allowed_modules=["detection"])`, `ctx_id=-1` (CPU), `det_thresh=0.5`. 0 wajah → `NoFaceDetectedError`, dilewati. **>1 wajah → sekarang OTOMATIS memilih bbox dengan confidence tertinggi, BUKAN lagi dilewati sebagai di luar cakupan** | Sesuai permintaan awal Arya untuk model deteksi; tapi aturan "pilih otomatis kalau >1" menyimpang dari keputusan awal (gaya sama dengan K2). Lisensi `buffalo_sc`: non-commercial research only — dipakai internal saja (titik periksa 6). Dicatat sebagai temuan, **belum diratifikasi** — lihat titik periksa 13 | Naik [S4, S5] |
| K9 | ~~Deteksi pose (DWPose/rtmlib, GPU wajib)~~ — **DIHAPUS, rancangan 004** | Kode deteksi pose (`rtmlib.Wholebody`) sudah tidak ada lagi di notebook 02. Kelas `GPUNotAvailableError`, `PoseDetectionError`, dst. masih ada di notebook 00 tapi tidak dipanggil kode manapun | Ditemukan sudah dihapus dari kode aktual (commit `b5d5bb4`), tidak diketahui alasan eksplisit dari Arya — dicatat sebagai temuan dokumentasi, lihat titik periksa 14 | — |
| K10 | ~~Kelompok keypoint & bbox upper/lower~~ — **DIHAPUS, rancangan 004** | Kode pengelompokan keypoint upper/lower sudah tidak ada lagi | Sama seperti K9 — dihapus bersamaan | — |
| K11 | ~~Penanganan keypoint tidak lengkap~~ — **DIHAPUS, rancangan 004** | Aturan anchor+min-2-titik sudah tidak ada di kode manapun | Sama seperti K9 — dihapus bersamaan | — |
| K12 | ~~Cakupan independen per jenis deteksi (face/upper/lower)~~ — **tidak relevan lagi, rancangan 004** | Hanya tersisa satu jenis deteksi aktif di modul 002 (wajah); prinsip "independen per jenis" masih berlaku secara implisit antara modul 001/002/03 (satu identitas bisa punya crop tubuh, crop wajah, dan caption secara independen) | Cakupan upper/lower dihapus; sisa prinsip independensi tetap relevan lintas modul | — |
| K13 | Struktur folder output modul 002 — **dipersempit rancangan 004** | Hanya `data/face/<identitas>/`. `data/upper_body/<identitas>/` dan `data/lower_body/<identitas>/` **tidak lagi dihasilkan** dan tidak ada di working tree saat ini | Konsekuensi K9–K11 dihapus | — |
| K14 | Padding & ukuran minimum crop wajah — **direvisi rancangan 004** | `PADDING_RATIO=0.7` khusus wajah (bukan lagi reuse 0.1 dari K3/K4 lama), `MIN_SIDE_PX=64` (tidak berubah). Nilai padding wajah jauh lebih besar karena wajah butuh ruang crop lebih longgar dibanding body | Nilai padding wajah dipisahkan dari body dan diperbesar signifikan (0.1 → 0.7); alasan detail tidak tercatat sebelum rancangan 004, dicatat sebagai temuan dokumentasi | Umum (pengetahuan umum) |
| K15 | Re-run aman modul 002 — **dipersempit rancangan 004** | Nama file hasil crop: `<nama_asli>_face.jpg` saja. Suffix `_upper`/`_lower` tidak lagi diproduksi | Konsekuensi K9–K13 dihapus | Umum |
| K16 | Struktur kode modul 002 — **direvisi rancangan 004** | Notebook `02_face_detection_and_cropping.ipynb` (nama file berubah dari `1_face_upper_lower_body_detection_and_cropping.ipynb`), fungsional (bukan OOP), berisi HANYA deteksi+crop wajah. Error dimuat dari notebook 00 (K17) via `%run`, bukan didefinisikan ulang di sini | Konsisten K6; penamaan file & isi disesuaikan ke cakupan yang sudah dipersempit | — |
| K17 | **(baru, rancangan 004)** Pemisahan definisi error pipeline | Semua kelas `Exception` pipeline dipindah ke `notebooks/00_pipeline_errors.ipynb`, dimuat oleh notebook 01/02/03 lewat `%run "{PROJECT_ROOT / 'notebooks' / '00_pipeline_errors.ipynb'}"` | Menghindari duplikasi definisi error di tiga notebook berbeda — pengetahuan umum praktik notebook multi-tahap | Umum |
| K18 | **(baru, rancangan 004)** Sumber input captioning | Notebook 03 membaca gambar dari `data/cropped/<identitas>/` (modul 001, tubuh penuh) DAN `data/face/<identitas>/` (modul 002, wajah) — dua sumber independen, diproses terpisah dalam satu orkestrasi (`run_captioning`) | Mengikuti kebutuhan training LoRA: caption dibutuhkan untuk kedua jenis crop yang dipakai sebagai data latih | — |
| K19 | **(baru, rancangan 004)** Model captioning | JoyCaption `fancyfeast/llama-joycaption-beta-one-hf-llava` (VLM berbasis Llava/Llama) via `transformers.LlavaForConditionalGeneration` + `AutoProcessor`, `torch_dtype=bfloat16`, `device_map="auto"` (dari `accelerate`), `temperature=0.7`, `max_new_tokens=150` | Dipilih dari kode aktual (bukan riset red-chan sebelum dibangun — dicatat retroaktif). JoyCaption dikenal luas dipakai komunitas untuk captioning data training diffusion/LoRA yang bebas sensor (S13). Lisensi model tunduk pada Meta Llama Community License — **belum diverifikasi penuh** (Belum pasti) | Naik [S13] |
| K20 | **(baru, rancangan 004)** Prompt captioning terstruktur | Prompt tetap, 4 bagian wajib berurutan: (1) sudut kamera & framing, (2) HANYA ekspresi wajah & arah pandang (bukan bentuk mata/hidung/bibir/rahang), (3) fit pakaian (longgar/ketat), (4) detail pakaian (jenis, warna, pola, tekstur, aksesori). Melarang eksplisit deskripsi tone kulit, struktur wajah permanen, bentuk tubuh. Output: satu paragraf, tanpa label bagian, dipisah koma, maksimal 60 kata | Mencegah caption "mengunci" fitur identitas (wajah/bentuk tubuh) ke dalam teks — fitur itu harus dipelajari model dari piksel gambar saat training LoRA, bukan dari kata-kata caption (asumsi red-chan berdasarkan pola umum captioning dataset LoRA identitas) | — |
| K21 | **(baru, rancangan 004)** Trigger word | `TRIGGER_WORD="<nama>"` ditambahkan di awal caption (`"<nama>, <caption>"`) secara idempoten — `post_process_caption` mengecek prefix sebelum menambah, aman dijalankan berulang | Pola umum training LoRA/Dreambooth: trigger word dipakai untuk memicu konsep identitas saat inference. `<nama>` adalah placeholder yang perlu diganti Arya per identitas sebelum training (Belum pasti) | Umum |
| K22 | **(baru, rancangan 004)** Batching inferensi caption | `CAPTION_BATCH_SIZE=2`: gambar diproses per batch dalam satu `model.generate` (padding oleh `AutoProcessor`), bukan satu-satu. Ditemukan sebagai penambahan setelah captioning pertama kali dibangun (commit `c52d007` "Add batched image captioning") | Efisiensi inferensi VLM — pengetahuan umum (batching mengurangi overhead per-panggilan model dibanding loop satu gambar) | Umum |
| K23 | **(baru, rancangan 004)** Penyimpanan caption | Caption disimpan sebagai file `.txt` bersebelahan gambar sumber, nama sama (stem sama, mis. `foto1_person.txt` untuk `foto1_person.jpg`) — menimpa saat re-run (re-run aman, konsisten K5/K15) | Format umum untuk dataset training LoRA (image + caption `.txt` berpasangan) — pengetahuan umum | Umum |

## Desain UI/UX
Tidak berlaku. Modul-modul ini tidak punya antarmuka untuk pengguna akhir; notebook adalah alat kerja developer (Arya/pink-chan), dijalankan langsung sebagai kode, bukan disajikan sebagai produk dengan tampilan.

## Model data
Tidak berlaku. Hasil pipeline disimpan sebagai file gambar dan file teks caption di sistem berkas (`data/raw/<identitas>/`, `data/cropped/<identitas>/`, `data/face/<identitas>/`), bukan sebagai data terstruktur di basis data. Tidak ada skema tabel atau ERD yang perlu dirancang di fase ini.

## Sumber
| # | Sumber | Tingkat | Tanggal | Dipakai untuk |
|---|---|---|---|---|
| S1 | Ultralytics Docs — Explore YOLOv8 (docs.ultralytics.com/models/yolov8) | 1 · dokumentasi resmi | dibaca 2026-09-26 | Konfirmasi model YOLOv8n, kelas `person`, cara pakai via package `ultralytics` (K1) |
| S2 | Ultralytics — AGPL-3.0 Open Source License (ultralytics.com/legal/agpl-3-0-software-license) dan `ultralytics/ultralytics` file `LICENSE` di GitHub | 1 · halaman lisensi resmi dan repository resmi terverifikasi | dibaca 2026-09-26 | Dasar titik periksa 2 |
| S3 | GitHub `ultralytics/assets` (repository resmi terverifikasi, berisi `bus.jpg`, `zidane.jpg`) | 1 · repository resmi | dibaca 2026-09-26 | Diusulkan sebagai data pengganti untuk uji mekanik pipeline; tidak dipakai (titik periksa 3) |
| S4 | GitHub `deepinsight/insightface`, `model_zoo/README.md` (repository resmi terverifikasi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K8 dan titik periksa 6: lisensi `buffalo_sc` |
| S5 | GitHub `deepinsight/insightface`, `README.md` dan `python-package/README.md` (repository resmi terverifikasi) | 1 · repository resmi | dibaca 2026-09-26 | Dasar K8: lisensi kode MIT, cara pakai `FaceAnalysis` |
| S6–S12 | (lihat rancangan 002/003 di riwayat) — dasar K9–K12 lama (YOLOv8n-pose, DWPose/`rtmlib`, COCO-WholeBody) | 1 | dibaca 2026-09-26 | **Tidak lagi relevan** untuk kode aktif setelah rancangan 004 (K9–K12 dihapus); dipertahankan di riwayat sebagai jejak keputusan |
| S13 | Hugging Face `fancyfeast/llama-joycaption-beta-one-hf-llava` (halaman model dan file `LLAMA_LICENSE`); GitHub `fpgaminer/joycaption` (repository resmi proyek JoyCaption) | 2 · halaman model pembuat + repository proyek open-source individu, dipakai luas komunitas captioning dataset diffusion/LoRA | dibaca 2026-09-28 | Dasar K19: konfirmasi model berbasis Llava/Llama, keberadaan `LLAMA_LICENSE` (Meta Llama Community License) — **klaim performa dan cakupan lisensi penuh belum ditelaah lebih dalam, dicatat "Belum pasti"** |

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-09-26 | Rancangan pertama ditulis (usulan) | Permintaan Arya: bangun modul deteksi manusia (YOLOv8n) + cropping, struktur proyek awal |
| 2026-09-26 | Empat titik periksa dijawab Arya; D2–D4, K2, K6 disesuaikan; status menjadi siap dikerjakan | Arya menyederhanakan cakupan (hanya 1 orang/foto), memindahkan tanggung jawab pengujian ke dirinya sendiri, dan menahan kode dalam satu notebook untuk MVP |
| 2026-09-26 | Rancangan 002 ditambahkan: K7–K16 baru, D2/D3 diperluas secara aditif, empat titik periksa baru (5–8) dijawab Arya | Permintaan Arya: tambahkan modul deteksi wajah, upper body dan lower body serta cropping-nya |
| 2026-09-26 | Rancangan 003: K9 direvisi in-place (YOLOv8n-pose CPU → DWPose via `rtmlib`, GPU) dan K10; empat titik periksa baru (9–12) dijawab Arya, termasuk koreksi GPU wajib | Permintaan Arya: ganti model deteksi upper/lower body ke DWPose dengan runtime GPU |
| 2026-09-28 | **Rancangan 004 (dokumentasi retroaktif) ditambahkan.** Notebook diberi nomor `00`–`03`: `00_pipeline_errors.ipynb` baru (pemisahan kelas error, K17); `01_human_detection_and_cropping.ipynb` direvisi (fungsional bukan kelas, K2 kini otomatis pilih confidence tertinggi — menyimpang dari titik periksa 1, `CONF_THRESHOLD` 0.5→0.7, `PADDING_RATIO` 0.1→0.2, `MIN_SIDE_PX` eksplisit 256); `02_face_detection_and_cropping.ipynb` dipersempit total (K9–K12 deteksi pose/upper/lower DIHAPUS, K8 kini otomatis pilih confidence tertinggi — menyimpang dari desain awal, `PADDING_RATIO` wajah jadi 0.7 terpisah dari body); `03_image_captioning.ipynb` BARU (JoyCaption, K18–K23, ditambah batching di commit `c52d007`). Tiga titik periksa baru (13–15) ditulis untuk meminta Arya meratifikasi atau membatalkan penyimpangan dari keputusan sebelumnya, karena perubahan ini ditemukan sudah ada di kode sebelum sempat melalui alur usulan→persetujuan normal | Permintaan Arya (lewat sesi lain): catat dokumentasi terhadap perubahan kode yang sudah terjadi di notebook 00–03 pada branch `data-preparation`, sebelum sempat didokumentasikan |
