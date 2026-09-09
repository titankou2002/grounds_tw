#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 開店作戰中心 page from 開店作戰中心.md.
   Output: docs/grounds_taiwan_開店作戰中心.html (self-contained).
   Reuses the dark visual language of the other command-center pages."""
import os
import re
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "開店作戰中心.md")
OUT = os.path.join(ROOT, "docs", "grounds_taiwan_開店作戰中心.html")

def esc(s):
    return html.escape(s, quote=False)

def bullets_to_html(lines):
    out = ["<ul>"]
    for ln in lines:
        t = ln.strip()
        if t.startswith("- "):
            out.append("<li>" + inline(t[2:]) + "</li>")
        elif t.startswith("1. "):
            out.append("<li class=\"ord\">" + inline(t[3:]) + "</li>")
        elif t.startswith(("2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "9. ", "10. ")):
            out.append("<li class=\"ord\">" + inline(t[3:]) + "</li>")
        elif t.startswith("["):
            out.append("<li class=\"task\">" + inline(t) + "</li>")
    out.append("</ul>")
    return "\n".join(out)

def inline(t):
    segs = t.split("**")
    out = []
    for i, s in enumerate(segs):
        if i % 2 == 1:
            s = "<b>" + s + "</b>"
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a class="doclink" href="\2">\1</a>', s)
        out.append(s)
    return "".join(out)

def render_table(rows):
    """rows: list of list of cell strings (first row header)."""
    h = ["<table>"]
    for i, r in enumerate(rows):
        tag = "th" if i == 0 else "td"
        cls = ' class="total"' if (i > 0 and r[0].replace("*", "").strip().startswith("初期總投資")) else ""
        cells = "".join(f"<{tag}{cls}>{inline(c)}</{tag}>" for c in r)
        h.append("<tr>" + cells + "</tr>")
    h.append("</table>")
    return "\n".join(h)

def parse_table(lines):
    rows = []
    for ln in lines:
        t = ln.strip()
        if t.startswith("|") and t.endswith("|"):
            if re.match(r"^\|[\s:|-]+\|$", t):
                continue
            cells = [c.strip() for c in t.strip("|").split("|")]
            rows.append(cells)
    return rows

def section_id(key):
    return {"①": "dashboard", "②": "decide", "③": "countdown",
            "④": "funding", "⑤": "mustknow", "⑥": "manual"}[key[0]]

def nav_label(key, title):
    return {"①": "① 儀表板", "②": "② 誰決定什麼", "③": "③ 開店倒數",
            "④": "④ 資金需求", "⑤": "⑤ 負責人必修", "⑥": "⑥ 作戰手冊"}[key[0]]

def main():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    sections = []
    cur = None
    for ln in lines:
        if ln.startswith("## "):
            m = re.match(r"## (.)\s+(.*)", ln)
            if cur: sections.append(cur)
            cur = {"key": m.group(1), "title": m.group(2).strip(),
                   "lines": [], "body": []}
        elif cur is not None:
            cur["lines"].append(ln)
    if cur: sections.append(cur)

    for s in sections:
        s["html"] = render_section(s)

    chaps = []
    # find chapters in section ⑥ for the sub-nav
    for s in sections:
        if s["key"] == "⑥":
            for ln in s["lines"]:
                if ln.startswith("### Ch"):
                    chaps.append((re.match(r"### (Ch\d+)\s+(.*)", ln).group(1),
                                  re.match(r"### (Ch\d+)\s+(.*)", ln).group(2)))
            break

    nav = []
    for s in sections:
        nav.append(f'<div class="ngroup"><a class="nitem" href="#{section_id(s["key"])}">{nav_label(s["key"], s["title"])}</a></div>')
    chap_nav = "\n".join(
        f'<a class="nlink" href="#{cid}">{cid} {esc(t)}</a>' for cid, t in chaps)

    body = "\n".join(s["html"] for s in sections)

    html_doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>開店作戰中心｜grounds Taiwan</title>
<meta name="description" content="grounds Taiwan 開店作戰中心：每天打開就知道現在到哪、今天幹嘛、誰卡住、等日本什麼。">
<link rel="icon" type="image/png" sizes="32x32" href="../assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#0e1116; --bg2:#151a22; --card:#1b222c; --card2:#202a36;
  --line:#2c3a4d; --txt:#e8eef6; --muted:#8fa0b5;
  --accent:#7fb3ff; --accent2:#ffd075;
  --do:#ffd075; --watch:#ff8f8f; --note:#7fe3c8;
  --ok1:#78d17f; --ok2:#ff9f5c; --ok3:#5cc8ff; --okr:#ff5c5c;
  --radius:14px;
}}
*{{box-sizing:border-box; margin:0; padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg); color:var(--txt); font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif; line-height:1.75; font-size:15px}}
::selection{{background:var(--accent); color:#000}}
a{{color:var(--accent); text-decoration:none}}
.app{{display:flex; min-height:100vh}}
nav.side{{
  width:280px; flex-shrink:0; background:var(--bg2); border-right:1px solid var(--line);
  position:sticky; top:0; height:100vh; overflow-y:auto; padding:22px 16px; z-index:20;
}}
nav.side .brand{{font-weight:800; font-size:17px; margin-bottom:2px}}
nav.side .brand span{{color:var(--accent2)}}
nav.side .sub{{color:var(--muted); font-size:12px; margin-bottom:16px; line-height:1.5}}
.ngroup{{margin-bottom:4px}}
.nitem{{display:block; padding:8px 12px; border-radius:9px; font-weight:700; font-size:13.5px; color:var(--txt); cursor:pointer; border:1px solid transparent}}
.nitem:hover{{background:var(--card); border-color:var(--line)}}
.nchap{{margin:2px 0 10px 12px; border-left:1px solid var(--line); padding-left:8px; display:flex; flex-direction:column; gap:3px}}
.nlink{{color:var(--muted); font-size:11.5px; padding:2px 6px; border-radius:5px}}
.nlink:hover{{color:var(--txt); background:var(--card)}}
main{{flex:1; min-width:0; padding:34px 40px 100px; max-width:1080px; margin:0 auto}}
.h1{{font-size:28px; font-weight:800; margin-bottom:6px}}
.tagline{{color:var(--muted); margin-bottom:4px}}
.doc-back{{display:inline-block; margin-top:14px; font-size:13px; color:var(--muted); border:1px solid var(--line); padding:5px 12px; border-radius:20px}}
.lede{{background:var(--card2); border-left:4px solid var(--accent2); border-radius:10px; padding:14px 18px; margin:20px 0 26px; font-size:15px; color:var(--txt)}}
.lede b{{color:var(--accent2)}}

.section{{margin-top:8px; padding-top:16px; border-top:1px solid var(--line); scroll-margin-top:12px}}
.section-head{{display:flex; align-items:center; gap:12px; border-bottom:2px solid var(--line); padding-bottom:10px; margin-bottom:14px; flex-wrap:wrap}}
.section-head .num{{font-size:12px; font-weight:800; letter-spacing:1px; padding:4px 10px; border-radius:7px; color:#0e1116; background:var(--accent2)}}
.section-head h2{{font-size:22px}}
blockquote{{margin:14px 0; padding:12px 16px; background:var(--card2); border-left:3px solid var(--muted); border-radius:8px; color:var(--muted); font-size:13.5px}}
blockquote p{{margin:4px 0}}
h3{{font-size:17px; margin:26px 0 10px}}
h4{{font-size:14.5px; margin:16px 0 6px; color:var(--accent2)}}
.phase-card{{background:linear-gradient(135deg,var(--card2),var(--card)); border:1px solid var(--line); border-radius:var(--radius); padding:16px 20px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin-bottom:14px}}
.phase-card .p-label{{font-size:12px; color:var(--muted); letter-spacing:1px; font-weight:800}}
.phase-card .p-name{{font-size:20px; font-weight:800; color:var(--accent2)}}
.phase-card .p-note{{font-size:13px; color:var(--muted)}}

table{{width:100%; border-collapse:collapse; font-size:13.5px; margin:14px 0 18px}}
th,td{{padding:9px 12px; border:1px solid var(--line); text-align:left; vertical-align:top}}
th{{background:var(--card2); font-weight:700; white-space:nowrap}}
td.total{{background:rgba(255,208,117,.12); font-weight:800}}
.top10{{display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:12px 0 8px}}
@media(max-width:860px){{.top10{{grid-template-columns:1fr}}}}
.top{{background:var(--card); border:1px solid var(--line); border-radius:11px; padding:11px 14px}}
.top .n{{font-size:11px; font-weight:800; color:var(--accent2)}}
.top .t{{font-weight:600; display:block}}
.top .d{{font-size:13px; color:var(--muted)}}

.pill{{display:inline-flex; align-items:center; gap:6px}}
.pill.ok{{color:var(--ok1)}} .pill.warn{{color:var(--ok2)}} .pill.pending{{color:var(--ok3)}} .pill.risk{{color:var(--okr)}}

.decide-grid{{display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin:14px 0}}
@media(max-width:900px){{.decide-grid{{grid-template-columns:1fr}}}}
.decide{{background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px}}
.decide.jp{{border-top:3px solid var(--accent)}}
.decide.tw{{border-top:3px solid var(--ok1)}}
.decide.both{{border-top:3px solid var(--accent2)}}
.decide h4{{margin:0 0 10px; color:var(--txt); font-size:15px}}
.decide ul{{list-style:none}}
.decide li{{padding-left:1px; margin-bottom:7px; font-size:13.5px; color:var(--muted)}}
.decide.tw li{{color:var(--txt)}}
.decide.both li{{color:var(--txt); font-weight:600}}
.decide .who{{font-size:10.5px; letter-spacing:1px; font-weight:800; color:var(--muted); padding:3px 9px; border:1px solid var(--line); border-radius:20px; display:inline-block; margin-bottom:10px}}

.timeline{{position:relative; margin:10px 0 14px; padding-left:0}}
.window{{background:var(--card); border:1px solid var(--line); border-left:4px solid var(--accent); border-radius:12px; padding:14px 18px; margin-bottom:14px}}
.window .w-range{{font-size:11px; font-weight:800; letter-spacing:1px; color:var(--accent)}}
.window h4{{margin:2px 0 8px; font-size:16px; color:var(--txt)}}
.window ul{{list-style:none}}
.window li{{padding-left:16px; position:relative; margin-bottom:5px; font-size:13.5px; color:var(--muted)}}
.window li:before{{content:"▸"; position:absolute; left:0; color:var(--muted)}}

.two{{display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:14px 0}}
@media(max-width:860px){{.two{{grid-template-columns:1fr}}}}
.mk{{background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px}}
.mk h4{{margin:0 0 10px; font-size:15.5px}}
.mk .row{{margin-bottom:10px}}
.mk .k{{font-size:11px; font-weight:800; letter-spacing:.5px; color:var(--muted); display:block; margin-bottom:2px}}
.mk .v{{font-size:13.5px}}

.task-card{{background:var(--card2); border:1px solid var(--line); border-radius:12px; padding:16px 18px; margin:12px 0; border-left:4px solid var(--ok1)}}
.task-card .tt{{font-weight:800; font-size:15.5px; margin-bottom:10px}}
.task-card .tt .tag{{font-size:11px; color:var(--ok1); letter-spacing:1px; font-weight:800; border:1px solid var(--line); padding:2px 8px; border-radius:20px; margin-right:8px}}
.task-card ul{{list-style:none}}
.task-card .cl{{font-size:12.5px; color:var(--muted); font-weight:800; letter-spacing:.5px; margin:8px 0 4px}}
.task-card li.chk{{padding-left:24px; position:relative; margin-bottom:4px; font-size:13.5px}}
.task-card li.chk:before{{content:"☐"; position:absolute; left:0; color:var(--muted)}}
.meta{{display:flex; gap:8px; flex-wrap:wrap; margin-top:10px}}
.meta .m{{font-size:12px; padding:3px 10px; border-radius:20px; border:1px solid var(--line); color:var(--muted)}}
.meta .m.jp{{color:var(--ok2); border-color:var(--ok2)}}

.blk{{margin-top:12px; background:var(--card2); border-radius:11px; padding:12px 15px; border-left:3px solid var(--muted)}}
.blk .lbl{{font-size:11px; letter-spacing:1px; font-weight:800; margin-bottom:6px}}
.blk.watch{{border-left-color:var(--watch)}} .blk.watch .lbl{{color:var(--watch)}}
.blk.note{{border-left-color:var(--note)}} .blk.note .lbl{{color:var(--note)}}
.blk ul{{list-style:none}}
.blk li{{padding-left:16px; position:relative; margin-bottom:5px; font-size:13.5px}}
.blk li:before{{content:"▸"; position:absolute; left:0}}

.manual-block{{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:18px 20px; margin-bottom:20px; scroll-margin-top:14px}}
.manual-block .ch-top{{display:flex; align-items:baseline; gap:12px; margin-bottom:6px; flex-wrap:wrap}}
.manual-block .cid{{font-size:12px; font-weight:800; color:var(--accent2); letter-spacing:1px}}
.manual-block h3{{font-size:19px; margin:0}}
.manual-block .why{{font-size:14px; color:var(--txt); margin:2px 0 8px}}
.manual-block .who{{font-size:13px; color:var(--muted); margin-bottom:4px}}
@media(max-width:700px){{nav.side{{display:none}}}}
</style>
</head>
<body>
<div class="app">

<nav class="side">
  <div class="brand">開店<span>作戰中心</span></div>
  <div class="sub">grounds Taiwan · 你每天打開的頁面<br>現在到哪 · 今天幹嘛 · 卡在哪 · 等日本什麼</div>
  {nav}
  <div class="nchap">{chap_nav}</div>
  <a class="doc-back" href="index.html">← 回文件庫</a>
</nav>

<main>
<div class="h1">開店作戰中心</div>
<div class="tagline">日本 100% 投資台灣，開一家公司＋第一家直營店。你是台灣端負責人。</div>
{body}
</main>

</div>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print("wrote", OUT)

def render_section(s):
    key = s["key"]
    if key == "①": return s_dashboard(s)
    if key == "②": return s_decide(s)
    if key == "③": return s_countdown(s)
    if key == "④": return s_funding(s)
    if key == "⑤": return s_mustknow(s)
    if key == "⑥": return s_manual(s)
    return ""

def s_dashboard(s):
    lines = s["lines"]
    phase = None
    lede = []
    q_rows = []
    top = []
    now = []
    rest = []
    mode = None
    for ln in lines:
        t = ln.strip()
        if t.startswith("**目前階段："):
            phase = t
        elif t.startswith("### "):
            mode = t[4:]
        elif t.startswith("> "):
            lede.append(t[2:])
        elif mode == "5 個關鍵問題" and t.startswith("|"):
            if re.match(r"^\|[\s:|-]+\|$", t): continue
            q_rows.append([c.strip() for c in t.strip("|").split("|")])
        elif mode == "現在最重要的 10 件事" and t:
            top.append(t)
        elif mode == "本週就能做的" and t:
            now.append(t)
    lead = lede[0] if lede else ""
    phase_html = ""
    if phase:
        pm = re.match(r"\*\*目前階段：(.*?)\*\*（(.*?)）(.*)", phase)
        if pm:
            phase_html = (f'<div class="phase-card"><div><div class="p-label">目前階段</div>'
                          f'<div class="p-name">Phase 1 · {esc(pm.group(1))}</div>'
                          f'<div class="p-note">{esc(pm.group(2))}</div></div></div>')
    top_html = ""
    if top:
        items = []
        for t in top:
            m = re.match(r"(\d+)\.\s+\*\*(.*?)\*\*\s*—\s*(.*)", t)
            if m:
                items.append(f'<div class="top"><span class="n">{esc(m.group(1))}</span>'
                             f'<span class="t">{esc(m.group(2))}</span>'
                             f'<span class="d">{esc(m.group(3))}</span></div>')
        top_html = '<div class="top10">' + "\n".join(items) + "</div>"
    now_html = "<ul>" + "".join(f"<li>{inline(t[2:])}</li>" for t in now) + "</ul>"
    return f"""
<section class="section" id="dashboard">
  <div class="section-head"><span class="num">①</span><h2>儀表板：每天打開先看這頁</h2></div>
  {phase_html}
  <div class="lede">{inline(lead)}</div>
  <h3>5 個關鍵問題</h3>
  {render_table(q_rows)}
  <h3>現在最重要的 10 件事</h3>
  {top_html}
  <h3>本週就能做的（台灣端，不等日本）</h3>
  {now_html}
</section>"""

def s_decide(s):
    blk = None
    cols = {"日本總公司決定": ["jp", []], "台灣負責人決定": ["tw", []], "必須兩邊一起決定": ["both", []]}
    lede = []
    for ln in s["lines"]:
        t = ln.strip()
        if t.startswith("### "):
            name = t[4:]
            if name in cols:
                blk = name
        elif t.startswith("> "):
            lede.append(t[2:])
        elif blk and t.startswith("- "):
            cols[blk][1].append(t[2:])
    cards = []
    for name, (kind, items) in cols.items():
        lis = "".join(f"<li>{inline(i)}</li>" for i in items)
        label = {"jp": "日本總公司拍板", "tw": "台灣負責人拍板", "both": "兩邊一起拍板"}[kind]
        cards.append(f'<div class="decide {kind}"><h4>{esc(name)}</h4><span class="who">{label}</span><ul>{lis}</ul></div>')
    led = "".join(f"<p>{inline(p)}</p>" for p in lede)
    cards_join = "\n".join(cards)
    return f"""
<section class="section" id="decide">
  <div class="section-head"><span class="num">②</span><h2>誰決定什麼</h2></div>
  <blockquote>{led}</blockquote>
  <div class="decide-grid">{cards_join}</div>
</section>"""

def s_countdown(s):
    windows = []
    cur = None
    lede = []
    for ln in s["lines"]:
        t = ln.strip()
        if t.startswith("### "):
            m = re.match(r"### (T-[\d]+ ~ T-[\d]+)｜(.*)", t)
            if m:
                cur = {"range": m.group(1), "title": m.group(2), "items": []}
                windows.append(cur)
        elif t.startswith("> "):
            lede.append(t[2:])
        elif cur and t.startswith("- "):
            cur["items"].append(inline(t[2:]))
    wins = []
    for w in windows:
        lis = "".join(f"<li>{i}</li>" for i in w["items"])
        wins.append(f'<div class="window"><div class="w-range">{esc(w["range"])}</div>'
                    f'<h4>{esc(w["title"])}</h4><ul>{lis}</ul></div>')
    led = "".join(f"<p>{inline(p)}</p>" for p in lede)
    wins_join = "\n".join(wins)
    return f"""
<section class="section" id="countdown">
  <div class="section-head"><span class="num">③</span><h2>開店倒數 T-180 → T-0</h2></div>
  <blockquote>{led}</blockquote>
  <div class="timeline">{wins_join}</div>
</section>"""

def s_funding(s):
    rows = []
    lede = []
    concl = []
    mode = None
    for ln in s["lines"]:
        t = ln.strip()
        if t.startswith("### "):
            mode = t[4:]
        elif t.startswith("> "):
            if mode == "結論": concl.append(t[2:])
            else: lede.append(t[2:])
        elif t.startswith("|") and re.match(r"^\|[\s:|-]+\|$", t):
            continue
        elif t.startswith("|"):
            rows.append([c.strip() for c in t.strip("|").split("|")])
    led = "".join(f"<p>{inline(p)}</p>" for p in lede) if lede else ""
    cc = "".join(f"<p>{inline(p)}</p>" for p in concl) if concl else ""
    return f"""
<section class="section" id="funding">
  <div class="section-head"><span class="num">④</span><h2>資金需求：日本到底要投多少錢</h2></div>
  <blockquote>{led}</blockquote>
  {render_table(rows)}
  {("<blockquote>" + cc + "</blockquote>") if cc else ""}
</section>"""

def s_mustknow(s):
    blocks = []
    cur = None
    lede = []
    for ln in s["lines"]:
        t = ln.strip()
        if t.startswith("### "):
            if cur: blocks.append(cur)
            cur = {"title": t[4:], "pairs": []}
        elif t.startswith("> "):
            lede.append(t[2:])
        elif cur and t.startswith("- **"):
            m = re.match(r"- \*\*(.*?)\*\*：(.*)", t)
            if m:
                cur["pairs"].append((m.group(1), m.group(2)))
    if cur: blocks.append(cur)
    cards = []
    for b in blocks:
        rows = ""
        order = {"為什麼": "why", "你要做": "do", "找誰": "who", "驗收": "ok"}
        for k, v in b["pairs"]:
            cls = order.get(k, "v")
            rows += f'<div class="row"><span class="k">{esc(k)}</span><span class="v">{inline(v)}</span></div>'
        cards.append(f'<div class="mk"><h4>{esc(b["title"])}</h4>{rows}</div>')
    led = "".join(f"<p>{inline(p)}</p>" for p in lede)
    cards_join = "\n".join(cards)
    return f"""
<section class="section" id="mustknow">
  <div class="section-head"><span class="num">⑤</span><h2>台灣負責人必修</h2></div>
  <blockquote>{led}</blockquote>
  <div class="two">{cards_join}</div>
</section>"""

def s_manual(s):
    out_extra = []
    chaps_html = []
    cur = None
    task = None
    paras = []
    for ln in s["lines"]:
        t = ln.strip()
        if t.startswith("### "):
            if cur:
                if task: cur["tasks"].append(task)
                chaps_html.append(render_chap(cur))
            m = re.match(r"### (Ch\d+)\s+(.*)", t)
            cur = {"id": m.group(1), "title": m.group(2), "why": "", "who": [],
                   "tasks": [], "note": []}
            task = None
        elif t.startswith("#### 任務："):
            if task: cur["tasks"].append(task)
            task = {"title": t[len("#### 任務："):], "checks": [], "need": None, "deadline": None}
        elif t.startswith("- **完成條件**：") and task is not None:
            continue
        elif t.startswith("- [ ] ") and task is not None:
            task["checks"].append(t[len("- [ ] "):])
        elif t.startswith("- 需要日本：") and task is not None:
            task["need"] = t[len("- 需要日本："):]
        elif t.startswith("- 截止：") and task is not None:
            task["deadline"] = t[len("- 截止："):]
        elif t.startswith("- **為什麼重要**："):
            cur["why"] = t[len("- **為什麼重要**："):]
        elif t.startswith("- **日本要決定**："):
            cur["who"].append(("日本要決定", t[len("- **日本要決定**："):]))
        elif t.startswith("- **台灣負責**："):
            cur["who"].append(("台灣負責", t[len("- **台灣負責**："):]))
        elif t.startswith("- **負責**："):
            cur["who"].append(("負責", t[len("- **負責**："):]))
        elif t.startswith("- **注意**："):
            cur["note"].append(t[9:])
        elif t.startswith("> "):
            paras.append(t[2:])
    if note_check := None: pass  # noqa
    if task: cur["tasks"].append(task)
    if cur: chaps_html.append(render_chap(cur))
    led = "".join(f"<p>{inline(p)}</p>" for p in paras)
    chaps_join = "\n".join(chaps_html)
    return f"""
<section class="section" id="manual">
  <div class="section-head"><span class="num">⑥</span><h2>作戰手冊：14 章詳細任務卡</h2></div>
  <blockquote>{led}</blockquote>
  {chaps_join}
</section>"""

def render_chap(cur):
    who = ""
    if cur["who"]:
        chips = "".join(f'<span class="m{" jp" if k=="日本要決定" else ""}">{esc(k)}：{esc(v)}</span>'
                        for k, v in cur["who"])
        who = f'<div class="meta">{chips}</div>'
    tasks = []
    for tk in cur["tasks"]:
        checks = ""
        if tk["checks"]:
            lis = "".join(f"<li class=\"chk\">{inline(c)}</li>" for c in tk["checks"])
            checks = f'<div class="cl">完成條件（勾完才算完成）</div><ul>{lis}</ul>'
        metas = []
        if tk["need"]:
            metas.append(f'<span class="m jp">需要日本：{esc(tk["need"])}</span>')
        if tk["deadline"]:
            metas.append(f'<span class="m">截止：{esc(tk["deadline"])}</span>')
        tasks.append(
            f'<div class="task-card"><div class="tt"><span class="tag">任務</span>{inline(tk["title"])}</div>'
            f'<ul>{checks}</ul>'
            f'<div class="meta">{"".join(metas)}</div></div>')
    note = ""
    if cur["note"]:
        lis = "".join(f"<li>{inline(n)}</li>" for n in cur["note"])
        note = f'<div class="blk watch"><div class="lbl">注意（不做會怎樣）</div><ul>{lis}</ul></div>'
    why = f'<div class="why">{inline(cur["why"])}</div>' if cur["why"] else ""
    return (f'<div class="manual-block" id="{cur["id"]}">'
            f'<div class="ch-top"><span class="cid">{esc(cur["id"])}</span><h3>{esc(cur["title"])}</h3></div>'
            f'{why}{who}{"".join(tasks)}{note}</div>')

if __name__ == "__main__":
    main()