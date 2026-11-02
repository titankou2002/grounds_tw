#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從《開店作戰中心.md》第⑥層（14 章任務卡）＋《grounds_taiwan_行動方案.md》（急迫度）
   抽出結構化任務，輸出 data/tasks.json。MD 仍是正本；改完 MD 重跑即可。
   依賴關係（DEPENDS）是人工整理的，因為 MD 沒寫成結構化。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.join(ROOT, "開店作戰中心.md")
PLAN = os.path.join(ROOT, "grounds_taiwan_行動方案.md")
OUT = os.path.join(ROOT, "data", "tasks.json")

# 任務 id → 必須先完成的任務 id（鎖定用）。id 格式：ch07-t3 = 第 7 章第 3 個任務
DEPENDS = {
    "ch07-t3": ["ch07-t2"],            # 執行公司設立 ← 日本拍板結構
    "ch07-t2": ["ch07-t1"],            # 拍板 ← 先有報價與比較
    "ch06-t1": [],
    "ch08-t3": ["ch07-t3", "ch03-t1", "ch08-t1"],  # 下單 ← 公司成立、引進範圍、報關行
    "ch05-t2": ["ch05-t1"],
    "ch09-t2": ["ch07-t3"],            # 刷卡收單 ← 公司帳戶
    "ch11-t3": ["ch11-t1"],
}


def parse_urgency():
    """行動方案每章『急迫度：P?』→ {章號: 'P0'}"""
    text = open(PLAN, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"## Chapter (\d\d)｜.*?\*\*急迫度：\*\*\s*(P\d)", text, re.S):
        out[int(m.group(1))] = m.group(2)
    return out


def parse_deadline(s):
    """'T-170' → 170；'T-30 前會勘' → 30；其他 → None"""
    m = re.search(r"T-(\d+)", s)
    return int(m.group(1)) if m else None


def parse_hub():
    text = open(HUB, encoding="utf-8").read()
    text = text[text.index("## ⑥ 作戰手冊"):]
    urgency = parse_urgency()
    chapters = []
    cur_ch = cur_task = None
    mode = None  # 目前在讀的清單類型

    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"### Ch(\d\d) (.+)", line)
        if m:
            cur_ch = {
                "num": int(m.group(1)),
                "title": m.group(2).strip(),
                "priority": urgency.get(int(m.group(1)), "P1"),
                "why": "", "owner": "", "japan_decides": "", "taiwan_does": "",
                "tasks": [],
            }
            chapters.append(cur_ch)
            cur_task = None
            continue
        if cur_ch is None:
            continue
        m = re.match(r"#### 任務：(.+)", line)
        if m:
            idx = len(cur_ch["tasks"]) + 1
            cur_task = {
                "id": f"ch{cur_ch['num']:02d}-t{idx}",
                "chapter": cur_ch["num"],
                "title": m.group(1).strip(),
                "priority": cur_ch["priority"],
                "conditions": [], "needs_japan": "", "deadline_t": None,
                "deadline_raw": "", "note": "", "depends": [],
            }
            cur_ch["tasks"].append(cur_task)
            mode = None
            continue

        def after(label):
            mm = re.match(rf"- \*{{0,2}}{label}\*{{0,2}}[：:]\s*(.*)", line)
            return mm.group(1).strip() if mm else None

        if cur_task is None:
            for key, label in (("why", "為什麼重要"), ("owner", "負責"),
                               ("japan_decides", "日本要決定"), ("taiwan_does", "台灣負責")):
                v = after(label)
                if v is not None:
                    cur_ch[key] = v
            continue

        if line.startswith("- 完成條件"):
            mode = "cond"
        elif mode == "cond" and re.match(r"\s+- \[[ x]\] (.+)", line):
            done = "[x]" in line
            cur_task["conditions"].append({
                "text": re.match(r"\s+- \[[ x]\] (.+)", line).group(1).strip(),
                "done_in_md": done})
        elif line.startswith("- 需要日本"):
            cur_task["needs_japan"] = line.split("：", 1)[1].strip()
            mode = None
        elif line.startswith("- 截止"):
            cur_task["deadline_raw"] = line.split("：", 1)[1].strip()
            cur_task["deadline_t"] = parse_deadline(cur_task["deadline_raw"])
            mode = None
        elif line.startswith("- **注意**"):
            # 注意事項掛在章最後一個任務之後，歸給該章最後一個任務
            cur_task["note"] = line.split("：", 1)[1].strip()
            mode = None

    for ch in chapters:
        for t in ch["tasks"]:
            t["depends"] = DEPENDS.get(t["id"], [])
            j = t["needs_japan"]
            t["waiting_japan"] = bool(j) and not j.startswith("無") and not j.endswith("則無")
    return chapters


def main():
    chapters = parse_hub()
    all_ids = {t["id"] for c in chapters for t in c["tasks"]}
    for k, v in DEPENDS.items():
        for x in [k] + v:
            assert x in all_ids, f"DEPENDS 指到不存在的任務：{x}"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"version": "0.1", "chapters": chapters}, f,
                  ensure_ascii=False, indent=2)
    n = sum(len(c["tasks"]) for c in chapters)
    print(f"{len(chapters)} 章、{n} 個任務 → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
