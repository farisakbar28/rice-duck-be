# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed

- Final A+C evidence freeze: primary C0 tetap `50 kg/are`; Xiong adalah reference-only tanpa fusion, fallback, atau perubahan economics.
- Literature contract memakai `VALID_DOMAIN` atau `OUTSIDE_LITERATURE_DOMAIN`; economics tetap bersumber dari primary C0.
- Current authenticated history memakai payload v4; storage v1-v3 tetap dipertahankan secara fisik dan tersembunyi dari current API.
- Optimizer legacy dan numerical impact engine dihapus dari API/engine aktif; harga dan boundary aktif disimpan sebagai A+C lookup metadata.
- Runtime validator sekarang menjalankan acceptance HTTP nyata, nonce provenance, replay holdout source-faithful, dan preservation check v1-v3 pada database terisolasi.

### Security

- JWT secret operasional tidak lagi memiliki default tracked; konfigurasi wajib melalui environment.

## [2.0.0] - 2026-07-16

### Historical

- Catatan rilis model pra-A+C dipertahankan hanya sebagai riwayat Git dan tidak mendeskripsikan kontrak runtime saat ini.

## [1.0.0] - 2026-07-15

### Historical

- Prototipe awal, termasuk optimizer, merupakan riwayat dan bukan bagian dari API riset A+C saat ini.
