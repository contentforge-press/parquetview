#!/usr/bin/env python3
"""ParquetView static site generator."""
import os, json, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
SITE_URL = "https://ggyg5gxksw.page.coze.site"  # current domain; canonical updated on custom domain

os.makedirs(SITE, exist_ok=True)
os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)

NAV = [
    ("/", "Viewer"),
    ("/parquet-to-csv/", "Parquet to CSV"),
    ("/parquet-to-json/", "Parquet to JSON"),
    ("/how-to-open-parquet/", "How to open"),
    ("/what-is-parquet/", "What is Parquet?"),
]

def nav_html(active):
    links = ""
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        links += f'<a href="{href}"{cls}>{label}</a>'
    return f"""<nav class="nav"><div class="in">
  <a class="brand" href="/"><span>🪶</span> ParquetView</a>
  <div class="navlinks">{links}</div>
</div></nav>"""

FOOTER = f"""<footer class="site"><div class="in"><div class="cols">
  <div><h4>ParquetView</h4>Free, privacy-first Parquet tools. Files never leave your browser.<br>© 2026 ParquetView</div>
  <div><h4>Tools</h4><a href="/">Parquet Viewer</a><br><a href="/parquet-to-csv/">Parquet to CSV</a><br><a href="/parquet-to-json/">Parquet to JSON</a></div>
  <div><h4>Guides</h4><a href="/what-is-parquet/">What is a Parquet file?</a><br><a href="/how-to-open-parquet/">How to open Parquet</a><br><a href="/open-parquet-windows/">On Windows</a> &middot; <a href="/open-parquet-mac/">Mac</a> &middot; <a href="/open-parquet-linux/">Linux</a> &middot; <a href="/open-parquet-excel/">Excel</a><br><a href="/parquet-vs-csv/">Parquet vs CSV</a> &middot; <a href="/parquet-vs-json/">JSON</a> &middot; <a href="/parquet-vs-orc/">ORC</a><br><a href="/parquet-viewer-online/">Parquet viewer online</a> &middot; <a href="/parquet-to-jsonl/">Parquet to JSONL</a></div>
</div></div></footer>"""

TOOL_MARKUP = """
  <header class="page">
    <h1>{h1}</h1>
  </header>
  <p class="sub">{sub}</p>
  <div class="badges">
    <span class="badge">&#128274; <b>100% local</b> &middot; no upload</span>
    <span class="badge">&#128683; <b>No signup</b></span>
    <span class="badge">&#9889; Snappy &middot; Gzip &middot; Zstd &middot; LZ4</span>
    <span class="badge">&#128241; Works on mobile</span>
  </div>
  <div id="dropzone" class="drop">
    <div class="big">&#128196;</div>
    <strong>{drop_strong}</strong>
    <span>{drop_span}</span>
    <div class="or"><button class="btn" id="pickbtn" type="button">Choose file</button></div>
    <span style="display:block;margin-top:10px;font-size:12px">Files stay on your device &mdash; they never leave your browser.</span>
  </div>
  <input type="file" id="fileinput" accept=".parquet,.pq,.parq">
  <section id="workspace" class="hidden">
    <div class="bar">
      <div class="search"><span class="ic">&#128269;</span><input id="q" type="search" placeholder="Search all columns&hellip;" autocomplete="off"></div>
      <button class="btn ghost small" id="resetbtn" type="button">New file</button>
    </div>
    <div class="meta">
      <div class="card"><div class="k">File</div><div class="v" id="m-filename" style="font-size:14px;word-break:break-all">&mdash;</div></div>
      <div class="card"><div class="k">Total rows</div><div class="v" id="m-rows">&mdash;</div></div>
      <div class="card"><div class="k">Columns</div><div class="v" id="m-cols">&mdash;</div></div>
      <div class="card"><div class="k">Row groups</div><div class="v" id="m-groups">&mdash;</div></div>
      <div class="card"><div class="k">File size</div><div class="v" id="m-size">&mdash;</div></div>
    </div>
    <div class="schemawrap" id="schemawrap">
      <div class="schemahd" id="schemahd"><span class="t">Schema &amp; columns (<span id="schemacount">0</span>)</span><span class="chev">&#9662;</span></div>
      <div class="schema" id="schema"></div>
    </div>
    <div class="bar">
      <span class="badge" id="matchbadge" style="padding:6px 11px">&mdash; matches</span>
      <div class="spacer"></div>
      <button class="btn ghost small" id="csvbtn" type="button">&#11015;&#65039; Export CSV</button>
      <button class="btn ghost small" id="jsonbtn" type="button">&#11015;&#65039; JSON</button>
    </div>
    <div class="tablewrap" id="tablewrap">
      <table class="data"><thead><tr id="headrow"></tr></thead><tbody id="body"></tbody></table>
    </div>
    <div class="pager">
      <button class="btn ghost small" id="prev" type="button">&lsaquo; Prev</button>
      <span class="info" id="pageinfo">&mdash;</span>
      <button class="btn ghost small" id="next" type="button">Next &rsaquo;</button>
      <button class="btn small" id="loadmore" type="button">Load more rows</button>
    </div>
  </section>
"""

def ld_json(kind, title, desc, url):
    base = {
        "@context": "https://schema.org",
        "@type": kind,
        "name": title,
        "description": desc,
        "url": SITE_URL + url,
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Any",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    if kind == "WebApplication":
        base["featureList"] = ["Open Parquet files locally", "Search and sort", "Export to CSV", "Export to JSON"]
    return '<script type="application/ld+json">' + json.dumps(base, ensure_ascii=False) + "</script>"

def article_ld(title, desc, url, headline):
    data = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": headline,
        "description": desc,
        "url": SITE_URL + url,
        "author": {"@type": "Organization", "name": "ParquetView"},
        "publisher": {"@type": "Organization", "name": "ParquetView"},
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"

def breadcrumb_ld(items):
    # items: list of (name, path)
    el = [{"@type": "ListItem", "position": i+1, "name": n,
           "item": SITE_URL + p} for i,(n,p) in enumerate(items)]
    return '<script type="application/ld+json">' + json.dumps(
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":el}, ensure_ascii=False) + "</script>"

def page(title, desc, canonical, body, active, extra_head="", og_image="/assets/og.png"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{H.escape(title)}</title>
<meta name="description" content={json.dumps(desc)}>
<link rel="canonical" href="{SITE_URL}{canonical}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#129702;</text></svg>">
<meta property="og:type" content="website">
<meta property="og:title" content={json.dumps(title)}>
<meta property="og:description" content={json.dumps(desc)}>
<meta property="og:url" content="{SITE_URL}{canonical}">
<meta property="og:image" content="{SITE_URL}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content={json.dumps(title)}>
<meta name="twitter:description" content={json.dumps(desc)}>
<meta name="twitter:image" content="{SITE_URL}{og_image}">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}
</head>
<body>
{nav_html(active)}
<div class="wrap">
{body}
</div>
{FOOTER}
<div class="toast" id="toast"></div>
<script type="module" src="/assets/tool.js"></script>
</body>
</html>
"""

def related_block(items):
    h = '<div class="related">'
    for href, title, sub in items:
        h += f'<a href="{href}">{title}<span>{sub}</span></a>'
    return h + "</div>"

# ---------------- Pages ----------------
PAGES = {}

def write_file(relpath, content):
    full = os.path.join(SITE, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

# 1) Home / Viewer
home_body = TOOL_MARKUP.format(
    h1='Parquet Viewer',
    sub='Open <code>.parquet</code> files instantly &mdash; right in your browser. Nothing is ever uploaded.',
    drop_strong='Drop your .parquet file here',
    drop_span='or tap to choose a file from your device',
) + related_block([
    ("/parquet-to-csv/", "Parquet to CSV", "Convert to spreadsheet, 100% local"),
    ("/parquet-to-json/", "Parquet to JSON", "Export rows as JSON"),
    ("/what-is-parquet/", "What is a Parquet file?", "Why teams use this format"),
])
PAGES["index.html"] = page(
    "Parquet Viewer — Open .parquet Files in Your Browser, 100% Private",
    "Free online Parquet viewer & converter. Open .parquet files directly in your browser — no upload, no signup, fully private. Preview, search, sort and export to CSV / JSON.",
    "/", home_body, "/",
    extra_head=ld_json("WebApplication", "ParquetView — Parquet Viewer",
                       "Open Parquet files in your browser, 100% locally and privately", "/")
)

# 2) Parquet to CSV
csv_body = TOOL_MARKUP.format(
    h1='Parquet to CSV Converter',
    sub='Convert <code>.parquet</code> to <code>.csv</code> entirely on your device. No upload, no size limit, no signup.',
    drop_strong='Drop a .parquet file to convert to CSV',
    drop_span='or tap to choose a file &mdash; then hit “Export CSV”',
) + """
<div class="prose">
<h2>How to convert Parquet to CSV</h2>
<ol>
<li><b>Drop or choose</b> your <code>.parquet</code> file above. It is parsed locally in your browser.</li>
<li>Preview the rows, then click <b>“Export CSV”</b>.</li>
<li>Your <code>.csv</code> downloads immediately &mdash; the file never touched a server.</li>
</ol>
<blockquote>Because conversion runs locally with WebAssembly, even large or confidential exports are safe. There is no upload step at all.</blockquote>
</div>
""" + related_block([
    ("/parquet-to-json/", "Parquet to JSON", "Need JSON instead?"),
    ("/", "Parquet Viewer", "Just want to inspect the file?"),
    ("/what-is-parquet/", "What is Parquet?", "Learn the format"),
])
PAGES["parquet-to-csv/index.html"] = page(
    "Parquet to CSV — Free Online Converter, No Upload",
    "Convert Parquet to CSV in your browser for free. No file upload, no signup, no limits — your data stays private. Preview then export to CSV instantly.",
    "/parquet-to-csv/", csv_body, "/parquet-to-csv/",
    extra_head=ld_json("WebApplication","Parquet to CSV Converter","Convert Parquet to CSV locally and privately","/parquet-to-csv/")
    + breadcrumb_ld([("Home","/"),("Parquet to CSV","/parquet-to-csv/")])
)

# 3) Parquet to JSON
json_body = TOOL_MARKUP.format(
    h1='Parquet to JSON Converter',
    sub='Turn <code>.parquet</code> rows into <code>.json</code> on your device. Private by design &mdash; nothing is uploaded.',
    drop_strong='Drop a .parquet file to convert to JSON',
    drop_span='or tap to choose a file &mdash; then hit “JSON”',
) + """
<div class="prose">
<h2>Export Parquet to JSON</h2>
<ol>
<li>Drop your <code>.parquet</code> file above.</li>
<li>Browse or search the rows to confirm the data.</li>
<li>Click <b>“JSON”</b> to download the rows as a formatted JSON array.</li>
</ol>
<p>Dates and timestamps are normalized so the output is ready for APIs, seed scripts and data pipelines.</p>
</div>
""" + related_block([
    ("/parquet-to-csv/", "Parquet to CSV", "Need a spreadsheet?"),
    ("/", "Parquet Viewer", "Inspect first"),
    ("/what-is-parquet/", "What is Parquet?", "Learn the format"),
])
PAGES["parquet-to-json/index.html"] = page(
    "Parquet to JSON — Free Online Converter, No Upload",
    "Convert Parquet to JSON in your browser for free. No upload, no signup, fully private. Preview rows and export a JSON array instantly.",
    "/parquet-to-json/", json_body, "/parquet-to-json/",
    extra_head=ld_json("WebApplication","Parquet to JSON Converter","Convert Parquet to JSON locally and privately","/parquet-to-json/")
    + breadcrumb_ld([("Home","/"),("Parquet to JSON","/parquet-to-json/")])
)

# 4) What is Parquet
what_body = """
<header class="page"><h1>What is a Parquet file?</h1></header>
<p class="sub">A plain-English guide to the columnar data format used everywhere in data and AI.</p>
<div class="prose">
<p><b>Apache Parquet</b> is an open, column-oriented file format designed for storing and processing large tables efficiently. If CSV is a simple grid of rows and columns you can open anywhere, Parquet is a compressed, typed, analytics-optimized version of the same idea.</p>

<h2>Row-oriented vs column-oriented storage</h2>
<p>A CSV (or a typical database table) stores data <i>row by row</i>. Parquet stores it <i>column by column</i>. This matters for analytics, where a query like “the average score across all records” only needs one column. Reading one compact column block is far faster than scanning every row.</p>

<table class="cmp">
<tr><th></th><th>CSV</th><th>Parquet</th></tr>
<tr><td>Layout</td><td>Row-based</td><td>Column-based</td></tr>
<tr><td>Size</td><td>Larger, plain text</td><td>Smaller (compression + encoding)</td></tr>
<tr><td>Types</td><td>None built in</td><td>Strong schema &amp; types</td></tr>
<tr><td>Best for</td><td>Sharing, spreadsheets</td><td>Analytics, data lakes, AI</td></tr>
<tr><td>Opens in Excel?</td><td>Yes</td><td>No &mdash; use a viewer</td></tr>
</table>

<h2>Why teams choose Parquet</h2>
<ul>
<li><b>Smaller files:</b> columnar encoding plus compression (Snappy, Zstd, Gzip) shrink storage dramatically.</li>
<li><b>Faster queries:</b> engines read only the columns they need.</li>
<li><b>Schema built in:</b> types, nullability and nested structures travel with the data.</li>
<li><b>Ecosystem:</b> Spark, DuckDB, pandas, Polars, Snowflake, BigQuery and most AI/data pipelines speak Parquet natively.</li>
</ul>

<h2>The catch</h2>
<p>Parquet is <b>binary</b>, so you cannot just double-click it in Excel or a text editor. That is exactly why tools like the <a href="/">ParquetView viewer</a> exist &mdash; open and inspect the file right in your browser without installing anything.</p>

<div class="cta">
<h3>Open your first Parquet file</h3>
<p>Free, private, no signup. It opens directly in your browser.</p>
<div class="row"><a class="btn" href="/">Open the viewer</a><a class="btn ghost" href="/how-to-open-parquet/">See how to open Parquet</a></div>
</div>
</div>
""" + related_block([
    ("/how-to-open-parquet/", "How to open Parquet", "4 ways, step by step"),
    ("/parquet-to-csv/", "Parquet to CSV", "Convert locally"),
    ("/", "Parquet Viewer", "Open in browser"),
])
PAGES["what-is-parquet/index.html"] = page(
    "What is a Parquet File? A Simple Explanation (2026)",
    "What is Parquet? A simple guide to the columnar file format — how it compares to CSV, why data and AI teams use it, and how to open .parquet files.",
    "/what-is-parquet/", what_body, "/what-is-parquet/",
    extra_head=article_ld("What is a Parquet File?","A simple guide to the columnar Parquet file format","/what-is-parquet/","What is a Parquet file?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("What is Parquet","/what-is-parquet/")])
)

# 5) How to open Parquet
open_body = """
<header class="page"><h1>How to open a Parquet file</h1></header>
<p class="sub">Four ways &mdash; pick the one that matches your tools. The fastest needs nothing installed.</p>
<div class="prose">

<h2>Option 1 &mdash; Open it in your browser (fastest)</h2>
<p>If you just need to look at the data, use a browser-based viewer. With <a href="/">ParquetView</a> the file is parsed on your device and is never uploaded, so it is safe for confidential data.</p>
<ol>
<li>Open the <a href="/">Parquet viewer</a>.</li>
<li>Drop your <code>.parquet</code> file.</li>
<li>Search, sort and export to CSV or JSON.</li>
</ol>

<h2>Option 2 &mdash; Python with pandas</h2>
<pre><code>import pandas as pd
df = pd.read_parquet("data.parquet")
print(df.head())
df.to_csv("data.csv", index=False)</code></pre>
<p>Requires Python with <code>pandas</code> and a Parquet engine such as <code>pyarrow</code>.</p>

<h2>Option 3 &mdash; DuckDB (great for large files and SQL)</h2>
<pre><code>INSTALL httpfs;
SELECT * FROM read_parquet('data.parquet') LIMIT 20;</code></pre>
<p>DuckDB runs locally and can query huge Parquet files without loading everything into memory.</p>

<h2>Option 4 &mdash; Command line / other tools</h2>
<p>Data engineers often inspect Parquet through Spark, Polars (<code>pl.read_parquet()</code>) or dedicated IDE plugins. These are powerful but require setup.</p>

<table class="cmp">
<tr><th>Method</th><th>Install needed?</th><th>Good for</th></tr>
<tr><td>Browser viewer</td><td>No</td><td>Quick, private inspection</td></tr>
<tr><td>pandas</td><td>Yes</td><td>Analysts who already use Python</td></tr>
<tr><td>DuckDB</td><td>Yes</td><td>Large files, SQL queries</td></tr>
<tr><td>Spark / Polars</td><td>Yes</td><td>Heavy data engineering</td></tr>
</table>

<div class="cta">
<h3>Want the no-install way?</h3>
<p>Open the viewer and drop your file &mdash; it stays on your device.</p>
<div class="row"><a class="btn" href="/">Open Parquet now</a></div>
</div>
</div>
""" + related_block([
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
    ("/parquet-to-csv/", "Parquet to CSV", "Convert locally"),
    ("/parquet-to-json/", "Parquet to JSON", "Export to JSON"),
])
PAGES["how-to-open-parquet/index.html"] = page(
    "How to Open a Parquet File (4 Easy Ways, 2026)",
    "How to open a .parquet file: in your browser instantly, with pandas, with DuckDB, or via command-line tools. Step-by-step, with code.",
    "/how-to-open-parquet/", open_body, "/how-to-open-parquet/",
    extra_head=article_ld("How to open a Parquet file","Four ways to open Parquet files, step by step","/how-to-open-parquet/","How to open a Parquet file")
    + breadcrumb_ld([("Home","/"),("Guides","/how-to-open-parquet/"),("How to open","/how-to-open-parquet/")])
)

# 6) Open Parquet on Windows
win_body = """
<header class="page"><h1>How to open a Parquet file on Windows</h1></header>
<p class="sub">No Python, no command line &mdash; open <code>.parquet</code> on Windows 10/11 in seconds.</p>
<div class="prose">
<p>Windows cannot open <code>.parquet</code> files by itself: double-clicking one won't work in File Explorer, and Excel for Windows has no built-in Parquet importer. You have three practical options.</p>

<h2>Option 1 &mdash; Browser viewer (nothing to install)</h2>
<ol>
<li>Open the <a href="/">ParquetView viewer</a> in Edge or Chrome.</li>
<li>Drag the <code>.parquet</code> file from File Explorer onto the page (or click <b>Choose file</b>).</li>
<li>Search and sort the rows, then export to CSV to open in Excel.</li>
</ol>
<p>The file is parsed locally on your PC and is <b>never uploaded</b>, which matters for work data you are not allowed to send online.</p>

<h2>Option 2 &mdash; Convert locally with Python</h2>
<pre><code>pip install pandas pyarrow
python -c "import pandas as pd; pd.read_parquet('data.parquet').to_csv('data.csv', index=False)"</code></pre>
<p>This requires installing Python and libraries &mdash; overkill if you only want a quick look.</p>

<h2>Option 3 &mdash; Power BI Desktop</h2>
<p>If you already use <b>Power BI Desktop</b>, choose <i>Get Data &rarr; More&hellip; &rarr; Parquet</i> and select the file. It is powerful for reporting but a heavy install just to inspect one file.</p>

<table class="cmp">
<tr><th>Windows method</th><th>Install?</th><th>Best for</th></tr>
<tr><td>Browser viewer</td><td>No</td><td>Quick, private look</td></tr>
<tr><td>Python</td><td>Yes</td><td>Repeated conversions</td></tr>
<tr><td>Power BI</td><td>Yes</td><td>Dashboards &amp; reporting</td></tr>
</table>

<div class="cta"><h3>Open Parquet on Windows now</h3>
<p>Free &middot; no install &middot; the file stays on your computer.</p>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/open-parquet-mac/", "On a Mac?", "Open Parquet on macOS"),
    ("/open-parquet-excel/", "Need it in Excel?", "Convert to CSV first"),
    ("/how-to-open-parquet/", "All methods", "Compare every option"),
])
PAGES["open-parquet-windows/index.html"] = page(
    "How to Open a Parquet File on Windows (No Python, 2026)",
    "Open .parquet files on Windows 10/11 without Python: use a free browser-based viewer that parses the file locally and privately, then export to CSV for Excel.",
    "/open-parquet-windows/", win_body, None,
    extra_head=article_ld("Open a Parquet file on Windows","How to open Parquet on Windows without Python","/open-parquet-windows/","How to open a Parquet file on Windows")
    + breadcrumb_ld([("Home","/"),("Guides","/how-to-open-parquet/"),("Windows","/open-parquet-windows/")])
)

# 7) Open Parquet on Mac
mac_body = """
<header class="page"><h1>How to open a Parquet file on Mac</h1></header>
<p class="sub">Open <code>.parquet</code> on macOS without Homebrew or the terminal.</p>
<div class="prose">
<p>Neither Finder, Quick Look nor Microsoft Excel for Mac can open a <code>.parquet</code> file directly. Here are the three routes that actually work.</p>

<h2>Option 1 &mdash; Browser viewer (fastest, private)</h2>
<ol>
<li>Open <a href="/">ParquetView</a> in Safari or Chrome.</li>
<li>Drag the file from Finder or the Downloads stack onto the page.</li>
<li>Browse the rows and export to CSV or JSON.</li>
</ol>
<p>Everything is parsed on your Mac and never uploaded, so confidential exports stay private.</p>

<h2>Option 2 &mdash; Python via Homebrew</h2>
<pre><code>brew install python
pip3 install pandas pyarrow
python3 -c "import pandas as pd; print(pd.read_parquet('data.parquet').head())"</code></pre>

<h2>Option 3 &mdash; DuckDB for SQL fans</h2>
<pre><code>brew install duckdb
duckdb -c "SELECT * FROM read_parquet('data.parquet') LIMIT 20;"</code></pre>

<table class="cmp">
<tr><th>macOS method</th><th>Install?</th><th>Best for</th></tr>
<tr><td>Browser viewer</td><td>No</td><td>Fast, private inspection</td></tr>
<tr><td>Python</td><td>Yes</td><td>Analysts using pandas</td></tr>
<tr><td>DuckDB</td><td>Yes</td><td>SQL on large files</td></tr>
</table>

<div class="cta"><h3>Open it now, no install</h3>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/open-parquet-windows/", "On Windows?", "Open Parquet on Windows"),
    ("/open-parquet-excel/", "Want Excel?", "Convert to CSV"),
    ("/how-to-open-parquet/", "All methods", "Compare options"),
])
PAGES["open-parquet-mac/index.html"] = page(
    "How to Open a Parquet File on Mac (No Terminal, 2026)",
    "Open .parquet files on macOS without Homebrew or terminal. Use a free browser viewer that parses locally and privately, then export CSV or JSON.",
    "/open-parquet-mac/", mac_body, None,
    extra_head=article_ld("Open a Parquet file on Mac","How to open Parquet on macOS without the terminal","/open-parquet-mac/","How to open a Parquet file on Mac")
    + breadcrumb_ld([("Home","/"),("Guides","/how-to-open-parquet/"),("Mac","/open-parquet-mac/")])
)

# 8) Open Parquet in Excel
excel_body = """
<header class="page"><h1>How to open a Parquet file in Excel</h1></header>
<p class="sub">Excel can't read Parquet directly &mdash; here's the no-install workaround.</p>
<div class="prose">
<p>Microsoft Excel (Windows and Mac) has <b>no native Parquet import</b>. If you open a <code>.parquet</code> file in Excel you will see garbled binary text. The reliable workaround is to convert it to CSV first &mdash; and you can do that without uploading anything.</p>

<h2>Step-by-step</h2>
<ol>
<li>Open the <a href="/">ParquetView viewer</a> in your browser.</li>
<li>Drop the <code>.parquet</code> file. It is parsed on your device, never uploaded.</li>
<li>Click <b>Export CSV</b>.</li>
<li>Open the downloaded <code>.csv</code> in Excel, or import it with <i>Data &rarr; From Text/CSV</i> to control encoding.</li>
</ol>
<blockquote>The CSV export includes a UTF-8 BOM, so text and special characters display correctly when you open it in Excel.</blockquote>

<h2>Alternative: Power Query</h2>
<p>Newer Excel builds can use Power Query connectors for Parquet in some enterprise setups, but this is not available to everyone and still requires configuration. Converting to CSV in the browser works on every version.</p>

<h2>Tips for large files</h2>
<ul>
<li>If a file has more rows than an Excel sheet supports (1,048,576 rows), export only what you need after searching.</li>
<li>Dates are written as clean <code>YYYY-MM-DD</code> values, which Excel parses predictably.</li>
</ul>

<div class="cta"><h3>Turn Parquet into an Excel file</h3>
<div class="row"><a class="btn" href="/parquet-to-csv/">Convert to CSV now</a></div></div>
</div>
""" + related_block([
    ("/parquet-to-csv/", "Parquet to CSV", "Dedicated converter"),
    ("/how-to-open-parquet/", "Other ways to open", "pandas, DuckDB, browser"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
])
PAGES["open-parquet-excel/index.html"] = page(
    "How to Open a Parquet File in Excel (Easy Workaround, 2026)",
    "Excel can't open Parquet directly. Convert .parquet to CSV for free in your browser — no upload, fully private — then open the CSV in Excel.",
    "/open-parquet-excel/", excel_body, None,
    extra_head=article_ld("Open a Parquet file in Excel","How to open Parquet in Excel by converting to CSV locally","/open-parquet-excel/","How to open a Parquet file in Excel")
    + breadcrumb_ld([("Home","/"),("Guides","/how-to-open-parquet/"),("Excel","/open-parquet-excel/")])
)

# 9) Parquet vs CSV
vs_body = """
<header class="page"><h1>Parquet vs CSV: which should you use?</h1></header>
<p class="sub">A practical comparison of size, speed, types and portability.</p>
<div class="prose">
<p>CSV and Parquet both store tabular data, but they were built for different jobs. CSV is for portability and human readability; Parquet is for compact storage and fast analytics.</p>

<table class="cmp">
<tr><th></th><th>CSV</th><th>Parquet</th></tr>
<tr><td>Storage layout</td><td>Row-based text</td><td>Column-based binary</td></tr>
<tr><td>File size</td><td>Larger</td><td>Often 3&ndash;10&times; smaller with compression</td></tr>
<tr><td>Schema / types</td><td>None &mdash; everything is text</td><td>Built-in types, dates, nesting</td></tr>
<tr><td>Query speed</td><td>Slower for big data</td><td>Faster; reads only needed columns</td></tr>
<tr><td>Human readable</td><td>Yes</td><td>No (needs a viewer)</td></tr>
<tr><td>Excel support</td><td>Yes</td><td>No &mdash; convert first</td></tr>
<tr><td>Best for</td><td>Sharing, small exports, spreadsheets</td><td>Data lakes, analytics, AI, big files</td></tr>
</table>

<h2>When to choose CSV</h2>
<ul>
<li>You need the file to open in Excel, Google Sheets or any text editor.</li>
<li>You are emailing a small export to a non-technical person.</li>
<li>Maximum compatibility matters more than size.</li>
</ul>

<h2>When to choose Parquet</h2>
<ul>
<li>You store large datasets in S3, a data lake or a pipeline (Spark, DuckDB, pandas, Polars).</li>
<li>You want smaller storage and faster column-level queries.</li>
<li>You need types and a reliable schema to travel with the data.</li>
</ul>

<h2>Convert between them</h2>
<p>You often need both: Parquet for storage, CSV for sharing. Convert in either direction privately in your browser &mdash; <a href="/parquet-to-csv/">Parquet to CSV</a> or <a href="/parquet-to-json/">Parquet to JSON</a>, with no upload.</p>

<div class="cta"><h3>Convert a file now</h3>
<div class="row"><a class="btn" href="/parquet-to-csv/">Parquet &rarr; CSV</a><a class="btn ghost" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/what-is-parquet/", "What is Parquet?", "Plain-English guide"),
    ("/parquet-to-csv/", "Parquet to CSV", "Convert locally"),
    ("/how-to-open-parquet/", "How to open Parquet", "Step by step"),
])
PAGES["parquet-vs-csv/index.html"] = page(
    "Parquet vs CSV: File Size, Speed and When to Use Each (2026)",
    "Parquet vs CSV compared by size, speed, schema and use cases. CSV is portable; Parquet is smaller and faster for analytics. Convert between them privately.",
    "/parquet-vs-csv/", vs_body, None,
    extra_head=article_ld("Parquet vs CSV","A practical comparison of Parquet and CSV","/parquet-vs-csv/","Parquet vs CSV: which should you use?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("Parquet vs CSV","/parquet-vs-csv/")])
)

# 10) Open Parquet on Linux
linux_body = """
<header class="page"><h1>How to open a Parquet file on Linux</h1></header>
<p class="sub">From the terminal, with Python, or in the browser &mdash; no desktop app required.</p>
<div class="prose">
<p>Linux has no default handler for <code>.parquet</code>. Depending on what you have installed, choose one of these.</p>

<h2>Option 1 &mdash; In the browser (nothing to install)</h2>
<ol>
<li>Open <a href="/">ParquetView</a> in Firefox or Chrome.</li>
<li>Drop the <code>.parquet</code> file onto the page.</li>
<li>Search, sort and export to CSV or JSON.</li>
</ol>
<p>The file is parsed locally and never uploaded &mdash; handy on shared servers where you cannot install packages.</p>

<h2>Option 2 &mdash; Python</h2>
<pre><code>pip install pandas pyarrow
python -c "import pandas as pd; print(pd.read_parquet('data.parquet').head())"</code></pre>

<h2>Option 3 &mdash; DuckDB CLI</h2>
<pre><code># Debian/Ubuntu
sudo apt install duckdb
duckdb -c "SELECT * FROM read_parquet('data.parquet') LIMIT 20;"</code></pre>

<h2>Option 4 &mdash; Inspect metadata only</h2>
<pre><code>python - <<'PY'
import pyarrow.parquet as pq
f = pq.ParquetFile('data.parquet')
print(f.metadata)
print(f.schema)
PY</code></pre>

<table class="cmp">
<tr><th>Linux method</th><th>Install?</th><th>Best for</th></tr>
<tr><td>Browser viewer</td><td>No</td><td>Quick, private inspection</td></tr>
<tr><td>pandas / pyarrow</td><td>Yes</td><td>Analysis and conversion</td></tr>
<tr><td>DuckDB</td><td>Yes</td><td>SQL on large files</td></tr>
</table>

<div class="cta"><h3>Open it without installing anything</h3>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/open-parquet-windows/", "On Windows?", "Open Parquet on Windows"),
    ("/open-parquet-mac/", "On a Mac?", "Open Parquet on macOS"),
    ("/how-to-open-parquet/", "All methods", "Compare every option"),
])
PAGES["open-parquet-linux/index.html"] = page(
    "How to Open a Parquet File on Linux (Terminal & Browser, 2026)",
    "Open .parquet files on Linux: in the browser with no install, or via pandas/pyarrow, DuckDB CLI and metadata inspection. Step by step.",
    "/open-parquet-linux/", linux_body, None,
    extra_head=article_ld("Open a Parquet file on Linux","How to open Parquet on Linux from the terminal or browser","/open-parquet-linux/","How to open a Parquet file on Linux")
    + breadcrumb_ld([("Home","/"),("Guides","/how-to-open-parquet/"),("Linux","/open-parquet-linux/")])
)

# 11) Parquet viewer online (tool page, intent = "parquet viewer online")
online_body = TOOL_MARKUP.format(
    h1='Parquet Viewer Online',
    sub='View <code>.parquet</code> files online &mdash; entirely in your browser. No upload, no signup, no plugin.',
    drop_strong='Drop your .parquet file to view it online',
    drop_span='or tap to choose a file &mdash; it stays on your device',
) + """
<div class="prose">
<h2>A private online Parquet viewer</h2>
<p>Most online viewers upload your file to a server to convert it. ParquetView does the opposite: the Parquet engine (hyparquet) runs inside your browser tab, so your data never leaves your device. There is nothing to install and no account to create.</p>
<ul>
<li><b>Preview</b> rows in a clean table, on desktop or mobile.</li>
<li><b>Search and sort</b> across columns.</li>
<li><b>See the schema</b>, row groups and file metadata.</li>
<li><b>Export</b> to CSV or JSON with one click.</li>
</ul>
<blockquote>Snappy, Gzip, Zstd and LZ4 compression are supported via WebAssembly.</blockquote>
</div>
""" + related_block([
    ("/", "Parquet Viewer", "Main viewer"),
    ("/parquet-to-csv/", "Parquet to CSV", "Export a spreadsheet"),
    ("/parquet-to-json/", "Parquet to JSON", "Export JSON"),
])
PAGES["parquet-viewer-online/index.html"] = page(
    "Parquet Viewer Online — Free, No Upload, No Signup",
    "View Parquet files online for free. Files are parsed in your browser and never uploaded — no signup, no plugin. Search, sort and export to CSV/JSON.",
    "/parquet-viewer-online/", online_body, "/",
    extra_head=ld_json("WebApplication","Parquet Viewer Online","View Parquet files online in your browser, privately","/parquet-viewer-online/")
    + breadcrumb_ld([("Home","/"),("Parquet Viewer Online","/parquet-viewer-online/")])
)

# 12) Parquet to JSONL / NDJSON
jsonl_body = TOOL_MARKUP.format(
    h1='Parquet to JSONL / NDJSON Converter',
    sub='Turn <code>.parquet</code> rows into newline-delimited JSON on your device. No upload, no signup.',
    drop_strong='Drop a .parquet file to convert to JSONL',
    drop_span='or tap to choose a file &mdash; then hit “JSON”',
) + """
<div class="prose">
<h2>What is JSONL / NDJSON?</h2>
<p><b>JSON Lines</b> (also called NDJSON) stores one JSON object per line. It is the standard format for streaming logs, BigQuery/Databricks exports and bulk APIs, because each line can be read independently without parsing one giant JSON array.</p>

<h2>How to convert Parquet to JSONL</h2>
<ol>
<li>Drop your <code>.parquet</code> file above.</li>
<li>Preview the rows and confirm the columns.</li>
<li>Click <b>“Export JSONL”</b>. You get a <code>.jsonl</code> file with one JSON object per line, containing all rows.</li>
</ol>
<p>The exported keys come straight from the Parquet schema, so column names and types line up with your data model.</p>
<blockquote>Common flows: Parquet &rarr; JSONL for log shippers, event streams and Elasticsearch/OpenSearch bulk indexing.</blockquote>
</div>
""" + related_block([
    ("/parquet-to-json/", "Parquet to JSON", "Need a JSON array?"),
    ("/parquet-to-csv/", "Parquet to CSV", "Need a spreadsheet?"),
    ("/", "Parquet Viewer", "Inspect the file"),
])
PAGES["parquet-to-jsonl/index.html"] = page(
    "Parquet to JSONL / NDJSON — Free Online Converter",
    "Convert Parquet to JSONL (NDJSON) in your browser for free. No upload, no signup. Preview rows and export newline-delimited JSON for logs and APIs.",
    "/parquet-to-jsonl/", jsonl_body, "/parquet-to-json/",
    extra_head=ld_json("WebApplication","Parquet to JSONL Converter","Convert Parquet to newline-delimited JSON locally","/parquet-to-jsonl/")
    + breadcrumb_ld([("Home","/"),("Parquet to JSON","/parquet-to-json/"),("Parquet to JSONL","/parquet-to-jsonl/")])
)

# 13) Parquet vs JSON
pjson_body = """
<header class="page"><h1>Parquet vs JSON: which should you use?</h1></header>
<p class="sub">Comparing size, speed, schema and tooling for storing tabular data.</p>
<div class="prose">
<p>JSON is flexible and human-readable; Parquet is compact and built for columnar analytics. Many pipelines use both &mdash; JSON at the edges, Parquet in the warehouse.</p>

<table class="cmp">
<tr><th></th><th>JSON / JSONL</th><th>Parquet</th></tr>
<tr><td>Layout</td><td>Documents, row-oriented</td><td>Column-oriented binary</td></tr>
<tr><td>File size</td><td>Larger; keys repeat every row</td><td>Much smaller (encoding + compression)</td></tr>
<tr><td>Schema</td><td>Optional / flexible, can drift</td><td>Strong, stored in the file</td></tr>
<tr><td>Analytics speed</td><td>Slower; parse whole records</td><td>Fast; reads only needed columns</td></tr>
<tr><td>Human readable</td><td>Yes</td><td>No (needs a viewer)</td></tr>
<tr><td>Nested data</td><td>Excellent</td><td>Supported, less ad-hoc</td></tr>
<tr><td>Best for</td><td>APIs, logs, configs, interchange</td><td>Data lakes, analytics, AI, big files</td></tr>
</table>

<h2>When to choose JSON</h2>
<ul>
<li>You talk to a web API or store event logs (JSONL/NDJSON).</li>
<li>Records have different or changing shapes.</li>
<li>You need developers to read and edit the raw file.</li>
</ul>

<h2>When to choose Parquet</h2>
<ul>
<li>You query columns over many rows in Spark, DuckDB, pandas or Polars.</li>
<li>Storage cost and query speed matter.</li>
<li>You want a reliable schema enforced on write.</li>
</ul>

<h2>Move between them</h2>
<p>Convert <a href="/parquet-to-json/">Parquet to JSON</a>, <a href="/parquet-to-jsonl/">JSONL</a> or <a href="/parquet-to-csv/">CSV</a> privately in your browser &mdash; nothing is uploaded.</p>

<div class="cta"><h3>Convert a file now</h3>
<div class="row"><a class="btn" href="/parquet-to-json/">Parquet &rarr; JSON</a><a class="btn ghost" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/parquet-vs-csv/", "Parquet vs CSV", "Other comparison"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
    ("/parquet-to-json/", "Parquet to JSON", "Convert locally"),
])
PAGES["parquet-vs-json/index.html"] = page(
    "Parquet vs JSON: Size, Speed and When to Use Each (2026)",
    "Parquet vs JSON compared by file size, speed, schema and use cases. JSON is flexible for APIs and logs; Parquet is smaller and faster for analytics.",
    "/parquet-vs-json/", pjson_body, None,
    extra_head=article_ld("Parquet vs JSON","A practical comparison of Parquet and JSON","/parquet-vs-json/","Parquet vs JSON: which should you use?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("Parquet vs JSON","/parquet-vs-json/")])
)

# 14) Parquet vs ORC
orc_body = """
<header class="page"><h1>Parquet vs ORC: which columnar format?</h1></header>
<p class="sub">Both compress data well &mdash; the choice usually follows your query engine.</p>
<div class="prose">
<p><b>Parquet</b> and <b>ORC</b> are both open, columnar, compressed formats for big-data analytics. They have similar performance for many jobs; the bigger factor is the ecosystem around them.</p>

<table class="cmp">
<tr><th></th><th>Parquet</th><th>ORC</th></tr>
<tr><td>Origin</td><td>Apache, from the Hadoop/Spark world</td><td>Apache, from the Hive world</td></tr>
<tr><td>Layout</td><td>Column chunks + row groups</td><td>Stripe-based, with a built-in index</td></tr>
<tr><td>Compression</td><td>Snappy, Gzip, Zstd, LZ4</td><td>Snappy, Zlib, ZSTD, LZ4</td></tr>
<tr><td>Strongest in</td><td>Spark, Trino, Impala, AWS, broad cloud support</td><td>Hive, and highly optimized Hive/ACID reads</td></tr>
<tr><td>Nested data</td><td>Excellent (very widely used)</td><td>Supported</td></tr>
<tr><td>Adoption 2026</td><td>Broadest default across data lakes</td><td>Common in Hive-centric stacks</td></tr>
</table>

<h2>Rule of thumb</h2>
<ul>
<li>Use <b>Parquet</b> as the default unless your platform is built around Hive and already standardizes on ORC. It has the widest tooling, from Spark and DuckDB to cloud data catalogs.</li>
<li>Use <b>ORC</b> when you are deep in a Hive ecosystem, especially with transactional Hive tables that benefit from its stripe indexes.</li>
</ul>

<h2>Opening either format</h2>
<p>ORC and Parquet are binary, so neither opens by double-clicking. You can open Parquet in the browser with the <a href="/">ParquetView viewer</a> and export to CSV or JSON, with no upload.</p>

<div class="cta"><h3>Open a Parquet file now</h3>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/parquet-vs-csv/", "Parquet vs CSV", "Other comparison"),
    ("/parquet-vs-json/", "Parquet vs JSON", "Other comparison"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
])
PAGES["parquet-vs-orc/index.html"] = page(
    "Parquet vs ORC: Columnar Formats Compared (2026)",
    "Parquet vs ORC compared: both are compressed columnar formats. Parquet is the broad default for Spark/cloud; ORC shines in Hive-centric stacks.",
    "/parquet-vs-orc/", orc_body, None,
    extra_head=article_ld("Parquet vs ORC","A practical comparison of Parquet and ORC columnar formats","/parquet-vs-orc/","Parquet vs ORC: which columnar format?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("Parquet vs ORC","/parquet-vs-orc/")])
)

# 15) Parquet to Excel
excel_body = TOOL_MARKUP.format(
    h1='Parquet to Excel Converter',
    sub='Open <code>.parquet</code> data in Excel &mdash; export to CSV that opens cleanly in a spreadsheet. No upload, no signup.',
    drop_strong='Drop a .parquet file to open in Excel',
    drop_span='or tap to choose a file &mdash; then hit “Export CSV”',
) + """
<div class="prose">
<h2>How to open Parquet in Excel</h2>
<p>Excel has no native <code>.parquet</code> importer (its Power Query Parquet support is limited and Windows-only). The reliable cross-platform path is to export to CSV, which every version of Excel opens:</p>
<ol>
<li>Drop your <code>.parquet</code> file above.</li>
<li>Preview the rows and confirm the columns look right.</li>
<li>Click <b>“Export CSV”</b>. The whole file is read before export, so you get every row (not just the first page).</li>
<li>Open the downloaded CSV in Excel, or use <b>Data &rarr; From Text/CSV</b>.</li>
</ol>
<p>The CSV is written with a UTF-8 BOM so non-ASCII text and dates display correctly.</p>
<blockquote>Excel's row limit is 1,048,576 rows. If your Parquet file is larger, filter or take the subset you need before exporting rather than loading everything into one sheet.</blockquote>
<h2>Date and number columns</h2>
<p>Parquet date and timestamp columns are exported as clean <code>YYYY-MM-DD</code> and <code>YYYY-MM-DD HH:MM:SS</code> text, so Excel does not misread them. Re-save as <code>.xlsx</code> from Excel if you need formulas and formatting.</p>
</div>
""" + related_block([
    ("/open-parquet-excel/", "Open Parquet in Excel", "Detailed Excel guide"),
    ("/parquet-to-csv/", "Parquet to CSV", "Direct CSV export"),
    ("/", "Parquet Viewer", "Inspect first"),
])
PAGES["parquet-to-excel/index.html"] = page(
    "Parquet to Excel — Open .parquet in Excel Free (2026)",
    "Convert Parquet to an Excel-friendly CSV for free. Files are parsed in your browser, never uploaded. Export all rows with clean dates and open them in Excel.",
    "/parquet-to-excel/", excel_body, "/parquet-to-csv/",
    extra_head=ld_json("WebApplication","Parquet to Excel Converter","Convert Parquet to an Excel-ready CSV locally","/parquet-to-excel/")
    + breadcrumb_ld([("Home","/"),("Parquet to CSV","/parquet-to-csv/"),("Parquet to Excel","/parquet-to-excel/")])
)

# 16) Large Parquet file viewer
large_body = TOOL_MARKUP.format(
    h1='Large Parquet File Viewer',
    sub='Inspect big <code>.parquet</code> files without loading them all into memory. Rows are read on demand in your browser.',
    drop_strong='Drop a large .parquet file to inspect it',
    drop_span='or tap to choose a file &mdash; the first rows load quickly',
) + """
<div class="prose">
<h2>Why big files are a problem</h2>
<p>Reading a multi-GB Parquet file into pandas or a text editor can hang your machine or run out of memory. ParquetView avoids this:</p>
<ul>
<li>Only the <b>first rows</b> are read initially, so a large file opens almost immediately.</li>
<li><b>Metadata and schema</b> come from the Parquet footer, which is tiny even for huge files.</li>
<li>Use <b>“Load more rows”</b> only if you need to page further through the data.</li>
<li><b>Export</b> reads the rest on demand, up to the in-browser limit.</li>
</ul>
<h2>Tips for very large datasets</h2>
<ul>
<li><b>Search</b> within the loaded rows to find the records you need before exporting.</li>
<li>Parquet stores data in <b>row groups</b>; files written with many small groups may be slower than files with a few large ones.</li>
<li>For files larger than the browser can comfortably hold, work on the subset you need, or use an engine like DuckDB/Spark for full-file aggregation.</li>
</ul>
<blockquote>Everything still runs locally: a large file is read from your disk in ranges and is never uploaded anywhere.</blockquote>
</div>
""" + related_block([
    ("/", "Parquet Viewer", "Main viewer"),
    ("/parquet-viewer-online/", "Parquet Viewer Online", "Online viewer"),
    ("/parquet-to-csv/", "Parquet to CSV", "Export data"),
])
PAGES["large-parquet-file-viewer/index.html"] = page(
    "Large Parquet File Viewer — Open Big Parquet Without Crashing",
    "Open large Parquet files without loading everything into memory. Rows load on demand in your browser, privately and free — schema, search and export.",
    "/large-parquet-file-viewer/", large_body, "/",
    extra_head=ld_json("WebApplication","Large Parquet File Viewer","Inspect large Parquet files with on-demand row loading","/large-parquet-file-viewer/")
    + breadcrumb_ld([("Home","/"),("Large Parquet File Viewer","/large-parquet-file-viewer/")])
)

# 17) Open Parquet on a phone / mobile
mobile_body = TOOL_MARKUP.format(
    h1='Open Parquet Files on Your Phone',
    sub='A mobile-friendly Parquet viewer for iPhone and Android. Pick a file from your device &mdash; it is parsed in the browser, nothing is uploaded.',
    drop_strong='Tap to choose a .parquet file',
    drop_span='or open one from Files, iCloud Drive or Google Drive',
) + """
<div class="prose">
<h2>Viewing Parquet on mobile</h2>
<p>There is no built-in Parquet app on iOS or Android. ParquetView is designed to work in your phone's browser:</p>
<ol>
<li>Open this page in <b>Safari</b> (iPhone) or <b>Chrome</b> (Android).</li>
<li>Tap <b>“Choose file”</b> and pick the <code>.parquet</code> file from Files, iCloud Drive, Google Drive or a download.</li>
<li>The rows render in a scrollable, searchable table.</li>
<li>Export to CSV or JSON if you need to move the data elsewhere.</li>
</ol>
<h2>Tips</h2>
<ul>
<li>Rotate to <b>landscape</b> to see more columns.</li>
<li>Only the first rows load initially, which keeps large files fast on a phone.</li>
<li>The file is processed on the device &mdash; useful when you only have your phone and no laptop.</li>
</ul>
<blockquote>No app to install, no account, and the file never leaves your phone.</blockquote>
</div>
""" + related_block([
    ("/", "Parquet Viewer", "Full viewer"),
    ("/parquet-viewer-online/", "Parquet Viewer Online", "Online viewer"),
    ("/how-to-open-parquet/", "How to open Parquet", "All platforms"),
])
PAGES["open-parquet-mobile/index.html"] = page(
    "Open Parquet Files on Your Phone (iPhone & Android) — Free",
    "View Parquet files on iPhone or Android for free. Pick a file from Files/iCloud/Google Drive; it is parsed in your mobile browser and never uploaded.",
    "/open-parquet-mobile/", mobile_body, "/",
    extra_head=ld_json("WebApplication","Mobile Parquet Viewer","Open Parquet files on a phone in the browser","/open-parquet-mobile/")
    + breadcrumb_ld([("Home","/"),("Open Parquet on Mobile","/open-parquet-mobile/")])
)

# 18) Parquet schema viewer
schema_body = TOOL_MARKUP.format(
    h1='Parquet Schema Viewer',
    sub='Inspect the schema, column types, row groups and metadata of any <code>.parquet</code> file. Read locally, no upload.',
    drop_strong='Drop a .parquet file to see its schema',
    drop_span='or tap to choose a file &mdash; metadata loads instantly',
) + """
<div class="prose">
<h2>What you can inspect</h2>
<p>The schema lives in the Parquet footer, so it appears even before the data rows are read:</p>
<ul>
<li><b>Columns and logical types</b> &mdash; names plus types such as int64, double, string, boolean, date and timestamp.</li>
<li><b>Row count and row groups</b> &mdash; <code>num_rows</code> and the number of row groups.</li>
<li><b>File metadata</b> &mdash; size and key/value metadata written by the producer.</li>
</ul>
<h2>Why check the schema?</h2>
<ul>
<li>Confirm column names and types <b>before</b> loading a file into a pipeline.</li>
<li>Diagnose why two "same" files differ (a column read as string vs int, missing fields, etc.).</li>
<li>Verify how dates, timestamps and nested fields were encoded by the writer.</li>
</ul>
<blockquote>Toggle columns in the chip bar to focus on the fields you need, then export to CSV or JSON.</blockquote>
</div>
""" + related_block([
    ("/", "Parquet Viewer", "Browse the rows"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
    ("/large-parquet-file-viewer/", "Large File Viewer", "Big files"),
])
PAGES["parquet-schema-viewer/index.html"] = page(
    "Parquet Schema Viewer — Inspect Column Types and Metadata",
    "Inspect a Parquet file's schema, column types, row groups and metadata for free. Parsed in your browser and never uploaded.",
    "/parquet-schema-viewer/", schema_body, "/",
    extra_head=ld_json("WebApplication","Parquet Schema Viewer","Inspect Parquet schema and metadata locally","/parquet-schema-viewer/")
    + breadcrumb_ld([("Home","/"),("Parquet Schema Viewer","/parquet-schema-viewer/")])
)

# 19) Parquet vs Avro
avro_body = """
<header class="page"><h1>Parquet vs Avro: row-based or columnar?</h1></header>
<p class="sub">Both are popular Apache formats &mdash; the difference is how they lay out and read data.</p>
<div class="prose">
<p><b>Avro</b> is a <b>row-based</b> serialization format; <b>Parquet</b> is <b>columnar</b>. The choice depends on whether you are writing/transporting whole records or querying a few columns over many rows.</p>

<table class="cmp">
<tr><th></th><th>Parquet</th><th>Avro</th></tr>
<tr><td>Layout</td><td>Column chunks</td><td>Rows, one after another</td></tr>
<tr><td>Schema</td><td>Embedded in footer</td><td>Embedded with data (often paired with a schema registry)</td></tr>
<tr><td>Best at</td><td>Analytical scans of a few columns</td><td>Streaming, messaging, whole-record serialization</td></tr>
<tr><td>Compression</td><td>Very high on columnar data</td><td>Good, but usually less compact for analytics</td></tr>
<tr><td>Typical use</td><td>Data lakes, Spark/Trino tables</td><td>Kafka topics, event transport, API payloads</td></tr>
<tr><td>Column projection</td><td>Reads only requested columns</td><td>Must scan full rows</td></tr>
</table>

<h2>Rule of thumb</h2>
<ul>
<li>Store <b>Parquet</b> for data that will be queried and analyzed, especially at scale.</li>
<li>Use <b>Avro</b> for events moving through Kafka or services that read/write complete records and need strong schema evolution.</li>
<li>A common pattern is <b>Avro in the stream, Parquet in the lake</b>: ingest as Avro, land as Parquet.</li>
</ul>

<h2>Opening either format</h2>
<p>Both are binary. You can open a Parquet file in the browser with the <a href="/">ParquetView viewer</a>, inspect its schema and export to CSV or JSON, with no upload.</p>

<div class="cta"><h3>Open a Parquet file</h3>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/parquet-vs-csv/", "Parquet vs CSV", "Other comparison"),
    ("/parquet-vs-orc/", "Parquet vs ORC", "Other comparison"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
])
PAGES["parquet-vs-avro/index.html"] = page(
    "Parquet vs Avro: When to Use Each Format (2026)",
    "Parquet vs Avro compared: Parquet is columnar for analytics, Avro is row-based for streaming and event transport. A common pattern is Avro in Kafka, Parquet in the lake.",
    "/parquet-vs-avro/", avro_body, None,
    extra_head=article_ld("Parquet vs Avro","Comparing the columnar Parquet and row-based Avro formats","/parquet-vs-avro/","Parquet vs Avro: which should you use?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("Parquet vs Avro","/parquet-vs-avro/")])
)

# 20) Parquet vs Feather / Arrow IPC
feather_body = """
<header class="page"><h1>Parquet vs Feather (Arrow IPC)</h1></header>
<p class="sub">Both come from the Apache Arrow world, but one is built for archiving and the other for in-memory speed.</p>
<div class="prose">
<p><b>Feather</b> (now the <b>Arrow IPC</b> format) stores Arrow data essentially as it sits in memory, optimized for fast interchange between Python, R and Arrow processes. <b>Parquet</b> is a compressed, columnar on-disk format built for long-term storage and analytics.</p>

<table class="cmp">
<tr><th></th><th>Parquet</th><th>Feather / Arrow IPC</th></tr>
<tr><td>Purpose</td><td>Storage and analytics</td><td>Fast in-memory interchange</td></tr>
<tr><td>File size</td><td>Smaller (strong compression)</td><td>Larger (light/no compression)</td></tr>
<tr><td>Read/write speed</td><td>Slightly more CPU to decode</td><td>Very fast, near zero-copy</td></tr>
<tr><td>Durability</td><td>Long-term archive standard</td><td>Temporary/interprocess exchange</td></tr>
<tr><td>Compatibility</td><td>Nearly every data engine</td><td>Arrow-native tools</td></tr>
</table>

<h2>Rule of thumb</h2>
<ul>
<li>Use <b>Feather</b> for short-lived data you shuffle between pandas, R and Arrow jobs on the same machine, when speed matters more than size.</li>
<li>Use <b>Parquet</b> to save datasets to disk, share them, or query them later &mdash; especially large or archival data where compression matters.</li>
</ul>

<h2>Opening Parquet files</h2>
<p>If you have a <code>.parquet</code> to inspect, open it in the browser with <a href="/">ParquetView</a>, view the schema and export to CSV or JSON &mdash; no install, no upload.</p>

<div class="cta"><h3>Inspect a Parquet file</h3>
<div class="row"><a class="btn" href="/">Open the viewer</a></div></div>
</div>
""" + related_block([
    ("/parquet-vs-csv/", "Parquet vs CSV", "Other comparison"),
    ("/parquet-vs-avro/", "Parquet vs Avro", "Other comparison"),
    ("/what-is-parquet/", "What is Parquet?", "Understand the format"),
])
PAGES["parquet-vs-feather/index.html"] = page(
    "Parquet vs Feather (Arrow IPC): Storage vs Speed (2026)",
    "Parquet vs Feather compared: Parquet is compressed for storage and analytics; Feather/Arrow IPC is optimized for fast in-memory interchange between Python, R and Arrow.",
    "/parquet-vs-feather/", feather_body, None,
    extra_head=article_ld("Parquet vs Feather","Comparing Parquet and Feather/Arrow IPC","/parquet-vs-feather/","Parquet vs Feather: which should you use?")
    + breadcrumb_ld([("Home","/"),("Guides","/what-is-parquet/"),("Parquet vs Feather","/parquet-vs-feather/")])
)

# 21) Free online Parquet file converter
converter_body = TOOL_MARKUP.format(
    h1='Free Online Parquet File Converter',
    sub='Convert <code>.parquet</code> to CSV, JSON or JSON Lines in your browser. No upload, no signup, free.',
    drop_strong='Drop a .parquet file to convert it',
    drop_span='or tap to choose a file &mdash; then pick an export format',
) + """
<div class="prose">
<h2>One file, three formats</h2>
<p>Drop a Parquet file, preview it, then export to whichever format you need:</p>
<ul>
<li><b>CSV</b> &mdash; for Excel, Google Sheets and databases. The whole file is read before export.</li>
<li><b>JSON</b> &mdash; a standard array for APIs and applications.</li>
<li><b>JSON Lines (NDJSON)</b> &mdash; one object per line for logs, BigQuery and bulk import.</li>
</ul>
<h2>Private by design</h2>
<p>Unlike server-side converters, this one runs the Parquet engine entirely in your browser tab. Your file is read from your disk in ranges and is never transmitted, which also means no file-size upload limit and no waiting on a queue.</p>
<blockquote>Snappy, Gzip, Zstd and LZ4 compression are supported. int64 values are preserved even when they exceed JavaScript's safe integer range.</blockquote>
<p>If you only need to inspect a file, use the <a href="/">main viewer</a>; if you specifically need a spreadsheet, the dedicated <a href="/parquet-to-csv/">Parquet to CSV</a> page walks through it.</p>
</div>
""" + related_block([
    ("/parquet-to-csv/", "Parquet to CSV", "CSV"),
    ("/parquet-to-json/", "Parquet to JSON", "JSON"),
    ("/parquet-to-jsonl/", "Parquet to JSONL", "JSON Lines"),
])
PAGES["parquet-file-converter/index.html"] = page(
    "Free Online Parquet File Converter — CSV, JSON, JSONL (No Upload)",
    "Convert Parquet to CSV, JSON or JSONL online for free. Files are converted in your browser and never uploaded — no signup, no queue, supports Snappy/Gzip/Zstd/LZ4.",
    "/parquet-file-converter/", converter_body, "/",
    extra_head=ld_json("WebApplication","Online Parquet File Converter","Convert Parquet to CSV, JSON or JSONL locally","/parquet-file-converter/")
    + breadcrumb_ld([("Home","/"),("Parquet File Converter","/parquet-file-converter/")])
)

# 22) Convert Parquet to CSV online
onlinecsv_body = TOOL_MARKUP.format(
    h1='Convert Parquet to CSV Online',
    sub='Turn <code>.parquet</code> into a CSV download in your browser. Private, free, no signup and no upload.',
    drop_strong='Drop a .parquet file to export CSV',
    drop_span='or tap to choose a file &mdash; then hit “Export CSV”',
) + """
<div class="prose">
<h2>Fast, private Parquet &rarr; CSV</h2>
<ol>
<li>Drop your <code>.parquet</code> file above.</li>
<li>Preview the columns and confirm types.</li>
<li>Click <b>“Export CSV”</b>. All rows are read first, so the download is the complete file.</li>
</ol>
<p>The CSV uses a UTF-8 BOM and clean date/timestamp formatting, so it opens correctly in Excel and other tools.</p>
<h2>Why in the browser?</h2>
<p>The conversion happens on your device with no server round-trip, so sensitive data stays local, there is no upload size limit, and the download starts as soon as the file is parsed.</p>
<blockquote>Need JSON instead? Use the <a href="/parquet-to-json/">Parquet to JSON</a> tool, or the general <a href="/parquet-file-converter/">Parquet file converter</a>.</blockquote>
</div>
""" + related_block([
    ("/parquet-to-csv/", "Parquet to CSV", "Main CSV tool"),
    ("/parquet-file-converter/", "File converter", "More formats"),
    ("/parquet-to-excel/", "Parquet to Excel", "For spreadsheets"),
])
PAGES["convert-parquet-to-csv/index.html"] = page(
    "Convert Parquet to CSV Online — Free, Private, All Rows",
    "Convert Parquet to CSV online for free. All rows are exported with clean dates and a UTF-8 BOM; files are parsed in your browser and never uploaded.",
    "/convert-parquet-to-csv/", onlinecsv_body, "/parquet-to-csv/",
    extra_head=ld_json("WebApplication","Convert Parquet to CSV Online","Export Parquet to CSV in the browser, all rows","/convert-parquet-to-csv/")
    + breadcrumb_ld([("Home","/"),("Convert Parquet to CSV","/convert-parquet-to-csv/")])
)

# ---------------- Write all ----------------
for rel, content in PAGES.items():
    write_file(rel, content)

# Copy shared assets
for name in ["site.css", "tool.js", "sample.parquet", "og.png"]:
    src = os.path.join(ROOT, "assets", name)
    dst = os.path.join(SITE, "assets", name)
    with open(src, "rb") as a, open(dst, "wb") as b:
        b.write(a.read())

# robots.txt
write_file("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

# sitemap.xml
urls = ""
for rel in PAGES:
    p = "/" if rel == "index.html" else "/" + rel.replace("index.html", "")
    urls += f"  <url><loc>{SITE_URL}{p}</loc><changefreq>weekly</changefreq></url>\n"
write_file("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")

print("Built", len(PAGES), "pages into", SITE)
