<?php
// 把週報快照（report_shares/<id>.json）輸出成可編輯的 Google 文件。
// 需登入 cookie。實際建文件的是 Apps Script（tools/apps_script/Code.gs 的 wlReportDoc_），
// 它只收快照 id，再自己去讀公開的 api_report.php?id=…，所以外人無法塞任意內容進來。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

// Apps Script「工時報告 Google 文件」部署（和翻譯用的部署分開，互不影響）
$GAS_DOC_URL = 'https://script.google.com/macros/s/AKfycbyV4ZL0FBoivjZ21D_0emkwghZcXE7M6H0MnGtZRzV14rgUNbg47Wc-srJtLIdA5itxnw/exec';

function wl_rd_out($a, $code = 200) {
    http_response_code($code);
    echo json_encode($a, JSON_UNESCAPED_UNICODE);
    exit;
}
function wl_rd_authed() {
    $secretFile = __DIR__ . '/.wl_secret';
    if (!is_file($secretFile)) return false;
    $secret = trim((string)file_get_contents($secretFile));
    if ($secret === '') return false;
    $token = hash_hmac('sha256', 'worklog-ok', $secret);
    return isset($_COOKIE['wl_auth']) && hash_equals($token, (string)$_COOKIE['wl_auth']);
}

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') wl_rd_out(['success' => false, 'error' => 'method'], 405);
if (!wl_rd_authed()) wl_rd_out(['success' => false, 'error' => 'Unauthorized'], 401);

$body = json_decode((string)file_get_contents('php://input'), true);
if (!is_array($body)) $body = [];
$id = strtolower(trim((string)($body['id'] ?? '')));
if (!preg_match('/^[a-f0-9]{32}$/', $id)) wl_rd_out(['success' => false, 'error' => 'bad id'], 400);
if (!is_file(__DIR__ . '/report_shares/' . $id . '.json')) wl_rd_out(['success' => false, 'error' => 'not found'], 404);

$ch = curl_init($GAS_DOC_URL);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode(['action' => 'wlreportdoc', 'id' => $id, 'fresh' => !empty($body['fresh'])]),
    CURLOPT_HTTPHEADER => ['Content-Type: text/plain'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_TIMEOUT => 95,
]);
$res = curl_exec($ch);
$code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);

$j = is_string($res) ? json_decode($res, true) : null;
if (!is_array($j)) {
    // Apps Script 還沒授權時回的是 HTML 錯誤頁，不是 JSON
    wl_rd_out(['success' => false, 'error' => 'Google 文件服務沒有回應（' . $code . '），請稍後再試', 'http' => $code], 502);
}
if (empty($j['ok']) && preg_match('/權限|permission|authoriz/i', (string)($j['error'] ?? ''))) {
    wl_rd_out(['success' => false, 'code' => 'gas_auth', 'error' => 'Google 文件服務還沒授權：請到 Apps Script 編輯器執行一次 wlAuthorizeDocs 並按「允許」'], 502);
}
if (empty($j['ok']) || empty($j['url']) || !preg_match('#^https://docs\.google\.com/document/d/[\w-]+#', (string)$j['url'])) {
    wl_rd_out(['success' => false, 'error' => (string)($j['error'] ?? 'Google 文件產生失敗')], 502);
}
wl_rd_out(['success' => true, 'url' => (string)$j['url'], 'reused' => !empty($j['reused'])]);
