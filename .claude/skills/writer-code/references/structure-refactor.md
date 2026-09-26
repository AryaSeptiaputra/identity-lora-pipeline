# Merapikan Struktur Project yang Sudah Ada

Dibaca saat Arya meminta merapikan struktur project yang sudah punya kode. Dikerjakan setelah `reader-code` menulis `docs/peta-kode.md`.

---

## Prinsip utama

**Merapikan struktur hanya memindahkan kode dan memperbaiki import. Perilaku program tidak boleh berubah.**

Kode yang perlu diperbaiki — misalnya penanganan error yang buruk — dicatat di bagian Di Luar Cakupan, tidak ikut diperbaiki saat memindah. Kalau pemindahan dan perubahan logika dicampur, saat test gagal tidak ketahuan penyebabnya dari yang mana.

---

## Putaran 1 — menyusun rencana

1. **Baca `docs/peta-kode.md`.**
2. **Tentukan struktur tujuan.** Pilih template dari pekerjaan project yang tercatat di peta. Kalau lebih dari satu pekerjaan, gabungkan mengikuti aturan penggabungan di `SKILL.md`. Kalau `CLAUDE.md` project menetapkan struktur tertentu, ikuti `CLAUDE.md` dan catat perbedaannya dengan template.
3. **Bandingkan.** Buat daftar folder dan file: dari mana, ke mana.
4. **Susun urutan langkah** mengikuti aturan urutan di bawah.
5. **Tulis `docs/rencana-refactor.md`** dengan format di bawah.
6. **Kembalikan ke Arya** dengan status `menunggu persetujuan`. Belum ada file yang dipindahkan di putaran ini.

---

## Langkah 0 — kondisi awal

Langkah pertama yang dikerjakan setelah rencana disetujui, sebelum memindahkan apa pun.

| Kondisi project | Yang dilakukan |
|---|---|
| **Ada test** | Jalankan dan catat hasilnya: jumlah lulus dan gagal. Test yang sudah gagal sejak awal dicatat namanya, supaya tidak dikira rusak karena pemindahan |
| **Tidak ada test** | Buat test sederhana: setiap modul bisa di-import, dan aplikasi bisa dijalankan. Lanjut tanpa test **hanya** kalau Arya menyetujuinya secara tertulis |

---

## Aturan urutan langkah

1. **Mulai dari folder yang paling sedikit diimpor folder lain.** Memindahkannya hanya memengaruhi sedikit file, jadi risikonya paling kecil. Datanya dari bagian Hubungan Antar Folder di peta kode.
2. **Folder yang dipakai banyak bagian — config, bentuk data, util — dipindah paling akhir.**
3. **Satu langkah = satu folder**, atau sekelompok kecil file yang memang harus pindah bersama.

---

## Putaran berikutnya — satu langkah per putaran

1. **Pindahkan dengan `git mv`**, supaya riwayat file tetap tersambung.
2. **Perbaiki semua import** yang merujuk lokasi lama, termasuk di `tests/`, `scripts/`, config, dan dokumen yang menyebut path.
3. **Jalankan test**, bandingkan dengan kondisi awal.
4. **Hasil sama dengan kondisi awal** → tandai langkah `selesai` di rencana.
   **Hasil berbeda** → perbaiki dalam langkah ini. Kalau tidak bisa, batalkan langkah tersebut, kembalikan file ke lokasi semula, dan laporkan penyebabnya.
5. **Kembalikan ke Arya** dengan status `menunggu persetujuan` untuk langkah berikutnya.

Commit dilakukan Arya. Sarankan satu commit per langkah, supaya setiap langkah bisa dibatalkan sendiri.

---

## Setelah semua langkah selesai

1. Perbarui `docs/peta-kode.md` sesuai struktur baru.
2. Perbarui bagian struktur folder dan perintah di `README.md` dan `CLAUDE.md`.
3. Laporkan ringkasan: jumlah langkah, hasil test akhir dibanding kondisi awal, dan isi bagian Di Luar Cakupan.

---

## Aturan tambahan

- **Berkas rahasia** mengikuti `berkas-rahasia.md`: tidak dibuka, tidak ikut dipindahkan.
- **Tidak menghapus file** kecuali file itu kosong setelah isinya dipindahkan, dan penghapusannya tercantum di rencana yang sudah disetujui.

---

## Format docs/rencana-refactor.md

```markdown
# Rencana Merapikan Struktur

Tanggal: YYYY-MM-DD
Struktur tujuan: <template yang dipakai>

## Kondisi awal
Test: <perintah> → <jumlah lulus / gagal>
Test yang sudah gagal sejak awal: <daftar, atau "tidak ada">

## Struktur tujuan
<pohon folder tujuan>

## Langkah
| No | Pindah dari | Ke | File yang import-nya ikut diperbaiki | Status |
|---|---|---|---|---|
| 0 | — | — | Mencatat kondisi awal | menunggu |
| 1 | ... | ... | ... | menunggu |

## Di luar cakupan
Temuan yang perlu diperbaiki tapi tidak dikerjakan saat merapikan struktur.
```

Status langkah: `menunggu`, `selesai`, `dibatalkan`.
