# Berkas dan Nilai Rahasia

Aturan ini berlaku untuk semua pekerjaan: membaca kode, menulis kode, merapikan struktur, dan menyiapkan production. Dirujuk oleh `writer-code`, `reader-code`, dan agent `pink-chan`.

---

## Yang termasuk berkas rahasia

| Jenis | Contoh nama |
|---|---|
| Setting lingkungan | `.env`, `.env.local`, `.env.production`, semua `.env.*` **kecuali** `.env.example` |
| Kunci dan sertifikat | `*.pem`, `*.key`, `*.p12`, `id_rsa`, `id_ed25519` |
| Kredensial layanan | `credentials*.json`, `service-account*.json`, `secrets.*`, `token*.json` |
| Kredensial alat | `.netrc`, `.pypirc`, `.npmrc`, `.git-credentials` |

Kalau ragu apakah sebuah berkas rahasia, perlakukan sebagai rahasia.

---

## Tidak boleh

- **Membuka atau menampilkan isinya**, dengan cara apa pun: membaca langsung, `cat`, `type`, `head`, atau pencarian teks yang menampilkan isi baris
- **Membuat berkas rahasia**, termasuk `.env` kosong. Yang dibuat hanya `.env.example`; Arya sendiri yang menyalinnya menjadi `.env` dan mengisi nilainya
- **Menyalin, memindahkan, mengganti nama, atau menghapus** berkas rahasia
- **Menuliskan nilai rahasia** ke kode, test, dokumen, laporan, log, atau pesan commit
- **Menulis nilai rahasia langsung di kode**, walaupun hanya sementara

---

## Boleh

- Mencatat **nama** berkas rahasia yang ada dan apakah sudah masuk `.gitignore`
- Membaca, membuat, dan memperbarui `.env.example` dengan **nilai kosong** atau contoh yang jelas palsu, misalnya `LLM_API_KEY=` atau `DATABASE_URL=postgresql://user:password@localhost:5432/dbname`
- Mencatat **nama** variabel setting yang dibaca kode, tanpa nilainya

---

## Saat menulis kode

1. **Nilai rahasia hanya dibaca lewat config dari environment.** Satu file config membaca `.env`; bagian lain kode mengambil dari config, bukan dari `.env` langsung.
2. **Tidak mencatat nilai rahasia ke log**, termasuk saat terjadi error. Log nama setting-nya saja kalau perlu.
3. **Test memakai nilai palsu**, tidak pernah membaca `.env` asli.
4. **Setiap setting baru ditambahkan ke `.env.example`** dengan nilai kosong dan satu baris keterangan.
5. **Saat membuat project baru, `.gitignore` wajib memuat** `.env`, `.env.*`, `!.env.example`, `*.pem`, `*.key`, dan `credentials*.json`.

---

## Saat mencari teks

Kecualikan berkas rahasia dari pencarian supaya isinya tidak ikut tampil. Contoh pada ripgrep: `--glob '!.env*'`, lalu sertakan kembali `.env.example` bila perlu.

---

## Kalau menemukan nilai rahasia di dalam kode

Misalnya kunci API atau kata sandi yang ditulis langsung di file `.py`:

1. Catat **lokasinya saja** (`file:baris`) dan jenisnya. **Jangan salin nilainya** ke mana pun.
2. Kalau pekerjaannya hanya membaca: masukkan sebagai temuan di laporan.
3. Kalau pekerjaannya memperbaiki kode: ganti dengan pembacaan dari config, tambahkan nama variabelnya ke `.env.example`, lalu minta Arya mengisi nilainya sendiri di `.env`.
4. Selalu sarankan agar nilai itu **diganti di penyedianya**, karena sudah pernah tersimpan di kode.

---

## Kalau berkas rahasia ikut tersimpan di git

Cek dengan `git ls-files`. Kalau ada berkas rahasia yang tercatat, laporkan sebagai temuan penting. **Jangan menghapus berkas atau mengubah riwayat git sendiri** — keputusan penanganannya ada di Arya.

---

## Kalau isi rahasia tidak sengaja terbaca

Jangan kutip, jangan pakai, dan sebutkan di laporan bahwa isi berkas tersebut sempat terbaca, supaya Arya bisa memutuskan perlu mengganti nilainya atau tidak.
