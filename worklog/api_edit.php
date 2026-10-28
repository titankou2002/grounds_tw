<?php
// MAP 頁寫入端點。gate.php 已要求登入 cookie（未登入會得到 401），這裡只處理寫入。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
require_once __DIR__ . '/lib_overrides.php';
require_once __DIR__ . '/lib_images.php';

function out($a, $code = 200) { http_response_code($code); echo json_encode($a, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] === 'GET') {   // 供前端確認是否已登入，並取回備註（備註只給登入者看）
    $notes = [];
    foreach (wl_ov_load() as $sid => $o) { if (!empty($o['notes'])) $notes[$sid] = $o['notes']; }
    out(['success' => true, 'notes' => $notes]);
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(['success' => false, 'error' => 'Method'], 405);

$isUpload = isset($_FILES['photo']);
$in = $isUpload ? $_POST : (json_decode(file_get_contents('php://input'), true) ?: []);
$id = (string)($in['id'] ?? '');
$action = (string)($in['action'] ?? '');
if (!preg_match('/^[\w.-]{1,80}$/', $id)) out(['success' => false, 'error' => 'bad id'], 400);

$data = json_decode(preg_replace('/^\xEF\xBB\xBF/', '', (string)@file_get_contents(__DIR__ . '/grounds_data.json')), true);
$exists = false;
foreach (($data['stores'] ?? []) as $s) { if (($s['id'] ?? '') === $id) { $exists = true; break; } }
if (!$exists) out(['success' => false, 'error' => 'unknown store'], 404);

$num = ['rent', 'area', 'deposit', 'realCost'];
$str = ['title' => 200, 'address' => 200, 'freeRent' => 80, 'depositText' => 40, 'pros' => 5000, 'cons' => 5000, 'titleJa' => 200, 'prosJa' => 5000, 'consJa' => 5000, 'statusLabel' => 30, 'url' => 500];
$bool = ['canRegister', 'canInvoice'];
// 中文欄位改了就清掉舊的日文翻譯，避免日文版還顯示舊內容
$clearJa = ['title' => 'titleJa', 'pros' => 'prosJa', 'cons' => 'consJa'];

$fp = fopen(WL_OV_FILE, 'c+');
flock($fp, LOCK_EX);
$raw = stream_get_contents($fp);
$ov = $raw ? (json_decode($raw, true) ?: []) : [];
$o = $ov[$id] ?? [];
$result = ['success' => true];

if ($action === 'edit') {
    $f = is_array($in['fields'] ?? null) ? $in['fields'] : [];
    foreach ($f as $k => $v) {
        if ((in_array($k, $num, true) || in_array($k, $bool, true)) && $v === null) { $o['fields'][$k] = null; continue; }
        if ($k === 'coverImg') {   // 主頁顯示的圖片（星號）。空字串 = 取消指定。data: 先存成檔案，不寫進 json。
            $v = trim((string)$v);
            if ($v === '') { $o['fields']['coverImg'] = ''; continue; }
            if (stripos($v, 'data:') === 0) {
                $saved = wl_data_image_to_file($v);
                if (is_string($saved) && $saved !== '') $o['fields']['coverImg'] = $saved;
                continue;
            }
            if (wl_public_image_ref($v) || wl_public_http_url($v)) $o['fields']['coverImg'] = mb_substr($v, 0, 500);
            continue;
        }
        if (in_array($k, $num, true)) { if (!is_numeric($v) || $v < 0 || $v > 1e9) continue; $o['fields'][$k] = $v + 0; }
        elseif (isset($str[$k])) {
            $v = trim(mb_substr((string)$v, 0, $str[$k]));
            if ($k === 'url' && $v !== '' && !preg_match('#^https?://#i', $v)) continue;
            $o['fields'][$k] = $v;
            if (isset($clearJa[$k])) $o['fields'][$clearJa[$k]] = null;
        }
        elseif (in_array($k, $bool, true)) $o['fields'][$k] = (bool)$v;
    }
} elseif ($action === 'note_add') {
    $t = trim(mb_substr((string)($in['text'] ?? ''), 0, 2000));
    if ($t === '') { flock($fp, LOCK_UN); out(['success' => false, 'error' => 'empty'], 400); }
    $o['notes'][] = ['id' => bin2hex(random_bytes(4)), 'text' => $t, 'ts' => time()];
} elseif ($action === 'note_del') {
    $nid = (string)($in['noteId'] ?? '');
    $o['notes'] = array_values(array_filter($o['notes'] ?? [], function ($n) use ($nid) { return $n['id'] !== $nid; }));
} elseif ($action === 'img_del') {
    $u = (string)($in['url'] ?? '');
    $o['imgAdd'] = array_values(array_diff($o['imgAdd'] ?? [], [$u]));
    if (isset($o['imgOrder']) && is_array($o['imgOrder'])) {
        $o['imgOrder'] = array_values(array_filter($o['imgOrder'], function ($x) use ($u) { return $x !== $u; }));
    } elseif (!in_array($u, $o['imgDel'] ?? [], true)) $o['imgDel'][] = $u;
} elseif ($action === 'img_set') {
    // 編輯後的完整照片順序。只收 http(s) 或 uploads/、files/ 的圖，不收 data:。
    $list = is_array($in['images'] ?? null) ? $in['images'] : null;
    if ($list === null) { flock($fp, LOCK_UN); out(['success' => false, 'error' => 'bad images'], 400); }
    $clean = array();
    foreach ($list as $u) {
        if (!is_string($u)) continue;
        $u = trim($u);
        if ($u === '' || stripos($u, 'data:') === 0 || strlen($u) > 500) continue;
        if (!wl_public_image_ref($u) && !wl_public_http_url($u)) continue;
        if (!in_array($u, $clean, true)) $clean[] = $u;
        if (count($clean) >= 40) break;
    }
    $o['imgOrder'] = $clean;
    $result['images'] = $clean;
} elseif ($action === 'img_add' && $isUpload) {
    $p = $_FILES['photo'];
    $info = ($p['error'] === UPLOAD_ERR_OK && $p['size'] <= 6 * 1024 * 1024) ? @getimagesize($p['tmp_name']) : false;
    $ext = $info ? ([IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp'][$info[2]] ?? null) : null;
    if (!$ext) { flock($fp, LOCK_UN); out(['success' => false, 'error' => 'bad image'], 400); }
    $dir = __DIR__ . '/uploads';
    if (!is_dir($dir)) mkdir($dir, 0755, true);
    $name = 'uploads/' . bin2hex(random_bytes(8)) . '.' . $ext;
    if (!move_uploaded_file($p['tmp_name'], __DIR__ . '/' . $name)) { flock($fp, LOCK_UN); out(['success' => false, 'error' => 'save failed'], 500); }
    if (isset($o['imgOrder']) && is_array($o['imgOrder'])) $o['imgOrder'][] = $name;
    else $o['imgAdd'][] = $name;
    $result['url'] = $name;
} else {
    flock($fp, LOCK_UN);
    out(['success' => false, 'error' => 'bad action'], 400);
}

$o['ts'] = (int)round(microtime(true) * 1000);
$ov[$id] = $o;
ftruncate($fp, 0); rewind($fp);
fwrite($fp, json_encode($ov, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
fflush($fp); flock($fp, LOCK_UN); fclose($fp);
out($result);
