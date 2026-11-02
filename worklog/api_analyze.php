<?php
// 店面優缺點分析：讀 591 等刊登頁的全文，請 Claude 依內容寫優缺點，只填空白欄位。
// 金鑰放在伺服器上的 .wl_anthropic_key（隱藏檔，.htaccess 擋掉、不進 repo）。gate.php 已要求登入 cookie。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
require_once __DIR__ . '/lib_fetch.php';
require_once __DIR__ . '/lib_overrides.php';

function out($a, $code = 200) { http_response_code($code); echo json_encode($a, JSON_UNESCAPED_UNICODE); exit; }

if (!function_exists('wl_call_claude')) {
    function wl_call_claude($key, $system, $user) {
        $ch = curl_init('https://api.anthropic.com/v1/messages');
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 75,
            CURLOPT_HTTPHEADER => ['content-type: application/json', 'anthropic-version: 2023-06-01', 'x-api-key: ' . $key],
            CURLOPT_POSTFIELDS => json_encode([
                'model' => 'claude-sonnet-5-5',
                'max_tokens' => 2000,
                'system' => $system,
                'messages' => [['role' => 'user', 'content' => $user]],
            ], JSON_UNESCAPED_UNICODE),
        ]);
        $body = curl_exec($ch);
        $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        if ($body === false) return [false, 'network ' . $err];
        $j = json_decode($body, true);
        if ($code !== 200 || !is_array($j)) return [false, 'api ' . $code . ' ' . mb_substr((string)($j['error']['message'] ?? ''), 0, 120)];
        $text = '';
        foreach (($j['content'] ?? []) as $blk) { if (($blk['type'] ?? '') === 'text') $text .= $blk['text']; }
        return [true, $text];
    }
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(['success' => false, 'error' => 'Method'], 405);
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$id = (string)($in['id'] ?? '');
if (!preg_match('/^[\w.-]{1,80}$/', $id)) out(['success' => false, 'error' => 'bad id'], 400);

$keyFile = __DIR__ . '/.wl_anthropic_key';
$key = is_readable($keyFile) ? trim((string)file_get_contents($keyFile)) : '';
if ($key === '') out(['success' => false, 'error' => 'no_key']);

$data = json_decode(preg_replace('/^\xEF\xBB\xBF/', '', (string)@file_get_contents(__DIR__ . '/grounds_data.json')), true);
$ov = wl_ov_load();
$store = null; $others = [];
foreach (($data['stores'] ?? []) as $s) {
    if (!is_array($s) || !isset($s['id'])) continue;
    $s = wl_ov_apply($s, $ov);
    if ($s['id'] === $id) { $store = $s; continue; }
    if ((float)($s['rent'] ?? 0) > 0 && (float)($s['area'] ?? 0) > 0) $others[] = $s;
}
if (!$store) out(['success' => false, 'error' => 'unknown store'], 404);
$needP = trim((string)($store['pros'] ?? '')) === '';
$needC = trim((string)($store['cons'] ?? '')) === '';
if (!$needP && !$needC) out(['success' => true, 'skipped' => true]);
if ((float)($store['rent'] ?? 0) <= 0 || (float)($store['area'] ?? 0) <= 0) out(['success' => false, 'error' => 'no_numbers']);

$url = (string)($store['url'] ?? '');
if (!preg_match('#^https?://#i', $url)) out(['success' => false, 'error' => 'no_url']);
$f = wl_http_get($url);
if (empty($f['ok']) || (int)$f['code'] !== 200) out(['success' => false, 'error' => 'fetch ' . ($f['code'] ?? '') . ' ' . ($f['error'] ?? '')]);
$html = (string)$f['body'];
$text = preg_replace(['#<script.*?</script>#is', '#<style.*?</style>#is', '#<[^>]+>#'], ' ', $html);
$text = trim(preg_replace('/\s+/u', ' ', html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8')));
if (mb_strlen($text) < 200) out(['success' => false, 'error' => 'empty_page']);
$text = mb_substr($text, 0, 7000);

$unit = function ($s) { return round((float)$s['rent'] / (float)$s['area']); };
$facts = [
    '標題' => $store['title'] ?? '', '地址' => $store['address'] ?? '', '月租' => (int)$store['rent'], '坪數' => (float)$store['area'],
    '每坪' => $unit($store), '押金' => $store['deposit'] ?? null, '押金文字' => $store['depositText'] ?? null, '免租期' => $store['freeRent'] ?? null,
    '可營業登記' => $store['canRegister'] ?? null, '可開發票' => $store['canInvoice'] ?? null,
];
$cmp = [];
foreach ($others as $o) { $cmp[] = ($o['title'] ?? '') . '｜' . ($o['address'] ?? '') . '｜月租' . (int)$o['rent'] . '｜' . (float)$o['area'] . '坪｜每坪' . $unit($o); }

$system = "你在協助日本品牌 grounds 在台北找第一家店。使用者是台灣端負責人，要依你的分析決定店面取捨，所以內容必須可靠。\n"
  . "規則：\n"
  . "1. 只寫「刊登頁文字」或「已知資料」裡有的事實。推論要在句尾標「（推論）」。\n"
  . "2. 不可編造人流、客群、鄰居品牌、行情、距離。刊登沒有的，就列成「刊登沒寫，需向仲介確認」。\n"
  . "3. 刊登自己互相矛盾，或與已知資料不一致（租金、押金、坪數等），一定要指出。\n"
  . "4. 與其他候選比較時，只能用我給的候選數字。\n"
  . "5. 優點 3 到 5 點、缺點 4 到 6 點，每點一到兩句，要具體，不要重講月租坪數這種卡片上已經有的數字。\n"
  . "6. 繁體中文（台灣用語）。每點以「• 」開頭，點與點用換行分開。\n"
  . "7. 缺點最後一行固定寫：（來源：刊登頁；實勘觀察請再補充）\n"
  . "只輸出 JSON：{\"pros\":\"...\",\"cons\":\"...\"}，不要任何其他文字。";
$user = "已知資料：\n" . json_encode($facts, JSON_UNESCAPED_UNICODE) . "\n\n其他候選：\n" . ($cmp ? implode("\n", $cmp) : '（無）')
  . "\n\n刊登頁文字：\n" . $text
  . "\n\n需要產生的欄位：" . ($needP ? 'pros ' : '') . ($needC ? 'cons' : '')
  . (!$needP ? "\n（優點已有人寫好，不要輸出 pros，缺點要與它一致：" . ($store['pros'] ?? '') . '）' : '')
  . (!$needC ? "\n（缺點已有人寫好，不要輸出 cons：" . ($store['cons'] ?? '') . '）' : '');

[$ok, $res] = wl_call_claude($key, $system, $user);
if (!$ok) out(['success' => false, 'error' => $res]);
$a = strpos($res, '{'); $b = strrpos($res, '}');
$j = ($a !== false && $b !== false) ? json_decode(substr($res, $a, $b - $a + 1), true) : null;
$pros = is_array($j) && is_string($j['pros'] ?? null) ? trim(mb_substr($j['pros'], 0, 3000)) : '';
$cons = is_array($j) && is_string($j['cons'] ?? null) ? trim(mb_substr($j['cons'], 0, 3000)) : '';
$fields = [];
if ($needP && $pros !== '') $fields['pros'] = $pros;
if ($needC && $cons !== '') $fields['cons'] = $cons;
if (!$fields) out(['success' => false, 'error' => 'bad_output']);

$fp = fopen(WL_OV_FILE, 'c+');
flock($fp, LOCK_EX);
$raw = stream_get_contents($fp);
$all = $raw ? (json_decode($raw, true) ?: []) : [];
$o = $all[$id] ?? [];
foreach ($fields as $k => $v) { $o['fields'][$k] = $v; $o['fields'][$k . 'Ja'] = null; }   // 日文翻譯之後由頁面補上
$o['ts'] = (int)round(microtime(true) * 1000);
$all[$id] = $o;
ftruncate($fp, 0); rewind($fp);
fwrite($fp, json_encode($all, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
fflush($fp); flock($fp, LOCK_UN); fclose($fp);
out(['success' => true] + $fields);
