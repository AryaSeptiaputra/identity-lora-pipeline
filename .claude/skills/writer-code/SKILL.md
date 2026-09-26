---
name: writer-code
description: Standar penulisan kode Python Arya, termasuk penentuan struktur folder project. Dipakai setiap kali menulis, mereview, atau merapikan kode Python, dan saat memulai project baru, menambah bagian besar pada project yang ada, atau menyiapkan project untuk dipasang di server. Berlaku walau tidak diminta secara khusus, karena ini standar default untuk semua project Arya.
---

# Writer Code

**Prinsip:**

1. **Sesederhana mungkin yang masih cukup.** Kerumitan hanya ditambah kalau ada alasannya sekarang, bukan karena mungkin dibutuhkan nanti.
2. **Buat yang dipakai saja.** Folder kosong dan lapisan kosong lebih membingungkan daripada membantu.
3. **Struktur menyesuaikan pekerjaan project**, bukan satu bentuk untuk semua.
4. **Kode dibaca lebih sering daripada ditulis.** Nama dan urutan penulisan harus menunjukkan peran dan jangkauan setiap function.

---

## Bagian 1 — Struktur Project

Dipakai saat memulai project, menambah bagian besar, atau menyiapkan pemasangan ke server.

### Dua pertanyaan

**Pertanyaan 1: project ini pekerjaannya apa?** Boleh lebih dari satu.

| Pekerjaan | Template |
|---|---|
| Melayani pengguna dengan chatbot atau asisten AI | `references/structure-ai-app.md` |
| Menyiapkan data: mengambil, membaca, memotong, menyimpan ke pencarian | `references/structure-pipeline.md` |
| Melatih model atau membandingkan pendekatan | `references/structure-riset.md` |
| Menyajikan prediksi model yang sudah dilatih | `references/structure-api-model.md` |
| Perintah yang dijalankan lalu selesai | `references/structure-cli.md` |
| Mengelola data dan transaksi bisnis | `references/structure-app-bisnis.md` |

**Pertanyaan 2: ada bagian yang dijalankan terpisah?** Misalnya penyiapan data berjalan terjadwal, sementara chatbot melayani terus-menerus.

Kalau nanti dipasang di server berbeda, baca `references/structure-pisah-server.md` saat fase Production.

**Cara bertanya:** pakai `AskUserQuestion`. Lewati pertanyaan yang sudah jelas dari kalimat Arya, cukup konfirmasi satu baris. Kalau keduanya sudah jelas, langsung buat strukturnya tanpa bertanya.

### Kalau project mencakup lebih dari satu pekerjaan

1. Baca template setiap pekerjaan yang terlibat.
2. Tiap pekerjaan mendapat satu folder di dalam `app/`, dinamai sesuai pekerjaannya.
3. Kode yang dipakai bersama diletakkan di `app/shared/`.
4. Folder antar pekerjaan **tidak boleh saling import**. Hubungannya lewat data di `data/processed/`.
5. Isi tiap folder mengikuti templatenya masing-masing, dalam versi seringkas mungkin saat MVP.

Batas ini yang membuat bagian project bisa dipisah ke server lain nanti hanya dengan memindahkan folder.

### Mengikuti fase pekerjaan

| Fase | Yang dilakukan |
|---|---|
| **MVP** | Buat struktur dari template, hanya folder yang benar-benar dipakai |
| **Dev** | Tambah folder mengikuti aturan pertumbuhan di masing-masing template. Jangan bertanya ulang soal struktur |
| **Production** | Siapkan pemasangan. Kalau terpisah server, baca `references/structure-pisah-server.md` |

### Merapikan struktur project yang sudah ada

Dipakai hanya saat Arya meminta merapikan struktur project yang sudah punya kode. Pelajari project lebih dulu dengan `reader-code` — baca `.claude/skills/reader-code/SKILL.md`, skill ini tidak dimuat otomatis — untuk menulis `docs/peta-kode.md`, lalu ikuti `references/structure-refactor.md`.

Prinsipnya: hanya memindahkan kode dan memperbaiki import, satu folder per langkah, test dijalankan sebelum dan sesudah tiap langkah. Perilaku program tidak boleh berubah.

Untuk permintaan lain pada project yang sudah ada — menambah fitur, memperbaiki bug — ikuti pola yang sudah dipakai project itu, walaupun berbeda dari template.

### Aturan umum semua template

- Nama root package: `app/`. Pakai `src/` hanya kalau project akan dipasang sebagai package.
- `tests/` mengikuti susunan folder `app/`.
- `data/`, `models/`, `outputs/` di-gitignore, strukturnya dijaga dengan `.gitkeep`.
- Setting dibaca dari `.env` lewat satu file config. Tidak ada kunci, kata sandi, atau URL yang ditulis langsung di kode.
- **Berkas rahasia** (`.env`, kunci, kredensial): jangan dibuka, jangan dibuat, jangan dipindah, dan nilainya tidak pernah ditulis ke mana pun. Yang boleh dibuat hanya `.env.example` dengan nilai kosong. Aturan lengkap: `.claude/skills/writer-code/references/berkas-rahasia.md`.
- `.env.example` selalu ikut diperbarui saat ada setting baru.

---

## Bagian 2 — Aturan Penulisan Kode

Contoh lengkap yang menerapkan semua aturan di bawah ada di `references/pola-kode.md`. Baca saat menulis bagian yang belum pernah ditulis di project itu, misalnya setup logger, config, atau pengakses luar pertama.

### 2.1 Peran function

Setiap function punya satu **peran alur** dan satu **peran pekerjaan**.

**Peran alur**

| Peran | Tugas | Nama | Letak |
|---|---|---|---|
| Titik masuk | Menerima panggilan dari framework atau terminal, lalu menyerahkan ke proses. Tidak berisi logika | Nama aksinya, atau `main` | `api/`, `scripts/`, `commands/` |
| Proses | Merangkai langkah. Badannya terbaca seperti daftar langkah | Kata kerja tanpa `_` | Method publik di `services/` atau folder tahap |
| Sub-proses | Satu langkah dari proses di class atau file yang sama | `_kata_kerja` | Di atas proses yang memanggilnya (lihat 2.2) |

**Peran pekerjaan**

| Peran | Tugas | Awalan nama |
|---|---|---|
| Pembentuk | Membuat object siap pakai beserta dependensinya | `build_`, `create_` |
| Pengakses luar | Menyentuh file, database, jaringan, atau model | `load_`, `save_`, `fetch_`, `delete_`, atau kata kerja layanannya (`search`, `generate`, `embed`) |
| Pengubah bentuk | Mengubah data ke bentuk lain tanpa efek ke luar | `parse_`, `to_`, `from_`, `format_` |
| Pemeriksa | Menjawab ya/tidak, atau melempar error bila tidak valid | `is_`, `has_`, `can_` / `validate_` |
| Pembantu | Pekerjaan kecil umum tanpa state | Kata kerja yang menjelaskan pekerjaannya |

**Arah panggilan selalu ke bawah:** titik masuk → proses → sub-proses → peran pekerjaan. Pengakses luar, pengubah bentuk, pemeriksa, dan pembantu tidak pernah memanggil proses.

**Akses ke dunia luar hanya lewat pengakses luar.** Tidak ada query database atau pemanggilan API yang ditulis langsung di proses.

**Satu function, satu peran.** Nama yang memakai "dan" (`load_and_parse`) tandanya harus dipecah.

### 2.2 Penamaan dan urutan

**Tujuan:** pembaca tahu jangkauan dan peran function dari namanya saja. Selebihnya ikuti PEP 8.

**Jangkauan:**

| Dipanggil oleh | Nama |
|---|---|
| Hanya di class atau file yang sama | `_nama` — sub-proses atau bagian dalam |
| Class lain atau file lain | `nama` |

**Nama harus jujur:**
- Tentukan siapa pemanggilnya sebelum memberi nama.
- Saat pemanggilnya berubah, ganti namanya di semua tempat.

**Urutan penulisan dalam class:**
1. `__init__` paling atas.
2. Sub-proses, sesuai urutan dipanggil. Sub-proses yang lebih dalam ditulis di atas pemanggilnya.
3. Method publik yang merangkainya, di bawah sub-prosesnya.

Class dengan beberapa proses publik: tiap proses menjadi satu kelompok (sub-prosesnya lalu prosesnya). Sub-proses yang dipakai bersama diletakkan di kelompok pemakai pertamanya. Fungsi di level file mengikuti pola yang sama.

**Batas sub-proses:**
- Maksimal dua tingkat (`answer` → `_retrieve` → `_is_relevant`).
- Jangan membuat sub-proses yang hanya meneruskan panggilan ke class lain. Proses memanggil method publik class lain secara langsung.

**Jangan dipakai:** `__nama` (dua garis bawah di depan), dan jangan membuat nama `__nama__` sendiri.

### 2.3 Class atau fungsi

| Peran | Bentuk |
|---|---|
| Proses, pengakses luar | Class — menyimpan dependensi dan setting |
| Pembantu, pemeriksa, pengubah bentuk yang dipakai lintas file | Fungsi di `utils/` |
| Pengubah bentuk yang melekat pada bentuk datanya | Method di class Pydantic (`from_`, `to_`) |
| Pembentuk | Fungsi di `factory.py` |
| Titik masuk | Fungsi, sesuai framework-nya |

Di luar tabel: pakai class kalau ada state yang disimpan, beberapa method berbagi setting yang sama, atau ada lebih dari satu implementasi yang ditukar. Selain itu, fungsi biasa.

`interfaces.py` hanya dibuat saat ada dua implementasi yang dipakai bergantian di kode aplikasi. Class palsu di test tidak dihitung sebagai implementasi kedua.

### 2.4 Type hints

- Wajib di `app/` dan `scripts/`: semua parameter dan nilai kembalian, termasuk `-> None`. Opsional di notebook. Pemeriksaan tipe di `tests/` boleh dilonggarkan.
- Sintaks modern: `list[str]`, `dict[str, int]`, `X | None`. Modul `typing` hanya untuk yang belum ada padanannya: `Protocol`, `Callable`, `TypeVar`, `Any`.
- `Any` hanya dengan alasan tertulis di docstring. Utamakan class Pydantic untuk data yang bentuknya diketahui.
- Nilai default list atau dict memakai `None`, bukan `[]` atau `{}`.

### 2.5 Docstring dan komentar

**Bahasa:** default Indonesia dengan istilah teknis Inggris. Pakai bahasa lain kalau `CLAUDE.md` project atau klien menetapkannya, project yang sudah ada konsisten memakai bahasa lain, atau Arya memintanya. Dalam satu project tetap satu bahasa.

**Docstring:**
- Google style untuk function dan class publik. Opsional untuk yang berawalan `_`.
- Isi hanya deskripsi teknis, `Args`, `Returns`, `Raises`.

**Komentar wajib** di baris atas setiap pola yang tidak bisa dibaca langsung, menjelaskan maksud atau contoh hasilnya:
- Regex
- Format string logging (`%(asctime)s ...`)
- Format tanggal dan waktu (`%Y-%m-%d`)

Komentar lain hanya untuk hal yang tidak terbaca dari kodenya, misalnya alasan sebuah keputusan.

**Dilarang** di docstring, komentar, dan sel markdown notebook: hasil reasoning AI, kalimat pembuka ("Fungsi ini akan…"), kalimat penutup, dan basa-basi.

### 2.6 Penanganan error

- Kode berisiko — file, jaringan, model, komputasi berat — dibungkus `try`/`except` **di pengakses luar**, lalu diubah menjadi error milik project yang didefinisikan di `errors.py`.
- Tangkap exception yang spesifik. `except Exception` hanya boleh di titik masuk paling luar, dan wajib dicatat ke log.
- Tidak ada `except:` kosong. Tidak menelan error diam-diam.
- Catat dengan `exc_info=True`, lalu lempar ulang dengan `raise ... from e`.

### 2.7 Logging

- `print()` hanya untuk keluaran yang dibaca pengguna: hasil CLI dan notebook. Selain itu `logging`.
- Satu helper `setup_logger(name)` di `app/utils/logger.py`, atau `app/shared/logger.py` di project gabungan. Setiap file memanggil `logger = setup_logger(__name__)`.
- Format dipilih lewat setting `LOG_FORMAT`: `text` untuk pengembangan, `json` untuk production (`python-json-logger`). Level default `INFO`.
- Tidak mencatat nilai rahasia atau data pribadi, termasuk di level `DEBUG`.

### 2.8 Config

- Satu class `Settings` (`pydantic-settings`) di `config.py`, membaca `.env`, diikuti `settings = Settings()`.
- Bagian lain mengambil setting dari object `settings`, bukan memanggil `os.getenv` sendiri-sendiri.
- Parameter percobaan yang banyak disimpan sebagai file YAML di `configs/`.
- Setiap setting baru ditambahkan ke `.env.example`.

### 2.9 Dependency

- `pip` + virtual environment `.venv/`, Python 3.12+.
- Semua versi dikunci persis (`==`).
- `requirements.txt` untuk produksi. `requirements-dev.txt` dimulai dengan `-r requirements.txt` lalu alat pengembangan.
- Dependency yang bentrok dengan produksi, misalnya alat evaluasi, dipisah ke `requirements-<nama>.txt` dengan virtual environment sendiri.
- Dependency baru langsung ditambahkan ke file requirements yang tepat.

### 2.10 API

- `api/<kelompok>/routes.py` dan `schemas.py` berperan sebagai titik masuk. Logikanya ada di `services/`. Pengecualian: template aplikasi bisnis memakai `service.py` di dalam folder fiturnya.
- Endpoint `/health` di root; endpoint lain berawalan `/api/v1`.
- Pakai `async def` hanya kalau seluruh rantai pemanggilannya memakai client async. Kalau client-nya sinkron, pakai `def` biasa.
- Semua masukan dan keluaran memakai class Pydantic.
- Endpoint mengubah error milik project menjadi status HTTP, tanpa logika lain.

### 2.11 Notebook

- Untuk eksplorasi. Kode yang dipakai ulang dipindah ke `app/`.
- Notebook meng-import dari `app/`, tidak menyalin kode.
- Nama diberi nomor urut: `01-lihat-data.ipynb`.
- Sel markdown berisi judul tahap dan ringkasan percobaan.

### 2.12 Format keluaran kode

- Kode atau markdown yang diminta ditulis tanpa pembuka dan penutup.
- Jawaban yang memuat beberapa file: baris pertama tiap blok kode `# file: <path>`.

### 2.13 Selesai jika

- [ ] Kode berjalan tanpa error
- [ ] Test ditulis dan lulus
- [ ] Type hint lengkap di `app/` dan `scripts/`
- [ ] Docstring ada untuk yang publik, tanpa basa-basi
- [ ] Regex dan format string diberi komentar
- [ ] Nama sesuai jangkauan dan peran; urutan penulisan benar
- [ ] Akses ke dunia luar hanya lewat pengakses luar
- [ ] Error ditangkap secara spesifik
- [ ] Diagnosa memakai `logging`, bukan `print()`
- [ ] `requirements*.txt` dan `.env.example` diperbarui bila ada tambahan
- [ ] Tidak ada nilai rahasia di kode, log, atau test
- [ ] Letak file sesuai template struktur

### 2.14 Hindari

- `from module import *`
- Default argument berupa list atau dict
- `except:` kosong, atau menelan error diam-diam
- `print()` untuk diagnosa di `app/`
- Nilai rahasia di kode
- Docstring atau komentar berisi reasoning AI dan basa-basi
- Class yang hanya punya satu method statis
- Type hint gaya lama (`List`, `Optional`, `Union`)
- Badan function lebih dari 50 baris — tanda sebagian isinya harus jadi sub-proses
- Comprehension bersarang lebih dari dua tingkat
- State global yang bisa berubah
- Memanggil `_method` milik class lain
