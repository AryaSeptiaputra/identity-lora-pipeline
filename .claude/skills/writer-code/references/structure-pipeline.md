# Template: Pipeline Data

Dipakai untuk project yang pekerjaan utamanya mengubah data mentah menjadi data siap pakai: mengambil dokumen, membaca isinya, membersihkan, memotong, lalu menyimpannya ke tempat pencarian.

**Jangan pakai template ini kalau:**
- Pipeline hanya bagian dari chatbot dan dikerjakan dalam satu project → pakai Bentuk B di `structure-ai-app.md`
- Tujuannya membandingkan beberapa pendekatan untuk mencari yang terbaik → pakai `structure-riset.md`

---

## Bentuk foldernya

Satu folder untuk satu tahap, diurutkan sesuai jalannya data.

```
project-name/
├── app/
│   ├── shared/             # dipakai semua tahap: config, bentuk data, util, logger
│   ├── ingest/             # mengambil data dari sumber
│   ├── parse/              # membaca isi file menjadi teks terstruktur
│   ├── clean/              # membuang bagian yang tidak perlu
│   ├── chunk/              # memotong teks menjadi bagian kecil
│   ├── index/              # menyimpan ke tempat pencarian
│   └── storage/            # mencatat status tiap dokumen
├── tests/                  # susunan folder mengikuti app/
├── scripts/
│   └── run_pipeline.py     # menjalankan seluruh tahap, atau satu tahap saja
├── data/
│   ├── raw/                # hasil unduhan asli, jangan pernah diubah
│   ├── interim/            # hasil setengah jadi tiap tahap
│   └── processed/          # hasil akhir yang dipakai sistem lain
├── docs/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

**Nama tahap mengikuti pekerjaannya, bukan istilah baku.** Kalau project Anda tidak punya tahap pembersihan, foldernya tidak usah ada. Kalau ada tahap khusus seperti menerjemahkan, buat `translate/`.

---

## Isi tiap folder

| Folder | Isinya |
|---|---|
| `shared/` | Setting dari `.env`, bentuk data yang dipakai lintas tahap, logger, fungsi bantu |
| `ingest/` | Kode pengambilan data: crawler, pembaca folder, pemanggil API sumber |
| `parse/` | Mengubah PDF, HTML, atau DOCX menjadi teks beserta strukturnya |
| `clean/` | Membuang menu, footer, halaman kosong, duplikat |
| `chunk/` | Memotong teks, menjaga potongan tetap utuh maknanya |
| `index/` | Menghitung embedding dan menyimpannya ke tempat pencarian |
| `storage/` | Mencatat dokumen mana sudah diproses, versi berapa, dan kapan terakhir berubah |

---

## Tiga aturan wajib

1. **`data/raw/` tidak pernah diubah.** Hasil pengambilan disimpan apa adanya. Semua perbaikan dilakukan pada salinan di `interim/` atau `processed/`.
2. **Tahap bisa dijalankan ulang tanpa merusak.** Menjalankan ulang tahap yang sama pada data yang sama harus menghasilkan keadaan yang sama, bukan data ganda.
3. **Catat status tiap dokumen di `storage/`.** Tanpa ini, proses yang terputus di tengah harus diulang dari awal.

---

## Saat fase MVP

Buat hanya tahap yang benar-benar dipakai. Pipeline paling sederhana biasanya cukup tiga tahap:

```
app/
├── shared/
├── ingest/
├── parse/
└── index/
```

Tahap pembersihan dan pemotongan ditambahkan setelah terlihat hasilnya kurang rapi.

---

## Saat fase Dev — tiga aturan pertumbuhan

1. **Tahap baru → folder baru.** Jangan menumpangkan pekerjaan baru ke tahap yang sudah ada hanya karena terlihat mirip.
2. **Dua cara → baru bikin `interfaces.py`.** Selama satu tahap punya satu cara kerja, tulis class biasa. Begitu ada cara kedua yang dipakai bergantian, baru pisahkan jadi `interfaces.py` + `providers/`.
3. **Dipakai ulang → pindahkan dari notebook.** Kode di `notebooks/` yang mulai dipakai file lain harus dipindah ke `app/`.

---

## Saat fase Production

Yang biasanya perlu disiapkan:

- **Penjadwalan** — pipeline dijalankan berkala atau dipicu manual
- **Lanjut dari kegagalan** — bisa melanjutkan dokumen yang belum selesai, memakai catatan di `storage/`
- **Pemberitahuan saat gagal** — minimal tercatat di log dengan jelas

Kalau hasil pipeline dipakai sistem lain yang berjalan di server berbeda, baca `structure-pisah-server.md`.
