# Tahap Rancangan Evaluasi

Dibaca red-chan saat Arya meminta "red-chan, rancang evaluasi ...". Hasilnya `docs/rencana-evaluasi.md`.

## Daftar isi

- Kapan dan apa masukannya
- Alur dan riset
- Isi rancangan evaluasi
- Golden set dan label
- Membaca hasil
- Gate
- Format dokumen
- Pembagian kerja dan serah terima

---

## Kapan dan apa masukannya

- **Mulai di fase Dev.** Di MVP tidak ada rencana evaluasi; tanda berhasil MVP cukup D4.
- **Syarat:** `docs/keputusan-produk.md` sudah berstatus `siap dikerjakan`. Modul yang dievaluasi harus sudah jelas. Kalau belum, kembalikan: rancangan sistem harus disetujui dulu.
- **Masukan:** prompt Arya + `docs/keputusan-produk.md` + status data (lihat `data.md`).

## Alur dan riset

Alurnya sama dengan rancangan sistem: analisis → riset → rancangan utuh → titik periksa → Arya menyetujui. Aturan riset sama (Bagian 4 `SKILL.md`), dengan tiga perbedaan:

| Hal | Aturan |
|---|---|
| Metrik klasik (Recall@k, MRR, nDCG, CER, confusion matrix, precision/recall) | Pengetahuan umum; tidak perlu riset |
| Metrik untuk LLM (faithfulness, answer relevance, dsb.) | **Wajib** merujuk definisi dari paper atau dokumentasi resmi — library yang berbeda menghitungnya berbeda |
| Angka target | **Tidak diambil dari internet.** Target awal ditulis sebagai asumsi, lalu disesuaikan setelah baseline. Target yang paling menentukan jadi titik periksa |

Yang juga perlu diriset kalau dipakai: praktik LLM-as-judge (bias yang dikenal, cara kalibrasi) dan library evaluasi (aturan repository dan lisensi sama dengan library lain).

---

## Isi rancangan evaluasi

1. **Modul yang dievaluasi** — diturunkan dari gambaran sistem. Setiap modul yang mengubah data punya evaluasinya sendiri (component-level evaluation), ditambah satu evaluasi end-to-end untuk jawaban akhir.
2. **Kartu metrik per modul** — di level engineering (Bagian 6.2 `SKILL.md`): keluaran yang dinilai, rumus dalam Unicode, target awal, cara menilai (otomatis / manual / LLM-as-judge).
3. **Dataset uji** — golden set dan ground truth (bagian berikut).
4. **Membaca hasil** — tabel pola hasil → modul penyebab.
5. **Gate** — baseline, target per langkah, rollback.

**Aturan metrik:**
- Embedding biasanya tidak dinilai sendiri; kualitasnya terlihat dari metrik retrieval.
- Hasil dilaporkan **per kelompok query**, bukan hanya rata-rata keseluruhan.
- LLM-as-judge memakai model yang berbeda dari model generator, dan dikalibrasi dulu terhadap minimal 10 penilaian manual Arya. Dipakai hanya kalau kesepakatannya ≥ 80%.
- Data rahasia (lihat `data.md`): judge dan pembuatan apa pun yang membaca isi data hanya dengan model lokal.

---

## Golden set dan label

**Golden set ditulis manual oleh Arya.** AI tidak membuat label kebenaran, karena kesalahan model akan ikut masuk ke kunci jawaban. Red-chan hanya merancang bentuk, kelompok, dan jumlahnya.

### Bentuk gabungan

| Dataset | Untuk modul | Bentuk |
|---|---|---|
| **Golden set** | Semua modul yang dilewati query: router, retrieval, lookup, generation, end-to-end | Satu baris per query, berisi label untuk setiap modul |
| **Ground truth extraction** | Extraction (dan chunking bila perlu) | Per halaman: `.txt` untuk teks (diketik apa adanya), `.csv` untuk tabel. Kalau klien punya naskah digital asli, pakai itu sebagai pembanding |

Butuh ketelitian lebih untuk satu modul → tambah baris ke golden set yang sama, isi hanya label modul itu.

### Kelompok wajib

Selain kelompok per jalur di sistem, empat kelompok selalu ada:

| Kelompok | Menguji |
|---|---|
| `ada_di_dokumen` | Kemampuan menjawab |
| `tidak_ada_di_dokumen` | Berani bilang tidak tahu |
| `di_luar_cakupan` | Penolakan |
| `sulit` | Salah ketik, singkatan, dua pertanyaan dalam satu kalimat |

±⅓ golden set disisihkan sebagai **uji akhir** yang tidak dilihat saat memperbaiki sistem.

### Sumber pertanyaan

| Cara | Keterangan |
|---|---|
| Dari dokumen | Pilih potongan dokumen, tulis pertanyaan yang jawabannya ada di sana. Cocok untuk topik apa pun |
| Dari pertanyaan nyata | FAQ, email, chat, tiket dari klien. Lebih realistis. Data pribadi disamarkan dulu oleh Arya |

### Media dan kolom

Ditulis di **spreadsheet**, lalu dikonversi ke `data/evaluation/golden_set.jsonl` oleh script buatan pink-chan.

| Kolom | Isi | Wajib |
|---|---|---|
| `id` | `Q001`, `Q002`, … | Ya |
| `pertanyaan` | Persis seperti pengguna mengetik | Ya |
| `kelompok` | Empat kelompok wajib atau kelompok jalur | Ya |
| `jalur` | Jalur di sistem, kalau ada router | Kondisional |
| `jenis_jawaban` | `fakta` · `prosedur` · `penjelasan` · `menolak` · `eskalasi` | Ya |
| `label_jawaban` | Kunci penilaian (tabel berikut) | Ya, kecuali `menolak` |
| `poin_boleh` | Informasi tambahan yang benar, tidak menambah atau mengurangi nilai | Tidak |
| `jawaban_contoh` | Kalimat jawaban ideal; tidak dipakai menilai benar-salah | Tidak |
| `sumber` | Letak jawaban di dokumen | Kalau `ada_di_dokumen` |
| `chunk_relevan` | ID chunk yang benar | Diisi setelah chunking |
| `bagian` | `perbaikan` · `uji_akhir` | Ya |
| `diverifikasi` | Pemeriksa; kosong kalau belum | Ya |
| `catatan` | Hal yang perlu diingat penilai | Tidak |

### Bentuk label per jenis jawaban

**Label adalah kunci penilaian, bukan kalimat jawaban** — satu pertanyaan bisa dijawab benar dengan banyak kalimat.

| Jenis | Bentuk label | Contoh | Dinilai |
|---|---|---|---|
| `fakta` | Nilai persis, dinormalisasi (angka tanpa titik/Rp, tanggal `YYYY-MM-DD`); beberapa nilai dipisah `\|` | `1250000` | Exact match |
| `prosedur` | Langkah wajib bernomor, dipisah `\|` | `1. isi formulir \| 2. bayar \| 3. kirim bukti` | Semua langkah ada, urutan benar |
| `penjelasan` | 2–4 poin kunci wajib, satu gagasan per poin, memakai istilah dokumen | `kapasitas lebih besar \| mode hemat energi` | Semua poin ada |
| `menolak` | Kosong; tulis di `catatan` bentuk penolakan yang benar | — | Sistem menolak / mengarahkan ke kontak |
| `eskalasi` | Tindakan wajib | `arahkan ke layanan pelanggan \| minta nomor pesanan` | Semua tindakan ada |

Jawaban benar lebih dari satu → pisahkan alternatif dengan `/`. Pertanyaan ambigu → tulis di `catatan` jawaban mana yang diterima, atau apakah sistem harus bertanya balik.

### Alat bantu dari pink-chan

- **Konversi + pemeriksaan:** menolak baris dengan `id` kosong/ganda, `jenis_jawaban` tak dikenal, `penjelasan` < 2 atau > 4 poin, `ada_di_dokumen` tanpa `sumber`, atau `diverifikasi` kosong pada baris yang masuk gate. Baris yang ditolak ditampilkan beserta alasannya.
- **Kandidat chunk:** menampilkan 20 kandidat hasil retrieval per pertanyaan; Arya memilih nomor yang benar. `chunk_relevan` diisi ulang kalau cara chunking berubah.

---

## Membaca hasil

Tabel yang memetakan pola hasil ke modul penyebab, diturunkan dari urutan modul di gambaran sistem — tidak perlu riset. Prinsipnya: baca dari hulu ke hilir; modul pertama yang angkanya jatuh adalah tersangka utama.

Contoh bentuk:

| Pola hasil | Kesalahan ada di |
|---|---|
| E2E rendah, retrieval rendah | Retrieval atau lebih awal — cek chunking dan extraction |
| E2E rendah, retrieval tinggi, faithfulness rendah | Generation (prompt atau model) |
| Semua turun bersamaan | Extraction — ukur ulang dari awal |

---

## Gate

1. Baseline diukur sebelum perubahan apa pun.
2. Setiap langkah di rencana pembangunan pink-chan wajib mencapai target modul yang ditargetkannya.
3. Metrik modul lain turun lebih dari 5 poin dari baseline → langkah itu di-rollback.
4. Hasil tiap putaran disimpan di `outputs/evaluation/<tanggal>/`.
5. Hanya angka dari **data asli** yang boleh dipakai untuk menyatakan target tercapai. Angka dari data pengganti publik ditulis terpisah dan tidak pernah dirata-rata dengan angka data asli.

---

## Format dokumen

```markdown
# Rencana Evaluasi

Produk: <nama>
Fase: Dev | Production
Dasar: docs/keputusan-produk.md (<tanggal>)
Data: tingkat 0 | 1 | 2 | 3 — <keterangan>
Status: usulan | siap dikerjakan
Diperbarui: YYYY-MM-DD

## Ringkasan
| Modul | Metrik utama | Target awal | Cara menilai |

## Dataset uji
Golden set: kelompok, jumlah, sumber pertanyaan, bagian uji akhir.
Ground truth extraction: halaman yang dipakai, pembandingnya.

## Metrik per modul
### M1 · <modul>
<kartu metrik: rumus, target, cara menilai>

## Membaca hasil
| Pola hasil | Kesalahan ada di |

## Gate dan baseline

## Asumsi
## Belum pasti
## Sumber
## Riwayat
```

Target awal yang belum diuji data asli ditandai `(sementara)`.

---

## Pembagian kerja dan serah terima

| Siapa | Tugas |
|---|---|
| red-chan | Rencana evaluasi: modul, metrik, bentuk dan jumlah dataset, gate |
| pink-chan | Script evaluasi (satu perintah, hasil tabel angka), konversi dan pemeriksaan golden set, alat kandidat chunk. Diuji dengan data pengganti publik |
| Arya | Golden set dan ground truth; menjalankan evaluasi di data asli |

Rancangan evaluasi mendapat nomor sendiri di arsip. Setelah disetujui dan file `a` ditulis, perintah untuk pink-chan:

```
pink-chan, susun rencana pembangunan dari docs/rancangan/<nomor>a_<tanggal>_dev-rancang-evaluasi.md
```

Pink-chan membangun alat evaluasi dan mengukur baseline **sebelum** langkah perbaikan Dev apa pun.
