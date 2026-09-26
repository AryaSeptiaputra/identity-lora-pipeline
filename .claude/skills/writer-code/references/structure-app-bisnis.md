# Template: Aplikasi Bisnis

Dipakai untuk aplikasi yang mengelola data dan transaksi: pencatatan penjualan, inventori, pemesanan, dan sejenisnya.

Template ini sengaja ringkas karena jarang dipakai. Kalau project seperti ini menjadi sering, isinya diperdalam.

---

## Bentuk foldernya

Dikelompokkan per fitur, bukan per jenis kode. Satu fitur berisi semua bagiannya.

```
project-name/
├── app/
│   ├── config.py
│   ├── shared/             # dipakai lintas fitur: bentuk data umum, util, koneksi database
│   ├── products/           # satu folder per fitur
│   │   ├── routes.py       # endpoint
│   │   ├── schemas.py      # bentuk data masuk dan keluar
│   │   ├── service.py      # aturan bisnis
│   │   └── repository.py   # akses database
│   ├── orders/
│   └── reports/
├── tests/                  # susunan folder mengikuti app/
├── migrations/             # perubahan struktur database
├── scripts/
├── docs/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

---

## Kenapa per fitur

Pada aplikasi seperti ini, perubahan hampir selalu datang sebagai fitur: tambah diskon, ubah cara hitung pajak. Dengan pengelompokan per fitur, satu permintaan perubahan cukup menyentuh satu folder.

---

## Tiga aturan wajib

1. **Aturan bisnis ada di `service.py`, bukan di `routes.py`.** Endpoint hanya menerima permintaan dan menyerahkannya.
2. **Perubahan struktur database lewat `migrations/`.** Jangan mengubah tabel langsung di database.
3. **Fitur tidak memanggil `repository.py` milik fitur lain.** Kalau butuh data fitur lain, panggil `service.py` miliknya.

---

## Saat fase MVP

Buat hanya fitur yang dipakai, dan di dalamnya hanya berkas yang terisi. Fitur sederhana boleh hanya punya `routes.py` dan `service.py`.

---

## Saat fase Dev, tiga aturan pertumbuhan

1. **Fitur baru jadi folder baru.**
2. **Kode yang dipakai dua fitur, pindahkan ke `shared/`.**
3. **Satu berkas melebihi sekitar 300 baris, pecah menurut pekerjaannya.**
