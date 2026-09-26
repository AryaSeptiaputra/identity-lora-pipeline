# Memisahkan Bagian Project ke Server Berbeda

Dibaca saat fase Production, ketika dua bagian project akan dipasang di tempat berbeda. Contoh yang paling umum: penyiapan data berjalan di server ber-GPU, sedangkan layanan yang melayani pengguna berjalan di server biasa.

Pemisahan ini **bukan** dikerjakan dengan branch git. Branch dipakai untuk versi kode yang berbeda sepanjang waktu, sedangkan kedua bagian ini harus ada bersamaan.

---

## Tiga cara, pilih satu

| Cara | Bentuknya | Dipakai kalau |
|---|---|---|
| **1. Folder terpisah** | Satu project, dua folder di dalam `app/`, tidak saling import | Keduanya masih di satu server |
| **2. Package terpisah** | Satu project, tiap bagian punya `requirements.txt` sendiri dan dipasang terpisah | Dijalankan di server berbeda, tapi sering diubah bersamaan |
| **3. Project terpisah** | Dua project berbeda | Dikerjakan orang berbeda, atau salah satunya dipakai lebih dari satu sistem |

Untuk pekerjaan satu orang, cara 2 biasanya paling pas: perubahan yang menyentuh kedua bagian tetap bisa dikerjakan sekaligus.

---

## Bentuk cara 2

```
project-name/
├── packages/
│   ├── shared/             # dipakai keduanya: bentuk data, kesepakatan format
│   │   └── requirements.txt
│   ├── pipeline/           # dipasang di server A
│   │   └── requirements.txt
│   └── chat/               # dipasang di server B
│       └── requirements.txt
├── docs/
└── README.md
```

Server A memasang `shared` dan `pipeline`. Server B memasang `shared` dan `chat`. Dengan begitu paket berat seperti pengolah dokumen tidak ikut terpasang di server layanan.

---

## Memindahkan hasil kerja antar server

Selama satu server, kedua bagian berbagi folder `data/processed/`. Setelah terpisah, hasil kerja harus dikirim.

Alur yang disarankan:

```
Server A
  1. Jalankan penyiapan data, simpan hasilnya ke folder baru bertanggal
       releases/2026-01-15-0200/
         ├── (hasil: index, database, atau berkas lain)
         └── manifest.json
  2. Kirim folder itu ke server B

Server B
  3. Terima folder
  4. Periksa manifest.json cocok dengan yang diharapkan
  5. Arahkan penunjuk "current" ke folder baru
  6. Nyalakan ulang layanan
  7. Simpan satu hasil sebelumnya, untuk berjaga kalau harus kembali
```

Cara ini membuat layanan tidak pernah membaca data yang sedang setengah ditulis, dan kembali ke versi sebelumnya cukup dengan memindahkan penunjuk.

---

## Isi manifest.json

Berkas kecil yang ikut dikirim, berisi identitas hasil kerja:

| Isi | Contoh | Kenapa perlu |
|---|---|---|
| Versi format | `2` | Layanan tahu bentuk data yang diterimanya |
| Model yang dipakai | nama dan versi model embedding | **Paling penting.** Kalau model di kedua server berbeda, pencarian tetap berjalan tapi hasilnya kacau tanpa pesan error |
| Nama koleksi atau tabel | `dokumen_utama` | Mencegah layanan membuka tempat yang salah |
| Waktu dibuat dan jumlah data | `2026-01-15 02:00`, `412 dokumen` | Mendeteksi hasil yang basi atau kosong |

**Aturan wajib:** saat layanan dinyalakan, periksa manifest. Kalau versi format atau model tidak cocok, layanan menolak memakai hasil baru dan tetap memakai yang lama.

---

## Yang tidak berubah

Struktur di dalam tiap bagian tetap seperti templatenya masing-masing. Pemisahan ini hanya menambah lapisan di luar, bukan mengubah isi folder.

Karena itu, selama `pipeline/` dan `chat/` sudah terpisah sejak MVP dan tidak saling import, pemisahan ke dua server hanya soal memindahkan folder.
