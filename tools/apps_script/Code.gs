/**
 * ============================================================
 *  grounds Taiwan 開店作戰中心 — Google Sheets + Gemini 橋樑
 * ============================================================
 *  用途：
 *    1) 讀取／寫入「開店作戰中心」活資料（筆記、決策紀錄、卡點、
 *       日本待決策、台灣進度、資金、會議決議）
 *    2) 代理 Gemini AI 對話（每一項旁邊的聊天框）
 *
 *  安裝前（重要，先做這兩步）：
 *    ① 在「專案設定 → 指令碼屬性」加入：
 *         GEMINI_API_KEY   ← 你的 Gemini API Key（必填，聊天用）
 *         ACCESS_TOKEN     ← 你自訂的一串密碼（選填；設了之後網站
 *                            每次呼叫都要帶同一個，避免被人亂寫）
 *         GEMINI_MODEL     ← 選填，預設 gemini-2.5-flash
 *    ② 部署： 部署 → 新的部署 → 網路應用程式
 *         執行身分 = 我
 *         存取權   = 所有人
 *       部署後把網址（…/exec 結尾）給 Dashboard 用。
 *
 *  這份檔案不含任何金鑰，可以安心放進 repo。
 * ============================================================
 */

var PROPS = PropertiesService.getScriptProperties();

// 掛在試算表上的話用 getActiveSpreadsheet()；獨立專案則用這張試算表 ID
var DEFAULT_SHEET_ID = '1ky5KDrxYV0pPaFVIU9RQRgTM4xt7r_WhHigR8dhXWZ0';

function ss() {
  var active = spread_();
  if (active) return active;
  var id = PROPS.getProperty('SHEET_ID') || DEFAULT_SHEET_ID;
  return SpreadsheetApp.openById(id);
}

function spread_() {
  try { return SpreadsheetApp.getActiveSpreadsheet(); } catch (e) { return null; }
}

// 用「頁籤名稱」當 key；順序就是欄位順序（時間列固定最後一格）
var COLUMNS = {
  Note:          ['item', 'type', 'note', 'author', 'ts'],
  DecisionLog:   ['date', 'topic', 'decision', 'followup', 'owner', 'ts'],
  IssueLog:      ['problem', 'blockedBy', 'waitingOn', 'impact', 'deadline', 'ts'],
  JapanWaiting:  ['item', 'status', 'deadline', 'note', 'ts'],
  TaiwanProgress:['item', 'pct', 'note', 'ts'],
  Funding:        ['item', 'amount', 'type', 'status', 'note', 'ts'],
  Meetings:       ['date', 'agenda', 'decisions', 'followup', 'ts']
};

// 頁籤顯示用的中文表頭（程式一律依 COLUMNS 的順序讀寫）
var HEADERS = {
  Note:           ['項目', '類型', '筆記', '作者', '時間'],
  DecisionLog:    ['日期', '議題', '日本決定', '台灣後續', '負責人', '時間'],
  IssueLog:       ['問題', '誰卡住', '等誰', '影響', '截止', '時間'],
  JapanWaiting:   ['項目', '狀態', 'Deadline', '備註', '時間'],
  TaiwanProgress: ['項目', '進度%', '備註', '時間'],
  Funding:        ['項目', '金額', '類型', '狀態', '備註', '時間'],
  Meetings:       ['日期', '議程', '決議', '後續', '時間']
};

/* ------------------------------------------------------------
 *  進入點
 * ---------------------------------------------------------- */
function doGet(e) {
  var p = (e && e.parameter) || {};
  return handle(p, 'GET');
}

function doPost(e) {
  var p = (e && e.parameter) || {};
  return handle(p, 'POST');
}

function handle(p, method) {
  var action = p.action || '';
  try {
    if (!authorized(p)) return jso({ ok: false, error: 'Unauthorized' });

    if (action === 'read' && method === 'GET') {
      return jso({ ok: true, data: readAll() });
    }
    if (action === 'row') {
      var tab = p.tab;
      if (!COLUMNS[tab]) return jso({ ok: false, error: 'bad tab: ' + tab });
      var values = COLUMNS[tab].map(function (c) { return p[c] || ''; });
      appendRow(tab, values);
      return jso({ ok: true, tab: tab });
    }
    if (action === 'updatePct') {
      setPct(p.item, p.pct, p.note || '');
      return jso({ ok: true, item: p.item, pct: p.pct });
    }
    if (action === 'chat') {
      return jso(chatP(p));
    }
    return jso({ ok: false, error: 'unknown action: ' + action });
  } catch (err) {
    return jso({ ok: false, error: String(err) });
  }
}

/* ------------------------------------------------------------
 *  權限（選填）
 * ---------------------------------------------------------- */
function authorized(p) {
  var tok = PROPS.getProperty('ACCESS_TOKEN');
  if (!tok) return true;              // 沒設令牌 → 放行
  return p.auth === tok;
}

/* ------------------------------------------------------------
 *  讀取全部頁籤
 * ---------------------------------------------------------- */
function readAll() {
  var out = {};
  Object.keys(COLUMNS).forEach(function (tab) {
    out[tab] = getRows(tab);
  });
  return out;
}

function getRows(tab) {
  var sheet = getSheet(tab);
  if (!sheet) return [];
  var last = sheet.getLastRow();
  if (last < 2) return [];
  var n = COLUMNS[tab].length;
  var data = sheet.getRange(2, 1, last - 1, n).getValues();
  return data.map(function (r) {
    var o = {};
    COLUMNS[tab].forEach(function (c, i) { o[c] = r[i]; });
    return o;
  }).filter(function (o) {
    var key = COLUMNS[tab][0];
    return String(o[key] || '').trim().length > 0;
  });
}

/* ------------------------------------------------------------
 *  寫入
 * ---------------------------------------------------------- */
function appendRow(tab, values) {
  var sheet = getSheet(tab);
  values[COLUMNS[tab].indexOf('ts')] = nowStr();
  sheet.appendRow(values);
}

function setPct(item, pct, note) {
  var sheet = getSheet('TaiwanProgress');
  var rows = getRows('TaiwanProgress');
  var lineRow = -1;
  for (var i = 0; i < rows.length; i++) {
    if (rows[i].item === item) { lineRow = i + 2; break; }
  }
  if (lineRow > 0) {
    sheet.getRange(lineRow, COLUMNS['TaiwanProgress'].indexOf('pct') + 1)
      .setValue(Number(pct));
    if (note) sheet.getRange(lineRow, COLUMNS['TaiwanProgress'].indexOf('note') + 1).setValue(note);
  } else {
    appendRow('TaiwanProgress', [item, Number(pct), note || '', nowStr()]);
  }
}

/* ------------------------------------------------------------
 *  Gemini 對話（Key 只在這裡用，不進前端）
 * ---------------------------------------------------------- */
function chatP(p) {
  var key = PROPS.getProperty('GEMINI_API_KEY');
  if (!key) return { ok: false, error: 'GEMINI_API_KEY 尚未設定' };

  var model = PROPS.getProperty('GEMINI_MODEL') || 'gemini-2.5-flash';
  var item = p.item || '';
  var question = p.q || '';
  var history = p.history || '';

  var sys = '你是「grounds Taiwan 開店作戰中心」的工作助理。' +
    '使用者是台灣端負責人，這是一家日本品牌在台灣的第一家 100% 子公司+門市。' +
    '你只能依據下面提供的「專案現況資料」和「該項目的筆記」回答，不要編造數字或決策。' +
    '資料不足時，明講還缺什麼、並建議這些是否要跟日本開會確認。' +
    '回答請用繁體中文，簡短、直接、可執行。';

  var prompt =
    '【專案現況摘要】\n' + summarizeContext(item) +
    '\n\n【項目筆記】\n' + notesFor(item) +
    '\n\n【之前的對話片段】\n' + (history || '（無）') +
    '\n\n【使用者問題】\n' + (question || '目前這個項目進展到哪、下一步該做什麼？');

  var reply = callGemini(key, model, sys, prompt);
  return { ok: true, reply: reply };
}

function callGemini(key, model, sys, prompt) {
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' +
    encodeURIComponent(model) + ':generateContent?key=' + encodeURIComponent(key);
  var payload = {
    system_instruction: { parts: [{ text: sys }] },
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0.3, maxOutputTokens: 1024 }
  };
  var res = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
  var code = res.getResponseCode();
  var txt = res.getContentText();
  if (code !== 200) {
    return '⚠️ Gemini 回應錯誤 ' + code + '\n' + txt.slice(0, 300);
  }
  try {
    var json = JSON.parse(txt);
    return json.candidates[0].content.parts
      .map(function (x) { return x.text || ''; })
      .join('')
      .replace(/\n{3,}/g, '\n\n');
  } catch (e) {
    return '⚠️ 無法解析回覆';
  }
}

/* ------------------------------------------------------------
 *  輔助
 * ---------------------------------------------------------- */
function notesFor(item) {
  if (!item) return '（未指定項目）';
  var rows = getRows('Note').filter(function (r) { return r.item === item; });
  if (!rows.length) return '（尚無筆記，可先新增。例如：今天跟日本開了會、簽了什麼、數字多少。）';
  return rows.map(function (r) {
    return '[' + r.ts + '] ' + (r.note || '') + (r.author ? ' — ' + r.author : '');
  }).join('\n');
}

function summarizeContext(item) {
  var lines = [];
  var prog = getRows('TaiwanProgress');
  lines.push('台灣進行中：' + (prog.length ? prog.map(function (r) {
    return r.item + ' ' + r.pct + '%';
  }).join('、') : '（暫無）'));
  var jp = getRows('JapanWaiting');
  lines.push('日本待決策：' + (jp.length ? jp.map(function (r) {
    return r.item + (r.status ? '[' + r.status + ']' : '') + (r.deadline ? '(截止' + r.deadline + ')' : '');
  }).join('、') : '（暫無）'));
  var iss = getRows('IssueLog');
  lines.push('卡點：' + (iss.length ? iss.map(function (r) {
    return r.problem + '（等' + (r.waitingOn || '?') + '）';
  }).join('；') : '（暫無）'));
  var dec = getRows('DecisionLog');
  lines.push('近期決議：' + (dec.length ? dec.map(function (r) {
    return r.date + ' ' + r.topic + '→' + r.decision;
  }).join('；') : '（暫無）'));
  return lines.join('\n').slice(0, 3000);
}

function getSheet(tab) {
  var s = ss().getSheetByName(tab);
  if (!s) {
    s = ss().insertSheet(tab);
  }
  if (s.getLastRow() === 0) {
    s.getRange(1, 1, 1, COLUMNS[tab].length).setValues([HEADERS[tab]]);
  }
  return s;
}

function nowStr() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy/MM/dd HH:mm');
}

/* ------------------------------------------------------------
 *  輸出 JSON（跨網域可讀）
 * ---------------------------------------------------------- */
function jso(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ------------------------------------------------------------
 *  （選用）直接在試算表裡手動生頁籤：
 *   執行一次 setupTabs() 之後，七個頁籤與表頭就會出現。
 * ---------------------------------------------------------- */
function setupTabs() {
  Object.keys(COLUMNS).forEach(function (tab) {
    getSheet(tab);
  });
  return 'done';
}