# Keputusan Produk

Produk: Deteksi Manusia & Cropping untuk Persiapan Data Identitas
Jenis: Data pipeline (persiapan dataset untuk fine-tuning LoRA identitas)
Fase: MVP
Data: tingkat 0 — belum ada foto identitas asli; pengujian dengan data sungguhan dilakukan Arya sendiri, di luar cakupan rancangan ini; mode data rahasia: tidak aktif
Status: siap dikerjakan
Diperbarui: 2026-09-26

## Ringkasan
Modul ini mengubah foto mentah per identitas (`data/raw/<identitas>/`) menjadi crop tubuh manusia siap pakai (`data/cropped/<identitas>/`) untuk tahap persiapan data LoRA berikutnya. Deteksi memakai YOLOv8n (kelas `person`); MVP ini diasumsikan hanya menerima foto yang sudah berisi satu orang, jadi tidak ada logika pemilihan subjek di antara banyak orang. Dipakai secara internal oleh Arya dan pink-chan; kode inti tetap dalam satu notebook untuk fase ini, pengujian dengan data sungguhan dilakukan Arya sendiri.

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

## Bentrokan
| Bentrokan | Cara rancangan menghindarinya |
|---|---|
| Cakupan MVP (hanya 1 orang per foto, titik periksa 1) vs foto identitas asli yang mungkin memuat lebih dari 1 orang | Foto dengan >1 box dilewati dan dicatat sebagai peringatan, tidak diproses otomatis; volume foto yang berhasil diproses tergantung kurasi awal foto oleh Arya |
| Ambang confidence tetap (0.5) vs variasi pose/jarak kamera foto identitas asli yang belum diketahui | Ambang ditandai (sementara), dikalibrasi ulang oleh Arya sendiri setelah menjalankan pipeline pada data asli |
| Tanda berhasil MVP berbasis validasi statis (impor & struktur kode) vs belum ada bukti pipeline benar-benar berjalan pada gambar sungguhan | Diterima sebagai keputusan Arya (titik periksa 3); Arya yang menjalankan dan memvalidasi dengan data miliknya sendiri setelah kode selesai |

## Asumsi
- Foto identitas asli, pada cakupan MVP ini, sudah dikurasi berisi satu orang dominan per foto (bukan foto grup) — sesuai keputusan titik periksa 1.
- Tidak ada batasan GPU dari klien; YOLOv8n cukup ringan untuk CPU laptop Arya di fase MVP.
- Pipeline dijalankan manual per identitas lewat notebook, belum ada penjadwalan otomatis.
- Nama "red-chan" dan "pink-chan" pada draft notebook adalah nama identitas uji coba, bukan data rahasia klien.
- Pipeline dipakai internal saja (tidak didistribusikan/dijual) — sesuai keputusan titik periksa 2; kalau model bisnis berubah, lisensi AGPL-3.0 perlu ditinjau ulang.

## Belum pasti
- Profil foto identitas asli: jumlah foto per identitas, resolusi, dan seberapa konsisten kurasi "satu orang per foto" bisa dijaga.
- Ketersediaan GPU di lingkungan produksi nanti (baru relevan kalau volume identitas membesar di fase Dev/Production).
- Hasil pengujian nyata oleh Arya pada data sungguhan — belum ada saat rancangan ini disetujui, karena sengaja di luar cakupan MVP.

## Ditunda
| Topik | Ditunda sampai |
|---|---|
| Penanganan foto berisi lebih dari 1 orang (pemilihan subjek utama atau multi-crop) | Fase Dev, kalau Arya memutuskan memperluas cakupan |
| Face alignment / normalisasi ukuran & rasio crop | Notebook berikutnya dalam pipeline (tahap alignment) |
| Deduplikasi foto & quality filtering (blur, wajah tertutup, dsb.) | Fase Dev, setelah foto identitas asli tersedia |
| Pemisahan kode notebook menjadi modul Python (`shared`, `detect`, `crop`) | Fase Dev — MVP ini sengaja tetap satu notebook (titik periksa 4) |
| Pengujian pipeline dengan data sungguhan | Dikerjakan Arya sendiri setelah pink-chan menyelesaikan codebase; bukan gate MVP |
| Pencatatan status per gambar (`storage/`), lanjut-dari-kegagalan, penjadwalan otomatis | Fase Dev/Production |

---
<!-- Bagian teknis — dibaca pink-chan -->

## Gambaran sistem

**Struktur folder (konseptual)** — letak dan penamaan file persis ditentukan pink-chan, mengikuti bentuk ini:
```
identity-lora-pipeline/
├── notebooks/
│   └── 0_<nama proses>.ipynb   ← satu notebook: config, HumanDetector,
│                                  validasi jumlah deteksi, Cropper, orkestrasi
├── data/
│   ├── raw/<identitas>/         ← foto asli per identitas, disediakan Arya, tidak diubah
│   └── cropped/<identitas>/     ← hasil crop, ditulis pipeline
├── requirements.txt             ← ultralytics, opencv-python-headless, numpy, dst.
└── README.md                    ← cara menjalankan notebook, letak data
```
Bobot model (`yolov8n.pt`) memakai cache unduhan bawaan `ultralytics` (tidak perlu folder khusus untuk fase MVP). Tidak ada `.env` karena tidak ada kredensial atau API key yang dipakai (model dan data seluruhnya lokal).

| Bagian | Tugasnya | Terhubung ke |
|---|---|---|
| Notebook tunggal (K6) | Berisi seluruh kode inti dan orkestrasi pipeline per identitas; tidak dipecah jadi modul `.py` di fase ini | Baca `[data/raw/<identitas>]`; tulis `[data/cropped/<identitas>]` |
| Config (sel notebook) | Menyimpan path `data/raw`, `data/cropped`, path/nama bobot model, ambang confidence, padding, ambang ukuran minimum crop | Dibaca semua sel/fungsi lain di notebook |
| `HumanDetector` (K1) | Membungkus YOLOv8n, memfilter kelas `person`, mengembalikan daftar bounding box + confidence untuk satu gambar | Menerima path gambar dari orkestrasi; mengirim daftar box ke validasi jumlah deteksi |
| Validasi jumlah deteksi (K2) | Memastikan tepat satu box `person` per gambar. 0 box → lewati & catat log. >1 box → lewati & catat log peringatan (di luar cakupan MVP), tidak dipilih otomatis | Menerima daftar box dari `HumanDetector`; kalau tepat 1, kirim box itu ke `Cropper` |
| `Cropper` (K3, K4) | Memotong region sesuai box + padding rasio; menolak dan mencatat crop yang sisinya di bawah ukuran minimum; menyimpan file hasil | Menerima box dari validasi jumlah deteksi; membaca gambar asli dari `[data/raw/<identitas>]`; menulis ke `[data/cropped/<identitas>]` |
| `[data/raw/<identitas>]` | Folder foto mentah per identitas, tidak pernah diubah oleh pipeline | Dibaca orkestrasi dan `Cropper` |
| `[data/cropped/<identitas>]` | Folder hasil crop siap dipakai notebook pipeline berikutnya (alignment) | Ditulis oleh `Cropper` |

## Keputusan
| # | Keputusan | Rancangan | Alasan | Label |
|---|---|---|---|---|
| D1 | Pengguna | Arya dan pink-chan (internal, developer); tidak ada pengguna akhir eksternal | Notebook dan kode adalah alat kerja persiapan data, bukan produk yang dipakai orang lain — asumsi | — |
| D2 | Cakupan | Deteksi manusia + validasi tepat-satu-box + cropping, dari `data/raw/<identitas>/` ke `data/cropped/<identitas>/`, per identitas. **MVP hanya menangani foto yang berisi 1 orang** — foto dengan 0 atau >1 orang terdeteksi dilewati dan dicatat, bukan diproses | Disederhanakan sesuai keputusan Arya di titik periksa 1; face alignment, dedup, filtering, multi-subjek, dan training LoRA sengaja tidak dikerjakan di modul ini (lihat Ditunda) | — |
| D3 | Sumber data | Folder lokal per identitas disediakan Arya; foto identitas asli belum ada (tingkat 0). Penyediaan dan pengujian data sungguhan **di luar cakupan rancangan dan pekerjaan pink-chan** — dilakukan Arya sendiri setelah kode selesai | Keputusan Arya di titik periksa 3: fokus pekerjaan pink-chan adalah codebase, bukan data uji | — |
| D4 | Tanda berhasil | Modul bisa diimpor tanpa error, seluruh kelas/fungsi (`HumanDetector`, validasi jumlah deteksi, `Cropper`, orkestrasi) ada dan sesuai rancangan di sini; **tidak** disyaratkan menjalankan pipeline pada gambar sungguhan sebagai gate MVP | Keputusan Arya di titik periksa 3: validasi statis/impor saja, pengujian nyata dilakukan Arya sendiri di luar rancangan ini | — |
| K1 | Model deteksi | YOLOv8n pretrained COCO via package `ultralytics`; filter kelas `person` (id 0); ambang confidence 0.5 (sementara — belum dikalibrasi pada data asli) | Sesuai permintaan prompt; nilai ambang mengikuti draft yang sudah dicoba. Lisensi AGPL-3.0 — dipakai internal saja sesuai keputusan Arya di titik periksa 2 | Umum [S1, S2] |
| K2 | Validasi jumlah deteksi (bukan pemilihan subjek) | Setiap gambar diharapkan menghasilkan **tepat satu** box `person`. 0 box → lewati, catat log. **>1 box → dianggap di luar cakupan MVP, lewati, catat log sebagai peringatan** — tidak ada logika memilih satu box otomatis dari banyak box | Keputusan Arya di titik periksa 1: cakupan MVP disederhanakan menjadi "hanya foto 1 orang", menggantikan usulan heuristik area terbesar/confidence tertinggi dan draft lama yang meng-crop semua deteksi | — |
| K3 | Validasi ukuran minimum crop | Tolak dan catat (skip) crop yang sisi terpanjangnya di bawah ambang piksel awal (nilai sementara, dikalibrasi Arya sendiri nanti) | Mencegah crop terlalu kecil/blur ikut menjadi data training — pengetahuan umum persiapan dataset gambar | Umum |
| K4 | Padding crop | Rasio padding 0.1 di semua sisi, dipertahankan dari draft; belum menyeragamkan aspek rasio (square/rectangle) | Dipertahankan karena sudah pernah dicoba dan cukup untuk MVP; penyeragaman rasio didorong ke tahap alignment berikutnya | — |
| K5 | Re-run aman | Nama file hasil crop diturunkan dari nama file gambar asal (bukan penomoran acak), sehingga menjalankan ulang pipeline pada data yang sama menimpa file lama, bukan menduplikasi | Mengikuti aturan wajib pipeline data: tahap harus bisa dijalankan ulang tanpa merusak — pengetahuan umum | Umum |
| K6 | Struktur proyek | Struktur **folder** dirancang sekarang (lihat diagram di atas: `notebooks/`, `data/raw/`, `data/cropped/`, `requirements.txt`, `README.md`). Struktur **kode** tetap satu notebook untuk fase ini — `HumanDetector`, validasi jumlah deteksi, `Cropper`, dan orkestrasi semua ditulis di dalam notebook yang sama, tidak dipecah jadi file `.py` | Keputusan Arya di titik periksa 4: kecepatan membangun MVP lebih diutamakan; pemisahan ke modul Python ditunda ke fase Dev | — |

## Desain UI/UX
Tidak berlaku. Modul ini tidak punya antarmuka untuk pengguna akhir; notebook adalah alat kerja developer (Arya/pink-chan), dijalankan langsung sebagai kode, bukan disajikan sebagai produk dengan tampilan.

## Model data
Tidak berlaku. Hasil pipeline disimpan sebagai file gambar di sistem berkas (`data/raw/<identitas>/`, `data/cropped/<identitas>/`), bukan sebagai data terstruktur di basis data. Tidak ada skema tabel atau ERD yang perlu dirancang di fase ini.

## Sumber
| # | Sumber | Tingkat | Tanggal | Dipakai untuk |
|---|---|---|---|---|
| S1 | Ultralytics Docs — Explore YOLOv8 (docs.ultralytics.com/models/yolov8) | 1 · dokumentasi resmi | dibaca 2026-09-26 | Konfirmasi model YOLOv8n, kelas `person`, cara pakai via package `ultralytics` (K1) |
| S2 | Ultralytics — AGPL-3.0 Open Source License (ultralytics.com/legal/agpl-3-0-software-license) dan `ultralytics/ultralytics` file `LICENSE` di GitHub | 1 · halaman lisensi resmi dan repository resmi terverifikasi | dibaca 2026-09-26 | Dasar titik periksa 2: lisensi AGPL-3.0 default paket `ultralytics`, alternatif Enterprise License |
| S3 | GitHub `ultralytics/assets` (repository resmi terverifikasi, berisi `bus.jpg`, `zidane.jpg`) | 1 · repository resmi | dibaca 2026-09-26 | Diusulkan sebagai data pengganti untuk uji mekanik pipeline; tidak dipakai karena Arya memilih menguji sendiri (titik periksa 3), disimpan sebagai catatan riset |

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-09-26 | Rancangan pertama ditulis (usulan) | Permintaan Arya: bangun modul deteksi manusia (YOLOv8n) + cropping, struktur proyek awal |
| 2026-09-26 | Empat titik periksa dijawab Arya; D2–D4, K2, K6 disesuaikan; status menjadi siap dikerjakan | Arya menyederhanakan cakupan (hanya 1 orang/foto), memindahkan tanggung jawab pengujian ke dirinya sendiri, dan menahan kode dalam satu notebook untuk MVP |
