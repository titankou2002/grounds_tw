#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the static, trilingual grounds Taiwan Launch Blueprint site."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The site is deployed into a subdirectory on cPanel (public_html/Grounds_TW/),
# not the domain root. Every internal link is written relative (no leading "/")
# and resolved against this <base href> so the site works at any mount path —
# change this one constant if the deploy target ever moves.
BASE_PATH = "/Grounds_TW/"

LANGS = ["ja", "en", "zh"]
LANG_LABEL = {"ja": "日本語", "en": "English", "zh": "中文"}

# ---------------------------------------------------------------------------
# Content model
# ---------------------------------------------------------------------------

SITE = {
    "ja": {
        "title": "夢想者",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "ホーム",
        "nav_blueprint": "ブループリント",
        "enter": "Proposalへ進む",
        "explore": "ブループリントを見る",
        "hero_line": "本気で、夢を実現する。",
        "footer_note": "Version 0.1 — Living Document. 内容は継続的に更新されます。",
        "toc_title": "目次",
        "back_top": "トップへ戻る",
    },
    "en": {
        "title": "Dreamer",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "Home",
        "nav_blueprint": "Blueprint",
        "enter": "Enter Proposal",
        "explore": "View the Blueprint",
        "hero_line": "Committed to making the dream real.",
        "footer_note": "Version 0.1 — Living Document. Content is continuously updated.",
        "toc_title": "Table of Contents",
        "back_top": "Back to top",
    },
    "zh": {
        "title": "夢想者",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "首頁",
        "nav_blueprint": "藍圖",
        "enter": "進入 Proposal",
        "explore": "查看 Blueprint",
        "hero_line": "認真實現夢想。",
        "footer_note": "Version 0.1 — Living Document，內容將持續更新。",
        "toc_title": "目錄",
        "back_top": "回到頂端",
    },
}

# Each chapter: id, number, title per lang, intent line per lang (not X / but Y), bullets per lang
CHAPTERS = [
    {
        "id": "overview",
        "num": "01",
        "title": {"ja": "プロジェクト概要", "en": "Project Overview", "zh": "專案概要"},
        "intent": {
            "ja": ["新しい店をオープンすることではなく、", "grounds Taiwan を築くこと。"],
            "en": ["Not about opening one store.", "About building grounds Taiwan."],
            "zh": ["不是開一家店，", "而是建立 grounds Taiwan。"],
        },
        "bullets": {"ja": [], "en": [], "zh": []},
    },
    {
        "id": "brand-philosophy",
        "num": "02",
        "title": {"ja": "ブランド哲学", "en": "Brand Philosophy", "zh": "品牌哲學"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["LEAP GRAVITY", "ブランドストーリー", "ブランドスピリット", "ブランドヒストリー",
                   "Mikio Sakabe のデザイン哲学", "grounds はどう生まれたか", "ブランドカルチャー", "ブランド DNA"],
            "en": ["LEAP GRAVITY", "Brand Story", "Brand Spirit", "Brand History",
                   "Mikio Sakabe's Design Philosophy", "How grounds Was Born", "Brand Culture", "Brand DNA"],
            "zh": ["LEAP GRAVITY", "品牌故事", "品牌精神", "品牌歷史",
                   "Mikio Sakabe 的設計理念", "grounds 如何誕生", "品牌文化", "品牌 DNA"],
        },
    },
    {
        "id": "product-philosophy",
        "num": "03",
        "title": {"ja": "商品哲学", "en": "Product Philosophy", "zh": "商品哲學"},
        "intent": {
            "ja": ["靴の紹介ではなく、", "各シリーズが存在する理由を伝える。"],
            "en": ["Not a shoe catalog.", "The reason each series exists."],
            "zh": ["不是介紹鞋子，", "而是介紹每一個系列存在的理由。"],
        },
        "bullets": {
            "ja": ["シリーズストーリー", "デザインインスピレーション", "素材", "テクノロジー",
                   "ターゲットユーザー", "スタイリング", "シリーズ愛称（中国語ネーミング）", "代表する精神"],
            "en": ["Series Story", "Design Inspiration", "Material", "Technology",
                   "Target User", "Styling", "Series Nickname (Chinese naming)", "Spirit It Represents"],
            "zh": ["Series Story", "Design Inspiration", "Material", "Technology",
                   "Target User", "Styling", "Series Nickname（中文命名）", "代表精神"],
        },
    },
    {
        "id": "taiwan-market",
        "num": "04",
        "title": {"ja": "台湾市場分析", "en": "Taiwan Market", "zh": "台灣市場分析"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["市場ポジショニング", "消費力", "日本ブランドの受容度", "デザイナーズブランド市場",
                   "競合ブランド分析", "SWOT", "Market Opportunity", "Threat", "Barrier"],
            "en": ["Market Positioning", "Purchasing Power", "Acceptance of Japanese Brands",
                   "Design-brand Market", "Competitor Analysis", "SWOT", "Market Opportunity", "Threat", "Barrier"],
            "zh": ["市場定位", "消費能力", "日本品牌接受度", "設計品牌市場",
                   "競爭品牌分析", "SWOT", "Market Opportunity", "Threat", "Barrier"],
        },
        "callout": {
            "ja": {
                "title": "私たちが考える最大の市場の壁",
                "lines": ["価格ではない。商圏でもない。競合でもない。", "それは「ブランド教育」。",
                          "消費者はまだ grounds が何かを知らない。",
                          "だからこそ、初年度の KPI は売上だけであってはならない。",
                          "含めるべき指標：ブランド露出／会員／コミュニティ／ブランド理解／リピート率。"],
            },
            "en": {
                "title": "The Biggest Market Challenge We See",
                "lines": ["Not price. Not location. Not competitors.", "It is brand education.",
                          "Consumers don't yet know what grounds is.",
                          "So Year-1 KPIs cannot be revenue alone.",
                          "They should include: brand exposure, membership, community, brand understanding, repeat rate."],
            },
            "zh": {
                "title": "我們目前認定最大的市場挑戰",
                "lines": ["不是價格。不是商圈。不是競爭者。", "而是品牌教育。",
                          "消費者不知道 grounds 是什麼。",
                          "因此第一年 KPI 不能只有營收，",
                          "應包含：品牌曝光、會員、社群、品牌理解、回購率。"],
            },
        },
    },
    {
        "id": "store-experience",
        "num": "05",
        "title": {"ja": "店舗戦略", "en": "Store Experience", "zh": "門市策略"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["1号店のポジショニング", "Brand Flagship", "Brand Experience", "Store Concept",
                   "Visual Merchandising", "Customer Journey", "Lighting", "Music", "Service Flow"],
            "en": ["First Store Positioning", "Brand Flagship", "Brand Experience", "Store Concept",
                   "Visual Merchandising", "Customer Journey", "Lighting", "Music", "Service Flow"],
            "zh": ["第一家店定位", "Brand Flagship", "Brand Experience", "Store Concept",
                   "Visual Merchandising", "Customer Journey", "Lighting", "Music", "Service Flow"],
        },
        "callout": {
            "ja": {"title": "ぜひご意見を伺いたい点",
                   "lines": ["1号店の位置づけについて、", "Brand Flagship として考えるべきか、", "Market Validation Store として考えるべきか、", "本社のお考えを伺えれば幸いです。"]},
            "en": {"title": "A Point We'd Love Japan HQ's Perspective On",
                   "lines": ["We'd love to understand how Japan HQ sees the first store —", "more as a Brand Flagship,", "or as a Market Validation Store."]},
            "zh": {"title": "想請教總部的想法",
                   "lines": ["關於第一家店的定位，", "是偏向 Brand Flagship，", "還是 Market Validation Store，", "很希望能聽聽總部的想法。"]},
        },
    },
    {
        "id": "taiwan-operation",
        "num": "06",
        "title": {"ja": "台湾オペレーション体制", "en": "Taiwan Operation", "zh": "台灣營運架構"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["組織図", "Governance", "会社構造", "部門", "業務内容", "フロー"],
            "en": ["Org Chart", "Governance", "Company Structure", "Departments", "Job Scope", "Process Flow"],
            "zh": ["組織圖", "Governance", "公司架構", "部門", "工作內容", "流程"],
        },
        "governance": {
            "ja": {
                "propose": "私たちの提案",
                "jp_col": "日本が保持する権限",
                "jp_items": ["ブランドディレクション", "年間予算", "重大投資", "ブランドコラボレーション", "2号店の出店", "重要なデザイン決定", "重要な仕入れ"],
                "tw_col": "台湾が担う権限",
                "tw_items": ["店舗運営", "人事", "シフト管理", "総務", "日常オペレーション", "在庫管理", "会員管理", "イベント運営", "予算内での執行"],
            },
            "en": {
                "propose": "What We Propose",
                "jp_col": "Retained by Japan HQ",
                "jp_items": ["Brand Direction", "Annual Budget", "Major Investment", "Brand Collaboration", "2nd Store Opening", "Major Design Decisions", "Major Procurement"],
                "tw_col": "Owned by Taiwan",
                "tw_items": ["Store Operations", "HR", "Scheduling", "Administration", "Daily Operations", "Inventory", "Membership", "Events", "Execution Within Budget"],
            },
            "zh": {
                "propose": "我們提出",
                "jp_col": "日本保留",
                "jp_items": ["品牌方向", "年度預算", "重大投資", "品牌合作", "第二店", "重大設計", "重大採購"],
                "tw_col": "台灣負責",
                "tw_items": ["門市", "人事", "排班", "行政", "日常營運", "庫存", "會員", "活動", "在預算內執行"],
            },
        },
        "delegation": {
            "ja": {"title": "Delegation Matrix", "desc": "完全な権限委譲制度を構築する。",
                   "rows": [["50万円以下", "台湾で承認"], ["50万円以上", "日本で承認"], ["すべての権限", "マトリクス化する"]]},
            "en": {"title": "Delegation Matrix", "desc": "Build a complete delegation-of-authority system.",
                   "rows": [["Under NT$500K", "Taiwan approval"], ["Over NT$500K", "Japan approval"], ["All authorities", "fully matrixed"]]},
            "zh": {"title": "Delegation Matrix", "desc": "建立完整授權制度。",
                   "rows": [["50萬以下", "台灣核准"], ["50萬以上", "日本核准"], ["所有權限", "全部 Matrix 化"]]},
        },
    },
    {
        "id": "company-setup",
        "num": "07",
        "title": {"ja": "会社設立", "en": "Company Setup", "zh": "公司成立"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["子会社", "支店", "違い", "外資規制の手続き", "銀行口座", "会社設立", "所要期間", "コスト", "Roadmap"],
            "en": ["Subsidiary", "Branch Office", "Difference", "Foreign Investment Process", "Banking", "Incorporation", "Timeline", "Cost", "Roadmap"],
            "zh": ["子公司", "分公司", "差異", "外資流程", "銀行", "公司設立", "時間", "成本", "Roadmap"],
        },
        "callout": {
            "ja": {"title": "現時点での初期方針", "lines": ["日本 100% 出資による台湾子会社の設立を提案する。",
                   "理由：ブランドコントロール、ガバナンス、出店拡大、将来展開の面で、", "より柔軟性が高いため。"]},
            "en": {"title": "Current Initial Direction", "lines": ["We recommend a Taiwan subsidiary, 100% owned by Japan.",
                   "Reason: greater flexibility for brand control,", "governance, store expansion, and future growth."]},
            "zh": {"title": "目前初步方向", "lines": ["建議 100% 日本持股，成立台灣子公司。",
                   "原因：品牌控制、治理、展店、未來發展，", "都較有彈性。"]},
        },
    },
    {
        "id": "logistics",
        "num": "08",
        "title": {"ja": "輸入・物流", "en": "Import & Logistics", "zh": "物流"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["サプライチェーン", "輸入", "HS Code", "関税", "物流", "通関", "表示規制", "安全在庫", "補充フロー"],
            "en": ["Supply Chain", "Import", "HS Code", "Tariffs", "Logistics", "Customs Clearance", "Labeling", "Safety Stock", "Replenishment Flow"],
            "zh": ["供應鏈", "進口", "HS Code", "關稅", "物流", "報關", "標示", "安全庫存", "補貨流程"],
        },
        "callout": {
            "ja": {"title": "教えていただきたい点", "lines": ["日本からの出荷、", "工場直送、", "日本の物流センター経由——", "どの形が望ましいか、ぜひ伺いたいです。"]},
            "en": {"title": "Something We'd Love to Learn", "lines": ["Shipped from Japan, direct from factory, or via a Japan logistics center —", "we'd love to hear which approach Japan HQ would prefer."]},
            "zh": {"title": "想了解的地方", "lines": ["日本出貨、工廠直送、還是透過日本物流中心——", "想請教總部比較希望的方式。"]},
        },
    },
    {
        "id": "it-infrastructure",
        "num": "09",
        "title": {"ja": "IT インフラ", "en": "IT Infrastructure", "zh": "數位系統"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["POS", "ERP", "CRM", "会員", "LINE", "電子インボイス", "公式サイト", "Dashboard", "データ分析"],
            "en": ["POS", "ERP", "CRM", "Membership", "LINE", "E-Invoice", "Website", "Dashboard", "Data Analytics"],
            "zh": ["POS", "ERP", "CRM", "會員", "LINE", "電子發票", "官網", "Dashboard", "數據分析"],
        },
        "callout": {
            "ja": {"title": "教えていただきたい点", "lines": ["日本の POS システムを継続利用するか、", "台湾独自のシステムを採用するか——", "本社のご意見を伺えればと思います。"]},
            "en": {"title": "Something We'd Love to Learn", "lines": ["Continue using Japan's POS system, or adopt a Taiwan-specific one —", "we'd love Japan HQ's thoughts here."]},
            "zh": {"title": "想了解的地方", "lines": ["日本 POS 是否沿用、或採台灣系統，", "想聽聽總部的想法。"]},
        },
    },
    {
        "id": "marketing",
        "num": "10",
        "title": {"ja": "マーケティング戦略", "en": "Marketing Strategy", "zh": "品牌策略"},
        "intent": {
            "ja": ["プロモーションではなく、", "ブランドビルディング。"],
            "en": ["Not promotion.", "Brand building."],
            "zh": ["不是 Promotion，", "而是 Brand Building。"],
        },
        "bullets": {
            "ja": ["ブランドポジショニング", "コンテンツ戦略", "IG", "公式サイト", "LINE", "KOL", "PR",
                   "Launch Event", "会員", "CRM", "Journal", "Lookbook"],
            "en": ["Brand Positioning", "Content Strategy", "IG", "Website", "LINE", "KOL", "PR",
                   "Launch Event", "Membership", "CRM", "Journal", "Lookbook"],
            "zh": ["品牌定位", "內容策略", "IG", "官網", "LINE", "KOL", "PR",
                   "Launch Event", "會員", "CRM", "Journal", "Lookbook"],
        },
        "callout": {
            "ja": {"title": "私たちの提案", "lines": ["初年度は、", "ブランド教育がプロモーションよりも重要である。"]},
            "en": {"title": "What We Propose", "lines": ["In Year 1,", "brand education matters more than promotion."]},
            "zh": {"title": "我們提出", "lines": ["第一年，", "品牌教育比促銷更重要。"]},
        },
    },
    {
        "id": "training",
        "num": "11",
        "title": {"ja": "教育制度", "en": "Training Academy", "zh": "教育訓練"},
        "intent": {"ja": ["grounds Taiwan Academy を設立する。"], "en": ["Establishing the grounds Taiwan Academy."],
                   "zh": ["建立 grounds Taiwan Academy。"]},
        "bullets": {
            "ja": ["ブランドカルチャー", "商品知識", "サービスフロー", "ブランドストーリー", "ブランドスピリット",
                   "POS", "店舗運営", "オペレーション", "試験", "Certification", "店長認定", "ブランドアンバサダー"],
            "en": ["Brand Culture", "Product Knowledge", "Service Flow", "Brand Story", "Brand Spirit",
                   "POS", "Store Operations", "Operations", "Examination", "Certification", "Store Manager Certification", "Brand Ambassador"],
            "zh": ["品牌文化", "產品知識", "服務流程", "品牌故事", "品牌精神",
                   "POS", "門市", "營運", "考試", "Certification", "店長認證", "品牌大使"],
        },
    },
    {
        "id": "financial-plan",
        "num": "12",
        "title": {"ja": "財務計画", "en": "Financial Plan", "zh": "財務計畫"},
        "intent": {"ja": ["Business Model"], "en": ["Business Model"], "zh": ["Business Model"]},
        "bullets": {
            "ja": ["CAPEX", "OPEX", "ROI", "Break-even", "Cash Flow", "Budget", "KPI"],
            "en": ["CAPEX", "OPEX", "ROI", "Break-even", "Cash Flow", "Budget", "KPI"],
            "zh": ["CAPEX", "OPEX", "ROI", "Break-even", "Cash Flow", "Budget", "KPI"],
        },
    },
    {
        "id": "risk",
        "num": "13",
        "title": {"ja": "リスク", "en": "Risk", "zh": "風險"},
        "intent": {
            "ja": ["成功を語るのではなく、", "失敗の要因を語る。"],
            "en": ["Not a story of success.", "A study of why things fail."],
            "zh": ["不是寫成功，", "而是失敗原因。"],
        },
        "bullets": {
            "ja": ["ブランド認知不足", "意思決定の遅れ", "補充の遅延", "人材", "キャッシュフロー", "ブランド理解の誤り"],
            "en": ["Low Brand Awareness", "Slow Decision-making", "Replenishment Delays", "Talent", "Cash Flow", "Brand Misunderstanding"],
            "zh": ["品牌知名度不足", "決策過慢", "補貨", "人才", "現金流", "品牌理解錯誤"],
        },
        "callout": {
            "ja": {"title": "そして提示するもの", "lines": ["Mitigation Plan"]},
            "en": {"title": "And What We Propose", "lines": ["A Mitigation Plan"]},
            "zh": {"title": "並提出", "lines": ["Mitigation Plan"]},
        },
    },
    {
        "id": "vision",
        "num": "14",
        "title": {"ja": "ビジョン", "en": "Vision", "zh": "願景"},
        "intent": {"ja": [], "en": [], "zh": []},
        "bullets": {
            "ja": ["3年後", "5年後", "10年後", "台湾でのポジション", "アジア展開", "将来の出店計画"],
            "en": ["3 Years", "5 Years", "10 Years", "Taiwan Position", "Asia Expansion", "Future Store Rollout"],
            "zh": ["3 Years", "5 Years", "10 Years", "Taiwan Position", "亞洲布局", "未來展店"],
        },
    },
]

SUCCESS_FACTORS = {
    "ja": {
        "title": "重要成功要因",
        "not": "靴をたくさん売ることではない。",
        "items": ["ブランドを築くこと", "ブランドを本当に理解すること", "ブランドの一貫性を維持すること",
                  "台湾チームを築くこと", "教育制度を築くこと", "SOP を築くこと", "ガバナンスを築くこと", "ブランドカルチャーを築くこと"],
    },
    "en": {
        "title": "Key Success Factors",
        "not": "Not about selling a lot of shoes.",
        "items": ["Build the brand", "Truly understand the brand", "Maintain brand consistency",
                  "Build the Taiwan team", "Build a training system", "Build SOPs", "Build governance", "Build brand culture"],
    },
    "zh": {
        "title": "關鍵成功因素",
        "not": "不是賣很多鞋。",
        "items": ["建立品牌", "真正理解品牌", "維持品牌一致性", "建立台灣團隊",
                  "建立教育制度", "建立 SOP", "建立治理", "建立品牌文化"],
    },
}

OPEN_QUESTIONS = {
    "ja": {
        "title": "すり合わせさせていただきたい点（Open Questions）",
        "intro": "以下は、私たちが今後の準備をより良く進めるために、日本本社の皆さまのお考えをぜひお伺いしたい点です。回答を急かすものではなく、私たちがブランドと本社の意向をより深く理解したいという気持ちからまとめました。",
        "groups": [
            ("Strategy", ["台湾進出にあたり、本社として特に大切にされたい軸は何か", "ブランドか", "売上か", "アジア展開か"]),
            ("Store", ["1号店の位置づけは？", "旗艦店か？", "市場検証店か？"]),
            ("Governance", ["子会社か？", "支店か？", "法定代表者は？", "権限委譲制度は？"]),
            ("Product", ["全シリーズ展開か？", "一部シリーズか？", "限定商品か？"]),
            ("Marketing", ["日本からどの素材が提供されるか？", "台湾で独自制作できるものは？", "日本の承認が必要なものは？"]),
            ("Training", ["日本の認定が必要か？", "訪日研修は必要か？"]),
            ("Digital", ["POS？ERP？CRM？会員？公式サイト？", "グローバルで同期するか？"]),
            ("Supply Chain", ["補充は？", "安全在庫は？", "物流は？", "日本工場か？", "第三者物流か？"]),
            ("KPI", ["初年度の成功の定義は？", "ブランドか？会員か？売上か？コミュニティか？"]),
        ],
    },
    "en": {
        "title": "Points We'd Love to Align On (Open Questions)",
        "intro": "The points below are things we would sincerely love to hear Japan HQ's thoughts on, so we can prepare more thoughtfully going forward. This isn't a request for an immediate decision — it comes from our wish to understand the brand and Japan HQ's intentions more deeply.",
        "groups": [
            ("Strategy", ["What matters most to Japan HQ in entering Taiwan", "Brand?", "Revenue?", "Asia expansion?"]),
            ("Store", ["What is the positioning of the first store?", "Flagship?", "Market validation store?"]),
            ("Governance", ["Subsidiary?", "Branch office?", "Who is the legal representative?", "What delegation system?"]),
            ("Product", ["Full product range?", "Partial series?", "Limited items only?"]),
            ("Marketing", ["What assets will Japan provide?", "What can Taiwan produce independently?", "What requires Japan's approval?"]),
            ("Training", ["Is Japan certification required?", "Is training in Japan required?"]),
            ("Digital", ["POS? ERP? CRM? Membership? Website?", "Should these sync globally?"]),
            ("Supply Chain", ["Replenishment?", "Safety stock?", "Logistics?", "Japan factory?", "Third-party logistics?"]),
            ("KPI", ["What defines success in Year 1?", "Brand? Membership? Revenue? Community?"]),
        ],
    },
    "zh": {
        "title": "想與總部一起對齊的方向（Open Questions）",
        "intro": "以下是我們希望能多了解、日後準備能更貼近總部想法的幾個方向。這不是要請總部立刻給出答案,而是我們真心想更理解品牌與總部的想法。",
        "groups": [
            ("Strategy", ["台灣進入初期，總部最重視的方向是什麼", "品牌？", "營收？", "亞洲布局？"]),
            ("Store", ["第一家店定位？", "旗艦店？", "市場驗證店？"]),
            ("Governance", ["子公司？", "分公司？", "法定負責人？", "授權制度？"]),
            ("Product", ["全部系列？", "部分系列？", "限定商品？"]),
            ("Marketing", ["日本提供哪些素材？", "哪些可自行製作？", "哪些需要日本核准？"]),
            ("Training", ["需不需要日本認證？", "是否赴日受訓？"]),
            ("Digital", ["POS？ERP？CRM？會員？官網？", "是否全球同步？"]),
            ("Supply Chain", ["補貨？", "安全庫存？", "物流？", "日本工廠？", "第三方物流？"]),
            ("KPI", ["第一年成功定義？", "品牌？會員？營收？社群？"]),
        ],
    },
}

LEADERSHIP = {
    "ja": {
        "title": "薛佶姈（Hsueh Chi-Ling）",
        "basics": "1982年1月7日生まれ　｜　高校卒業",
        "summary": "小売現場から代理店運営まで、15年にわたるオペレーション経験。ブランドのローカライズ、在庫・物流管理、店舗運営、財務諸表分析を得意とする。単独での実務遂行力とチームを牽引するリーダーシップを併せ持ち、運転免許を保有し機動力も高い。",
        "sections": [
            ("タイル代理店 ― 運営管理｜15年", [
                "数千 SKU に及ぶ在庫管理と物流スケジューリング",
                "ERP／仕入販売在庫システムの導入と日常運用",
                "売上レポート・財務諸表・損益分析による経営判断のサポート",
                "カタログ・DM・販促物の制作とブランドサポート",
                "サプライヤーとの折衝、調達・スケジュール調整",
            ]),
            ("小売現場での接客・販売｜10年", [
                "店舗運営と顧客対応",
                "商品陳列、販売転換、顧客関係の維持",
            ]),
            ("運営管理", ["在庫管理", "物流スケジューリング", "店舗運営"]),
            ("財務分析", ["売上レポート", "財務諸表", "損益分析"]),
            ("ブランドサポート", ["カタログ／DM 制作", "販促提案", "プレゼン資料"]),
            ("システムツール", ["ERP", "仕入販売在庫システム", "Office"]),
            ("その他", ["普通自動車運転免許を保有、機動力が高い"]),
        ],
    },
    "en": {
        "title": "Hsueh Chi-Ling (薛佶姈)",
        "basics": "Born January 7, 1982　|　High School Graduate",
        "summary": "15+ years of operations experience spanning retail front-line and brand distribution. Skilled in brand localization, inventory & logistics management, store operations, and financial statement analysis. An independent operator with team leadership ability, holding a valid driver's license for high operational mobility.",
        "sections": [
            ("Tile Distributor — Operations Management | 15 Years", [
                "Inventory management and logistics scheduling across thousands of SKUs",
                "ERP / inventory management system implementation and daily operation",
                "Sales reports, financial statements, and P&L analysis to support management decisions",
                "Catalog, DM, and promotional material production, and brand support",
                "Supplier communication, procurement, and scheduling coordination",
            ]),
            ("Retail Front-Line Sales | 10 Years", [
                "Store operations and customer service",
                "Visual merchandising, sales conversion, and client relationship management",
            ]),
            ("Operations", ["Inventory management", "Logistics scheduling", "Store operations"]),
            ("Financial Analysis", ["Sales reports", "Financial statements", "P&L analysis"]),
            ("Brand Support", ["Catalog / DM production", "Promotional proposals", "Presentations"]),
            ("Systems", ["ERP", "Inventory management systems", "Office Suite"]),
            ("Other", ["Valid driver's license, high mobility"]),
        ],
    },
    "zh": {
        "title": "薛佶姈",
        "basics": "1982年1月7日生　｜　高中畢業",
        "summary": "15 年營運管理經驗，橫跨第一線零售與代理商營運。擅長品牌落地、庫存物流、門市管理、財務報表分析。具備獨立作業與團隊領導能力，可自行駕駛，移動與物流調度彈性高。",
        "sections": [
            ("磁磚代理商 — 營運管理｜15 年", [
                "庫存管理與物流排程，控管數千品項 SKU",
                "ERP / 進銷存系統導入與日常操作",
                "銷售報表分析、財報分析、損益表分析，提供管理決策依據",
                "產品型錄、DM、廣告文宣製作與品牌支援",
                "供應商溝通、採購與排程協調",
            ]),
            ("零售第一線銷售｜10 年", [
                "門市營運與顧客服務",
                "商品陳列、銷售轉換、客戶關係維護",
            ]),
            ("營運管理", ["庫存管理", "物流排程", "門市營運"]),
            ("財務分析", ["銷售報表", "財報", "損益表分析"]),
            ("品牌支援", ["型錄 / DM 製作", "文宣提案", "簡報"]),
            ("系統工具", ["ERP", "進銷存", "Office"]),
            ("其他", ["具備汽車駕駛能力，移動彈性高"]),
        ],
    },
}

CLOSING = {
    "ja": {
        "title": "私たちが日本本社に本当に証明したいこと",
        "lines": [
            "私たちはブランドの代理店として来たのではない。",
            "靴屋を一軒開きに来たのでもない。",
            "grounds のブランド精神を長期的に守り、日本のブランドカルチャーを完全に台湾へ根付かせ、",
            "持続的に拡張できる grounds Taiwan の運営チームを築きたい。",
            "この Blueprint は提案書ではない。",
            "これからのすべての意思決定・実行・協働の共通基盤である。",
        ],
    },
    "en": {
        "title": "What We Truly Want to Prove to Japan HQ",
        "lines": [
            "We are not here to license the brand.",
            "We are not here to open a single shoe store.",
            "We want to build a grounds Taiwan operations team that can protect the brand's spirit long-term,",
            "fully localize Japan's brand culture, and sustain future expansion.",
            "This Blueprint is not a proposal.",
            "It is the shared foundation for every decision, execution, and collaboration to come.",
        ],
    },
    "zh": {
        "title": "我們真正想向日本總部證明的事情",
        "lines": [
            "我們不是來代理品牌。",
            "不是來開一家鞋店。",
            "而是希望建立一個能夠長期維護 grounds 品牌精神、完整落地日本品牌文化，",
            "並具備持續擴張能力的 grounds Taiwan 營運團隊。",
            "這份 Blueprint，不是一份提案，",
            "而是未來所有決策、執行與合作的共同基礎。",
        ],
    },
}

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def lang_switch_html(current, page):
    # page: "index" or "blueprint"
    links = []
    for l in LANGS:
        href = f"{page}.html" if l == "ja" else f"{l}/{page}.html"
        cls = " current" if l == current else ""
        links.append(f'<a class="lang-link{cls}" href="{href}">{LANG_LABEL[l]}</a>')
    return '<div class="lang-switch">' + "".join(links) + "</div>"


def nav_html(current, active_page):
    t = SITE[current]
    home_href = "index.html" if current == "ja" else f"{current}/index.html"
    bp_href = "blueprint.html" if current == "ja" else f"{current}/blueprint.html"
    return f'''<header class="site-nav">
  <a class="wordmark" href="{home_href}" aria-label="grounds Taiwan"></a>
  <nav class="nav-links">
    <a href="{home_href}" class="{'active' if active_page=='index' else ''}">{t['nav_home']}</a>
    <a href="{bp_href}" class="{'active' if active_page=='blueprint' else ''}">{t['nav_blueprint']}</a>
  </nav>
  {lang_switch_html(current, active_page)}
</header>'''


def html_shell(lang, active_page, body, extra_head=""):
    t = SITE[lang]
    html_lang = {"ja": "ja", "en": "en", "zh": "zh-Hant"}[lang]
    return f'''<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<base href="{BASE_PATH}">
<title>{t['title']}</title>
<meta name="description" content="{t['subtitle']}">
<link rel="stylesheet" href="assets/css/style.css">
{extra_head}
</head>
<body>
{nav_html(lang, active_page)}
{body}
<footer class="site-footer">
  <p>{t['footer_note']}</p>
</footer>
<script src="assets/js/main.js"></script>
</body>
</html>
'''


def index_body(lang):
    t = SITE[lang]
    bp_href = "blueprint.html" if lang == "ja" else f"{lang}/blueprint.html"
    leadership_section = render_leadership_section(lang)
    return f'''<main class="hero">
  <div class="hero-inner reveal">
    <h1 class="hero-line">{t['hero_line']}</h1>
  </div>
  <div class="scroll-cue reveal-delay">↓</div>
</main>
<div class="blueprint-content profile-page">
{leadership_section}
</div>
<p class="explore-link"><a href="{bp_href}">{t['explore']} →</a></p>
'''


def render_bullets(items):
    if not items:
        return ""
    lis = "\n".join(f"      <li>{i}</li>" for i in items)
    return f'''    <ul class="bullet-grid">
{lis}
    </ul>
'''


def render_intent(lines):
    if not lines:
        return ""
    ps = "\n".join(f"    <p class=\"intent-line\">{l}</p>" for l in lines)
    return ps + "\n"


def render_callout(data):
    if not data:
        return ""
    lines = "\n".join(f"      <p>{l}</p>" for l in data["lines"])
    return f'''    <div class="callout">
      <p class="callout-title">{data['title']}</p>
{lines}
    </div>
'''


def render_governance(gov):
    if not gov:
        return ""
    jp_items = "\n".join(f"        <li>{i}</li>" for i in gov["jp_items"])
    tw_items = "\n".join(f"        <li>{i}</li>" for i in gov["tw_items"])
    return f'''    <p class="callout-title">{gov['propose']}</p>
    <div class="two-col">
      <div class="col">
        <p class="col-title">{gov['jp_col']}</p>
        <ul>
{jp_items}
        </ul>
      </div>
      <div class="col">
        <p class="col-title">{gov['tw_col']}</p>
        <ul>
{tw_items}
        </ul>
      </div>
    </div>
'''


def render_delegation(dele):
    if not dele:
        return ""
    rows = "\n".join(
        f'      <tr><td>{r[0]}</td><td>{r[1]}</td></tr>' for r in dele["rows"]
    )
    return f'''    <div class="matrix">
      <p class="callout-title">{dele['title']}</p>
      <p class="matrix-desc">{dele['desc']}</p>
      <table class="matrix-table">
{rows}
      </table>
    </div>
'''


def render_leadership_section(lang):
    lp = LEADERSHIP[lang]
    basics_html = f'<p class="lead-basics">{lp["basics"]}</p>' if lp.get("basics") else ""
    summary_html = f'<p class="lead-summary">{lp["summary"]}</p>' if lp.get("summary") else ""
    lead_sections = []
    for name, items in lp["sections"]:
        items_html = "\n".join(f"        <li>{i}</li>" for i in items)
        lead_sections.append(f'''    <div class="lead-group">
      <p class="lead-group-title">{name}</p>
      <ul class="bullet-grid compact">
{items_html}
      </ul>
    </div>''')
    return f'''  <section id="leadership" class="chapter reveal">
    <h2 class="chapter-title">{lp['title']}</h2>
    {basics_html}
    {summary_html}
    <div class="lead-grid">
{"".join(lead_sections)}
    </div>
  </section>'''


def blueprint_body(lang):
    t = SITE[lang]
    # NOTE: with <base href> set, a bare "#id" link resolves against the base
    # path (i.e. it navigates to the site root), not the current document —
    # per RFC 3986 §5.3, an empty-path reference inherits the base's path.
    # So in-page anchors must repeat this page's own path explicitly.
    bp_href = "blueprint.html" if lang == "ja" else f"{lang}/blueprint.html"
    sections_nav = "\n".join(
        f'    <a href="{bp_href}#{c["id"]}">{c["num"]} — {c["title"][lang]}</a>' for c in CHAPTERS
    )
    sections_nav += f'\n    <a href="{bp_href}#success-factors">{SUCCESS_FACTORS[lang]["title"]}</a>'
    sections_nav += f'\n    <a href="{bp_href}#open-questions">{OPEN_QUESTIONS[lang]["title"]}</a>'
    sections_nav += f'\n    <a href="{bp_href}#leadership">{LEADERSHIP[lang]["title"]}</a>'

    chapter_sections = []
    for c in CHAPTERS:
        intent = render_intent(c["intent"][lang])
        bullets = render_bullets(c["bullets"][lang])
        callout = render_callout(c.get("callout", {}).get(lang)) if "callout" in c else ""
        gov = render_governance(c.get("governance", {}).get(lang)) if "governance" in c else ""
        dele = render_delegation(c.get("delegation", {}).get(lang)) if "delegation" in c else ""
        chapter_sections.append(f'''  <section id="{c['id']}" class="chapter reveal">
    <p class="chapter-num">{c['num']}</p>
    <h2 class="chapter-title">{c['title'][lang]}</h2>
{intent}{bullets}{gov}{dele}{callout}  </section>''')

    sf = SUCCESS_FACTORS[lang]
    sf_items = "\n".join(f"      <li>{i}</li>" for i in sf["items"])
    success_section = f'''  <section id="success-factors" class="chapter reveal">
    <h2 class="chapter-title">{sf['title']}</h2>
    <p class="intent-line">{sf['not']}</p>
    <ul class="bullet-grid">
{sf_items}
    </ul>
  </section>'''

    oq = OPEN_QUESTIONS[lang]
    groups_html = []
    for name, items in oq["groups"]:
        items_html = "\n".join(f"        <li>{i}</li>" for i in items)
        groups_html.append(f'''    <div class="oq-group">
      <p class="oq-group-title">{name}</p>
      <ul>
{items_html}
      </ul>
    </div>''')
    open_questions_section = f'''  <section id="open-questions" class="chapter reveal">
    <h2 class="chapter-title">{oq['title']}</h2>
    <p class="intent-line oq-intro">{oq['intro']}</p>
    <div class="oq-grid">
{"".join(groups_html)}
    </div>
  </section>'''

    leadership_section = render_leadership_section(lang)

    cl = CLOSING[lang]
    closing_lines = "\n".join(f"    <p>{l}</p>" for l in cl["lines"])
    closing_section = f'''  <section id="closing" class="chapter closing reveal">
    <h2 class="chapter-title">{cl['title']}</h2>
{closing_lines}
  </section>'''

    return f'''<div class="blueprint-layout">
  <aside class="toc">
    <p class="toc-title">{t['toc_title']}</p>
{sections_nav}
  </aside>
  <main class="blueprint-content">
{chr(10).join(chapter_sections)}
{success_section}
{open_questions_section}
{leadership_section}
{closing_section}
  </main>
</div>
'''


CSS = '''/* grounds Taiwan Launch Blueprint — design system
   Japanese-first, minimal, white space, typography-driven, editorial, calm, premium. */

:root{
  --bg: #fdfdfc;
  --fg: #14140f;
  --muted: #6b6b62;
  --line: #e4e2da;
  --accent: #14140f;
  --callout-bg: #f4f3ee;
  --serif: "Georgia", "Noto Serif JP", "Noto Serif TC", serif;
  --sans: -apple-system, BlinkMacSystemFont, "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Noto Sans TC", sans-serif;
  --max-w: 880px;
}

@media (prefers-color-scheme: dark){
  :root{
    --bg: #111110;
    --fg: #ece9e2;
    --muted: #9a978d;
    --line: #2a2a26;
    --accent: #ece9e2;
    --callout-bg: #1a1a17;
  }
}

*{ box-sizing: border-box; }
html{ scroll-behavior: smooth; }
body{
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--sans);
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
}

a{ color: inherit; }

/* Nav */
.site-nav{
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 18px 32px;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.wordmark{
  display: inline-block;
  min-width: 120px;
  height: 1px;
}
.nav-links{ display: flex; gap: 20px; font-size: 13px; }
.nav-links a{ text-decoration: none; color: var(--muted); padding-bottom: 2px; }
.nav-links a.active{ color: var(--fg); border-bottom: 1px solid var(--fg); }
.lang-switch{ display: flex; gap: 12px; font-size: 12px; }
.lang-link{ text-decoration: none; color: var(--muted); }
.lang-link.current{ color: var(--fg); font-weight: 600; }

/* Hero */
.hero{
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 24px;
}
.hero-inner{ max-width: 720px; }
.hero-eyebrow{
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 28px;
}
.hero-line{
  font-family: var(--serif);
  font-weight: 400;
  font-size: clamp(28px, 4.4vw, 44px);
  line-height: 1.45;
  margin: 0;
}
.hero-line-2{ color: var(--muted); }
.hero-sub{
  margin-top: 28px;
  font-size: 14px;
  color: var(--muted);
  letter-spacing: 0.02em;
}
.cta{
  display: inline-block;
  margin-top: 44px;
  padding: 14px 32px;
  border: 1px solid var(--fg);
  border-radius: 999px;
  text-decoration: none;
  font-size: 13px;
  letter-spacing: 0.06em;
  transition: background 0.25s ease, color 0.25s ease;
}
.cta:hover{ background: var(--fg); color: var(--bg); }
.scroll-cue{
  margin-top: 60px;
  color: var(--muted);
  animation: bob 2.2s ease-in-out infinite;
}
@keyframes bob{
  0%,100%{ transform: translateY(0); }
  50%{ transform: translateY(8px); }
}

/* Blueprint layout */
.blueprint-layout{
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 48px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 56px 32px 120px;
}
.toc{
  position: sticky;
  top: 76px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 12.5px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}
.toc-title{
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 6px;
}
.toc a{
  text-decoration: none;
  color: var(--muted);
  padding: 2px 0;
}
.toc a:hover{ color: var(--fg); }

.blueprint-content{ max-width: var(--max-w); }
.chapter{
  padding: 56px 0;
  border-bottom: 1px solid var(--line);
}
.chapter:last-child{ border-bottom: none; }
.chapter-num{
  font-family: var(--serif);
  font-size: 13px;
  color: var(--muted);
  letter-spacing: 0.1em;
  margin: 0 0 8px;
}
.chapter-title{
  font-family: var(--serif);
  font-weight: 400;
  font-size: clamp(24px, 3vw, 32px);
  margin: 0 0 20px;
}
.intent-line{
  font-size: 16px;
  color: var(--muted);
  margin: 0 0 6px;
}

.bullet-grid{
  list-style: none;
  margin: 24px 0 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 10px 24px;
}
.bullet-grid.compact{ grid-template-columns: 1fr; gap: 6px; }
.bullet-grid li{
  font-size: 14.5px;
  padding: 8px 0;
  border-bottom: 1px dotted var(--line);
}

.callout{
  margin-top: 32px;
  padding: 24px 28px;
  background: var(--callout-bg);
  border-radius: 4px;
}
.callout p{ margin: 0 0 4px; font-size: 14.5px; }
.callout-title{
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px !important;
}

.two-col{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 12px;
}
.col-title{ font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.col ul{ margin: 0; padding-left: 18px; font-size: 14px; color: var(--muted); }
.col li{ margin-bottom: 4px; }

.matrix{ margin-top: 32px; }
.matrix-desc{ color: var(--muted); font-size: 14px; margin: 0 0 14px; }
.matrix-table{ width: 100%; border-collapse: collapse; font-size: 14px; }
.matrix-table td{ padding: 10px 12px; border: 1px solid var(--line); }

.oq-intro{ max-width: 640px; margin-bottom: 32px !important; }
.oq-grid{
  display: grid;
  grid-template-columns: repeat(3, minmax(0,1fr));
  gap: 28px;
}
.oq-group-title{ font-weight: 600; font-size: 13px; margin: 0 0 8px; }
.oq-group ul{ margin: 0; padding-left: 18px; font-size: 13.5px; color: var(--muted); }
.oq-group li{ margin-bottom: 6px; }

.lead-basics{
  font-size: 13px;
  letter-spacing: 0.02em;
  color: var(--muted);
  margin: 0 0 20px;
}
.lead-summary{
  max-width: 640px;
  font-size: 16px;
  color: var(--muted);
  margin: 0 0 24px;
}
.profile-page{
  margin: 0 auto;
  padding: 40px 32px 80px;
}
.profile-page .chapter{ border-bottom: none; padding-top: 0; }
.explore-link{
  text-align: center;
  padding: 0 24px 80px;
}
.explore-link a{
  font-size: 13px;
  letter-spacing: 0.04em;
  color: var(--muted);
  text-decoration: none;
  border-bottom: 1px solid var(--line);
  padding-bottom: 2px;
}
.explore-link a:hover{ color: var(--fg); border-color: var(--fg); }
.lead-grid{
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 32px;
}
.lead-group-title{ font-weight: 600; font-size: 13.5px; margin-bottom: 10px; }

.closing p{ font-size: 16px; margin: 0 0 10px; }
.closing .chapter-title{ margin-bottom: 28px; }

.site-footer{
  text-align: center;
  padding: 40px 24px 60px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--line);
}

/* Content is always visible (opacity never hidden) — only a subtle slide-up
   motion is deferred to scroll-in, so nothing ever depends on JS/IO timing. */
.reveal{ transform: translateY(24px); transition: transform 0.7s ease; }
.reveal.in-view{ transform: translateY(0); }
.reveal-delay{ animation: slideup 0.8s ease 0.4s both; }
@keyframes slideup{ from{ transform: translateY(10px); } to{ transform: translateY(0); } }

@media (max-width: 860px){
  .blueprint-layout{ grid-template-columns: 1fr; }
  .toc{ position: static; flex-direction: row; flex-wrap: wrap; max-height: none; }
  .bullet-grid{ grid-template-columns: 1fr; }
  .two-col, .oq-grid, .lead-grid{ grid-template-columns: 1fr; }
  .nav-links{ display: none; }
}
'''

JS = '''document.addEventListener("DOMContentLoaded", () => {
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.01, rootMargin: "0px 0px -10% 0px" });
    revealEls.forEach((el) => io.observe(el));
    // Safety net: never let content stay offset if IO misses a fast/programmatic scroll.
    setTimeout(() => revealEls.forEach((el) => el.classList.add("in-view")), 2000);
  } else {
    revealEls.forEach((el) => el.classList.add("in-view"));
  }
});
'''


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


def main():
    write("assets/css/style.css", CSS)
    write("assets/js/main.js", JS)

    for lang in LANGS:
        idx = html_shell(lang, "index", index_body(lang))
        bp = html_shell(lang, "blueprint", blueprint_body(lang))
        if lang == "ja":
            write("index.html", idx)
            write("blueprint.html", bp)
        else:
            write(f"{lang}/index.html", idx)
            write(f"{lang}/blueprint.html", bp)


if __name__ == "__main__":
    main()
