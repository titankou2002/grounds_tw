#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert Chinese planning MD files into styled HTML docs pages
   that match the existing grounds Taiwan site design system."""
import os
import re
import hashlib
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
os.makedirs(OUT, exist_ok=True)

CSS_VERSION = "162f86dd72"
JS_VERSION = "e0a8d70253"

SHELL_HEAD = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<base href="/Grounds_TW/">
<title>__TITLE__｜grounds Taiwan 工作文件</title>
<meta name="description" content="__DESC__">
<link rel="icon" type="image/png" sizes="32x32" href="../assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="../assets/img/favicon.png">
<link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css?v=__CSSV__">
<style>
.docs-layout{max-width:900px;margin:0 auto;padding:56px 32px 120px}
.docs-nav{display:flex;gap:18px;font-size:13px;margin-bottom:40px;flex-wrap:wrap}
.docs-nav a{text-decoration:none;color:var(--muted)}
.docs-nav a:hover{color:var(--fg)}
.docs-body h1{font-family:var(--serif);font-weight:400;font-size:clamp(24px,3vw,32px);margin:0 0 8px}
.docs-body h2{font-size:18px;margin:40px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.docs-body h3{font-size:15px;margin:24px 0 8px}
.docs-body h4{font-size:14px;margin:18px 0 6px}
.docs-body p{font-size:14.5px;margin:0 0 12px}
.docs-body ul,.docs-body ol{margin:0 0 16px;padding-left:22px;font-size:14px}
.docs-body li{margin-bottom:5px}
.docs-body li p{display:inline}
.docs-body table{width:100%;border-collapse:collapse;font-size:13px;margin:16px 0}
.docs-body th,.docs-body td{padding:8px 10px;border:1px solid var(--line);text-align:left;vertical-align:top}
.docs-body th{background:var(--callout-bg);font-weight:600}
.docs-body blockquote{margin:16px 0;padding:14px 18px;background:var(--callout-bg);border-radius:4px;font-size:13.5px;color:var(--muted)}
.docs-body blockquote p{margin:0 0 6px;font-size:13.5px}
.docs-body hr{border:none;border-top:1px solid var(--line);margin:32px 0}
.docs-body code{background:var(--callout-bg);padding:1px 5px;border-radius:3px;font-size:12.5px}
.docs-tag{display:inline-block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border:1px solid var(--line);padding:3px 8px;border-radius:20px;margin:0 0 8px}
.task{list-style:none;padding-left:2px}
.task li{padding-left:22px;position:relative}
.task li::before{content:"☐";position:absolute;left:0;color:var(--muted)}
.task li.done::before{content:"☑";color:var(--accent)}
</style>
</head>
<body>
<header class="site-nav">
  <a class="wordmark" href="../zh/index.html" aria-label="grounds Taiwan"></a>
  <nav class="nav-links">
    <a href="../zh/index.html">首頁</a>
    <a href="../zh/blueprint.html">Blueprint</a>
    <a href="../zh/trademark.html">商標</a>
    <a href="../docs/index.html" class="active">文件</a>
  </nav>
  <div class="lang-switch"><a class="lang-link" href="../index.html">日本語</a><a class="lang-link" href="../en/index.html">English</a><a class="lang-link current" href="../zh/index.html">中文</a></div>
</header>
"""

SHELL_TAIL = """
<footer class="site-footer">
  <p>2026 <a href="../zh/blueprint.html" class="stealth-link">AUG</a></p>
</footer>
<script src="../assets/js/main.js?v=%s"></script>
</body>
</html>""" % JS_VERSION


def inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\s][^*]*?)\*", r"<em>\1</em>", text)
    text = text.replace("[x]", "☑").replace("[X]", "☑").replace("[ ]", "☐")
    return text


def render_table(lines):
    header = lines[0]
    cols = [c.strip() for c in header.strip("|").split("|")]
    body = []
    for ln in lines[2:]:
        if not ln.strip():
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        body.append("   <tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
    return ('<table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in cols) + '</tr></thead><tbody>\n' + "\n".join(body) + "\n</tbody></table>")


def md_to_html(mdtext):
    lines = mdtext.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    list_stack = []  # types: 'ul', 'ol', 'task'
    in_p = False
    in_blockquote = False
    buf = []

    def close_p():
        nonlocal in_p
        if in_p:
            out.append("".join(buf))
            buf.clear()
            in_p = False

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            out.append('<blockquote>' + "".join(buf) + '</blockquote>')
            buf.clear()
            in_blockquote = False

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        # table
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            close_p(); flush_blockquote()
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(render_table(tbl))
            continue

        # hr
        if stripped == "---":
            close_p(); flush_blockquote()
            out.append("<hr>")
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            close_p(); flush_blockquote()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            close_p()
            if not in_blockquote:
                in_blockquote = True
            buf.append("<p>" + inline(stripped.lstrip(">").strip()) + "</p>")
            i += 1
            continue
        if in_blockquote:
            flush_blockquote()

        # lists
        m = re.match(r"^\s{0,4}[-*]\s+(.*)$", ln)
        if m and not stripped.startswith(("- ", "-[")):
            pass
        if re.match(r"^\s*[-]\s+\[ \]", ln) or re.match(r"^\s*[-]\s+\[x\]", ln) or re.match(r"^\s*[-]\s+\[X\]", ln):
            close_p(); flush_blockquote()
            is_done = bool(re.match(r"^\s*[-]\s+\[[xX]\]", ln))
            content = re.sub(r"^\s*[-]\s+\[[ xX]\]\s*", "", ln)
            if not list_stack or list_stack[-1] != "task":
                if list_stack:
                    out.append("</ul>")
                list_stack = ["task"]
                out.append('<ul class="task">')
            out.append(f'<li class="{"done" if is_done else ""}">{inline(content)}</li>')
            i += 1
            continue
        if re.match(r"^[-*]\s+", ln) or re.match(r"^\s+[-*]\s+", ln):
            close_p(); flush_blockquote()
            indent = len(ln) - len(ln.lstrip())
            content = re.sub(r"^[-*]\s+", "", ln.lstrip())
            if not list_stack or list_stack[-1] != "ul":
                if list_stack and list_stack[-1] == "ol":
                    out.append("</ol>")
                list_stack = ["ul"]
                out.append("<ul>")
            elif indent > 0:
                out.append("<ul>")
                list_stack.append("ul")
            out.append(f"<li>{inline(content)}</li>")
            i += 1
            continue
        if re.match(r"^\s*\d+[.)]\s+", ln):
            close_p(); flush_blockquote()
            content = re.sub(r"^\s*\d+[.)]\s+", "", ln)
            if not list_stack or list_stack[-1] != "ol":
                if list_stack:
                    out.append("</ul>")
                list_stack = ["ol"]
                out.append("<ol>")
            out.append(f"<li>{inline(content)}</li>")
            i += 1
            continue
        # end of list
        if list_stack and not stripped and i + 1 < len(lines) and lines[i + 1].strip():
            out.append("</ul>" if list_stack[-1] == "ul" else "</ol>" if list_stack[-1] == "ol" else "</ul>")
            list_stack = []

        # blank
        if not stripped:
            close_p(); flush_blockquote()
            i += 1
            continue

        # paragraph
        if not in_p:
            in_p = True
            buf.append("<p>")
        buf.append(inline(stripped) + " ")
        i += 1

    close_p(); flush_blockquote()
    if list_stack:
        out.append("</ul>" if list_stack[-1] != "ol" else "</ol>")
    return "\n".join(out)


DOCS = [
    ("過程框架_決策總表.md", "過程框架 — 決策總表", "grounds Taiwan 全過程決策框架 6 階段 30 模組"),
    ("grounds_taiwan_行動方案.md", "台灣執行行動方案", "grounds Taiwan Launch Blueprint 實務執行清單"),
    ("週五會議_提問清單.md", "與日本總部會議提問清單", "週五會議與日本總部對齊的決策點與台灣市場情報"),
    ("門市地點分析_中山北路二段36巷.md", "門市地點分析（中山北路二段36巷）", "土屋鞄台北店店面分析"),
    ("商標事務所洽談_QA.md", "商標事務所洽談 QA", "與宏景智權洽談的問題清單"),
    ("商標事務所報價_宏景.md", "商標報價整理（宏景）", "宏景智權三類報價 NT$30,000 基礎"),
    ("商標申請回覆Sharon.md", "商標申請回覆（Sharon）", "回覆宏景劉上禎的申請人資料"),
    ("給宏景的初期資料.md", "給宏景的初期資料", "品牌與日本註冊現況摘要"),
]

LINKS = []
for fname, title, desc in DOCS:
    slug = os.path.splitext(fname)[0]
    with open(os.path.join(ROOT, fname), "r", encoding="utf-8") as f:
        mdtext = f.read()
    body = md_to_html(mdtext)
    page = SHELL_HEAD.replace("__TITLE__", html.escape(title)).replace("__DESC__", html.escape(desc)).replace("__CSSV__", CSS_VERSION)
    page += '<div class="docs-layout">'
    page += '<nav class="docs-nav">'
    page += f'<a href="index.html">← 全部文件</a>'
    for f2, t2, _ in DOCS:
        page += f'<a href="{os.path.splitext(f2)[0]}.html">{t2}</a>'
    page += '</nav>'
    page += '<div class="docs-body">' + body + '</div>'
    page += '</div>' + SHELL_TAIL
    with open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    LINKS.append((slug, title, desc))
    print("wrote", slug + ".html")

# Hub page
hub = SHELL_HEAD.replace("__TITLE__", "工作文件").replace("__DESC__", "grounds Taiwan 工作文件庫").replace("__CSSV__", CSS_VERSION)
cards = []
for slug, title, desc in LINKS:
    cards.append(f'''      <a class="doc-card reveal" href="{slug}.html">
        <p class="doc-card-title">{title}</p>
        <p class="doc-card-desc">{desc}</p>
      </a>''')
hub += '''<div class="docs-layout">
<div class="docs-body">
  <h1>工作文件｜Docs</h1>
  <p>grounds Taiwan 團隊的工作文件庫：決策框架、行動方案、會議提問、地點分析、商標洽談與報價。內容與外部網站設計一致，僅供專案內部協作參考。</p>
  <style>
    .doc-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:28px}
    @media(max-width:860px){.doc-grid{grid-template-columns:1fr}}
    .doc-card{border:1px solid var(--line);border-radius:8px;padding:20px 22px;text-decoration:none;transition:border-color .2s,transform .2s;display:block}
    .doc-card:hover{border-color:var(--accent);transform:translateY(-2px)}
    .doc-card-title{font-size:15px;font-weight:600;margin:0 0 6px}
    .doc-card-desc{font-size:13px;color:var(--muted);margin:0}
  </style>
  <div class="doc-grid">
''' + "\n".join(cards) + '''
  </div>
</div>
</div>
''' + SHELL_TAIL
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(hub)
print("wrote index.html")