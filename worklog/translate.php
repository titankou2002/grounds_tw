<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// 譯文不該含「思考／分析／說明」：長度離譜或含這類標記就視為壞輸出（不採用）
function wl_bad_translation($src, $out) {
    if (preg_match('/THOUGHTS?\s*:|分解と翻訳|原文\s*[：:]|翻訳\s*[：:]|Translation\s*:|思考過程|Here is|Here\'s/iu', $out)) return true;
    if (mb_strlen($out) > mb_strlen($src) * 6 + 80) return true;
    if (substr_count($out, "\n") > substr_count($src, "\n") + 3) return true;
    return false;
}

$text = isset($_REQUEST['text']) ? trim($_REQUEST['text']) : '';
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
