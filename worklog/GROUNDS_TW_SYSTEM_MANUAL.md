# grounds Taiwan 專案系統架構與功能規格說明書

本文件詳細記載 **grounds Taiwan** 台灣展店籌備與總部協作系統（Worklog & Store Intelligence System）之程式規格、資料結構、各大房仲平台解析演算法與操作手冊。

---

## 1. 系統架構總覽 (System Architecture)

- **前端技術**：原生 HTML5 + 現代 CSS3（自適應響應式佈局、觸覺點擊縮放動畫、CSS 關鍵影格動畫） + 原生非同步 JavaScript（ES6+、Fetch API、FileReader API）。
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

### 2.1 檔案與照片/PDF夾帶系統 (Multi-Attachment Engine)
系統於**工作動態發布區**以及**台灣端/日本端每一則留言對話框**中，全面配備檔案夾帶功能：
- **格式支援**：支援各類圖片（`image/*`，如 PNG、JPEG、WebP）與文件檔案（`.pdf`）。
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

### 2.5 店面卡片預設收折與防誤觸機制 (Compact MAP Cards)
- **高度緊湊卡片**：MAP 視圖左側店面卡片預設為緊湊排版（高度約 75px），一眼即可瀏覽 6~8 間店面。
  - 左側縮圖附有照片張數膠囊（如 `📷 3`）。
  - 清楚列出刊登月租、坪數、每坪單價與真實月成本。
- **防誤觸比較勾選**：勾選「比較」Checkbox 時加入 `event.stopPropagation()`，僅切換比較清單，絕不誤開詳情彈窗。
- **行內展開 (`[展開 ▾]`)**：點擊卡片右上方的「展開」鈕，可在清單內就地展開詳細規格、照片縮圖列與商圈優缺點；點擊 `[詳細 ↗]` 或雙擊卡片才開啟全螢幕詳情彈窗。
- **點擊空白處關閉**：點擊彈窗外暗色遮罩區塊即可輕鬆關閉浮動視窗。

---

### 2.6 店面條件比較表動態名次邏輯 (Comparison Table Badges)
比較表依照選取店面總數動態呈現最符合商業直覺的象徵徽章：
- **僅比較 2 間店面時**：
  - 條件優勢者標示金色皇冠 **`👑 No.1`**（或 **`👑 最佳`**）。
  - 次者**不顯示紅2**，突顯勝出者優勢指標。
- **比較 3 間以上店面時**：
  - 第 1 名標示 **`🥇 金1位`**（中文為 **`🥇 金1`**）。
  - 第 2 名標示 **`🥈 紅2位`**（中文為 **`🥈 紅2`**）。

---

### 2.7 地圖點選連動與雙擊開啟 (Map Interaction)
- **單擊地圖 Marker**：左側候選店面清單自動平滑捲動到該店面卡片，並加上藍色高亮外框（`.map-focused`）。
- **雙擊地圖 Marker**：直接開啟該店面的浮動詳細視窗。

---

### 2.8 美觀刪除確認浮動視窗 (Delete Confirmation Modal)
- 動態與店面的刪除全面揚棄陽春的 `prompt()`，統一改用 `#delete-confirm-modal` 浮動視窗。
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
  data: string;             // Base64 Data URL
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

- [x] **附件夾帶**：工作動態發布框與留言回覆框皆可順暢夾帶照片與 PDF，照片支援點擊燈箱放大，PDF 支援下載。
- [x] **工時預設**：發布工時預設值成功調整為 `0.5`。
- [x] **多連結解析**：一次貼入 1~5 個網址均可正確辨識，內文 URL 成功轉化為 `[🏢 案名](連結)`，卡片預覽完整並列。
- [x] **自訂條件管理**：點擊「條件」按鈕開啟浮動視窗，支援自訂標籤之新增與刪除，無原生彈窗。
- [x] **店面詳細彈窗**：
  - 數值全面四捨五入整數化，無任何多餘小數點。
  - 大圖配備左右箭頭與張數計數器，切換流暢。
  - 重複店名自動隱藏。
  - 配備 Google Maps 直達連結。
- [x] **緊湊店面清單**：
  - 卡片高度收折至約 75px，首頁一屏可瀏覽多間店面。
  - 比較 Checkbox 加入 `stopPropagation()` 杜絕誤觸開啟彈窗。
  - 支援 `[展開 ▾]` 就地檢視照片與規格。
  - 點擊彈窗外空白暗色區域可關閉彈窗。
- [x] **動態比較表名次**：
  - 2 間店面比較時：勝出者標示 `👑 No.1`（或 `👑 最佳`），次者不標示紅2。
  - 3 間以上店面比較時：標示 `🥇 金1位` 與 `🥈 紅2位`。
- [x] **地圖雙向連動**：
  - 單擊地圖 Marker：左側店面卡片平滑滾動至可視區域並高亮藍框。
  - 雙擊地圖 Marker：直接呼叫並開啟該店面之詳細浮動視窗。
- [x] **美觀刪除視窗**：刪除動態與店面皆使用專屬浮動視窗輸入存證原因。
- [x] **按鈕觸覺縮放**：全站所有按鈕具備點擊回饋動畫。
