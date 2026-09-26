# Status Data, Data Pengganti, dan Data Rahasia

Dibaca red-chan saat data asli belum ada, tidak lengkap, atau tidak boleh dibaca AI. Berlaku untuk rancangan sistem dan rancangan evaluasi.

## Daftar isi

- Tingkat ketersediaan data
- Profil data
- Data pengganti publik
- Keputusan sementara dan kalibrasi
- Mode data rahasia

---

## Tingkat ketersediaan data

| Tingkat | Yang diterima | Bisa dipakai untuk |
|---|---|---|
| **0 · Tidak ada** | Hanya brief | Data pengganti untuk mekanik; semua parameter sementara |
| **1 · Deskripsi** | Profil data dari klien, tanpa isi | Memilih data pengganti yang mirip; risiko salah rancang turun banyak |
| **2 · Sampel kecil** | 3–10 dokumen atau 20 pertanyaan nyata | Uji awal extraction, golden set kecil, kalibrasi pertama |
| **3 · Lengkap** | Semua data | Evaluasi penuh dan gate kualitas |

Kalau tingkatnya 0, masukkan ke "Belum pasti": minta klien minimal profil data (tingkat 1). Profil data paling murah bagi klien dan paling besar dampaknya.

Tulis di kepala dokumen keputusan dan rencana evaluasi:

```
Data: tingkat <0–3> — <keterangan>
```

---

## Profil data

Deskripsi data **tanpa isi rahasia**, ditulis Arya atau klien:

```
Profil data:
- Jenis      : <jenis dokumen/tabel>, <jumlah>, <bahasa>
- Format     : <PDF teks / hasil scan / Word / Excel / ...>
- Struktur   : <bab-subbab / pasal / kolom apa saja / ...>
- Kualitas   : <porsi hasil scan, sel kosong, format campur, ...>
- Pertanyaan pengguna: <jenis pertanyaan yang biasa muncul>
- Yang sensitif: <data pribadi, nominal, konten berlisensi, ...>
- Lingkungan : <tempat data boleh berada; GPU tersedia atau tidak>
```

---

## Data pengganti publik

Selama data asli belum ada atau tidak boleh dibaca AI, fase Dev memakai **data pengganti publik saja**. Tidak ada konten tiruan buatan agent.

### Syarat lisensi

| Status | Contoh |
|---|---|
| Aman | Domain publik, CC0, CC BY, lisensi data terbuka pemerintah |
| Catat kewajibannya | CC BY (sebut sumber), CC BY-SA (turunan berlisensi sama) |
| Tidak boleh | CC BY-NC untuk proyek klien berbayar, tanpa lisensi, atau sekadar "gratis dibaca" |

Lisensi dicek **per dataset**, bukan per situs.

### Syarat kemiripan

Bandingkan dengan profil data. Minimal cocok di **bahasa, format, dan struktur**. Perbedaan lain dicatat.

| Aspek | Kalau tidak cocok |
|---|---|
| Bahasa | Pilihan embedding dan model salah untuk data asli |
| Format dan kualitas file | Extraction terlihat baik di data bersih, gagal di hasil scan |
| Struktur | Cara chunking yang terpilih tidak cocok |
| Ukuran | Kecepatan dan pilihan penyimpanan salah perkiraan |
| Istilah bidang | Kualitas retrieval berbeda jauh |
| Kolom dan pola (tabel) | Pembersihan data tidak menangani masalah data asli |

### Yang berlaku dan tidak berlaku di data asli

| Hasil dari data pengganti | Berlaku di data asli? |
|---|---|
| Kode berjalan, script evaluasi benar | Ya |
| Pendekatan A lebih baik dari B | Mungkin — cek ulang di data asli |
| Angka metrik | Tidak |
| Nilai parameter terbaik | Tidak — dikalibrasi ulang |

### Siapa mengerjakan

- **red-chan** mengusulkan sumber data publik hasil riset beserta lisensi dan kemiripannya.
- **Arya** memilih dan mengunduh. Agent tidak mengunduh data.
- **pink-chan** membangun dan menguji kode dengan data yang sudah disediakan Arya.

Catat di dokumen:

```
Data pengganti: <nama dataset>, <lisensi>, <alamat sumber>
  Cocok : <aspek yang cocok>
  Beda  : <perbedaan yang diketahui>
```

---

## Keputusan sementara dan kalibrasi

Setiap keputusan yang nilainya bergantung pada data asli ditandai `(sementara)`: parameter (ukuran chunk, top-k, ambang), pilihan akhir model dan pendekatan retrieval, target metrik.

```
K2 · Chunk 500 token, overlap 50        (sementara — belum diuji data asli)
```

Fase Dev terbagi dua kalau data asli belum ada:

```
Dev-A  tanpa data asli   → mekanik, fitur, alat evaluasi, data pengganti publik
Dev-B  dengan data asli  → kalibrasi, optimasi kualitas, gate
```

**Saat data asli datang, langkah pertama selalu kalibrasi:**

1. Arya menulis golden set asli (kecil dulu, 20–30 query).
2. Evaluasi dijalankan → baseline data asli.
3. red-chan meninjau semua keputusan `(sementara)`: dipertahankan, parameter diubah, atau pendekatan diganti.
4. Tanda `(sementara)` dihapus; perubahan dicatat di Riwayat.

Kalau data asli tidak pernah datang sampai serah terima, tulis di dokumen: **parameter belum dikalibrasi pada data asli.**

---

## Mode data rahasia

Berlaku kalau data asli bersifat rahasia atau berlisensi dan tidak boleh keluar dari lingkungan klien.

**Dasarnya:** setiap file yang dibaca AI dikirim ke penyedia model untuk diproses. Membaca = mengeluarkan data. Karena itu AI tidak membaca data asli sama sekali; AI bekerja dengan **bentuk** data, manusia bekerja dengan **isi** data.

### Tanda mode aktif

`CLAUDE.md` project berisi bagian:

```markdown
## Data rahasia
Folder: data/raw/, data/interim/, data/processed/, data/evaluation/
Tidak boleh dibaca AI. Kerjakan dari profil data.
```

Dan `.claude/settings.json` project memblokir pembacaannya:

```json
{ "permissions": { "deny": ["Read(./data/**)"] } }
```

Laptop Arya termasuk lingkungan klien: data asli boleh ada di laptop, asalkan kedua penanda di atas terpasang. Pink-chan menambahkan keduanya saat memulai project dalam mode ini, setelah Arya menyetujui.

### Yang boleh dan tidak boleh keluar

| Barang | Boleh dibaca AI / keluar? |
|---|---|
| File data asli, hasil extraction, chunk, index | Tidak |
| Golden set asli dan ground truth (mengutip isi data) | Tidak |
| Kode program, profil data | Ya |
| Angka hasil evaluasi agregat | Ya |
| Query riset web | Ya, **tanpa** nama klien, judul, istilah internal, atau kutipan isi |

### Akibat ke rancangan

| Bagian | Harus |
|---|---|
| Model embedding dan generator | Lokal, di lingkungan klien. Model lewat API = bentrokan yang wajib dicatat |
| LLM-as-judge | Lokal, atau penilaian manual |
| Tempat evaluasi data asli | Laptop Arya atau server klien, dijalankan Arya atau staf klien |
| Laporan hasil ke red-chan | Angka agregat per modul dan per kelompok saja; analisis contoh gagal dikerjakan Arya |
| Script evaluasi | Satu perintah, hasil tabel angka, supaya bisa dijalankan orang lain |

Red-chan menyebut di laporan bahwa mode data rahasia aktif.
