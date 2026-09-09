#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build standalone self-contained HTML pages for the 專題文件庫 split files.
Internal planning .md stay git-ignored (never pushed to the public repo);
these generated docs/*.html are the published copies, matching the site."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

CSS = """
:root{--bg:#0e1116;--bg2:#151a22;--card:#1b222c;--line:#2c3a4d;--txt:#e8eef6;
--muted:#8fa0b5;--accent:#7fb3ff;--accent2:#ffd075;--note:#7fe3c8;--do:#ffd075;--danger:#ff8f8f}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif;line-height:1.8;font-size:15px}
main{max-width:860px;margin:0 auto;padding:34px 22px 80px}
h1{font-size:26px;border-bottom:3px solid var(--accent);padding-bottom:10px;margin-bottom:8px}
h2{font-size:19px;margin:28px 0 8px;padding-left:10px;border-left:4px solid var(--accent2)}
h3{font-size:16px;margin:18px 0 6px;color:var(--accent)}
h4{font-size:14.5px;margin:14px 0 5px}
.lede,.quote{background:var(--bg2);border-left:3px solid var(--accent2);border-radius:8px;padding:10px 14px;margin:12px 0;font-size:13.5px;color:var(--muted)}
p{margin:8px 0}
strong{color:#fff}
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:var(--bg2);color:var(--accent2)}
ul,ol{margin:6px 0 6px 22px}
li{margin-bottom:3px}
ul.task{list-style:none;margin-left:0}
ul.task li{list-style:none;padding-left:22px;position:relative}
ul.task li:before{content:"☐";position:absolute;left:0;color:var(--do)}
a{color:var(--accent)}
.top{font-size:12.5px;color:var(--muted);margin-bottom:14px}
.top a{color:var(--accent)}
@media(max-width:680px){body{font-size:14px}main{padding:20px 14px 60px}}
"""


def inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\s][^*]*?)\*", r"<em>\1</em>", text)
    return text


def render(lines):
    out = []
    i = 0
    task_pat = re.compile(r"^[-*]\s+\[[ xX]\]\s*")
    list_pat = re.compile(r"^[-*]\s+")
    num_pat = re.compile(r"^\d+[.)]\s+")
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
                rows.append("".join("<td>%s</td>" % inline(c.strip()) for c in r.strip("|").split("|")))
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
                       % ("".join("<th>%s</th>" % h for h in head), "".join("<tr>%s</tr>" % r for r in rows)))
            continue
        m = re.match(r"^(#{1,4})(\s+.*)$", s)
        if m:
            n = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (n, inline(m.group(2).strip()), n))
            i += 1
            continue
        if s.startswith(">"):
            out.append("<div class='quote'>%s</div>" % inline(s.lstrip(">").strip()))
            i += 1
            continue
        if s == "---":
            i += 1
            continue
        if re.match(r"^[-*]\s+\[[ xX]\]", s):
            lis = []
            while i < len(lines) and re.match(r"^[-*]\s+\[[ xX]\]", lines[i].strip()):
                lis.append("<li>%s</li>" % inline(task_pat.sub("", lines[i].strip())))
                i += 1
            out.append("<ul class='task'>%s</ul>" % "".join(lis))
            continue
        if re.match(r"^[-*]\s+", s):
            lis = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                lis.append("<li>%s</li>" % inline(list_pat.sub("", lines[i].strip())))
                i += 1
            out.append("<ul>%s</ul>" % "".join(lis))
            continue
        if re.match(r"^\d+[.)]\s+", s):
            lis = []
            while i < len(lines) and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                lis.append("<li>%s</li>" % inline(num_pat.sub("", lines[i].strip())))
                i += 1
            out.append("<ol>%s</ol>" % "".join(lis))
            continue
        out.append("<p>%s</p>" % inline(s))
        i += 1
    return "\n".join(out)


PAGES = [
    ("知識_商標佈局調查結果.md", "知識_商標佈局調查結果.html", "商標佈局調查結果"),
    ("知識_子公司vs分公司.md", "知識_子公司vs分公司.html", "子公司 vs 分公司"),
    ("策略_選品店通路.md", "策略_選品店通路.html", "台灣選品店通路策略"),
    ("策略_進口路線比較.md", "策略_進口路線比較.html", "進口路線比較"),
    ("策略_電商三階段.md", "策略_電商三階段.html", "電商三階段策略"),
    ("記錄_快閃活動.md", "記錄_快閃活動.html", "快閃活動"),
    ("檢查_開店前置合規.md", "檢查_開店前置合規.html", "開店前置合規 Checklist"),
]


def main():
    for srcname, outname, title in PAGES:
        src = os.path.join(ROOT, srcname)
        lines = open(src, encoding="utf-8").read().split("\n")
        body = render(lines)
        page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}｜grounds Taiwan</title>
<style>{CSS}</style>
</head>
<body>
<main>
<div class="top">← <a href="grounds_taiwan_行動方案.html">回執行行動方案</a>（專題文件庫）</div>
{body}
</main>
</body>
</html>"""
        open(os.path.join(DOCS, outname), "w", encoding="utf-8").write(page)
        print("wrote", outname)


if __name__ == "__main__":
    main()