# Template: Chatbot / AI App

Dipakai untuk chatbot, asisten AI, dan aplikasi tanya-jawab yang melayani pengguna.

Template ini hanya mengatur bagian yang **melayani pengguna**: menerima pertanyaan, mencari jawaban, menjawab.

**File lain untuk pekerjaan lain:**
- Menyiapkan data (mengambil, membaca, memotong, menyimpan ke pencarian) → `structure-pipeline.md`
- Membandingkan beberapa pendekatan untuk mencari yang terbaik → `structure-riset.md`
- Menyajikan prediksi model yang sudah dilatih → `structure-api-model.md`

---

## Bentuk foldernya

```
project-name/
├── app/
│   ├── config.py           # semua setting, dibaca dari .env
│   ├── prompts/            # teks prompt
│   ├── models/             # bentuk data (Pydantic)
│   ├── services/           # logika utama: pencarian, jawaban, sesi
│   ├── storage/            # akses database atau file
│   ├── providers/          # client layanan luar: model bahasa, embedding, API pihak ketiga
│   ├── api/                # endpoint
│   └── utils/              # fungsi bantu
├── tests/                  # susunan folder mengikuti app/
├── scripts/                # perintah sekali jalan
├── data/                   # isi di-gitignore
├── docs/
├── .env / .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

---

## Isi tiap folder

| Folder | Isinya | Contoh file |
|---|---|---|
| `config.py` | Semua setting dalam satu class, dibaca dari `.env` | — |
| `prompts/` | Teks prompt, terpisah dari kode | `chat.py` |
| `models/` | Bentuk data yang dipakai lintas file | `conversation.py`, `retrieval.py` |
| `services/` | Logika utama | `retriever.py`, `generator.py`, `conversation.py`, `session_store.py` |
| `storage/` | Akses database atau file | `conversation_db.py`, `vector_store.py` |
| `providers/` | Client layanan luar: model bahasa, embedding, API pihak ketiga | `llm_client.py` |
| `api/` | Endpoint, satu folder per kelompok endpoint | `chat/routes.py`, `chat/schemas.py` |
| `utils/` | Fungsi bantu tanpa state | `text.py` |

**Aturan `services/`:** satu file untuk satu pekerjaan. Mencari dokumen, menyusun jawaban, dan mengatur sesi adalah tiga pekerjaan berbeda, jadi tiga file berbeda.

---

## Saat fase MVP

Buat **hanya folder yang benar-benar dipakai**. Folder kosong untuk kebutuhan masa depan justru membingungkan.

Contoh MVP chatbot yang belum menyimpan percakapan:

```
app/
├── config.py
├── prompts/
├── models/
├── services/
└── api/
```

`storage/` dan `utils/` ditambahkan nanti saat memang ada isinya.

---

## Saat fase Dev — tiga aturan pertumbuhan

1. **Kemampuan baru → file baru di `services/`.** Jangan menumpuk semuanya di satu file hanya karena masih berkaitan dengan percakapan.
2. **Dua cara → baru bikin `interfaces.py`.** Selama satu komponen punya satu cara kerja, tulis class biasa. Begitu benar-benar ada cara kedua yang dipakai bergantian (mis. dua model yang dibandingkan), baru pisahkan jadi `interfaces.py` + `providers/`.
3. **Dipakai ulang → pindahkan dari notebook.** Kode di `notebooks/` yang mulai dipakai file lain harus dipindah ke `app/`.

---

## Saat fase Production

Kalau aplikasi ini akan dipasang terpisah dari bagian lain project, baca `structure-pisah-server.md`.
