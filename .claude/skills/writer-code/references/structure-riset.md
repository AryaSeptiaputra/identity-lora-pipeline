# Template: Riset & Training Model

Dipakai untuk project yang tujuannya mencari jawaban, bukan melayani pengguna: melatih model, fine-tune, atau membandingkan beberapa pendekatan untuk memilih yang terbaik.

**File lain untuk pekerjaan lain:**
- Menyajikan model yang sudah jadi: `structure-api-model.md`
- Chatbot yang melayani pengguna: `structure-ai-app.md`
- Menyiapkan data sebagai pekerjaan utama: `structure-pipeline.md`

---

## Bentuk foldernya

```
project-name/
├── notebooks/              # eksplorasi, diberi nomor urut
│   ├── 01_explore_data.ipynb
│   └── 02_baseline_model.ipynb
├── app/
│   ├── shared/             # config, bentuk data, util
│   ├── data/               # memuat dan menyiapkan data latih
│   ├── training/           # proses melatih model
│   └── evaluation/         # mengukur hasil
├── configs/                # satu file per percobaan
│   ├── baseline.yaml
│   └── percobaan-02.yaml
├── scripts/
│   ├── train.py            # menjalankan pelatihan dari satu config
│   └── evaluate.py         # mengukur hasil satu model
├── data/
│   ├── raw/                # data asli, jangan pernah diubah
│   ├── interim/
│   └── processed/
├── models/                 # model hasil latihan
├── outputs/                # hasil tiap percobaan
│   └── 2026-01-15-baseline/
│       ├── config.yaml     # salinan config yang dipakai
│       ├── metrics.json    # angka hasilnya
│       └── log.txt
├── docs/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

---

## Tiga aturan wajib

1. **Angka percobaan disimpan, bukan diingat.** Tiap menjalankan percobaan, simpan hasilnya ke folder sendiri di `outputs/` beserta salinan config-nya. Tanpa ini, dua minggu lagi Anda tidak tahu angka mana berasal dari pengaturan apa.
2. **Yang diubah antar percobaan ada di `configs/`, bukan di kode.** Ukuran batch, learning rate, nama model: semuanya di file config. Kode tetap sama, config yang berganti.
3. **Catat seed acak.** Tanpa seed yang dicatat, hasil percobaan tidak bisa diulang.

---

## Pembagian notebook dan app/

| Di `notebooks/` | Di `app/` |
|---|---|
| Melihat data, mencoba ide, membuat grafik | Kode yang dipakai lebih dari sekali |
| Boleh berantakan, boleh dibuang | Rapi, ada testnya |

**Aturannya:** begitu kode di notebook dipakai notebook lain atau dipanggil dari `scripts/`, pindahkan ke `app/`. Notebook memanggil fungsi dari `app/`, bukan menyalin kodenya.

---

## Saat fase MVP

Riset biasanya dimulai dari notebook saja. Struktur di atas baru dibangun setelah arah percobaannya jelas.

Urutan yang wajar:

1. Satu notebook untuk melihat data
2. Satu notebook untuk mencoba pendekatan pertama
3. Begitu ada kode yang dipakai ulang, buat `app/` dan pindahkan
4. Begitu percobaan mulai banyak, buat `configs/` dan `outputs/`

---

## Saat fase Dev, tiga aturan pertumbuhan

1. **Pendekatan baru jadi config baru, bukan kode baru.** Kalau harus mengubah kode untuk tiap percobaan, berarti ada yang seharusnya jadi config.
2. **Dua cara baru bikin `interfaces.py`.** Saat membandingkan dua cara memuat data atau dua arsitektur model, barulah kontraknya dipisahkan supaya bisa ditukar lewat config.
3. **Dipakai ulang, pindahkan dari notebook.**

---

## Saat fase Production

Model hasil riset yang akan dipakai sistem lain tidak dijalankan dari project ini. Simpan model beserta catatan versinya, lalu sajikan lewat project terpisah memakai `structure-api-model.md`.
