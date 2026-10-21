<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit;
}

$dataFile = __DIR__ . '/grounds_data.json';

// GET: Retrieve the shared cloud data
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($dataFile)) {
        $content = file_get_contents($dataFile);
        if ($content && trim($content) !== '') {
            echo $content;
            exit;
        }
    }
    // Return empty fallback
    echo json_encode([
        'success' => true,
        'posts' => null,
        'stores' => null,
        'deletedLogs' => null,
        'updatedAt' => time()
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// POST: Save updated state from client (Mobile, PC, etc.)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $rawInput = file_get_contents('php://input');
    if (!$rawInput || trim($rawInput) === '') {
        echo json_encode(['success' => false, 'error' => 'Empty payload'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $json = json_decode($rawInput, true);
    if (!$json || !is_array($json)) {
        echo json_encode(['success' => false, 'error' => 'Invalid JSON'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $json['updatedAt'] = time();

    // Atomic write to prevent file corruption
    $tempFile = $dataFile . '.tmp.' . uniqid();
    if (file_put_contents($tempFile, json_encode($json, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)) !== false) {
        rename($tempFile, $dataFile);
        echo json_encode(['success' => true, 'updatedAt' => $json['updatedAt']], JSON_UNESCAPED_UNICODE);
    } else {
        echo json_encode(['success' => false, 'error' => 'Write failed'], JSON_UNESCAPED_UNICODE);
    }
    exit;
}
