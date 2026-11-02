<?php
// 動態／留言的附件上傳（圖片、PDF）。gate.php 已要求登入 cookie，沒登入到不了這裡。
// 只收真的圖片或 PDF（檢查檔案內容，不看副檔名）；檔名一律隨機，原始檔名只當顯示用文字。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
function out($a, $code = 200) { http_response_code($code); echo json_encode($a, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(['success' => false, 'error' => 'method'], 405);
$limit = ini_get('upload_max_filesize');
// 超過主機上限時 PHP 會讓 $_FILES 整個是空的
if (!isset($_FILES['file'])) out(['success' => false, 'error' => 'too_large', 'limit' => $limit], 413);
$f = $_FILES['file'];
if ($f['error'] === UPLOAD_ERR_INI_SIZE || $f['error'] === UPLOAD_ERR_FORM_SIZE) out(['success' => false, 'error' => 'too_large', 'limit' => $limit], 413);
if ($f['error'] !== UPLOAD_ERR_OK) out(['success' => false, 'error' => 'upload_error'], 400);

$MAX_IMG = 10 * 1024 * 1024;
$MAX_PDF = 20 * 1024 * 1024;
$type = null; $ext = null; $w = null; $h = null;
$head = (string)@file_get_contents($f['tmp_name'], false, null, 0, 5);
if ($head === '%PDF-') {
    if ($f['size'] > $MAX_PDF) out(['success' => false, 'error' => 'too_large', 'limit' => '20MB'], 413);
    $type = 'pdf'; $ext = 'pdf';
} else {
    $info = @getimagesize($f['tmp_name']);
    $map = [IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp', IMAGETYPE_GIF => 'gif'];
    if (!$info || !isset($map[$info[2]])) out(['success' => false, 'error' => 'bad_type'], 415);
    if ($f['size'] > $MAX_IMG) out(['success' => false, 'error' => 'too_large', 'limit' => '10MB'], 413);
    $w = $info[0]; $h = $info[1];
    if ($w < 1 || $h < 1 || $w > 12000 || $h > 12000 || $w * $h > 60000000) out(['success' => false, 'error' => 'bad_type'], 415);
    // 圖檔裡夾帶程式碼的一律拒絕
    $raw = (string)@file_get_contents($f['tmp_name'], false, null, 0, 1048576);
    if (stripos($raw, '<?php') !== false || strpos($raw, '<?=') !== false) out(['success' => false, 'error' => 'bad_type'], 415);
    $type = 'image'; $ext = $map[$info[2]];
}

$dir = 'files/' . date('Ym');
if (!is_dir(__DIR__ . '/' . $dir) && !@mkdir(__DIR__ . '/' . $dir, 0755, true)) out(['success' => false, 'error' => 'save_failed'], 500);
$name = bin2hex(random_bytes(10)) . '.' . $ext;
if (!move_uploaded_file($f['tmp_name'], __DIR__ . '/' . $dir . '/' . $name)) out(['success' => false, 'error' => 'save_failed'], 500);

$orig = (string)($_POST['name'] ?? $f['name']);
$orig = preg_replace('/[^\p{L}\p{N}._ ()（）\-]/u', '_', basename($orig));
$orig = mb_substr($orig, 0, 120);
out(['success' => true, 'url' => $dir . '/' . $name, 'name' => $orig, 'type' => $type, 'size' => (int)$f['size'], 'w' => $w, 'h' => $h]);
