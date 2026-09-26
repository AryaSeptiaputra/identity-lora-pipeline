# Domain Desain Basis Data

Dibaca red-chan saat produk menyimpan data terstruktur, dan pink-chan saat menyusun rencana pembangunan atau membangun basis datanya.

Red-chan menetapkan **apa** model datanya; pink-chan membangunnya persis seperti tertulis.

## Aturan pokok

1. **Produk menyimpan data terstruktur:** desain data wajib berdasarkan domain **Database Design / Database Modeling** di Bagian 1. Produk tanpa basis data: tulis "tidak berlaku" di dokumen, jangan merancang.
2. **Bertahap dari conceptual ke physical.** Conceptual dan logical dirancang di semua fase; physical sesuai fase.
3. **Keputusan tertulis** dengan rancangan, alasan, dan label. Hal yang belum bisa diputuskan (misalnya kebutuhan retensi data) ditulis sebagai asumsi dan masuk "Belum pasti", bukan dilewati.
4. **Cocokkan dengan proyek**, bukan template generik: pakai alur bisnis dan status dari keputusan produk, batasan klien, dan engine yang dikunci di `CLAUDE.md`.
5. **Level mengikuti fase** (Bagian 6 `SKILL.md`): MVP hanya yang dibutuhkan fitur MVP dan yang portabel antarengine; Dev dan Production memakai kartu engineering untuk yang baru atau berubah. Jangan merancang untuk fase berikutnya.
6. **Model data adalah keputusan yang paling mahal diubah setelah kode ditulis**, jadi masuk prioritas pertama titik periksa (Bagian 3 `SKILL.md`).
7. **Riset** mengikuti Bagian 4 `SKILL.md`. Konsep dasar (normalisasi, ERD, kunci) cukup "pengetahuan umum". Untuk keputusan yang terikat engine atau framework ORM, sumber tingkat 1 adalah dokumentasi resminya.

## Bagian 1 — Database Design / Database Modeling

Dirancang bertahap dari yang paling bebas engine ke yang paling terikat engine.

| Tingkat | Yang diputuskan | Fase |
|---|---|---|
| **Conceptual** | Entitas bisnis, atribut kunci, relasi dan kardinalitas (1:1, 1:N, N:M), dalam bahasa domain bisnis. | Semua fase |
| **Logical** | Tabel dan kolom, primary key, foreign key, jenis kunci (natural atau surrogate), normalisasi (target 3NF; denormalisasi hanya dengan alasan), tabel penghubung untuk N:M, tipe logis (uang dengan desimal, bukan float), nullability, unique constraint, status beserta transisi yang sah, aturan hapus (soft delete atau hapus fisik, perilaku on delete), jejak waktu, dan letak data pribadi. | Semua fase |
| **Physical** | Engine, tipe kolom, indeks berdasarkan pola query, constraint di level database, migrasi, portabilitas antarengine, backup dan retensi. | MVP: hanya yang perlu dan portabel. Dev dan Production: kartu engineering |

**Cara menulis di dokumen:** bagian `Model data` di bagian teknis `docs/keputusan-produk.md`: tabel `Entitas | Isi | Kunci | Relasi | Aturan integritas`, ditambah keputusan tingkat physical yang berlaku di fase itu. Diagram ERD hanya di laporan (Bagian 6.5 `SKILL.md`).

## Bentrokan yang diperiksa

| Bentrokan | Contoh |
|---|---|
| Status yang harus ada di model data tidak terwakili | Alur status di keputusan bisnis tanpa kolom atau constraint |
| Data pribadi bercampur dengan data yang tampil publik | Identitas donor anonim di tabel yang sama dengan agregat publik |
| Aturan hapus merusak riwayat atau relasi | Menghapus entitas yang masih dirujuk data lain |
| Model MVP tidak bisa pindah ke engine fase berikutnya | Fitur khusus satu engine tanpa alasan |

## Untuk pink-chan

1. **Bangun persis model data di file `a`.** Entitas, relasi, kunci, dan constraint tidak diputuskan sendiri. Kalau pekerjaan menyentuh basis data tetapi model yang dibutuhkan belum ada di file `a`, berhenti, kembalikan pertanyaan, dan sarankan Arya menyelesaikannya lewat red-chan.
2. **Rencana `b`:** kolom Peta keputusan → kode menyebut tingkat modelnya (misalnya `K8 Model data → donations/models.py`). Model data dan migrasi dibangun sebelum API dan UI yang memakainya.
3. **Saat membangun:**
   - Perubahan skema selalu lewat migrasi, dan migrasi yang sudah diterapkan tidak diubah.
   - Relasi, unique constraint, dan aturan integritas dari rancangan diterapkan di level database, bukan hanya validasi aplikasi.
   - Transisi status yang sah diperiksa di kode dan dites.
   - Indeks mengikuti rancangan, tidak ditambah atas dugaan.
   - Nama tabel dan kolom mengikuti model logis.
   - Data pribadi tidak masuk log.
4. **Sebuah keputusan tidak bisa dibangun** (misalnya bentrok dengan keputusan lain, atau engine tidak mendukungnya): berhenti dan laporkan; Arya membawanya ke red-chan.
5. **Laporan** menyebut tingkat model yang disentuh pekerjaan itu.
