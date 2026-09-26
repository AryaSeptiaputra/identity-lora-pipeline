# Domain Desain UI/UX

Dibaca red-chan saat produk punya antarmuka (web, aplikasi, dashboard, portal), dan pink-chan saat menyusun rencana pembangunan atau membangun antarmuka itu.

Red-chan menetapkan **apa** keputusan tiap domain; pink-chan membangunnya persis seperti tertulis.

## Aturan pokok

1. **Produk punya antarmuka:** desain UI/UX wajib disusun berdasarkan **delapan domain** di Bagian 1. Produk tanpa antarmuka (misalnya CLI atau pipeline): tulis "tidak berlaku" di dokumen, jangan merancang.
2. **Tiap domain punya keputusan tertulis** dengan rancangan, alasan, dan label. Dua domain yang memang satu keputusan boleh berbagi satu K (misalnya Design Tokens + Color System), tetapi kedua domain tetap disebut di kolom Domain.
3. **Domain tidak dilewati diam-diam.** Kalau belum bisa diputuskan (misalnya font menunggu klien), tulis asumsi sementara dan masukkan ke "Belum pasti".
4. **Cocokkan dengan proyek**, bukan template generik: pakai identitas brand, pengguna (D1), dan tech stack yang dikunci di `CLAUDE.md`. Kalau brief sudah menetapkan sebagian (misalnya palet warna), tulis sebagai keputusan domain terkait, jangan dirancang ulang.
5. **Level mengikuti fase** (Bagian 6 `SKILL.md`): MVP satu keputusan ringkas per domain, hanya untuk yang dibutuhkan halaman MVP; Dev dan Production memakai kartu engineering untuk yang baru atau berubah. Jangan merancang untuk fase berikutnya.
6. **Riset** mengikuti Bagian 4 `SKILL.md`. Konsep dasar (Gestalt, visual hierarchy, teori warna) cukup "pengetahuan umum". Sumber tingkat 1: standar W3C (WCAG, format Design Tokens Community Group), dokumentasi framework yang dikunci project, pedoman resmi Material Design atau Apple Human Interface Guidelines.

## Bagian 1 — Delapan domain UI/UX

Urutan ini juga urutan ketergantungannya: Design System menjadi payung, token membawa nilainya, dan komponen serta tata letak memakai token.

| # | Domain | Yang diputuskan |
|---|---|---|
| 1 | **Design System** | Cakupan (token, komponen, pola halaman, aturan pakai), satu sumber kebenaran, letaknya di kode, prinsip desain proyek. |
| 2 | **Design Tokens** | Nilai desain bernama peran (bukan nama nilai) sebagai satu-satunya sumber: kategori (color, typography, spacing, radius, shadow), tingkat (primitive → semantic → component, hanya bila perlu), format dan tempat, aturan penamaan, dan aturan "nilai mentah hanya di berkas token". |
| 3 | **Typography System** | Keluarga font dan fallback, skala ukuran (`ukuran_n = dasar · rasio^n` atau daftar langkah), weight, line-height, batas lebar baris, dan peran teks (heading, body, label, caption). |
| 4 | **Color System** | Palet per peran (brand, netral, semantik), pasangan kontras dan ambangnya (WCAG 2.2: teks ≥ 4,5, non-teks ≥ 3), state (hover, focus, selected, disabled), aturan tidak mengandalkan warna saja, dan ada tidaknya dark mode. |
| 5 | **Spacing & Layout System** | Unit dasar dan skala (`spasi_n = unit · n`), grid dan kolom, breakpoint, lebar konten maksimum, pola tata letak per jenis halaman (publik, dashboard, form), dan perilaku responsif. |
| 6 | **Component Design** | Daftar komponen dasar, anatomi, varian, state, kontrak (masukan dan perilaku), aksesibilitas (keyboard, fokus terlihat, label), dan aturan komposisi. Hanya komponen yang dipakai halaman fase ini. |
| 7 | **Visual Hierarchy** | Apa yang paling penting di tiap jenis halaman, alat hierarkinya (ukuran, weight, kontras, posisi, spasi), satu aksi utama per tampilan, dan urutan pindai mata. |
| 8 | **Gestalt Principles** | Prinsip yang dipakai dan di mana: proximity, similarity, continuity, closure, figure-ground, common region, uniform connectedness. Diterapkan ke pengelompokan field form, kartu, tabel, dan navigasi. |

**Cara menulis di dokumen:** tabel `Domain | Keputusan (K#) | Ringkasan` dengan delapan baris, di bagian `Desain UI/UX` pada bagian teknis `docs/keputusan-produk.md`. Rumus dan parameter (skala tipografi, unit spasi, ambang kontras) ditulis lengkap di Rincian engineering karena pink-chan mengimplementasikannya persis.

## Bentrokan yang diperiksa

| Bentrokan | Contoh |
|---|---|
| Komponen memakai nilai mentah, bukan token | Hex atau px tertulis langsung di komponen |
| Warna brand dipakai terlalu banyak sehingga hierarki visual hilang | Semua tautan, tombol, dan status berwarna brand |
| Jarak antarkelompok tidak lebih besar dari jarak dalam kelompok | Prinsip proximity rusak walau skala spasi benar |
| Warna brand atau semantik tidak lolos kontras | Teks di atas latar lembut |

## Untuk pink-chan

1. **Bangun persis keputusan domain di file `a`.** Nilai token, skala tipografi dan spasi, ambang kontras, dan bentuk komponen tidak diputuskan sendiri. Kalau pekerjaan menyentuh UI tetapi domain yang dibutuhkan belum ada di file `a`, berhenti, kembalikan pertanyaan, dan sarankan Arya menyelesaikannya lewat red-chan.
2. **Rencana `b`:** kolom Peta keputusan → kode menyebut domainnya (misalnya `K12 Design Tokens → src/styles.css`). Urutan langkah: token sebelum komponen, komponen sebelum halaman.
3. **Saat membangun:**
   - Token adalah satu sumber; tidak ada nilai mentah di luar berkas token.
   - Komponen hanya memakai token.
   - Aksesibilitas dasar dari Component Design dibangun: fokus terlihat, label field, dan navigasi keyboard.
   - Nilai yang ditetapkan dengan ambang (kontras, skala) dijaga test.
4. **Dua keputusan domain bentrok di kode**, atau sebuah keputusan tidak bisa dibangun: berhenti dan laporkan; Arya membawanya ke red-chan.
5. **Laporan** menyebut domain yang disentuh pekerjaan itu.
