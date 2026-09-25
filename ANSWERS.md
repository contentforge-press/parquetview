# ParquetView — Stack Overflow 备用英文回答

每个回答先真正解决问题，末尾自然、克制地带一次工具，并按 SO 自我推广规则注明这是我做的工具。
等主人回去用自己的 SO 账号逐条粘贴。**不要短时间连续发多条**，每天 1–2 条，先给账号一些正常提问/点赞活动。

---

## 回答 1 — Q61113328「Convert parquet to csv file」(0 answers, 1.2k views)

链接: https://stackoverflow.com/questions/61113328/convert-parquet-to-csv-file
报错: `ArrowIOError: Invalid parquet file. Corrupt footer`

```
That error is raised before any conversion happens — pyarrow cannot read the file's
footer, so the problem is the file itself, not your to_csv() line.

A Parquet file stores its metadata (schema, row groups) in a footer at the very end
of the file. "Corrupt footer" almost always means one of:

1. The download/copy was interrupted and the file is truncated. This is the most
   common cause — the footer is the last bytes written, so a partial file is missing
   it. Check the file size against the size reported by the source (S3, SFTP, etc.).
2. It is not actually a Parquet file. Sometimes an export that failed produces an
   HTML/JSON error page or a CSV that was simply saved with a .parquet name.
3. The file got corrupted in transfer.

Quick checks:

    # real Parquet files start with the magic bytes "PAR1"
    head -c 4 filename.parquet        # should print: PAR1

    python - <<'PY'
    import pyarrow.parquet as pq
    print(pq.read_metadata('filename.parquet'))   # reads only the footer
    PY

If head -c 4 does not show PAR1, or read_metadata fails, the file is not a valid
Parquet and pandas cannot convert it — you need to re-export/re-download it from the
source. A truncated file generally cannot be recovered because the schema lives in
that missing footer.

If the file is valid, your original two lines are correct (optionally pin the engine):

    df = pd.read_parquet('filename.parquet', engine='pyarrow')
    df.to_csv('filename.csv', index=False)

If you only need to look at or export the file occasionally and don't want to set up
Python/pyarrow, you can open it in the browser at https://ggyg5gxksw.page.coze.site —
it parses the file locally and can export to CSV without uploading anything (disclosure:
it's a tool I built). But first run the checks above, since a corrupt file won't open
anywhere.
```

---

## 回答 2 — Q63083888「Converting Parquet to csv and vice versa without schema issues by using Pyspark」(0 answers)

链接: https://stackoverflow.com/questions/63083888/converting-parquet-to-csv-and-vice-versa-without-schema-issues-by-using-pyspark
问题: parquet→csv→改值→csv→parquet 后类型不兼容

```
The incompatibility is expected: CSV has no schema/type information. When you read it
back with spark.read.csv(header=True) without a schema, every column is read as
STRING. So an int/double/date/boolean column that was typed in the original Parquet
comes back as string, and writing that out gives you a Parquet with all-string columns
— which then breaks anything expecting the original types. Editing the CSV by hand can
also change formatting (e.g. "1", "1.0", dates, empty cells) in ways a plain read
cannot reconcile.

Best fix: don't round-trip through CSV at all. Read the Parquet, apply your changes
as Spark transformations (types are preserved), and write Parquet:

    df = spark.read.parquet("input.snappy.parquet")
    df2 = df.withColumn("field_a", ...)              # make your edits here
    df2.write.mode("overwrite").parquet("output.parquet")

If you genuinely must go through an edited CSV, give the reader the original schema
explicitly instead of relying on inference. Capture it first:

    schema = spark.read.parquet("input.snappy.parquet").schema

then read the edited CSV with that exact schema:

    sample = spark.read.csv("test.csv", header=True, schema=schema)
    sample.write.mode("overwrite").parquet("test.snappy.parquet")

That will fail loudly on a value that doesn't match the type (which is what you want),
rather than silently turning everything into strings.

Two related notes:
- df.write.csv("test.csv") writes a *directory* of part files (part-00000-...), not a
  single test.csv file. If you need one file, use df.coalesce(1).write.csv(...), then
  rename the part file inside.
- Make sure the edited values match the type formatting, especially dates/timestamps;
  you may need to pass the matching timestampFormat / dateFormat options.

For a quick, one-off view or small edit of a Parquet file without Spark, you can also
open it locally in the browser at https://ggyg5gxksw.page.coze.site and export to CSV,
with no upload (disclosure: I built it). For a repeatable pipeline though, keep the
edits inside Spark and keep the schema as shown above.
```

---

## 回答 3 — Q57662146「Add parquet-tools to path (Visual Studio Code)」
- 链接：https://stackoverflow.com/questions/57662146
- 5,830 浏览 / 0 回答 / 4 分。macOS 用户，想在 VS Code 看 .parquet，brew 装了 parquet-tools 但 GUI 应用拿不到 PATH。
- 策略：先给真正的 PATH 修复（macOS GUI 应用不读 .bash_profile/.zshrc），再给"根本不用装"的免安装替代。

```
The problem isn't your install — it's that apps launched from the macOS Dock/Finder
(GUI apps, including VS Code) do NOT read your shell startup files (.bash_profile,
.zshrc). So "parquet-tools on the PATH in Terminal" and "parquet-tools on the PATH
that a VS Code extension inherits" are two different things. The extension warning is
gone only because the check itself changed, not because VS Code can now find the binary.

First, find where Homebrew put it:

    which parquet-tools

That typically prints /opt/homebrew/bin/parquet-tools (Apple Silicon) or
/usr/local/bin/parquet-tools (Intel). Pick the fix that matches your setup:

Option A — point the extension at it directly (preferred).
Open the extension's settings and look for a "parquet-tools path" / executable setting,
then paste the full path from `which parquet-tools` (e.g. /opt/homebrew/bin/parquet-tools).
This avoids PATH entirely.

Option B — launch VS Code from the terminal, which then inherits your shell PATH:

    code .

If `code` isn't found, open the Command Palette in VS Code (Cmd+Shift+P) and run
"Shell Command: Install 'code' command in PATH" once, then use `code .`.

Option C — make GUI apps see Homebrew's PATH (macOS way):

    sudo launchctl config user path /opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin

then reboot. (Use /usr/local/bin instead of /opt/homebrew/bin on Intel Macs.)

One more gotcha: the Homebrew parquet-tools needs a Java runtime; if it opens and fails
silently, `brew install openjdk` (or follow the caveat printed by brew) usually fixes it.

If you just want to look at a .parquet file occasionally and don't want to maintain
Java + a CLI + a PATH at all, you can open it entirely in the browser with no install
and no upload at https://ggyg5gxksw.page.coze.site (disclosure: I built it); it also
exports to CSV/JSON. For repeated in-editor viewing, fixing the path in Option A is the
durable solution.
```

---

## 进度记录
- PR#49 awesome-parquet：**已合并（2026-09-25）**，维护者 severo 留言 "Very nice!"。
- PR#103 AwesomeCSV：open，等待中。
- 本文件 3 条回答待主人回电脑用本人 SO 账号逐条贴（每天≤1条）。

## 后续候选（持续观察）
- 持续捞**新近 + 0 回答 + 偏"打开/查看/转换/无安装"**的问题，关键词：
  "open parquet", "view parquet", "parquet viewer", "parquet to csv",
  "read parquet without python/spark", "parquet-tools path"
- 老问题（如 Scala/HDFS/AWS/Athena 深工程问题）不强答，相关度低。
