<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// 比較表是已經組好的中日兩份表格，不能拿去翻譯（表格會被拆掉）。
function wl_is_compare_markup($text) {
    return is_string($text) && stripos($text, 'post-cmp') !== false && stripos($text, '<table') !== false;
}

// 翻譯請求裡的 data: 整段拿掉，避免把 base64 照片送到外部翻譯。
function wl_strip_data_payloads($text) {
    if (!is_string($text) || stripos($text, 'data:') === false) return (string)$text;
    $out = '';
    $i = 0;
    $len = strlen($text);
    while (($p = stripos($text, 'data:', $i)) !== false) {
        $out .= substr($text, $i, $p - $i);
        $end = $p;
        while ($end < $len) {
            $c = $text[$end];
            if ($c === '"' || $c === "'" || $c === '<' || $c === '>' || $c === ' ' || $c === "\n" || $c === "\r" || $c === "\t" || $c === ')') break;
            $end++;
        }
        if ($end <= $p) $end = min($len, $p + 5);
        $chunk = substr($text, $p, $end - $p);
        if (!preg_match('#^data:[a-z0-9.+-]+[/;,]#i', $chunk)) $out .= $chunk;
        $i = $end;
    }
    $out .= substr($text, $i);
    return $out;
}

// 回傳要送去翻譯的文字。比較表不送；data: 會先被拿掉。
function wl_prepare_translation($raw) {
    $raw = trim((string)$raw);
    if ($raw === '') return array('empty' => true, 'text' => '');
    if (wl_is_compare_markup($raw)) return array('skip' => true, 'text' => '');
    $text = trim(wl_strip_data_payloads($raw));
    if ($text === '') return array('empty' => true, 'text' => '');
    return array('text' => $text);
}

if (PHP_SAPI === 'cli' && !empty($GLOBALS['WL_TRANSLATE_AS_LIB'])) return;

// 譯文不該含「思考／分析／說明」：長度離譜或含這類標記就視為壞輸出（不採用）
function wl_bad_translation($src, $out) {
    if (preg_match('/THOUGHTS?\s*:|分解と翻訳|原文\s*[：:]|翻訳\s*[：:]|Translation\s*:|思考過程|Here is|Here\'s/iu', $out)) return true;
    if (mb_strlen($out) > mb_strlen($src) * 6 + 80) return true;
    if (substr_count($out, "\n") > substr_count($src, "\n") + 3) return true;
    return false;
}

$prepared = wl_prepare_translation(isset($_REQUEST['text']) ? $_REQUEST['text'] : '');
if (!empty($prepared['skip'])) {
    echo json_encode(['success' => false, 'error' => 'structured', 'translation' => ''], JSON_UNESCAPED_UNICODE);
    exit;
}
$text = isset($prepared['text']) ? $prepared['text'] : '';
if (!$text) {
    echo json_encode(['success' => false, 'error' => 'Empty text'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 1. Determine translation direction (zh-TW <-> ja)
$pair = isset($_REQUEST['pair']) ? trim($_REQUEST['pair']) : '';
if (!$pair) {
    // If text contains Japanese Kana, default to Japanese -> Traditional Chinese
    if (preg_match('/[\x{3040}-\x{309F}\x{30A0}-\x{30FF}]/u', $text)) {
        $pair = 'ja|zh-TW';
    } else {
        $pair = 'zh-TW|ja';
    }
}

// 1.5 優先使用 Gemini（經 Apps Script，金鑰只存在 Apps Script，不在這台主機）
$gasUrl = 'https://script.google.com/macros/s/AKfycbyZog9Sw2JpEX0EsEyyunM3oTbvVQBoKiwQnj3B8SNLHRtrjpmFadoli9ioohLIH_a_1A/exec';
if (mb_strlen($text) <= 1500) {
    $ch0 = curl_init();
    curl_setopt($ch0, CURLOPT_URL, $gasUrl);
    curl_setopt($ch0, CURLOPT_POST, true);
    curl_setopt($ch0, CURLOPT_POSTFIELDS, json_encode(['action' => 'wltranslate', 'text' => $text, 'pair' => $pair], JSON_UNESCAPED_UNICODE));
    curl_setopt($ch0, CURLOPT_HTTPHEADER, ['Content-Type: text/plain']);
    curl_setopt($ch0, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch0, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch0, CURLOPT_TIMEOUT, 25);
    $gres = curl_exec($ch0);
    if ($gres) {
        $gj = json_decode($gres, true);
        if (is_array($gj) && !empty($gj['ok']) && !empty($gj['translation']) && !wl_bad_translation($text, $gj['translation'])) {
            echo json_encode([
                'success' => true,
                'translation' => $gj['translation'],
                'pair' => $pair,
                'source' => 'gemini'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
    }
}

// 2. Fallback: MyMemory Translation API
$encoded = urlencode($text);
$apiUrl = "https://api.mymemory.translated.net/get?q={$encoded}&langpair=" . urlencode($pair);

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_TIMEOUT, 9);
curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
$response = curl_exec($ch);

if ($response) {
    $data = json_decode($response, true);
    if (isset($data['responseData']['translatedText']) && !empty($data['responseData']['translatedText'])) {
        $trans = html_entity_decode($data['responseData']['translatedText'], ENT_QUOTES, 'UTF-8');
        echo json_encode([
            'success' => true,
            'translation' => $trans,
            'pair' => $pair,
            'source' => 'mymemory'
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
}

echo json_encode([
    'success' => false,
    'translation' => $text,
    'pair' => $pair,
    'error' => 'Translation service unavailable'
], JSON_UNESCAPED_UNICODE);
