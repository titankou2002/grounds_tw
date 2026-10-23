<?php
// 密碼閘門：輸入正確密碼後，瀏覽器 cookie 記住 365 天
// 密碼存在伺服器上的 worklog/.wl_pw（不進 repo）。檔案不存在時，第一次輸入的密碼就成為密碼
$pwFile = __DIR__ . '/.wl_pw';
$PASSWORD = file_exists($pwFile) ? trim((string)file_get_contents($pwFile)) : '';
$DAYS = 365;
$dir = __DIR__;
$secretFile = $dir . '/.wl_secret';
if (!file_exists($secretFile)) {
    file_put_contents($secretFile, bin2hex(random_bytes(32)));
}
$secret = trim(file_get_contents($secretFile));
$token = hash_hmac('sha256', 'worklog-ok', $secret);
$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');

// 請求的檔案（相對 worklog/）
$base = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/');
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$rel = ltrim(substr($path, strlen($base)), '/');
$rel = rawurldecode($rel);
if ($rel === '' || substr($rel, -1) === '/') $rel .= 'index.html';

// 登入
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['wl_pw'])) {
    if ($PASSWORD === '' && trim((string)$_POST['wl_pw']) !== '') {
        $PASSWORD = trim((string)$_POST['wl_pw']);
        file_put_contents($pwFile, $PASSWORD);
    }
    if ($PASSWORD !== '' && hash_equals($PASSWORD, (string)$_POST['wl_pw'])) {
        setcookie('wl_auth', $token, [
            'expires' => time() + 86400 * $DAYS, 'path' => $base ?: '/',
            'secure' => $https, 'httponly' => true, 'samesite' => 'Lax',
        ]);
        header('Location: ' . $base . '/');
        exit;
    }
    sleep(1);
    $error = true;
}

// 不需密碼：獨立 MAP 頁與它的唯讀店面 API、圖片、圖示
$publicAsset = preg_match('/^(map\.html|api_stores\.php|manifest\.json|favicon[\w-]*\.png|apple-touch-icon\.png|(uploads\/)?[\w.-]+\.(jpe?g|png|webp))$/i', $rel);
$ok = $publicAsset || isset($_COOKIE['wl_auth']) && hash_equals($token, $_COOKIE['wl_auth']);

if (!$ok) {
    if (preg_match('/\.(php|json)$/', $rel)) {
        http_response_code(401);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['success' => false, 'error' => 'Unauthorized']);
        exit;
    }
    http_response_code(401);
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: no-store');
    ?><!DOCTYPE html>
<html lang="zh-TW"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>grounds Taiwan Worklog</title>
<style>body{font-family:-apple-system,"Noto Sans TC",sans-serif;background:#f6f6f4;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
form{background:#fff;padding:32px 28px;border-radius:14px;border:1px solid #ddd;width:min(320px,86vw);text-align:center}
h1{font-size:17px;margin:0 0 4px}p{font-size:12.5px;color:#777;margin:0 0 18px}
input{width:100%;box-sizing:border-box;padding:10px 12px;font-size:16px;border:1px solid #ccc;border-radius:8px;margin-bottom:12px}
button{width:100%;padding:10px;font-size:15px;font-weight:700;background:#111;color:#fff;border:0;border-radius:8px;cursor:pointer}
.e{color:#b91c1c;font-size:12.5px;margin-bottom:10px}</style></head>
<body><form method="post"><h1>grounds Taiwan Worklog</h1><p><?php echo file_exists($pwFile) ? 'パスワード / 請輸入密碼' : '初回設定：好きなパスワードを入力 / 首次使用：請設定密碼'; ?></p>
<?php if (!empty($error)) echo '<div class="e">パスワードが違います / 密碼錯誤</div>'; ?>
<input type="password" name="wl_pw" autofocus autocomplete="current-password" inputmode="numeric">
<button type="submit">OK</button></form></body></html>
<?php
    exit;
}

// 已登入：提供檔案
$file = realpath($dir . '/' . $rel);
if ($file === false || strpos($file, $dir . DIRECTORY_SEPARATOR) !== 0 || !is_file($file)
    || basename($file)[0] === '.' || basename($file) === 'gate.php') {
    http_response_code(404);
    echo 'Not found';
    exit;
}
if (substr($file, -4) === '.php') {
    chdir($dir);
    include $file;
    exit;
}
$types = ['html'=>'text/html; charset=utf-8','json'=>'application/json; charset=utf-8','png'=>'image/png','jpg'=>'image/jpeg','jpeg'=>'image/jpeg','webp'=>'image/webp','md'=>'text/markdown; charset=utf-8','js'=>'application/javascript','css'=>'text/css','svg'=>'image/svg+xml'];
$ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
header('Content-Type: ' . ($types[$ext] ?? 'application/octet-stream'));
if ($ext === 'html' || $ext === 'json') header('Cache-Control: no-cache, no-store, must-revalidate');
readfile($file);
