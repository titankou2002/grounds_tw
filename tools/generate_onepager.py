#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an A4-printable one-pager for decision-makers from 一頁版_給決策者.md."""
import os
import re
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "一頁版_給決策者.md")
OUT = os.path.join(ROOT, "docs", "一頁版.html")

CSS = """
:root{--ink:#1a2027;--mut:#5c6b7a;--red:#c0392b;--blue:#2d5d8f;--green:#1f7a4d}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif;color:var(--ink);font-size:12px;line-height:1.55;background:#fff}
.page{max-width:210mm;margin:0 auto;padding:9mm 11mm}
h1{font-size:19px;border-bottom:3px solid var(--ink);padding-bottom:6px}
.lede{margin:8px 0 12px;font-size:12.5px;color:var(--mut)}
h2{font-size:13.5px;margin:12px 0 5px;padding-left:8px;border-left:4px solid var(--blue)}
h3{font-size:12px;margin:6px 0 3px;color:var(--blue)}
table{width:100%;border-collapse:collapse;font-size:11.5px}
th,td{border:1px solid #cdd5dd;padding:4px 6px;text-align:left;vertical-align:top}
th{background:#f2f5f8}
ul,ol{margin:2px 0 4px 18px}
li{margin-bottom:1px}
ul.tasks li{list-style:none;position:relative;padding-left:20px}
ul.tasks li:before{content:"☐";position:absolute;left:0;color:var(--blue)}
.tag{display:inline-block;font-size:10px;font-weight:700;padding:1px 7px;border-radius:9px;margin-right:4px}
.t-yes{background:#e3f3ea;color:var(--green)}
.t-wait{background:#fdeeea;color:var(--red)}
.t-none{background:#eef1f4;color:var(--mut)}
.note{border-top:1px solid #cdd5dd;margin-top:10px;padding-top:5px;font-size:10.5px;color:var(--mut)}
@media print{
  body{font-size:11px}
  .page{padding:0}
  h2{margin-top:8px}
}
"""


def inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def render(lines):
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            head = [inline(c.strip()) for c in tbl[0].strip("|").split("|")]
            rows = []
            for r in tbl[2:]:
                if not r.strip():
                    continue
                rows.append("".join(f"<td>{inline(c.strip())}</td>" for c in r.strip("|").split("|")))
            out.append(f"<table><thead><tr>{''.join(f'<th>{h}</th>' for h in head)}</tr></thead><tbody>{''.join(f'<tr>{r}</tr>' for r in rows)}</tbody></table>")
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            i += 1
            continue
        if s.startswith(">"):
            out.append(f"<p class='lede'>{inline(s.lstrip('> ').strip())}</p>")
            i += 1
            continue
        if re.match(r"^[-*]\s+\[[ xX]\]", s):
            lis = []
            patx = re.compile(r"^[-*]\s+\[[ xX]\]\s*")
            while i < len(lines) and re.match(r"^[-*]\s+\[[ xX]\]", lines[i].strip()):
                lis.append("<li>" + inline(patx.sub("", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ul class='tasks'>" + "".join(lis) + "</ul>")
            continue
        if s.startswith("---"):
            i += 1
            continue
        if re.match(r"^[-*]\s+", s):
            lis = []
            pat = re.compile(r"^[-*]\s+")
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                lis.append("<li>" + inline(pat.sub("", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ul>" + "".join(lis) + "</ul>")
            continue
        if re.match(r"^\d+[.)]\s+", s):
            lis = []
            pat = re.compile(r"^\d+[.)]\s+")
            while i < len(lines) and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                lis.append("<li>" + inline(pat.sub("", lines[i].strip())) + "</li>")
                i += 1
            out.append("<ol>" + "".join(lis) + "</ol>")
            continue
        out.append(f"<p>{inline(s)}</p>")
        i += 1
    return "\n".join(out)


def main():
    md = open(SRC, encoding="utf-8").read()
    body_lines = md.split("\n")
    # drop H1 (page title is in <title>)
    body_lines = [ln for ln in body_lines if not ln.startswith("# grounds Taiwan｜一頁版")]
    page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>grounds Taiwan｜一頁版（給決策者）</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
  <h1>grounds Taiwan｜一頁版（給決策者）</h1>
  {render(body_lines)}
  <p class="note">print 用：瀏覽器 Ctrl/⌘+P 選 A4、邊距「無」直接列印。對應執行行動方案 v0.11。</p>
</div>
</body>
</html>"""
    open(OUT, "w", encoding="utf-8").write(page)
    print("wrote", OUT)


if __name__ == "__main__":
    main()