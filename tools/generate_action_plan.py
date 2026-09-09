#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an interactive, dark, color-coded reading page for 行動方案.md,
   reusing the visual language of 過程框架_互動學習.html.
   Output: docs/grounds_taiwan_行動方案.html (self-contained)."""
import os
import re
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "grounds_taiwan_行動方案.md")
OUT = os.path.join(ROOT, "docs", "grounds_taiwan_行動方案.html")

CSS = """
:root{
  --bg:#0e1116; --bg2:#151a22; --card:#1b222c; --card2:#202a36;
  --line:#2c3a4d; --txt:#e8eef6; --muted:#8fa0b5;
  --accent:#7fb3ff; --accent2:#ffd075;
  --do:#ffd075; --watch:#ff8f8f; --note:#7fe3c8;
  --phase0:#66b3ff; --phase1:#ff9f5c; --phase2:#78d17f; --phase3:#5cc8ff;
  --r0:#ff5c5c; --r1:#ff9f5c; --r2:#ffd075; --r3:#8fa0b5;
  --radius:14px;
}
*{box-sizing:border-box; margin:0; padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg); color:var(--txt); font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif; line-height:1.75; font-size:15.5px}
::selection{background:var(--accent); color:#000}

.app{display:flex; min-height:100vh}
nav.side{
  width:290px; flex-shrink:0; background:var(--bg2); border-right:1px solid var(--line);
  position:sticky; top:0; height:100vh; overflow-y:auto; padding:22px 18px; z-index:20;
}
nav.side .brand{font-weight:800; font-size:18px; margin-bottom:2px}
nav.side .brand span{color:var(--accent)}
nav.side .sub{color:var(--muted); font-size:12px; margin-bottom:14px}
.ngroup{margin-bottom:6px}
.nav-phase{display:flex; align-items:center; gap:8px; padding:7px 10px; border-radius:9px; cursor:pointer; font-weight:700; font-size:13px}
.nav-phase:hover{background:var(--card)}
.nav-phase .dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.nav-link{margin-left:18px; padding:4px 8px; border-left:1px solid var(--line); color:var(--muted); font-size:12.5px; cursor:pointer; border-radius:0 7px 7px 0; display:flex; gap:6px; align-items:center}
.nav-link:hover{color:var(--txt); background:var(--card)}
.nav-link .mp{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.nav-head{font-size:11px; letter-spacing:1px; color:var(--muted); font-weight:800; margin:14px 4px 6px}

main{flex:1; min-width:0; padding:30px 40px 90px; max-width:1020px; margin:0 auto}
.h1{font-size:30px; font-weight:800; margin-bottom:6px}
.tagline{color:var(--muted); margin-bottom:6px}
.vtag{font-size:12px; color:var(--muted); margin:0 0 18px}
.one-liner{background:var(--card2); border-left:4px solid var(--accent2); border-radius:10px; padding:14px 18px; margin:18px 0; font-size:15px; font-weight:600}

.flow{display:flex; flex-direction:column; margin:18px 0 30px}
.flow .node{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:12px 16px; cursor:pointer; font-weight:700; display:flex; align-items:center; gap:12px; transition:transform .15s}
.flow .node:hover{transform:translateX(4px)}
.flow .node .d{color:var(--muted); font-weight:400; font-size:13px}
.flow .bar{height:2px;width:100%;background:var(--line)}

.section{margin-top:30px; scroll-margin-top:16px}
.section-head{display:flex; align-items:center; gap:12px; border-bottom:2px solid var(--line); padding-bottom:10px; margin-bottom:4px; flex-wrap:wrap}
.section-head .ph{font-size:12px; font-weight:800; letter-spacing:1px; padding:4px 10px; border-radius:7px; color:#0e1116}
.section-head h2{font-size:22px}
.section-desc{color:var(--muted); margin-bottom:14px}

details.module{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); margin-bottom:14px; overflow:hidden}
details.module>summary{display:flex; align-items:center; gap:10px; padding:14px 18px; cursor:pointer; user-select:none; list-style:none}
details.module>summary::-webkit-details-marker{display:none}
details.module>summary .mnum{font-size:12px; color:var(--muted); font-weight:800}
details.module>summary h3{font-size:17px; flex:1}
details.module>summary .arrow{transition:transform .25s; color:var(--muted)}
details.module[open]>summary .arrow{transform:rotate(180deg)}
details.module .mod-body{padding:6px 18px 18px; border-top:1px solid var(--line)}

.blk{margin-top:12px; background:var(--card2); border-radius:11px; padding:13px 15px; border-left:3px solid var(--muted)}
.blk .lbl{font-size:11px; letter-spacing:1px; font-weight:800; margin-bottom:8px}
.blk.do{border-left-color:var(--do)} .blk.do .lbl{color:var(--do)}
.blk.watch{border-left-color:var(--watch)} .blk.watch .lbl{color:var(--watch)}
.blk.note{border-left-color:var(--note)} .blk.note .lbl{color:var(--note)}
.blk ul{list-style:none}
.blk li{list-style:none; padding-left:16px; position:relative; margin-bottom:6px; font-size:14px}
.blk li:before{content:"▸"; position:absolute; left:0}
.blk li.ck{padding-left:24px}
.blk li.ck:before{content:"☐"; color:var(--do)}
.blk li.ck.done:before{content:"☑"; color:var(--do)}
.blk.do li:before{color:var(--do)}
.blk.watch li:before{content:"!"; font-weight:900; color:var(--watch); font-size:12px}
.blk.note li:before{color:var(--note)}
.blk p{font-size:14px}
.act{margin-top:12px; background:var(--bg); border:1px solid var(--line); border-left:3px solid var(--do); border-radius:10px; padding:12px 15px}
.act .act-head{display:flex; align-items:flex-start; gap:8px; font-weight:700; font-size:14.5px}
.act .actchk{color:var(--do); flex-shrink:0}
.act.done .act-head b{color:var(--muted); text-decoration:line-through}
.act .kw{display:flex; gap:8px; margin-top:8px; font-size:13.5px; color:var(--muted); align-items:flex-start}
.act .kwl{color:var(--do); font-weight:800; flex-shrink:0}
.act ol.steps{margin:8px 0 0; list-style:none; counter-reset:st}
.act ol.steps li{list-style:none; counter-increment:st; padding-left:24px; position:relative; font-size:13.5px; margin-bottom:4px}
.act ol.steps li:before{content:counter(st); position:absolute; left:0; top:1px; width:16px; height:16px; border-radius:5px; background:rgba(255,208,117,.14); color:var(--do); font-size:10.5px; font-weight:800; display:flex; align-items:center; justify-content:center}
.chips{display:flex; gap:6px; flex-wrap:wrap; margin-right:4px}
.chip{font-size:11px; font-weight:800; padding:3px 10px; border-radius:20px; color:#0e1116; white-space:nowrap}
.chip.tw{background:#7fe3c8}
.chip.jp{background:#7fb3ff}
.chip.both{background:#d299ff}
.task{list-style:none}
.task li{list-style:none; padding-left:22px; position:relative; margin-bottom:6px; font-size:14px}
.task li:before{content:"☐"; position:absolute; left:0; color:var(--do)}
.task li.done:before{content:"☑"; color:var(--do)}

table{width:100%; border-collapse:collapse; margin:12px 0 6px; font-size:13px}
th,td{padding:8px 10px; border:1px solid var(--line); text-align:left; vertical-align:top}
th{background:var(--bg2); font-weight:700; color:var(--accent2)}
strong{color:#fff}
blockquote{background:var(--card2); border-left:3px solid var(--accent2); border-radius:8px; padding:11px 14px; margin:12px 0; font-size:13.5px; color:var(--muted)}
h4{margin:14px 0 6px; font-size:15px}
ol,ul{margin:8px 0}

footer{margin-top:40px; color:var(--muted); font-size:12.5px; border-top:1px solid var(--line); padding-top:18px}
.progress{position:fixed; top:0; left:0; height:3px; background:var(--accent); width:0; z-index:50}

.mobile-menu{display:none}
@media(max-width:860px){
  nav.side{position:fixed; left:-100%; transition:left .3s; width:320px}
  nav.side.show{left:0}
  main{padding:20px 18px 70px}
  .mobile-menu{display:flex; align-items:center; gap:10px; padding:14px 18px; position:sticky; top:0; background:var(--bg); z-index:15; border-bottom:1px solid var(--line)}
  .mobile-menu button{background:var(--card); border:1px solid var(--line); color:var(--txt); padding:6px 12px; border-radius:8px; cursor:pointer}
  table{font-size:12px}
  .app{display:block}
  main{padding-top:8px}
}
.menu-overlay{display:none; position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:18}
@media(max-width:860px){ .menu-overlay.show{display:block} }
"""


def inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\s][^*]*?)\*", r"<em>\1</em>", text)
    return text


def render_table(header, rows):
    head = "".join(f"<th>{inline(c.strip())}</th>" for c in header.strip("|").split("|"))
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(c.strip())}</td>" for c in r.strip("|").split("|")) + "</tr>"
        for r in rows if r.strip()
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_md(lines):
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            out.append(render_table(tbl[0], tbl[2:]))
            continue
        if re.match(r"^#{2,4}\s+", s):
            i += 1
            continue
        if s.startswith(">"):
            parts = [inline(x.strip().lstrip(">").strip()) for x in s.split(">") if x.strip()]
            out.append("<blockquote>" + "".join(f"<p>{p}</p>" for p in parts) + "</blockquote>")
            i += 1
            continue
        if re.match(r"^[-*]\s+\[[ xX]\]", s):
            out.append('<ul class="task">')
            while i < len(lines) and re.match(r"^[-*]\s+\[[ xX]\]", lines[i].strip()):
                done = bool(re.match(r"^[-*]\s+\[[xX]\]", lines[i].strip()))
                content = re.sub(r"^[-*]\s+\[[ xX]\]\s*", "", lines[i].strip())
                out.append(f'<li class="{"done" if done else ""}">{inline(content)}</li>')
                i += 1
            out.append("</ul>")
            continue
        if re.match(r"^[-*]\s+", s):
            out.append("<ul>")
            pat = re.compile(r"^[-*]\s+")
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                out.append(f"<li>{inline(pat.sub('', lines[i].strip()))}</li>")
                i += 1
            out.append("</ul>")
            continue
        if re.match(r"^\d+[.)]\s+", s):
            out.append("<ol>")
            pat = re.compile(r"^\d+[.)]\s+")
            while i < len(lines) and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                raw = lines[i].strip()
                norm = pat.sub("", raw)
                mck = re.match(r"^\[([ xX])\]\s*(.*)$", norm)
                if mck:
                    done = mck.group(1) in "xX"
                    out.append(f'<li class="ck{" done" if done else ""}">{inline(mck.group(2))}</li>')
                else:
                    out.append(f"<li>{inline(raw)}</li>")
                i += 1
            out.append("</ol>")
            continue
        out.append(f"<p>{inline(s)}</p>")
        i += 1
    return "\n".join(out)


def phase_of(num):
    return "p0" if num <= 4 else ("p1" if num <= 9 else "p2")


def render_chapter(title, lines):
    m = re.match(r"^Chapter\s*(\d+)", title)
    num = int(m.group(1))
    cnum = str(num).zfill(2)
    clean_title = re.sub(r"^Chapter\s*\d+\s*｜", "", title)
    phase = phase_of(num)
    pcolor = {"p0": "var(--phase0)", "p1": "var(--phase1)", "p2": "var(--phase2)"}[phase]

    body = render_md(lines)
    return cnum, clean_title, pcolor, phase, body


def split_blocks(lines):
    """Split md lines into (header_text_without_marker, [body_lines]).
    Markers like **先做什麼：** start a block, block ends at next marker."""
    blocks = []
    cur = None
    for ln in lines:
        m = re.match(r"^\*\*([^*]+)：\*\*(.*)$", ln)
        if m:
            if cur:
                blocks.append(cur)
            cur = [m.group(1).strip(), [m.group(2).strip()]] if m.group(2).strip() else [m.group(1).strip(), []]
            continue
        if cur is not None:
            cur[1].append(ln)
        else:
            pass  # lines before first marker dropped
    if cur:
        blocks.append(cur)
    return blocks


def block_kind(name):
    if "先做什麼" in name or "現在能做" in name:
        return "do"
    if "要注意" in name or "無法推進" in name or "待確認" in name:
        return "watch"
    if "主責" in name or "負責歸屬" in name:
        return "owner"
    return "other"


def owner_chips(text):
    """Parse 主責 line like '日本決策／台灣執行設立流程' into small chips."""
    parts = [p.strip() for p in re.split(r"[／/]", text) if p.strip()]
    out = []
    for p in parts:
        label = p
        cname = "both"
        if re.search(r"台灣", p) and not re.search(r"日本", p):
            cname = "tw"
        elif re.search(r"日本", p) and not re.search(r"台灣", p):
            cname = "jp"
        out.append((label, cname))
    return out


def block_items(body_lines):
    """Body as <li> items; inline text if not a list. Handles [ ]/[x] checkboxes."""
    items = [l.strip() for l in body_lines if l.strip() and l.strip() != "---"]
    if not items:
        return ""
    if any(re.match(r"^[-*]\s+", x) or is_check(x) for x in items):
        pat = re.compile(r"^[-*]\s+(\[[ xX]\]\s*)?")
        lis = ""
        for x in items:
            txt = pat.sub("", x)
            if is_check(x):
                done = bool(re.match(r"^[-*]\s+\[[xX]\]", x))
                lis += f'<li class="ck{" done" if done else ""}">{inline(txt)}</li>'
            else:
                lis += f"<li>{inline(txt)}</li>"
        return f"<ul>{lis}</ul>"
    return "".join(f"<p>{inline(x)}</p>" for x in items)


def is_check(x):
    return bool(re.match(r"^[-*]\s+\[[ xX]\]", x))


def render_do_actions(body_lines):
    """Render a 先做什麼 block into numbered action cards, each with 目的 + 辦法.
    Expected md shape:
      1. [ ] **動作標題**
          - 目的：...
          - 辦法：
            1. ...
            2. ...
    """
    acts = []
    cur = None
    in_steps = False
    for raw in body_lines:
        s = raw.strip()
        m_top = re.match(r"^(\d+)[.)]\s+(\[[ xX]\]\s*)?\*\*(.+?)\*\*\s*$", s)
        if m_top:
            if cur:
                acts.append(cur)
            ck = m_top.group(2) or ""
            done = bool(re.match(r"\[\s*[xX]", ck))
            cur = {"n": int(m_top.group(1)), "title": m_top.group(3).strip(), "done": done, "purpose": "", "steps": []}
            in_steps = False
            continue
        if cur is None:
            continue
        m_p = re.match(r"^[-*]\s*目的[:：]\s*(.*)$", s)
        if m_p:
            cur["purpose"] = m_p.group(1).strip()
            in_steps = False
            continue
        m_m = re.match(r"^[-*]\s*辦法[:：]\s*(.*)$", s)
        if m_m:
            tail = m_m.group(1).strip()
            if tail:
                cur["steps"].append(tail)
            in_steps = True
            continue
        if in_steps:
            m_s = re.match(r"^\s+\d+[.)]\s+(.*)$", raw)
            if m_s and m_s.group(1).strip():
                cur["steps"].append(m_s.group(1).strip())
                continue
            m_s2 = re.match(r"^\d+[.)]\s+(.*)$", s)
            if m_s2 and m_s2.group(1).strip():
                cur["steps"].append(m_s2.group(1).strip())
                continue
    if cur:
        acts.append(cur)

    out = []
    for a in acts:
        steps_html = ""
        if a["steps"]:
            lis = "".join(f"<li>{inline(x)}</li>" for x in a["steps"])
            steps_html = f'<ol class="steps">{lis}</ol>'
        purpose_html = ""
        if a["purpose"]:
            purpose_html = f'<div class="kw"><span class="kwl">目的</span><span>{inline(a["purpose"])}</span></div>'
        done = " done" if a["done"] else ""
        chk = "☑" if a["done"] else "☐"
        out.append(f'<div class="act{done}">'
                   f'<div class="act-head"><span class="actchk">{chk}</span><b>{inline(a["title"])}</b></div>'
                   f'{purpose_html}{steps_html}</div>')
    return "".join(out)


def build():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    sections = []  # (title, body_lines)
    cur_title = None
    cur = []
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            if cur_title:
                sections.append((cur_title, cur))
            cur_title = m.group(1).strip()
            cur = []
        else:
            if cur_title:
                cur.append(ln)
    if cur_title:
        sections.append((cur_title, cur))

    phase_meta = [
        ("p0", "Phase 0 對齊", "先跟日本把話說開、把基礎文件定案", "var(--phase0)"),
        ("p1", "Phase 1 籌備", "公司、供應鏈、系統、選址裝修、教育", "var(--phase1)"),
        ("p2", "Phase 2 開店", "招募、訓練、行銷、Launch、營運", "var(--phase2)"),
    ]

    chapters = {"p0": [], "p1": [], "p2": []}
    topics = []
    overview_html = ""
    quick_html = ""

    for title, body_lines in sections:
        if re.match(r"^Chapter\s\d+", title):
            cnum, clean_title, pcolor, phase, _ = render_chapter(title, body_lines)
            blocks = split_blocks(body_lines)
            blks = []
            chips = []
            for name, blines in blocks:
                kind = block_kind(name)
                raw = blines[0].strip() if blines else ""
                if kind == "do":
                    items = render_do_actions(blines)
                    blks.append(f'<div class="blk do"><div class="lbl">✔ 先做什麼</div>{items}</div>')
                elif kind == "watch":
                    items = block_items(blines)
                    is_none = re.match(r"^(暫?無)[，。、]?", raw) or raw in ("無", "暫無", "-")
                    if is_none:
                        passing = re.sub(r"^(暫?無)[，。、]?", "", raw).strip()
                        detail = f"；{inline(passing)}" if passing else "；先照先做什麼推進即可。"
                        blks.append(f'<div class="blk note"><div class="lbl">✔ 目前沒有特別要注意的</div><p>{detail}</p></div>')
                    else:
                        blks.append(f'<div class="blk watch"><div class="lbl">▶ 開店要注意的事</div>{items}</div>')
                elif kind == "owner":
                    chips = owner_chips(raw)
                else:
                    blks.append(render_md(blines))
            chip_html = ""
            if chips:
                ch = "".join(f'<span class="chip {c}">{inline(l)}</span>' for l, c in chips)
                chip_html = f'<span class="chips">{ch}</span>'
            card = f"""<details class="module" id="ch{cnum}">
  <summary><span class="mnum">CH {cnum}</span><h3>{inline(clean_title)}</h3>{chip_html}<span class="arrow">▼</span></summary>
  <div class="mod-body">{"".join(blks)}</div>
</details>"""
            chapters[phase].append((cnum, clean_title, pcolor, card))
        elif title.startswith("總覽"):
            overview_html = f"""<div class="section" id="overview">
  <div class="section-head"><span class="ph" style="background:var(--phase0)">OVERVIEW</span><h2>{inline(title)}</h2></div>
  <div class="section-desc">三個階段的大方向與依賴關係。</div>
  {render_md(body_lines)}
</div>"""
        elif title.startswith("立即行動"):
            quick_html = f"""<div class="section" id="quick">
  <div class="section-head"><span class="ph" style="background:var(--r0)">NOW</span><h2>{inline(title)}</h2></div>
  {render_md(body_lines)}
</div>"""
        else:
            slug = "topic-" + str(len(topics))
            topics.append((slug, title, render_md(body_lines)))

    flow_nodes = []
    phase_html = ""
    for pid, label, desc, color in phase_meta:
        if not chapters[pid]:
            continue
        cards = "".join(c for _, _, _, c in chapters[pid])
        phase_html += f"""<div class="section" id="ph-{pid}">
  <div class="section-head"><span class="ph" style="background:{color}">{label.upper()}</span><h2>{label}</h2></div>
  <div class="section-desc">{desc}</div>
  {cards}
</div>"""
        flow_nodes.append(
            f"""<div class="node" onclick="scrollToId('ph-{pid}')"><span class="dot" style="width:12px;height:12px;border-radius:50%;background:{color};flex-shrink:0"></span><span>{label}</span><span class="d">{desc}</span></div>"""
        )

    topic_html = ""
    if topics:
        tcards = "".join(
            f"""<details class="module" id="{slug}">
  <summary><span class="arrow" style="margin-right:2px">▼</span><h3>{inline(t)}</h3></summary>
  <div class="mod-body">{b}</div>
</details>""" for slug, t, b in topics
        )
        topic_html = f"""<div class="section" id="topics">
  <div class="section-head"><span class="ph" style="background:var(--phase3)">TOPICS</span><h2>專題調查與策略</h2></div>
  <div class="section-desc">商標佈局、子公司vs分公司、選品店、進口路線、電商、快閃、合規清單等。</div>
  {tcards}
</div>"""

    nav = []
    for pid, label, desc, color in phase_meta:
        if chapters[pid]:
            nav.append(f'<div class="ngroup"><div class="nav-phase" onclick="scrollToId(\'ph-{pid}\')"><span class="dot" style="background:{color}"></span>{label}</div>')
            for cnum, clean_title, pcolor, _ in chapters[pid]:
                nav.append(f'<div class="nav-link" onclick="scrollToId(\'ch{cnum}\')"><span class="mp" style="background:{color}"></span>Ch{cnum} {html.escape(clean_title)}</div>')
            nav.append("</div>")
    nav.append('<div class="nav-head">專題</div>')
    for slug, t, _ in topics:
        nav.append(f'<div class="nav-link" onclick="scrollToId(\'{slug}\')"><span class="mp" style="background:var(--phase3)"></span>{html.escape(t)}</div>')
    nav_html = "\n".join(nav)
    flow_html = '<div class="bar"></div>'.join(flow_nodes)

    page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>grounds Taiwan｜執行行動方案（互動版）</title>
<style>{CSS}</style>
</head>
<body>
<div class="progress" id="progress"></div>
<div class="menu-overlay" id="overlay" onclick="toggleMenu()"></div>
<div class="mobile-menu"><button onclick="toggleMenu()">☰ 導覽</button><b>執行行動方案</b></div>
<div class="app">
  <nav class="side" id="side">
    <div class="brand">grounds <span>Taiwan</span></div>
    <div class="sub">執行行動方案 · 互動閱讀版</div>
    {nav_html}
  </nav>
  <main>
    <div class="h1">執行行動方案</div>
    <div class="tagline">每一章：先做什麼（台灣可直接行動）、開店要注意的事（實務細節）、以及誰主責。</div>
    <div class="vtag">依據《grounds Taiwan Launch Blueprint》14 章整理 · 隨執行進度更新</div>
    <div class="one-liner">輕重緩急一句話：<b>商標最急（先申請主義）、公司最關鍵、快閃是眼前、消防沒過不能營業、定價要防代購。</b></div>
    <div class="flow">{flow_html}</div>
    {overview_html}
    {quick_html}
    {phase_html}
    {topic_html}
    <footer>這是內部執行與溝通文件，非對外檔案。</footer>
  </main>
</div>
<script>
function scrollToId(id){{ var el=document.getElementById(id); if(el) el.scrollIntoView({{behavior:"smooth"}}); closeMenu(); }}
function toggleMenu(){{ document.getElementById("side").classList.toggle("show"); document.getElementById("overlay").classList.toggle("show"); }}
function closeMenu(){{ document.getElementById("side").classList.remove("show"); document.getElementById("overlay").classList.remove("show"); }}
window.addEventListener("scroll",function(){{
  var h=document.documentElement;
  document.getElementById("progress").style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+"%";
}});
document.querySelectorAll("details.module").forEach(function(d,i){{ if(i<4) d.open=true; }});
</script>
</body>
</html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote", OUT)


if __name__ == "__main__":
    build()