# 🪶 ParquetView

**100% private, in-browser Parquet viewer & converter.** Open `.parquet` files instantly — they are parsed on your device and **never uploaded**. No signup, no ads, works on desktop and mobile.

🔗 **Try it:** https://ggyg5gxksw.page.coze.site

## Features

- 🔍 Search across all columns
- ↕️ Sort by any column
- 📄 Pagination and lazy row loading
- ⬇️ Export to **CSV** and **JSON**
- 🔒 Files never leave your browser — safe for confidential data
- 📱 Mobile-friendly, responsive UI
- Supports Snappy, Gzip, Zstd and LZ4 compression

## How it works

ParquetView is a static website with no backend. All parsing runs locally in the browser using:

- [hyparquet](https://github.com/hyparam/hyparquet) — Parquet reader
- [hyparquet-compressors](https://github.com/hyparam/hyparquet-compressors) — Snappy/Zstd/Gzip/LZ4 codecs
- WebAssembly + browser APIs

Because there is no server, there is nowhere for your data to be uploaded to.

## Project layout

```
assets/        Shared CSS, browser Parquet engine, sample file
index.html     Viewer
parquet-to-csv/   Converter landing page
parquet-to-json/  Converter landing page
what-is-parquet/      Guide
how-to-open-parquet/ Guide
open-parquet-windows/ open-parquet-mac/ open-parquet-excel/
parquet-vs-csv/
build_site.py  Static site generator
```

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Build the site

```bash
python3 build_site.py   # outputs ./site
```

## License

[MIT](./LICENSE)
