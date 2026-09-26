# Template: API Prediksi Model

Dipakai untuk project yang menyajikan model yang sudah dilatih sebagai layanan: menerima masukan, mengembalikan prediksi.

**File lain untuk pekerjaan lain:**
- Melatih atau membandingkan model: `structure-riset.md`
- Chatbot yang menjawab dengan bahasa alami: `structure-ai-app.md`

---

## Bentuk foldernya

```
project-name/
├── app/
│   ├── config.py           # semua setting, termasuk path dan versi model
│   ├── models/             # bentuk data masuk dan keluar (Pydantic)
│   ├── services/           # memuat model, menyiapkan masukan, menjalankan prediksi
│   ├── api/                # endpoint
│   └── utils/              # fungsi bantu
├── tests/
├── scripts/                # perintah sekali jalan, mis. mengunduh model
├── models/                 # berkas model, isi di-gitignore
├── docs/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

Perhatikan dua arti kata model yang berbeda: `app/models/` berisi bentuk data, sedangkan `models/` di root berisi berkas model hasil latihan.

---

## Isi services/

| File | Isinya |
|---|---|
| `loader.py` | Memuat model sekali saat aplikasi start, bukan tiap permintaan |
| `preprocess.py` | Menyiapkan masukan agar sesuai bentuk yang diharapkan model |
| `predictor.py` | Menjalankan prediksi dan merapikan hasilnya |

---

## Tiga aturan wajib

1. **Model dimuat sekali di awal.** Memuat model tiap permintaan membuat layanan lambat.
2. **Versi model dicatat dan ikut ditampilkan.** Sertakan versi model pada hasil prediksi atau pada endpoint pengecekan, supaya saat hasil berubah penyebabnya bisa ditelusuri.
3. **Cara menyiapkan masukan harus sama persis dengan saat latihan.** Perbedaan kecil di tahap ini membuat prediksi meleset tanpa error apa pun.

---

## Saat fase MVP

```
app/
├── config.py
├── models/
├── services/
└── api/
```

Satu endpoint prediksi dan satu endpoint pengecekan sudah cukup.

---

## Saat fase Dev, tiga aturan pertumbuhan

1. **Jenis prediksi baru jadi endpoint dan file service baru**, jangan menambah cabang di dalam fungsi yang sudah ada.
2. **Dua model yang dipakai bergantian baru bikin `interfaces.py`.**
3. **Dipakai ulang, pindahkan dari notebook.**

---

## Saat fase Production

Yang biasanya perlu disiapkan:

- **Batas waktu dan batas ukuran masukan**, supaya satu permintaan berat tidak menghentikan layanan
- **Endpoint pengecekan yang benar-benar memuat model**, bukan sekadar menjawab hidup
- **Cara mengganti versi model tanpa mematikan layanan**, minimal dengan mencatat versi mana yang sedang aktif
