# grounds Taiwan 專案系統架構與功能規格說明書

本文件詳細記載 **grounds Taiwan** 台灣展店籌備與總部協作系統（Worklog & Store Intelligence System）之程式規格、資料結構、各大房仲平台解析演算法與操作手冊。

---

## 1. 系統架構總覽 (System Architecture)

- **前端技術**：原生 HTML5 + 現代 CSS3（自適應響應式佈局、觸覺點擊縮放動畫、CSS 關鍵影格動畫） + 原生非同步 JavaScript（ES6+、Fetch API、FileReader API、Canvas 智慧壓縮）。
- **圖資整合**：Leaflet.js + OpenStreetMap 開源圖資，即時標註台北市中山區候選門市定位，支援單點雙向連動高亮與雙擊直開詳情。
- **後端服務**：
  - cPanel (LiteSpeed / Cloudflare CDN 邊緣快取)。
  - `worklog/translate.php`：伺服器端中日雙向自然語言翻譯代理服務。
  - `worklog/api_scrape.php`：**全平台房仲網址即時爬蟲解析引擎**（支援 樂屋網、永慶房屋、信義房屋、591 房屋交易、住商不動產、中信房屋、台灣房屋及各大房仲網址）。
  - `worklog/api_591.php`：向後相容包裝層，自動重定向/引用 `api_scrape.php`。
- **持續整合與部署 (CI/CD)**：GitHub Actions FTP 自動化工作流程，推送到 `main` 分支即自動同步至主機目錄。
- **存取網址**：[`https://bigt.cc/Grounds_TW/worklog/index.html`](https://bigt.cc/Grounds_TW/worklog/index.html)

---

## 2. 核心功能規格詳細說明

### 2.1 檔案與照片/PDF夾帶系統 (Multi-Attachment Engine & Canvas Compression)
系統於**工作動態發布區**以及**台灣端/日本端每一則留言對話框**中，全面配備檔案夾帶功能：
- **格式支援**：支援各類圖片（`image/*`，如 PNG、JPEG、WebP）與文件檔案（`.pdf`）。
- **相片智慧 Canvas 壓縮**：內建 `compressImageFile` 輔助函式，自動將高解析度手機相片於前端等比例壓縮至 1200px 內並轉為高品質 JPEG（~60KB），杜絕圖片過大爆掉瀏覽器 `localStorage` 限制。
- **安全本機狀態持久化 (`saveAppState`)**：加入配額溢出自我保護機制，當本機儲存空間不足時自動剔除冗餘暫存 Base64，確保動態發布與店面新增 100% 成功，絕不中斷。
- **即時預覽 Chip**：選擇檔案後，輸入框上方立即浮現預覽膠囊（`🖼️ 檔名` 或 `📄 檔名`），附有 `×` 快捷移除鈕。
- **發布呈現**：
  - **圖片檔案**：於動態或對話中以高質感縮圖呈現，點擊可開啟**高畫質圖片燈箱 (Lightbox Modal)** 放大檢視。
  - **PDF 檔案**：呈現精美文件膠囊按鈕，點擊即可一鍵下載或在瀏覽器新分頁中開啟閱讀。

---

### 2.2 預設工時 0.5h 與多連結一次貼入辨識 (Multi-Link Intelligent Recognition)
- **預設投入工時**：由原本 1.5h 調降為最貼近日常零碎溝通與回報的 **`0.5h`**。
- **一次貼入 1~5 個房仲網址**：
  - 支援在發布框中一次貼入多個網址（包含 591、樂屋網、永慶房屋、信義房屋等）。
  - **內文超連結案名美化**：系統自動解析所有連結，並將內文中生硬落長的 URL 自動置換為優雅的物件案名超連結（例如：`🏢 條通商圈店面（安家京漾）`）。
  - **多物件卡片並列**：動態卡片下方自動並列呈現所有被辨識之店面預覽卡片，點擊即可開啟詳細評估浮動視窗。

---

### 2.3 分類條件與工作標籤浮動管理視窗 (Custom Tag Manager Modal)
- **全面移除瀏覽器原生彈窗 (`prompt`)**，改為專業設計的 `#tag-manager-modal` 浮動視窗。
- **標籤清單管理**：視覺化呈現所有現有條件標籤膠囊，點擊紅色 `×` 即可直接移除不再適用的標籤。
- **新增條件**：提供獨立文字輸入框，輸入後按 Enter 或點擊「新增條件」即可即時新增並自動儲存至 `localStorage`。

---

### 2.4 店面詳細資料浮動視窗精緻化 (Store Detail Modal Refinements)
1. **數值全數四捨五入整數化 (`Math.round`)**：
   - 月租（萬）、真實成本（元）、使用坪數（坪）、平米（㎡）、每坪單價（元/坪）、每平米單價（元/㎡）、押金（萬）全面以整數呈現，徹底消除 `.0` 或小數點零碎感。
2. **照片左右滑動/切換按鈕 (`‹` 與 `›`) 與照片計數器**：
   - 大圖主視覺兩側配備左右導覽按鈕，點擊即可於所有照片間無縫輪播。
   - 右下角常駐照片計數器（如 `1 / 6`），掌握物件照片總量。
3. **重複店名智慧去重**：
   - 若日文店面標題與中文標題完全相同時，系統自動隱藏重複的副標題，避免視覺干擾。
4. **Google Maps 地圖導航連結**：
   - 地址旁新增 Google 地圖專屬圖示按鈕，點擊即在新分頁以 Google Maps 定位該物件精準地址。

---

### 2.5 店面卡片防折字橫向排版與雙色高亮 (Anti-Wrapping MAP Cards & Color Highlights)
- **欄寬擴展至 530px**：MAP 視圖左側店面欄寬調整為 530px，確保卡片內部所有標籤、核選方塊與案名並列展開，徹底杜絕直式折字問題。
- **防擠壓標籤與水平核取膠囊**：
  - **「比較」核取方塊**：採用 `.store-compare-chk-pill`，具備 `white-space: nowrap !important; flex-shrink: 0 !important;`，核選方塊與「比較」字樣嚴格保持水平一行，絕不垂直折成兩行。
  - **狀態標籤**：`.store-tag`（房仲推薦、重點候選等）設定強制 `white-space: nowrap !important; flex-shrink: 0 !important;`，絕不逐字垂直折行。
  - **案名彈性截斷**：`.store-compact-title` 設定 `flex: 1; min-width: 0`，僅在極端窄螢幕時於案名尾端顯示 `...`，絕不壓擠狀態標籤與比較按鈕。
- **重點價格與坪數不同顏色高亮顯示**：
  - **租金價格（月租）**：採用**鮮明珊瑚/玫瑰紅**高亮徽章（`.metric-pill.metric-price`，背景 `#fee2e2`、文字 `#b91c1c`），一眼掌握預算。
  - **使用面積（坪數）**：採用**清新翡翠/青綠色**高亮徽章（`.metric-pill.metric-area`，背景 `#ccfbf1`、文字 `#0f766e`），與價格形成高對比色彩分流，雙重關鍵指標互不混淆。
  - **單價與實月成本**：以精緻灰藍與琥珀金膠囊襯托，維持版面專業洗鍊。
- **防誤觸比較勾選**：勾選「比較」Checkbox 時加入 `event.stopPropagation()`，僅切換比較清單，絕不誤開詳情彈窗。
- **行內展開 (`[展開 ▾]`)**：點擊卡片右上方的「展開」鈕，可在清單內就地展開詳細規格、照片縮圖列與商圈優缺點；點擊 `[詳細 ↗]` 或雙擊卡片才開啟全螢幕詳情彈窗。
- **點擊空白處關閉**：點擊彈窗外暗色遮罩區塊即可輕鬆關閉浮動視窗。

---

### 2.6 店面條件比較表動態名次邏輯 (Comparison Table Badges)
比較表依照選取店面總數動態呈現最符合商業直覺的象徵徽章，文字嚴格採用純淨的 **`No.1`** 與 **`No.2`**（絕不出現生硬的「金1」或「紅2」中文字樣）：
- **指標排序商業邏輯**：
  - **租金、單價、真實月成本**：採用**遞增排序（越低越好）**，低租金為第 1 順位（高房租不是優點，高房租者不給獎勵徽章）。
  - **使用面積、裝潢免租期**：採用**遞減排序（越高越好）**，大坪數與長免租期為第 1 順位。
- **僅比較 2 間店面時**：
  - 條件優勢者標示金色皇冠 **`👑 No.1`**。
  - 次者**不顯示任何名次徽章**（高房租為劣勢，不予標註）。
- **比較 3 間以上店面時**：
  - 第 1 名標示金色徽章 **`No.1`**。
  - 第 2 名標示紅色徽章 **`No.2`**。
- **圖例與空狀態純淨化**：
  - 圖例說明顯示：`順位表記：<span class="rank-badge rank-gold">No.1</span> 第一順位 ｜ <span class="rank-badge rank-red">No.2</span> 第二順位`。
  - 數值全面四捨五入整數化，日幣換算、平米（㎡）換算一應俱全。

---

### 2.7 地圖點選連動與雙擊開啟 (Map Interaction)
- **單擊地圖 Marker**：左側候選店面清單自動平滑捲動到該店面卡片，並加上藍色高亮外框（`.map-focused`）。
- **雙擊地圖 Marker**：直接開啟該店面的浮動詳細視窗。

---

### 2.8 美觀刪除確認浮動視窗與全面零原生 Alert (Floating Modals & Zero Native Alerts)
- **全站零原生 `alert()` / `confirm()`**：原有的 4 處原生 `alert()`（動態為空、人員姓名為空、唯一成員不可刪除、發布錯誤）全數由精美非阻塞通知 `showToast` 或專屬浮動視窗取代。
- **專屬刪除存證視窗**：動態與店面的刪除全面揚棄陽春的 `prompt()`，統一改用 `#delete-confirm-modal` 浮動視窗。
- 顯示警示圖示、項目摘要，並提供預設存證原因輸入框（動態預設「紀錄調整」、店面預設「不符展店需求」），確認後才執行刪除並將稽核存證寫入審計日誌。

---

### 2.9 全站按鈕觸覺縮放動畫 (Tactile Button Feedback)
- 全站所有按鈕（發布、送出、切換分頁、展開、操作按鈕等）點擊時皆具備 `:active { transform: scale(0.94) }` 物理回饋微動畫，提供原生 App 般精緻的操作手感。

---

## 3. 資料結構定義 (Data Model)

```typescript
interface StoreItem {
  id: string;               // 物件編號，如 "rakuya-034d4c34943093e"、"591-21939969"
  platform?: string;        // 來源平台
  title: string;            // 中文標題
  titleJa?: string;         // 日文標題
  address: string;          // 詳細地址
  lat: number;              // 緯度
  lng: number;              // 經度
  rent: number;             // 刊登月租 (TWD 整數)
  area: number;             // 使用面積 (坪 整數)
  deposit: number;          // 押金 (TWD 整數)
  freeRent: string;         // 免租期，如 "1 個月"
  realCost: number;         // 真實月成本 (含扣繳稅款10%與健保補充保費2.11% 整數)
  floor?: string;           // 樓層資訊
  canRegister: boolean;     // 是否可設立營業登記
  canInvoice: boolean;      // 是否具備開立統一發票資格
  fireSafety: boolean;      // 消防合格
  pros: string;             // 商圈優點
  prosJa?: string;          // 商圈優點日文
  cons: string;             // 考量與風險
  consJa?: string;          // 考量與風險日文
  images: string[];         // 照片連結清單
  activeImgIdx?: number;    // 當前主照片索引
  sourceType?: string;      // 來源識別
  url?: string;             // 原始房仲網頁
}

interface PostItem {
  id: number;               // 唯一時間戳記 ID
  author: string;           // 發布人
  date: string;             // 發布時間 (YYYY/MM/DD HH:mm)
  hours: number;            // 投入工時 (預設 0.5)
  tag: string;              // 條件標籤
  zh: string;               // 繁體中文內文 (URL 自動替換為案名超連結)
  ja: string;               // 日文內文
  propId?: string;          // 首個關聯店面 ID
  propIds?: string[];       // 所有被辨識之店面 ID 清單
  attachment?: Attachment;  // 附件 (圖片或 PDF)
  comments: CommentItem[];  // 回覆討論串
}

interface CommentItem {
  author: string;           // 留言者
  date: string;             // 留言時間
  zh: string;               // 中文留言
  ja: string;               // 日文留言
  attachment?: Attachment;  // 留言附件 (圖片或 PDF)
}

interface Attachment {
  type: 'image' | 'pdf';    // 附件類型
  name: string;             // 檔案名稱
  data: string;             // Base64 Data URL (經 Canvas 壓縮至 ~60KB)
}

interface AuditLogItem {
  id: string | number;      // 被刪除項目 ID
  type: string;             // "工作動態" 或 "店面物件"
  title: string;            // 標題摘要
  reason: string;           // 刪除存證原因
  deletedBy: string;        // 執行人
  deletedAt: string;        // 刪除時間
}
```

---

## 4. 驗證與測試清單

- [x] **店面卡片排版與防折疊**：
  - MAP 左側欄寬擴大至 530px。
  - `.store-tag`（房仲推薦、重點候選等）強制不折行，絕無直式文字。
  - `.store-compare-chk-pill` 強制水平並列，方塊與「比較」字樣絕不折成兩行。
  - 案名超長時以 `...` 平滑截斷，不壓迫標籤。
- [x] **重點價格與坪數不同顏色高亮**：
  - 刊登月租以鮮明珊瑚/玫瑰紅徽章高亮標示。
  - 使用坪數以清新翡翠/青綠色徽章高亮標示（與價格形成截然不同的雙色對比）。
  - 單價與真實月成本採灰藍與琥珀色襯托。
- [x] **比較表動態名次與純淨 No.1 / No.2**：
  - 徹底移除「金1」、「紅2」字樣，純淨採用金色 `No.1` 與紅色 `No.2`。
  - 2 間店面比較時：優勢者標示 `👑 No.1`，高房租等劣勢者不顯示任何徽章。
  - 3 間以上店面比較時：第 1 名金色 `No.1`，第 2 名紅色 `No.2`。
  - 租金/單價/真實成本越低越好（低者為 No.1），坪數/免租期越高越好。
- [x] **全面移除原生彈窗**：
  - 原生 `alert()` 數量為 0。
  - 發布狀態、空白驗證等全數改為溫和浮動 Toast 或專屬彈窗。
- [x] **圖片智慧壓縮與安全持久化**：
  - 上傳相片自動經 Canvas 等比縮放至 1200px 內（~60KB）。
  - `saveAppState()` 具備自我修復機制，防止 `localStorage` 超額報錯。
