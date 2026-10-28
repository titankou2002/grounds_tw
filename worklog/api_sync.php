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
            $content = preg_replace('/^\xEF\xBB\xBF/', '', $content);
            // 套用 MAP 頁的線上修改，讓原本的頁面也看得到
            require_once __DIR__ . '/lib_overrides.php';
            $ov = wl_ov_load(); $d = json_decode($content, true);
            if ($ov && is_array($d) && isset($d['stores']) && is_array($d['stores'])) {
                foreach ($d['stores'] as $i => $s) { $d['stores'][$i] = wl_ov_apply($s, $ov); }
                $content = json_encode($d, JSON_UNESCAPED_UNICODE);
            }
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

// ---------- 合併：兩個人幾乎同時存檔時，不互相覆蓋 ----------
function wl_comment_id($c) {
    return !empty($c['id']) ? (string)$c['id'] : 'lg' . dechex(crc32(($c['author'] ?? '') . '|' . ($c['date'] ?? '') . '|' . ($c['zh'] ?? '') . '|' . ($c['ja'] ?? '')));
}
function wl_key_comment($c) { return 'i:' . wl_comment_id($c); }
// 回覆：依 id 取聯集（回覆不可編輯，同一則留一份），依建立時間排序
function wl_merge_comments($a, $b) {
    $m = [];
    foreach (array_merge(is_array($a) ? $a : [], is_array($b) ? $b : []) as $c) {
        if (!is_array($c)) continue;
        $c['id'] = wl_comment_id($c);
        $k = wl_key_comment($c);
        if (isset($m[$k])) {
            $r = wl_merge_reactions($m[$k]['reactions'] ?? [], $c['reactions'] ?? []);
            $m[$k] = $c + $m[$k];
            if ($r) $m[$k]['reactions'] = $r;
        } else $m[$k] = $c;
    }
    $list = array_values($m);
    usort($list, function ($x, $y) { return ((int)($x['ts'] ?? 0)) <=> ((int)($y['ts'] ?? 0)); });
    return $list;
}
// 表情：每個人對每個表情只留最新一筆（on=true/false）
function wl_merge_reactions($a, $b) {
    $m = [];
    foreach (array_merge(is_array($a) ? $a : [], is_array($b) ? $b : []) as $r) {
        if (!is_array($r)) continue;
        $k = ($r['u'] ?? '') . '|' . ($r['e'] ?? '');
        if (!isset($m[$k]) || (int)($r['ts'] ?? 0) >= (int)($m[$k]['ts'] ?? 0)) $m[$k] = $r;
    }
    return array_values($m);
}
function wl_stamp($p) { return ((int)($p['editedAt'] ?? 0)) ?: (int)($p['id'] ?? 0); }
function wl_merge_post($old, $new) {
    $base = ((int)($new['editedAt'] ?? 0) >= (int)($old['editedAt'] ?? 0)) ? $new : $old;   // 文字內容以較新的編輯為準
    $base['comments'] = wl_merge_comments($old['comments'] ?? [], $new['comments'] ?? []);
    $r = wl_merge_reactions($old['reactions'] ?? [], $new['reactions'] ?? []);
    if ($r) $base['reactions'] = $r;
    return $base;
}
function wl_merge_store($old, $new) {
    return ((int)($new['editedAt'] ?? 0) >= (int)($old['editedAt'] ?? 0)) ? $new : $old;
}
function wl_merge_topic($old, $new) {
    $dead = array_unique(array_merge($old['delC'] ?? [], $new['delC'] ?? []));
    $base = $new;
    $cs = [];
    foreach (array_merge($old['comments'] ?? [], $new['comments'] ?? []) as $c) {
        if (!is_array($c) || isset($c['id']) && in_array($c['id'], $dead, true)) continue;
        $k = wl_key_comment($c);
        $cs[$k] = isset($cs[$k]) ? ($c + $cs[$k]) : $c;
    }
    $base['comments'] = array_values($cs);
    if ($dead) $base['delC'] = array_values($dead);
    return $base;
}
function wl_merge_by_id($old, $new, $fn, $dead) {
    $m = [];
    foreach ((is_array($old) ? $old : []) as $x) { if (is_array($x) && isset($x['id']) && !isset($dead[(string)$x['id']])) $m[(string)$x['id']] = $x; }
    foreach ((is_array($new) ? $new : []) as $x) {
        if (!is_array($x) || !isset($x['id'])) continue;
        $id = (string)$x['id'];
        if (isset($dead[$id])) continue;
        $m[$id] = isset($m[$id]) ? $fn($m[$id], $x) : $x;
    }
    return array_values($m);
}
function wl_merge_state($old, $new) {
    $out = $new;
    // 刪除紀錄：取聯集（防止已刪除的東西被別人的舊資料救活）
    $dl = [];
    foreach (array_merge(is_array($old['deletedLogs'] ?? null) ? $old['deletedLogs'] : [], is_array($new['deletedLogs'] ?? null) ? $new['deletedLogs'] : []) as $l) {
        if (!is_array($l)) continue;
        $k = ($l['type'] ?? '') . '_' . ($l['id'] ?? '');
        if (!isset($dl[$k])) $dl[$k] = $l; elseif (!empty($l['hidden'])) $dl[$k]['hidden'] = true;
    }
    $dead = ['工作動態' => [], '店面物件' => [], '決策議題' => []];
    foreach ($dl as $l) { if (isset($dead[$l['type'] ?? ''])) $dead[$l['type']][(string)$l['id']] = true; }
    $out['deletedLogs'] = array_values($dl);
    $posts = wl_merge_by_id($old['posts'] ?? [], $new['posts'] ?? [], 'wl_merge_post', $dead['工作動態']);
    foreach ($posts as $i => $pp) { if (!empty($pp['comments'])) $posts[$i]['comments'] = wl_merge_comments($pp['comments'], []); }   // 舊回覆補 id、去重
    usort($posts, function ($a, $b) { return wl_stamp($b) <=> wl_stamp($a); });
    $out['posts'] = $posts;
    $out['stores'] = wl_merge_by_id($old['stores'] ?? [], $new['stores'] ?? [], 'wl_merge_store', $dead['店面物件']);
    $out['boardTopics'] = wl_merge_by_id($old['boardTopics'] ?? [], $new['boardTopics'] ?? [], 'wl_merge_topic', $dead['決策議題']);
    $seen = ['tw' => 0, 'jp' => 0];
    foreach (['tw', 'jp'] as $r) { $seen[$r] = max((int)($old['seen'][$r] ?? 0), (int)($new['seen'][$r] ?? 0)); }
    $out['seen'] = $seen;
    return $out;
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

    // 讀—合併—寫 整段上鎖，兩個人同時存檔也不會互相覆蓋
    $lock = fopen(__DIR__ . '/grounds_data.lock', 'c');
    flock($lock, LOCK_EX);
    $old = [];
    if (file_exists($dataFile)) {
        $c = preg_replace('/^\xEF\xBB\xBF/', '', (string)file_get_contents($dataFile));
        $d = json_decode($c, true);
        if (is_array($d)) $old = $d;
    }
    $merged = wl_merge_state($old, $json);
    $merged['updatedAt'] = time();

    // Atomic write to prevent file corruption
    $tempFile = $dataFile . '.tmp.' . uniqid();
    if (file_put_contents($tempFile, json_encode($merged, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)) !== false) {
        rename($tempFile, $dataFile);
        flock($lock, LOCK_UN);
        echo json_encode(['success' => true, 'updatedAt' => $merged['updatedAt'], 'merged' => $merged], JSON_UNESCAPED_UNICODE);
    } else {
        flock($lock, LOCK_UN);
        echo json_encode(['success' => false, 'error' => 'Write failed'], JSON_UNESCAPED_UNICODE);
    }
    exit;
}
