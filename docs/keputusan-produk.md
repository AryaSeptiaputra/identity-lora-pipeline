# Keputusan Produk

Produk: Deteksi Manusia & Cropping untuk Persiapan Data Identitas
Jenis: Data pipeline (persiapan dataset untuk fine-tuning LoRA identitas)
Fase: MVP
Data: tingkat 0 — belum ada foto identitas asli; data pengganti publik: gambar demo resmi Ultralytics (`bus.jpg`, `zidane.jpg`); mode data rahasia: tidak aktif
Status: usulan
Diperbarui: 2026-09-26

## Ringkasan
Modul ini mengubah foto mentah per identitas (`data/raw/<identitas>/`) menjadi crop tubuh manusia siap pakai (`data/cropped/<identitas>/`) untuk tahap persiapan data LoRA berikutnya. Deteksi memakai YOLOv8n (kelas `person`), lalu dari semua orang yang terdeteksi di satu foto dipilih satu subjek utama sebelum dipotong dan disimpan. Dipakai secara internal oleh Arya dan pink-chan lewat notebook, bukan produk dengan pengguna akhir.

## Titik periksa
1. [Subjek] Bagaimana pipeline memilih bounding box saat satu foto berisi lebih dari satu orang?
   a. Satu box per foto, area terbesar (Usulan) — cocok untuk foto identitas solo, tapi bisa salah pilih kalau orang di latar justru tampak lebih besar dari subjek asli.
   b. Satu box per foto, confidence tertinggi — lebih tahan ke sudut kamera ganjil, tapi bisa salah pilih kalau orang di latar terdeteksi lebih yakin.
   c. Simpan semua box seperti draft lama — tidak ada data yang hilang, tapi mencemari dataset identitas dengan foto orang lain.

2. [Lisensi] Ultralytics YOLOv8 berlisensi AGPL-3.0 secara default — bagaimana status pemakaian pipeline ini?
   a. Dipakai internal saja, tidak didistribusikan atau dijual ke klien lain (Usulan) — kewajiban copyleft AGPL kemungkinan besar tidak berlaku, tapi tetap dicatat sebagai risiko kalau rencana bisnis berubah.
   b. Akan ditawarkan sebagai layanan/produk ke pihak lain — perlu Enterprise License Ultralytics berbayar, menambah biaya ke rancangan.
   c. Belum tahu model bisnisnya — keputusan ditunda, masuk "Belum pasti".

3. [DataUji] Data pengganti apa yang dipakai untuk menguji pipeline sebelum foto identitas asli tersedia?
   a. Gambar demo resmi Ultralytics: `bus.jpg` (banyak orang) dan `zidane.jpg` (dua orang) (Usulan) — sumber resmi dan legal, cukup untuk menguji kasus satu-orang dan banyak-orang, tapi tidak mirip foto potret identitas asli.
   b. Arya menyiapkan beberapa foto pribadi non-rahasia sendiri — lebih mirip data asli, tapi butuh disiapkan dulu sebelum pink-chan mulai.
   c. Tunda pengujian sampai foto identitas asli datang — paling akurat, tapi MVP tidak bisa dipastikan berjalan lebih dulu.

4. [Struktur] Kode inti (deteksi, pemilih subjek, cropping) langsung dipisah jadi modul Python sejak MVP, atau tetap di satu notebook dulu?
   a. Modul Python (`shared`, `detect`, `crop`) dipanggil dari notebook untuk orkestrasi dan demo (Usulan) — notebook berikutnya (alignment) bisa memakai ulang tanpa menyalin kode, dengan sedikit lebih banyak file di MVP pertama.
   b. Semua kode tetap di satu notebook dulu, dipisah nanti di fase Dev — paling cepat dibangun sekarang, tapi berisiko disalin manual saat notebook berikutnya dibuat.

## Bentrokan
| Bentrokan | Cara rancangan menghindarinya |
|---|---|
| Lisensi AGPL-3.0 Ultralytics YOLOv8 vs kemungkinan pipeline ini didistribusikan/dijual ke klien lain | Dijadikan titik periksa 2; default fase ini memakai asumsi "internal saja" sampai Arya konfirmasi model bisnisnya |
| Heuristik "satu subjek utama per foto" vs foto identitas asli yang mungkin berisi lebih dari satu pose/orang valid | Default MVP: satu box (area terbesar) per foto; mode "ambil semua box" disimpan sebagai opsi konfigurasi, tidak dipakai sampai dikonfirmasi |
| Data pengganti publik (frame berisi banyak orang) vs data asli (kemungkinan besar foto solo per identitas) | Data pengganti hanya untuk uji mekanik pipeline (kode berjalan), bukan uji kualitas pemilihan subjek; wajib dikalibrasi ulang begitu data asli identitas datang |
| Ambang confidence tetap (0.5) vs variasi pose/jarak kamera foto identitas asli yang belum diketahui | Ambang ditandai (sementara), dikalibrasi ulang setelah data asli tersedia |

## Asumsi
- Foto identitas asli pada umumnya berisi satu orang dominan (foto potret individu), bukan foto grup — mendasari keputusan K2.
- Tidak ada batasan GPU dari klien; YOLOv8n cukup ringan untuk berjalan di CPU laptop Arya pada fase MVP.
- Pipeline dijalankan manual per identitas oleh Arya/pink-chan lewat notebook, belum ada penjadwalan otomatis.
- Tidak ada kebutuhan antarmuka pengguna akhir; notebook dan modul adalah alat kerja developer, bukan produk yang dipakai orang lain.
- Nama "red-chan" dan "pink-chan" pada draft notebook adalah nama identitas uji coba, bukan data rahasia klien.

## Belum pasti
- Apakah pipeline ini akan didistribusikan atau ditawarkan sebagai layanan/produk ke pihak selain internal (menentukan risiko lisensi AGPL-3.0, titik periksa 2).
- Profil foto identitas asli: jumlah foto per identitas, resolusi, apakah selalu satu orang per foto atau bisa berisi orang lain di latar.
- Ketersediaan GPU di lingkungan produksi nanti (baru relevan kalau volume identitas membesar di fase Dev/Production).

## Ditunda
| Topik | Ditunda sampai |
|---|---|
| Face alignment / normalisasi ukuran & rasio crop | Notebook berikutnya dalam pipeline (tahap alignment) |
| Deduplikasi foto & quality filtering (blur, wajah tertutup, dsb.) | Fase Dev, setelah foto identitas asli tersedia |
| Mode "ambil semua subjek" per foto (untuk foto grup) | Fase Dev, kalau Arya konfirmasi kebutuhan ini |
| Pencatatan status per gambar (`storage/`) dan lanjut-dari-kegagalan | Fase Dev/Production, kalau volume identitas dan foto membesar |
| Penjadwalan otomatis dan pemberitahuan kegagalan | Fase Production |

---
<!-- Bagian teknis — dibaca pink-chan -->

## Gambaran sistem
| Bagian | Tugasnya | Terhubung ke |
|---|---|---|
| Notebook pipeline (K6) | Menjalankan alur deteksi → pemilihan subjek → cropping per identitas; menampilkan ringkasan jumlah crop dan gambar yang dilewati | Config bersama; Modul deteksi; Modul cropping |
| Config bersama (K6) | Menyimpan path `data/raw`, `data/cropped`, path bobot model, ambang confidence, padding, ambang ukuran minimum crop | Dibaca oleh semua bagian lain |
| Modul deteksi manusia — `HumanDetector` (K1) | Membungkus YOLOv8n, memfilter kelas `person`, mengembalikan daftar bounding box + confidence untuk satu gambar | Menerima path gambar dari notebook pipeline; mengirim daftar box ke pemilih subjek utama |
| Pemilih subjek utama (K2) | Dari daftar bounding box satu gambar, memilih satu box paling representatif (area terbesar; fallback confidence tertinggi bila area sama) | Menerima daftar box dari `HumanDetector`; mengirim satu box ke modul cropping; kalau daftar kosong, gambar dilewati dan dicatat |
| Modul cropping — `Cropper` (K3, K4) | Memotong region sesuai box + padding rasio; menolak dan mencatat crop yang sisinya di bawah ukuran minimum; menyimpan file hasil | Menerima box terpilih; membaca gambar asli dari `[data/raw/<identitas>]`; menulis ke `[data/cropped/<identitas>]` |
| `[data/raw/<identitas>]` | Folder foto mentah per identitas, tidak pernah diubah oleh pipeline | Dibaca notebook pipeline dan modul cropping |
| `[data/cropped/<identitas>]` | Folder hasil crop siap dipakai notebook pipeline berikutnya (alignment) | Ditulis oleh modul cropping |

## Keputusan
| # | Keputusan | Rancangan | Alasan | Label |
|---|---|---|---|---|
| D1 | Pengguna | Arya dan pink-chan (internal, developer); tidak ada pengguna akhir eksternal | Notebook dan modul adalah alat kerja persiapan data, bukan produk yang dipakai orang lain — asumsi | — |
| D2 | Cakupan | Deteksi manusia + pemilihan subjek utama + cropping, dari `data/raw/<identitas>/` ke `data/cropped/<identitas>/`, per identitas | Sesuai permintaan prompt; face alignment, dedup, filtering, dan training LoRA sengaja tidak dikerjakan di modul ini (lihat Ditunda) | — |
| D3 | Sumber data | Folder lokal per identitas disediakan Arya; foto identitas asli belum ada (tingkat 0); MVP diuji dengan data pengganti publik | Data asli belum tersedia saat rancangan ini dibuat | — |
| D4 | Tanda berhasil | Notebook berjalan end-to-end tanpa error pada data pengganti; jumlah crop tersimpan dan jumlah gambar dilewati (0 deteksi / crop terlalu kecil) tercetak di log | Ukuran sederhana yang bisa dicek langsung oleh Arya tanpa alat evaluasi tambahan | — |
| K1 | Model deteksi | YOLOv8n pretrained COCO via package `ultralytics`; filter kelas `person` (id 0); ambang confidence 0.5 (sementara — belum dikalibrasi pada data asli) | Sesuai permintaan prompt; nilai ambang mengikuti draft yang sudah dicoba. Lisensi paket ini AGPL-3.0 secara default — lihat titik periksa 2 | Umum [S1, S2] |
| K2 | Pemilihan subjek utama | Dari semua box `person` pada satu gambar, pilih satu dengan luas area terbesar; fallback confidence tertinggi bila luas sama | Foto identitas untuk LoRA diasumsikan berisi satu subjek dominan; mencegah crop orang lain di latar ikut masuk dataset — beda dari draft lama yang meng-crop semua deteksi | — |
| K3 | Validasi ukuran minimum crop | Tolak dan catat (skip) crop yang sisi terpanjangnya di bawah ambang piksel awal (nilai sementara, dikalibrasi setelah lihat distribusi ukuran data asli) | Mencegah crop terlalu kecil/blur ikut menjadi data training — pengetahuan umum persiapan dataset gambar | Umum |
| K4 | Padding crop | Rasio padding 0.1 di semua sisi, dipertahankan dari draft; belum menyeragamkan aspek rasio (square/rectangle) | Dipertahankan karena sudah pernah dicoba dan cukup untuk MVP; penyeragaman rasio didorong ke tahap alignment berikutnya | — |
| K5 | Re-run aman | Nama file hasil crop diturunkan dari nama file gambar asal (bukan penomoran acak), sehingga menjalankan ulang pipeline pada data yang sama menimpa file lama, bukan menduplikasi | Mengikuti aturan wajib pipeline data: tahap harus bisa dijalankan ulang tanpa merusak — pengetahuan umum | Umum |
| K6 | Struktur proyek (konseptual) | Kode inti dipisah jadi modul (config bersama, modul deteksi, modul pemilih subjek + cropping); notebook pipeline memanggil modul-modul itu untuk orkestrasi dan demo. Letak file dan penamaan persis ditentukan pink-chan | Supaya notebook pipeline berikutnya (alignment) bisa memakai ulang modul deteksi/cropping tanpa menyalin kode, sesuai aturan pertumbuhan pipeline data | — |

## Desain UI/UX
Tidak berlaku. Modul ini tidak punya antarmuka untuk pengguna akhir; notebook adalah alat kerja developer (Arya/pink-chan), dijalankan langsung sebagai kode, bukan disajikan sebagai produk dengan tampilan.

## Model data
Tidak berlaku. Hasil pipeline disimpan sebagai file gambar di sistem berkas (`data/raw/<identitas>/`, `data/cropped/<identitas>/`), bukan sebagai data terstruktur di basis data. Tidak ada skema tabel atau ERD yang perlu dirancang di fase ini.

## Sumber
| # | Sumber | Tingkat | Tanggal | Dipakai untuk |
|---|---|---|---|---|
| S1 | Ultralytics Docs — Explore YOLOv8 (docs.ultralytics.com/models/yolov8) | 1 · dokumentasi resmi | dibaca 2026-09-26 | Konfirmasi model YOLOv8n, kelas `person`, cara pakai via package `ultralytics` (K1) |
| S2 | Ultralytics — AGPL-3.0 Open Source License (ultralytics.com/legal/agpl-3-0-software-license) dan `ultralytics/ultralytics` file `LICENSE` di GitHub | 1 · halaman lisensi resmi dan repository resmi terverifikasi | dibaca 2026-09-26 | Dasar titik periksa 2: lisensi AGPL-3.0 default paket `ultralytics`, alternatif Enterprise License |
| S3 | GitHub `ultralytics/assets` (repository resmi terverifikasi, berisi `bus.jpg`, `zidane.jpg`) | 1 · repository resmi | dibaca 2026-09-26 | Usulan data pengganti publik untuk uji mekanik pipeline (titik periksa 3) |

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-09-26 | Rancangan pertama ditulis (usulan) | Permintaan Arya: bangun modul deteksi manusia (YOLOv8n) + cropping, struktur proyek awal |
