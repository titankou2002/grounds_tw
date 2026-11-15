<?php
// 工作日誌週報快照：POST 建立（需登入 cookie）、GET 讀取（公開，給日本同事免密碼看）
// 快照建立後就跟日誌脫鉤（之後再改日誌不會影響已分享的那一份）。
// 登入的人可以在 report.html 直接修改快照（action=update：標題、備註、每筆文字／工時、照片刪除與排序）。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

require_once __DIR__ . '/lib_images.php';
require_once __DIR__ . '/lib_overrides.php';

$DIR = __DIR__ . '/report_shares';
$MAX_POSTS = 400;
$MAX_FILE_BYTES = 1500 * 1024;
$MAX_SHARES = 200;

function wl_rp_authed() {
    $secretFile = __DIR__ . '/.wl_secret';
    if (!is_file($secretFile)) return false;
    $secret = trim((string)file_get_contents($secretFile));
    if ($secret === '') return false;
    $token = hash_hmac('sha256', 'worklog-ok', $secret);
    return isset($_COOKIE['wl_auth']) && hash_equals($token, (string)$_COOKIE['wl_auth']);
}
function wl_rp_out($a, $code = 200) {
    http_response_code($code);
    echo json_encode($a, JSON_UNESCAPED_UNICODE);
    exit;
}
function wl_rp_id_ok($id) { return is_string($id) && (bool)preg_match('/^[a-f0-9]{32}$/', $id); }
function wl_rp_str($v, $max) { return mb_substr(is_string($v) ? $v : '', 0, $max); }
function wl_rp_day($v) {
    return (is_string($v) && preg_match('#^\d{4}/\d{2}/\d{2}$#', $v)) ? $v : '';
}
function wl_rp_clean_post(array $p) {
    $day = wl_rp_day($p['day'] ?? '');
    if ($day === '') return null;
    $atts = [];
    foreach ((array)($p['atts'] ?? []) as $a) {
        if (!is_array($a)) continue;
        $url = (string)($a['url'] ?? '');
        $type = ($a['type'] ?? '') === 'pdf' ? 'pdf' : 'image';
        if ($type === 'image' && !wl_public_image_ref($url)) continue;
        if ($type === 'pdf') continue; // PDF 需登入才開得了，週報不放
        $atts[] = ['type' => 'image', 'url' => $url, 'name' => wl_rp_str($a['name'] ?? '', 120)];
        if (count($atts) >= 12) break;
    }
    return [
        'day' => $day,
        'author' => wl_rp_str($p['author'] ?? '', 40),
        'tag' => wl_rp_str($p['tag'] ?? '', 40),
        'hours' => max(0, min(24, (float)($p['hours'] ?? 0))),
        'zh' => wl_rp_str($p['zh'] ?? '', 6000),
        'ja' => wl_rp_str($p['ja'] ?? '', 6000),
        'atts' => $atts,
    ];
}
function wl_rp_load($path) {
    if (!is_file($path)) return null;
    $data = json_decode((string)file_get_contents($path), true);
    return (is_array($data) && isset($data['posts'])) ? $data : null;
}
function wl_rp_view($id, array $data) {
    $posts = [];
    foreach ((array)$data['posts'] as $p) { if (is_array($p) && ($c = wl_rp_clean_post($p))) $posts[] = $c; }
    return [
        'success' => true,
        'id' => $id,
        'createdAt' => (int)($data['createdAt'] ?? 0),
        'updatedAt' => (int)($data['updatedAt'] ?? ($data['createdAt'] ?? 0)),
        'from' => wl_rp_day($data['from'] ?? ''),
        'to' => wl_rp_day($data['to'] ?? ''),
        'title' => wl_rp_str($data['title'] ?? '', 120),
        'notes' => wl_rp_str($data['notes'] ?? '', 4000),
        'posts' => $posts,
        'canEdit' => wl_rp_authed(),
    ];
}
function wl_rp_prune($dir, $max) {
    $files = glob($dir . '/*.json');
    if (!is_array($files) || count($files) <= $max) return;
    usort($files, function ($a, $b) { return filemtime($a) <=> filemtime($b); });
    for ($i = 0, $n = count($files) - $max; $i < $n; $i++) @unlink($files[$i]);
}

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

if ($method === 'GET') {
    $id = strtolower(trim((string)($_GET['id'] ?? '')));
    if (!wl_rp_id_ok($id)) wl_rp_out(['success' => false, 'error' => 'bad id'], 400);
    $data = wl_rp_load($DIR . '/' . $id . '.json');
    if (!$data) wl_rp_out(['success' => false, 'error' => 'not found'], 404);
    wl_rp_out(wl_rp_view($id, $data));
}

if ($method === 'POST') {
    if (!wl_rp_authed()) wl_rp_out(['success' => false, 'error' => 'Unauthorized'], 401);
    $body = json_decode((string)file_get_contents('php://input'), true);
    if (!is_array($body)) $body = [];

    // 修改既有快照（只能刪除／排序原本就有的照片，不能塞新網址進來）
    if (($body['action'] ?? '') === 'update') {
        $id = strtolower(trim((string)($body['id'] ?? '')));
        if (!wl_rp_id_ok($id)) wl_rp_out(['success' => false, 'error' => 'bad id'], 400);
        $path = $DIR . '/' . $id . '.json';
        $lock = fopen($DIR . '/.lock', 'c');
        if ($lock) flock($lock, LOCK_EX);
        $old = wl_rp_load($path);
        $fail = function ($err, $code) use ($lock) { if ($lock) { flock($lock, LOCK_UN); fclose($lock); } wl_rp_out(['success' => false, 'error' => $err], $code); };
        if (!$old) $fail('not found', 404);
        $known = [];
        foreach ((array)$old['posts'] as $op) foreach ((array)($op['atts'] ?? []) as $a) if (is_array($a) && isset($a['url'])) $known[(string)$a['url']] = true;
        $posts = [];
        foreach ((array)($body['posts'] ?? []) as $p) {
            if (!is_array($p)) continue;
            $p['atts'] = array_values(array_filter((array)($p['atts'] ?? []), function ($a) use ($known) { return is_array($a) && isset($known[(string)($a['url'] ?? '')]); }));
            if ($c = wl_rp_clean_post($p)) $posts[] = $c;
        }
        if (count($posts) < 1) $fail('no posts', 400);
        if (count($posts) > $MAX_POSTS) $fail('too many posts', 400);
        $old['posts'] = $posts;
        $old['title'] = wl_rp_str($body['title'] ?? '', 120);
        $old['notes'] = wl_rp_str($body['notes'] ?? '', 4000);
        $old['updatedAt'] = time();
        $json = json_encode($old, JSON_UNESCAPED_UNICODE);
        if ($json === false || strlen($json) > $MAX_FILE_BYTES) $fail('snapshot too large', 400);
        $ok = wl_atomic_write($path, $json);
        if ($lock) { flock($lock, LOCK_UN); fclose($lock); }
        if (!$ok) wl_rp_out(['success' => false, 'error' => 'write failed'], 500);
        wl_rp_out(wl_rp_view($id, $old));
    }

    $in = is_array($body['posts'] ?? null) ? $body['posts'] : [];
    $posts = [];
    foreach ($in as $p) { if (is_array($p) && ($c = wl_rp_clean_post($p))) $posts[] = $c; }
    if (count($posts) < 1) wl_rp_out(['success' => false, 'error' => 'no posts'], 400);
    if (count($posts) > $MAX_POSTS) wl_rp_out(['success' => false, 'error' => 'too many posts'], 400);
    if (!is_dir($DIR) && !@mkdir($DIR, 0755, true)) wl_rp_out(['success' => false, 'error' => 'mkdir failed'], 500);

    $id = bin2hex(random_bytes(16));
    $payload = [
        'id' => $id,
        'createdAt' => time(),
        'title' => wl_rp_str($body['title'] ?? '', 120),
        'from' => wl_rp_day($body['from'] ?? ''),
        'to' => wl_rp_day($body['to'] ?? ''),
        'posts' => $posts,
    ];
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE);
    if ($json === false || strlen($json) > $MAX_FILE_BYTES) wl_rp_out(['success' => false, 'error' => 'snapshot too large'], 400);

    $lock = fopen($DIR . '/.lock', 'c');
    if ($lock) flock($lock, LOCK_EX);
    $ok = wl_atomic_write($DIR . '/' . $id . '.json', $json);
    if ($ok) wl_rp_prune($DIR, $MAX_SHARES);
    if ($lock) { flock($lock, LOCK_UN); fclose($lock); }
    if (!$ok) wl_rp_out(['success' => false, 'error' => 'write failed'], 500);
    wl_rp_out(['success' => true, 'id' => $id, 'path' => 'report.html?id=' . $id]);
}

wl_rp_out(['success' => false, 'error' => 'method'], 405);
