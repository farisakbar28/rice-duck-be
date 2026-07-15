# Changelog

## [1.0.0] - 2026-07-15
- Transisi total ke SoT mutlak: Model Matematika Data Collection DSS Padi Bebek FINAL.docx.
- Optimalisasi runtime backend (penghapusan dead code, referensi legacy, dan logic yang superseded).
- Sinkronisasi parameter Material Engine dengan data empiris lokal Bali (B5A04).
- Pembaruan struktur output JSON dan Database memisahkan komponen Core (Kas Tunai Inti) dan Isolated (Indikatif).
- Migrasi konstanta asimtot R_weed dari 0.95 menjadi 0.93.
- Pembaruan parameter lambda_eff survival dari 0.67 menjadi 0.78125.
- Perbaikan basis kalkulasi fungsi ekologi gulma murni berbasis A_are, bukan upah buruh lama.
- Koreksi batas bawah threshold fungsi penalti umur bebek menjadi rentang interval 14-29 (bukan 14-20).
- Pembaruan skenario pengujian unit test backend dan payload integrasi merujuk tes_skenario.md hasil simulasi clean data terbaru (36 Baris Dataset Actual).
