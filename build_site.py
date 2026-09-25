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
  <div><h4>Guides</h4><a href="/what-is-parquet/">What is a Parquet file?</a><br><a href="/how-to-open-parquet/">How to open Parquet</a><br><a href="/open-parquet-windows/">On Windows</a> &middot; <a href="/open-parquet-mac/">Mac</a> &middot; <a href="/open-parquet-excel/">Excel</a><br><a href="/parquet-vs-csv/">Parquet vs CSV</a></div>
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
