<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

$text = isset($_REQUEST['text']) ? trim($_REQUEST['text']) : '';
if (!$text) {
    echo json_encode(['success' => false, 'error' => 'Empty text'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 1. Call MyMemory Translation API
$encoded = urlencode($text);
$apiUrl = "https://api.mymemory.translated.net/get?q={$encoded}&langpair=zh-TW|ja";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_TIMEOUT, 8);
curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
$response = curl_exec($ch);
curl_close($ch);

if ($response) {
    $data = json_decode($response, true);
    if (isset($data['responseData']['translatedText']) && !empty($data['responseData']['translatedText'])) {
        $trans = html_entity_decode($data['responseData']['translatedText'], ENT_QUOTES, 'UTF-8');
        echo json_encode([
            'success' => true,
            'translation' => $trans,
            'source' => 'mymemory'
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
}

echo json_encode([
    'success' => false,
    'translation' => $text,
    'error' => 'Translation service unavailable'
], JSON_UNESCAPED_UNICODE);
