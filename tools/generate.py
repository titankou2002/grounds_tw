#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the static, trilingual grounds Taiwan Launch Blueprint site."""
import hashlib
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
        "title": "PROFILE",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "ホーム",
        "enter": "Proposalへ進む",
        "hero_line": "ブランドを理解し、運営で育てる。",
        "toc_title": "目次",
        "back_top": "トップへ戻る",
    },
    "en": {
        "title": "PROFILE",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "Home",
        "enter": "Enter Proposal",
        "hero_line": "Understanding the Brand, Building the Operation.",
        "toc_title": "Table of Contents",
        "back_top": "Back to top",
    },
    "zh": {
        "title": "PROFILE",
        "subtitle": "Building the Official Taiwan Operation Together.",
        "nav_home": "首頁",
        "enter": "進入 Proposal",
        "hero_line": "理解品牌，用營運滋養它。",
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

PROFILE_PHOTO = "assets/img/profile.jpg"

# Brand names themselves are proper nouns and stay unchanged across ja/en/zh.
# Everything ELSE — role titles, category labels, skill items, language
# levels — must be fully localized; keeping those in English on the ja/zh
# pages was a mistake in the first pass and read as broken, not "editorial."
# Section labels are NOT shared across languages. Translating the body copy
# while leaving section headers like "About" / "Career" in English reads as
# "a résumé translated into Japanese," not a page designed the way a
# Japanese company site would read. ja gets a fully native structure; en
# stays international/concise (its native register already is English);
# zh gets fully native Chinese labels too.
SECTION_LABELS = {
    "ja": {
        "about": "プロフィール", "career": "職務経歴", "expertise": "専門分野",
        "languages": "語学",
        "profile_info": "基本情報",
    },
    "en": {
        "about": "About", "career": "Career", "expertise": "Core Expertise",
        "languages": "Languages",
        "profile_info": "Profile Information",
    },
    "zh": {
        "about": "個人簡介", "career": "職務經歷", "expertise": "專業領域",
        "languages": "語言能力",
        "profile_info": "基本資料",
    },
}

PROFILE = {
    "ja": {
        "name_display": "薛 佶姈",
        "name_sub": "Hsueh Chi-Ling",
        "role_title": "事業運営・ブランドサポート",
        "subtitle": ["25年間の実務経験", "小売 × 事業運営 × ブランドサポート"],
        "about": [
            "2011年、輸入タイル代理店に加わりました。会社は主にイタリア製の高級タイルを取り扱っており、日々の運営は夫と私の二人で担っています。夫は主に営業面を担当し、私は行政、人事、購買、物流出荷、在庫管理、経理、そして各部門間の調整など、社内のさまざまな業務を担当しています。",
            "あれから15年が経ち、会社も少しずつ発展し、毎年安定して成長してきました。この間の仕事を通じて、物事を段取りよく進める習慣が身につき、問題が起きても冷静に対処すること、そして細部まで大切にすることを学びました。毎日やるべきことを一つひとつ丁寧にこなせば、会社は自然と安定して前進していくと、私はずっと信じています。",
            "私のこれまでの職務経験はアパレル小売業ではありませんが、家族の影響もあり、以前からファッションや靴が大好きで、ブランド情報やスタイリングにもよく目を向けてきました。貴社が台湾に出店されると知り、この機会をぜひ活かして、異なる業界に挑戦してみたいと強く思っています。",
            "小売店長の仕事と現在の業務には多くの違いがあることは承知していますが、マネジメント、人とのコミュニケーション、商品管理、突発的な状況への対応、そして物事を最後まできちんとやり遂げる姿勢は、根本では共通していると信じています。ゼロから学ぶ意欲もあり、これまで培ってきた経験を新しい仕事に活かしていきたいと考えています。",
            "現在は主に中国語を使用しており、英語と日本語はまだ力を伸ばす必要があります。もし貴社に加わる機会をいただけましたら、時間をかけて学び続け、一日も早くブランドの文化と業務内容に慣れ、チームと共に台湾第一号店を育てていきたいと思います。そして、ブランドの成長にも寄り添っていきたいと考えています。",
        ],
        "career": [
            {"eyebrow": "リテール経験",
             "orgs": [
                 {"name": "LEVI'S", "period": "2000年〜2004年（4年）"},
                 {"name": "KOZIOL", "period": "2005年〜2006年（2年）"},
                 {"name": "francfranc", "period": "2006年〜2008年（2年）"},
                 {"name": "ALBION", "period": "2008年〜2009年（1年）"},
                 {"name": "Brooks Brothers", "period": "2009年〜2010年（1年）"},
             ]},
            {"eyebrow": "事業運営経験", "period": "2011年〜現在", "role": "事業運営",
             "orgs": ["REFIN（台湾総代理店）"]},
        ],
        "expertise": [
            ("事業運営", ["受発注管理", "在庫管理", "購買管理", "物流管理", "総務"]),
            ("リテール", ["接客", "顧客対応", "売場運営", "ブランド体験"]),
            ("デザイン", ["Adobe Illustrator", "Canva", "カタログ制作", "プレゼン資料制作"]),
            ("システム", ["ERP", "在庫管理システム", "Microsoft Office"]),
        ],
        "languages": [("中国語", "母語")],
        "profile_info": [("生年月日", "1982.01.07"), ("学歴", "高等学校卒業"), ("免許", "普通自動車第一種運転免許")],
    },
    "en": {
        "name_display": "Hsueh Chi-Ling",
        "name_sub": "薛佶姈",
        "role_title": "Business Operations Professional",
        "subtitle": ["25 Years of Experience", "Retail × Operations × Brand Support"],
        "about": [
            "In 2011, I joined an import tile distribution company. The company mainly distributes premium Italian tiles, and day-to-day operations have been run jointly by my husband and me — he mainly handles the sales side, while I'm responsible for everything on the internal side: administration, HR, procurement, logistics and shipping, inventory management, accounting, and coordination across departments.",
            "Fifteen years in, the company has grown steadily from its early days to where it is now, with stable growth every year. This work has taught me to keep things organized, to stay calm when problems arise, and to care about every detail. I've always believed that if you take care of what needs doing each day, the company will naturally keep moving forward steadily.",
            "My work experience isn't in apparel retail, but because of my family, I've always loved fashion and shoes, and I regularly follow brand news and styling. Seeing that your company is about to open a store in Taiwan, I'd really like to take this opportunity to challenge myself in a different industry.",
            "I know a retail store manager's job is quite different from what I do now, but I believe management, communicating with people, organizing merchandise, handling the unexpected, and the attitude of seeing things through to completion are, at their core, the same. I'm willing to learn from the ground up and apply what I've built up over the years to this new role.",
            "Right now I mainly work in Chinese, and my English and Japanese still need improvement. But if I have the opportunity to join your company, I'm willing to put in the time to keep learning, so I can get up to speed on the brand's culture and the work as quickly as possible — growing Taiwan's first store together with the team, and growing alongside the brand.",
        ],
        "career": [
            {"eyebrow": "Retail Experience",
             "orgs": [
                 {"name": "LEVI'S", "period": "2000–2004 (4 years)"},
                 {"name": "KOZIOL", "period": "2005–2006 (2 years)"},
                 {"name": "francfranc", "period": "2006–2008 (2 years)"},
                 {"name": "ALBION", "period": "2008–2009 (1 year)"},
                 {"name": "Brooks Brothers", "period": "2009–2010 (1 year)"},
             ]},
            {"eyebrow": "Business Experience", "period": "2011–Present", "role": "Business Operations",
             "orgs": ["REFIN (Taiwan Distributor)"]},
        ],
        "expertise": [
            ("Operations", ["Order Management", "Inventory Control", "Purchasing", "Logistics", "Administration"]),
            ("Retail", ["Customer Service", "Brand Experience", "Visual Merchandising"]),
            ("Design", ["Adobe Illustrator", "Canva", "Catalog Design", "Presentation Design"]),
            ("Systems", ["ERP", "Inventory System", "Microsoft Office"]),
        ],
        "languages": [("Chinese", "Native")],
        "profile_info": [("Date of Birth", "1982.01.07"), ("Education", "High School"), ("License", "Driver's License")],
    },
    "zh": {
        "name_display": "薛佶姈",
        "name_sub": "Hsueh Chi-Ling",
        "role_title": "營運管理專業",
        "subtitle": ["25 年實務經驗", "零售 × 營運 × 品牌支援"],
        "about": [
            "2011年，我加入一間進口磁磚代理公司。公司主要是代理義大利精品磁磚，平時的營運是由我和先生一起負責，先生主要負責業務方面，我則負責公司內部整體營運，並管理約15位員工，工作涵蓋行政、人事、採購、物流出貨、庫存管理、帳務，以及各部門間的溝通協調。",
            "一路走來已經十五年，公司也從剛開始慢慢發展到現在，每年都穩定成長。這些年的工作，讓我習慣把事情安排好，也學會遇到問題時冷靜處理，並且重視每一個細節。我一直認為，只要把每天該做的事情做好，公司自然就會穩定向前。",
            "雖然我的工作經驗不是服飾零售業，但因為家人的關係，我一直很喜歡流行服飾和鞋子，也常常關注品牌資訊和穿搭。看到貴公司即將在台灣展店，我真的很想把握這次機會，挑戰自己到不同的產業發展。",
            "我知道零售店長和現在的工作有很多不同，但我相信管理、人員溝通、商品整理、處理突發狀況，以及把事情做好、做完整的態度，其實是共通的。我也願意從頭開始學習，把過去累積的經驗運用在新的工作上。",
            "目前工作主要使用中文，英文與日文仍持續學習中。雖然目前還無法流利使用，但我希望透過持續學習與實際工作累積經驗，不斷提升自己的語言能力，期許未來能更順利地與日本總部及團隊合作。希望能盡快熟悉品牌文化與工作內容，和團隊一起把台灣第一間店經營好，也希望能陪著品牌一起成長。",
        ],
        "career": [
            {"eyebrow": "零售經驗",
             "orgs": [
                 {"name": "LEVI'S", "period": "2000年～2004年（4年）"},
                 {"name": "KOZIOL", "period": "2005年～2006年（2年）"},
                 {"name": "francfranc", "period": "2006年～2008年（2年）"},
                 {"name": "ALBION", "period": "2008年～2009年（1年）"},
                 {"name": "Brooks Brothers", "period": "2009年～2010年（1年）"},
             ]},
            {"eyebrow": "企業營運經驗", "period": "2011年～現在", "role": "企業營運",
             "orgs": ["REFIN（台灣總代理）"]},
        ],
        "expertise": [
            ("營運", ["訂單管理", "庫存管理", "採購管理", "物流管理", "行政"]),
            ("零售", ["接待", "顧客應對", "賣場營運", "品牌體驗"]),
            ("設計", ["Adobe Illustrator", "Canva", "型錄製作", "簡報製作"]),
            ("系統", ["ERP", "庫存管理系統", "Microsoft Office"]),
        ],
        "languages": [("中文", "母語")],
        "profile_info": [("出生日期", "1982.01.07"), ("學歷", "高中畢業"), ("駕照", "普通汽車駕照")],
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
    return f'''<header class="site-nav">
  <a class="wordmark" href="{home_href}" aria-label="grounds Taiwan"></a>
  <nav class="nav-links">
    <a href="{home_href}" class="{'active' if active_page=='index' else ''}">{t['nav_home']}</a>
  </nav>
  {lang_switch_html(current, active_page)}
</header>'''


def html_shell(lang, active_page, body, extra_head=""):
    t = SITE[lang]
    html_lang = {"ja": "ja", "en": "en", "zh": "zh-Hant"}[lang]
    bp_href = "blueprint.html" if lang == "ja" else f"{lang}/blueprint.html"
    # The only path into the Blueprint document is hidden in plain sight here:
    # "AUG" is a real link (styled identically to the surrounding text, no
    # underline/color/cursor change), "2026" is inert. Nothing should read as
    # a clickable "view the blueprint" prompt anywhere on the page.
    return f'''<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<base href="{BASE_PATH}">
<title>{t['title']}</title>
<meta name="description" content="{t['subtitle']}">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={CSS_VERSION}">
{extra_head}
</head>
<body>
{nav_html(lang, active_page)}
{body}
<footer class="site-footer">
  <p>2026 <a href="{bp_href}" class="stealth-link">AUG</a></p>
</footer>
<script src="assets/js/main.js?v={JS_VERSION}"></script>
</body>
</html>
'''


def index_body(lang):
    profile_section = render_profile_section(lang)
    return f'''<div class="pf-page">
{profile_section}
</div>
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


def render_profile_section(lang):
    p = PROFILE[lang]
    L = SECTION_LABELS[lang]

    about_html = "\n".join(f'      <p>{line}</p>' for line in p["about"])

    career = p["career"]
    career_html = []
    for i, job in enumerate(career):
        orgs = job["orgs"]
        if orgs and isinstance(orgs[0], dict):
            # Each org carries its own employment period (e.g. multiple short
            # retail roles) rather than sharing one period across the node.
            orgs_html = "".join(
                f'<div class="pf-timeline-org-row"><span>{o["name"]}</span><span class="pf-timeline-org-period">{o["period"]}</span></div>'
                for o in orgs
            )
        else:
            orgs_html = "".join(f"<span>{o}</span>" for o in orgs)
        eyebrow_html = f'<p class="pf-timeline-eyebrow">{job["eyebrow"]}</p>' if job.get("eyebrow") else ""
        period_html = f'<p class="pf-timeline-period">{job["period"]}</p>' if job.get("period") else ""
        role_html = f'<p class="pf-timeline-role">{job["role"]}</p>' if job.get("role") else ""
        career_html.append(f'''      <div class="pf-timeline-node">
        {eyebrow_html}
        {period_html}
        {role_html}
        <div class="pf-timeline-orgs">{orgs_html}</div>
      </div>''')
        if i < len(career) - 1:
            career_html.append('      <div class="pf-timeline-arrow" aria-hidden="true">→</div>')
    career_html = "\n".join(career_html)

    expertise_html = "\n".join(f'''      <div class="pf-expertise-col">
        <p class="pf-expertise-title">{name}</p>
        <ul>
{"".join(f"          <li>{i}</li>" for i in items)}
        </ul>
      </div>''' for name, items in p["expertise"])

    lang_html = "".join(
        f'<li><span class="pf-lang-name">{name}</span><span class="pf-lang-level">{level}</span></li>'
        for name, level in p["languages"]
    )

    info_html = "".join(
        f'<li><span class="pf-lang-name">{label}</span><span class="pf-lang-level">{value}</span></li>'
        for label, value in p["profile_info"]
    )

    return f'''  <section class="pf-hero reveal">
    <div class="pf-hero-text">
      <p class="pf-name">{p['name_display']}</p>
      <p class="pf-name-sub">{p['name_sub']}</p>
      <p class="pf-role-title">{p['role_title']}</p>
      <p class="pf-subtitle">{p['subtitle'][0]}</p>
      <p class="pf-subtitle">{p['subtitle'][1]}</p>
    </div>
    <div class="pf-hero-photo">
      <img src="{PROFILE_PHOTO}" alt="{p['name_display']}" loading="eager">
    </div>
  </section>

  <section class="pf-section pf-section-small reveal">
    <p class="pf-section-title">{L['profile_info']}</p>
    <ul class="pf-lang-list">{info_html}</ul>
  </section>

  <section class="pf-section reveal">
    <p class="pf-section-title">{L['about']}</p>
    <div class="pf-about">
{about_html}
    </div>
  </section>

  <section class="pf-section reveal">
    <p class="pf-section-title">{L['career']}</p>
    <div class="pf-timeline">
{career_html}
    </div>
  </section>

  <section class="pf-section reveal">
    <p class="pf-section-title">{L['expertise']}</p>
    <div class="pf-expertise-grid">
{expertise_html}
    </div>
  </section>

  <section class="pf-section reveal">
    <p class="pf-section-title">{L['languages']}</p>
    <ul class="pf-lang-list">{lang_html}</ul>
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
    sections_nav += f'\n    <a href="{bp_href}#leadership">Profile</a>'

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

    leadership_section = f'<div id="leadership" class="pf-page">{render_profile_section(lang)}</div>'

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

/* Editorial profile page (pf-*) styles are defined further below. */

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

.stealth-link, .stealth-link:hover, .stealth-link:visited{
  color: inherit;
  text-decoration: none;
}

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
  .two-col, .oq-grid{ grid-template-columns: 1fr; }
  .nav-links{ display: none; }
}

/* ---------------------------------------------------------------------
   Editorial profile page (pf-*) — international-brand style personal
   introduction (Apple / MUJI / Aesop reference direction). Deliberately
   separate from the Blueprint's serif/editorial chapter styling: light
   sans-serif type, large white space, no shadows, no progress bars.
   --------------------------------------------------------------------- */
:root{ --pf-sans: "Inter", "Noto Sans JP", var(--sans); }

.pf-page{
  max-width: 1080px;
  margin: 0 auto;
  padding: 0 32px 100px;
  font-family: var(--pf-sans);
}
.blueprint-content .pf-page{ max-width: none; padding-left: 0; padding-right: 0; }

.pf-hero{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
  min-height: 72vh;
  padding: 64px 0 32px;
}
.pf-hero-text{ max-width: 420px; }
.pf-name{ font-size: clamp(28px, 3.6vw, 40px); font-weight: 300; margin: 0; letter-spacing: 0.01em; }
.pf-name-sub{ font-size: 15px; color: var(--muted); margin: 4px 0 28px; font-weight: 300; }
.pf-role-title{ font-size: 16px; font-weight: 400; margin: 0 0 24px; }
.pf-subtitle{ font-size: 13px; color: var(--muted); margin: 0 0 4px; letter-spacing: 0.02em; }
.pf-hero-photo{
  width: 34%;
  margin-left: auto;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  background: var(--callout-bg);
}
.pf-hero-photo img{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  display: block;
}
.pf-section{ padding: 56px 0; border-bottom: 1px solid var(--line); }
.pf-section-small{ padding: 32px 0; }
.pf-section-title{
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 32px;
}

.pf-about{ max-width: 640px; }
.pf-about p{ font-size: 15.5px; font-weight: 300; line-height: 1.9; margin: 0 0 16px; }

.pf-timeline{ display: flex; align-items: flex-start; gap: 32px; flex-wrap: wrap; }
.pf-timeline-node{ flex: 1; min-width: 220px; }
.pf-timeline-eyebrow{ font-size: 11px; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 10px; font-weight: 500; }
.pf-timeline-period{ font-size: 13px; color: var(--muted); margin: 0 0 8px; font-weight: 300; }
.pf-timeline-role{ font-size: 17px; font-weight: 400; margin: 0 0 12px; }
.pf-timeline-orgs{ display: flex; flex-direction: column; gap: 4px; }
.pf-timeline-orgs span{ font-size: 14px; color: var(--muted); font-weight: 300; }
.pf-timeline-org-row{ display: flex; justify-content: space-between; gap: 12px; padding: 6px 0; border-bottom: 1px dotted var(--line); font-size: 14px; font-weight: 300; }
.pf-timeline-org-row span:first-child{ color: var(--fg); }
.pf-timeline-org-period{ color: var(--muted); white-space: nowrap; }
.pf-timeline-arrow{ padding-top: 28px; color: var(--muted); font-size: 18px; }

.pf-expertise-grid{
  display: grid;
  grid-template-columns: repeat(4, minmax(0,1fr));
  gap: 40px;
}
.pf-expertise-title{ font-size: 13px; font-weight: 500; margin: 0 0 16px; }
.pf-expertise-col ul{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.pf-expertise-col li{ font-size: 14px; font-weight: 300; color: var(--muted); }

.pf-lang-list{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; max-width: 320px; }
.pf-lang-list li{ display: flex; justify-content: space-between; font-size: 14px; font-weight: 300; }
.pf-lang-name{ color: var(--fg); }
.pf-lang-level{ color: var(--muted); }
.pf-section-small .pf-lang-list li{ font-size: 12.5px; }

@media (max-width: 860px){
  .pf-hero{ grid-template-columns: 1fr; min-height: auto; gap: 40px; padding-top: 40px; }
  .pf-hero-photo{ width: 60%; max-width: 220px; margin: 0 auto; }
  .pf-expertise-grid{ grid-template-columns: repeat(2, minmax(0,1fr)); }
  .pf-timeline{ flex-direction: column; }
  .pf-timeline-arrow{ display: none; }
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

# Content-hash cache-busting: browsers (and LiteSpeed's static-file caching)
# can hold onto assets/css/style.css long past a deploy. Appending a hash of
# the current content forces a fresh URL — and therefore a fresh fetch —
# every time the CSS or JS actually changes, while still caching normally
# when it hasn't.
CSS_VERSION = hashlib.md5(CSS.encode("utf-8")).hexdigest()[:10]
JS_VERSION = hashlib.md5(JS.encode("utf-8")).hexdigest()[:10]


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
