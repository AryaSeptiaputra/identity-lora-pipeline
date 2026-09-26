# Template: Tool CLI

Dipakai untuk perintah yang dijalankan lalu selesai: konversi berkas, pengolahan sekali jalan, tugas berkala.

**File lain untuk pekerjaan lain:**
- Pengolahan data bertahap yang perlu mencatat status: `structure-pipeline.md`
- Layanan yang hidup terus menerima permintaan: `structure-ai-app.md` atau `structure-api-model.md`

---

## Bentuk foldernya

Tool CLI biasanya kecil. Mulai dari bentuk paling sederhana.

**Kalau hanya satu perintah:**

```
project-name/
├── main.py                 # seluruh isinya di sini
├── tests/
├── .env / .env.example
├── requirements.txt
└── README.md
```

**Kalau sudah lebih dari satu perintah, atau main.py mulai panjang:**

```
project-name/
├── app/
│   ├── config.py
│   ├── commands/           # satu file per perintah
│   │   ├── convert.py
│   │   └── report.py
│   ├── core/               # logika utama yang dipakai perintah
│   └── utils/
├── main.py                 # hanya membaca argumen dan memanggil commands/
├── tests/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

---

## Tiga aturan wajib

1. **`main.py` tidak berisi logika.** Tugasnya hanya membaca argumen lalu memanggil fungsi di `commands/`. Dengan begitu logikanya bisa dites tanpa menjalankan perintah.
2. **Pesan ke pengguna memakai `print()`, catatan proses memakai logging.** Hasil yang dibaca pengguna dan catatan untuk menelusuri masalah jangan dicampur.
3. **Beri kode keluar yang benar.** Berhasil keluar dengan 0, gagal dengan angka selain 0, supaya bisa dipakai di penjadwal atau skrip lain.

---

## Saat fase MVP

Satu berkas `main.py` sudah cukup. Jangan membuat folder `app/` sebelum benar-benar dibutuhkan.

---

## Saat fase Dev, tiga aturan pertumbuhan

1. **Perintah baru jadi file baru di `commands/`.**
2. **`main.py` lebih dari sekitar 150 baris, pecah ke `app/`.**
3. **Logika yang dipakai dua perintah, pindahkan ke `core/`.**

---

## Saat fase Production

Yang biasanya perlu disiapkan:

- **Perintah bisa dijalankan ulang dengan aman**, terutama kalau dipasang di penjadwal
- **Pesan gagal yang jelas**, menyebut berkas atau baris yang bermasalah
- **Semua pengaturan lewat argumen atau `.env`**, bukan nilai yang ditulis langsung di kode
