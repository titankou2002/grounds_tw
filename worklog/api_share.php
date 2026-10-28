<?php
// 比較表分享快照：POST 建立（需登入 cookie）、GET 讀取（公開，給日本同事免密碼看）
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

require_once __DIR__ . '/lib_images.php';
require_once __DIR__ . '/lib_overrides.php';

$SHARE_DIR = __DIR__ . '/compare_shares';
$SHARE_KEYS = ['id','title','titleJa','address','lat','lng','rent','area','deposit','freeRent','pros','prosJa','cons','consJa','images','status','statusLabel','canRegister','canInvoice','url','unverified','depositText','floor','coverImg'];
$MAX_STORES = 8;
$MAX_FILE_BYTES = 400 * 1024;
$MAX_SHARES = 300;

function wl_share_authed() {
    $secretFile = __DIR__ . '/.wl_secret';
    if (!is_file($secretFile)) return false;
    $secret = trim((string)file_get_contents($secretFile));
    if ($secret === '') return false;
    $token = hash_hmac('sha256', 'worklog-ok', $secret);
    return isset($_COOKIE['wl_auth']) && hash_equals($token, (string)$_COOKIE['wl_auth']);
}

function wl_share_id_ok($id) {
    return is_string($id) && (bool)preg_match('/^[a-f0-9]{32}$/', $id);
}

function wl_share_path($id) {
    return __DIR__ . '/compare_shares/' . $id . '.json';
}

function wl_share_ensure_dir($dir) {
    if (is_dir($dir)) return true;
    return @mkdir($dir, 0755, true);
}

function wl_share_whitelist_store(array $s, array $keys) {
    $row = [];
    foreach ($keys as $k) {
        if (!array_key_exists($k, $s)) continue;
        $row[$k] = $s[$k];
    }
    if (isset($row['url']) && !(wl_public_http_url($row['url']) || wl_public_image_ref($row['url']))) unset($row['url']);
    if (isset($row['coverImg']) && !wl_public_image_ref($row['coverImg'])) unset($row['coverImg']);
    if (isset($row['images']) && is_array($row['images'])) {
        $row['images'] = array_values(array_filter($row['images'], 'wl_public_image_ref'));
    } else {
        unset($row['images']);
    }
    // 絕不帶 notes 或其他私密欄位
    unset($row['notes']);
    return $row;
}

function wl_share_load_store_map() {
    $file = __DIR__ . '/grounds_data.json';
    $data = wl_migrate_grounds_file($file);
    wl_migrate_overrides_file();
    $fixFile = __DIR__ . '/store_fixes.json';
    $fixes = is_file($fixFile) ? (json_decode((string)file_get_contents($fixFile), true) ?: []) : [];
    $ov = wl_ov_load();
    $map = [];
    if (!is_array($data) || !isset($data['stores']) || !is_array($data['stores'])) return $map;
    foreach ($data['stores'] as $s) {
        if (!is_array($s) || empty($s['id'])) continue;
        if (isset($fixes[$s['id']]) && (int)($s['fixV'] ?? 0) < (int)($fixes[$s['id']]['fixV'] ?? 0)) {
            foreach ($fixes[$s['id']] as $fk => $fv) {
                if ($fv === null) unset($s[$fk]);
                else $s[$fk] = $fv;
            }
            $s['unverified'] = !empty($fixes[$s['id']]['unverified']);
        }
        $s = wl_ov_apply($s, $ov);
        $map[(string)$s['id']] = $s;
    }
    return $map;
}

function wl_share_prune($dir, $max) {
    $files = glob($dir . '/*.json');
    if (!is_array($files) || count($files) <= $max) return;
    usort($files, function ($a, $b) {
        return filemtime($a) <=> filemtime($b);
    });
    $drop = count($files) - $max;
    for ($i = 0; $i < $drop; $i++) @unlink($files[$i]);
}

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

if ($method === 'GET') {
    $id = isset($_GET['id']) ? strtolower(trim((string)$_GET['id'])) : '';
    if (!wl_share_id_ok($id)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'bad id'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $path = wl_share_path($id);
    if (!is_file($path)) {
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'not found'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $raw = (string)file_get_contents($path);
    $data = json_decode($raw, true);
    if (!is_array($data) || empty($data['stores']) || !is_array($data['stores'])) {
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'not found'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    // 再過濾一次，避免舊快照多帶欄位
    global $SHARE_KEYS;
    $stores = [];
    foreach ($data['stores'] as $s) {
        if (is_array($s)) $stores[] = wl_share_whitelist_store($s, $SHARE_KEYS);
    }
    echo json_encode([
        'success' => true,
        'id' => $id,
        'createdAt' => (int)($data['createdAt'] ?? 0),
        'lang' => in_array(($data['lang'] ?? ''), ['bilingual', 'zh', 'ja'], true) ? $data['lang'] : 'bilingual',
        'stores' => $stores,
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($method === 'POST') {
    if (!wl_share_authed()) {
        http_response_code(401);
        echo json_encode(['success' => false, 'error' => 'Unauthorized'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $body = json_decode((string)file_get_contents('php://input'), true);
    if (!is_array($body)) $body = [];
    $action = (string)($body['action'] ?? 'create');
    if ($action !== 'create') {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'bad action'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $ids = $body['ids'] ?? [];
    if (!is_array($ids)) $ids = [];
    $ids = array_values(array_unique(array_filter(array_map(function ($x) {
        return is_string($x) || is_int($x) ? (string)$x : '';
    }, $ids))));
    if (count($ids) < 2) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'need 2+ stores'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    if (count($ids) > $MAX_STORES) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'too many stores'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $lang = (string)($body['lang'] ?? 'bilingual');
    if (!in_array($lang, ['bilingual', 'zh', 'ja'], true)) $lang = 'bilingual';

    $map = wl_share_load_store_map();
    $stores = [];
    foreach ($ids as $id) {
        if (!isset($map[$id])) continue;
        $stores[] = wl_share_whitelist_store($map[$id], $SHARE_KEYS);
    }
    if (count($stores) < 2) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'stores not found'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    if (!wl_share_ensure_dir($SHARE_DIR)) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'mkdir failed'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $shareId = bin2hex(random_bytes(16));
    $payload = [
        'id' => $shareId,
        'createdAt' => time(),
        'lang' => $lang,
        'stores' => $stores,
    ];
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE);
    if ($json === false || strlen($json) > $MAX_FILE_BYTES) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'snapshot too large'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $lock = fopen($SHARE_DIR . '/.lock', 'c');
    if ($lock) flock($lock, LOCK_EX);
    $ok = wl_atomic_write(wl_share_path($shareId), $json);
    if ($ok) wl_share_prune($SHARE_DIR, $MAX_SHARES);
    if ($lock) { flock($lock, LOCK_UN); fclose($lock); }

    if (!$ok) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'write failed'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    echo json_encode([
        'success' => true,
        'id' => $shareId,
        'path' => 'share.html?id=' . $shareId,
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'method'], JSON_UNESCAPED_UNICODE);
