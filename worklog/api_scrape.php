<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit;
}

$url = isset($_GET['url']) ? trim($_GET['url']) : '';
$id = isset($_GET['id']) ? trim($_GET['id']) : '';
$platform = isset($_GET['platform']) ? strtolower(trim($_GET['platform'])) : '';

// Built-in verified database for instantaneous authentic resolution
// (bypasses Cloudflare / AWS WAF anti-bot blocks on servers)
$KNOWN_TARGETS = [];   // 不內建任何店面資料：數字只能來自網頁本身或人工核對

// Detect platform and ID from URL if provided
$detectedPlatform = '591';
$extractedId = $id;

if ($url) {
    if (preg_match('/rakuya\.com\.tw/i', $url)) {
        $detectedPlatform = 'rakuya';
        if (preg_match('/rent\/([a-zA-Z0-9]+)/i', $url, $m)) {
            $extractedId = $m[1];
        } elseif (preg_match('/ehid=([a-zA-Z0-9]+)/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/yungching\.com\.tw/i', $url)) {
        $detectedPlatform = 'yungching';
        if (preg_match('/case\/([a-zA-Z0-9]+)/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/sinyi\.com\.tw/i', $url)) {
        $detectedPlatform = 'sinyi';
        if (preg_match('/rentItem\/([a-zA-Z0-9]+)/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/hbhousing\.com\.tw/i', $url)) {
        $detectedPlatform = 'hbhousing';
        if (preg_match('/([a-zA-Z0-9]{5,})/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/cthouse\.com\.tw/i', $url)) {
        $detectedPlatform = 'cthouse';
        if (preg_match('/([a-zA-Z0-9]{5,})/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/twhg\.com\.tw/i', $url)) {
        $detectedPlatform = 'twhg';
        if (preg_match('/([a-zA-Z0-9]{5,})/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } elseif (preg_match('/591\.com\.tw/i', $url)) {
        $detectedPlatform = '591';
        if (preg_match('/\/rent\/(\d+)/i', $url, $m)) {
            $extractedId = $m[1];
        } elseif (preg_match('/rent-detail-(\d+)/i', $url, $m)) {
            $extractedId = $m[1];
        }
    } else {
        $detectedPlatform = 'general';
        if (preg_match('/\/(\d{5,})/i', $url, $m)) {
            $extractedId = $m[1];
        }
    }
}

// 有網址時以網址的主機為準，不讓 platform 參數把任意網址說成 591。
// 只有「沒給網址、只給物件編號」時，才用 platform 組出允許清單裡的網址。
$allowedPlatforms = array('591', 'rakuya', 'yungching', 'sinyi', 'hbhousing', 'cthouse', 'twhg');
if (!$url && $platform && in_array($platform, $allowedPlatforms, true)) {
    $detectedPlatform = $platform;
}
if ($extractedId !== '' && !preg_match('/^[A-Za-z0-9]{1,40}$/', $extractedId)) {
    $extractedId = '';
}

$lookupKey = strtolower($extractedId);

// Check if matched in built-in verified targets
if ($lookupKey && isset($KNOWN_TARGETS[$lookupKey])) {
    $item = $KNOWN_TARGETS[$lookupKey];
    $item['success'] = true;
    $item['cached'] = true;
    echo json_encode($item, JSON_UNESCAPED_UNICODE);
    exit;
}

// If no URL provided and ID was checked, try standard 591
if (!$url && $extractedId) {
    if ($detectedPlatform === '591') {
        $url = "https://business.591.com.tw/rent/{$extractedId}";
    } elseif ($detectedPlatform === 'rakuya') {
        $url = "https://community.rakuya.com.tw/509/rent/{$extractedId}";
    } elseif ($detectedPlatform === 'yungching') {
        $url = "https://rent.yungching.com.tw/case/{$extractedId}";
    } elseif ($detectedPlatform === 'sinyi') {
        $url = "https://rent.sinyi.com.tw/rentItem/{$extractedId}";
    }
}

if (!$url) {
    echo json_encode(['error' => 'Missing URL or target ID', 'success' => false], JSON_UNESCAPED_UNICODE);
    exit;
}

require_once __DIR__ . '/lib_fetch.php';

$platformNames = [
    'rakuya' => '樂屋網',
    'yungching' => '永慶房屋',
    'sinyi' => '信義房屋',
    '591' => '591 房屋交易',
    'hbhousing' => '住商不動產',
    'cthouse' => '中信房屋',
    'twhg' => '台灣房屋',
    'general' => '房仲平台'
];

// 不在允許的房仲主機就不要連。允許的主機若解析到內網或查無 IP，也不連，改走下面的「讀不到網頁」空白結果。
$targetOk = wl_validate_fetch_target($url);
$html = '';
$httpCode = 0;
$effectiveUrl = $url;
$hostForCheck = parse_url($url, PHP_URL_HOST);
$allowedHost = $hostForCheck && wl_host_allowed($hostForCheck);
if (!$targetOk['ok'] && !($allowedHost && in_array($targetOk['error'], array('dns', 'ip'), true))) {
    $safeId = ($extractedId !== '' && preg_match('/^[A-Za-z0-9]{1,40}$/', $extractedId)) ? $extractedId : substr(md5($url), 0, 8);
    $pName = isset($platformNames[$detectedPlatform]) ? $platformNames[$detectedPlatform] : '房仲網';
    $echoUrl = '';
    $pu = parse_url($url);
    if ($pu && !empty($pu['scheme']) && preg_match('#^https?$#i', $pu['scheme']) && empty($pu['user']) && empty($pu['pass']) && !empty($pu['host'])) {
        $echoUrl = $url;
    }
    echo json_encode([
        'success' => true,
        'fallback' => true,
        'unverified' => true,
        'unsupported' => true,
        'platform' => $detectedPlatform,
        'platformName' => $pName,
        'id' => "{$detectedPlatform}-{$safeId}",
        'rawId' => $safeId,
        'url' => $echoUrl,
        'title' => '',
        'rent' => null,
        'area' => null,
        'address' => '',
        'images' => [],
        'deposit' => null,
        'freeRent' => ''
    ], JSON_UNESCAPED_UNICODE);
    exit;
}
if ($targetOk['ok']) {
    $fetched = wl_http_get($url);
    $html = !empty($fetched['ok']) ? $fetched['body'] : '';
    $httpCode = (int)(isset($fetched['code']) ? $fetched['code'] : 0);
    if (!empty($fetched['ok']) && !empty($fetched['url'])) $effectiveUrl = $fetched['url'];
}

// If anti-bot challenge (403, 503, or Cloudflare / AWS WAF challenge page)
$isChallenge = ($httpCode >= 400) || ($html !== '' && ((stripos($html, 'challenge-error-text') !== false) || (stripos($html, 'x-amzn-waf') !== false) || (stripos($html, 'Just a moment...') !== false)));

if ($isChallenge || !$html) {
    $pName = isset($platformNames[$detectedPlatform]) ? $platformNames[$detectedPlatform] : '房仲網';
    $safeId = $extractedId ?: substr(md5($url), 0, 8);
    $propId = "{$detectedPlatform}-{$safeId}";

    // 讀不到網頁：不編任何資料，明確回報「未驗證」
    echo json_encode([
        'success' => true,
        'fallback' => true,
        'unverified' => true,
        'platform' => $detectedPlatform,
        'platformName' => $pName,
        'id' => $propId,
        'rawId' => $safeId,
        'url' => $url,
        'title' => '',
        'rent' => 0,
        'area' => 0,
        'address' => '',
        'images' => []
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Successful HTML parsing。標題只採用網頁自己寫的，不另外編一個。
$title = '';
if (preg_match('/<title>(.*?)<\/title>/is', $html, $tm)) {
    $cleanT = trim(preg_replace('/[-|_].*$/', '', $tm[1]));
    if ($cleanT) $title = $cleanT;
}
if (preg_match('/<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']/is', $html, $ogTm)) {
    $title = trim($ogTm[1]);
}

$desc = '';
if (preg_match('/<meta\s+(?:property=["\']og:description["\']|name=["\']description["\'])\s+content=["\'](.*?)["\']/is', $html, $dm)) {
    $desc = $dm[1];
}

$rent = 0;
$area = 0;
$address = '';
$floor = '';

// Extract rent
if (preg_match('/租金[\s:：]*(\d+(?:,\d{3})*)[\s元]*\/月/u', $desc . ' ' . $html, $rm)) {
    $rent = (int)str_replace(',', '', $rm[1]);
} elseif (preg_match('/(\d+(?:,\d{3})*)[\s]*元\/月/u', $desc . ' ' . $html, $rm)) {
    $rent = (int)str_replace(',', '', $rm[1]);
} elseif (preg_match('/(\d+)[\s]*萬\/月/u', $desc . ' ' . $html, $rm)) {
    $rent = (int)$rm[1] * 10000;
}

// Extract area
if (preg_match('/(?:使用坪數|總坪數|坪數|面積)[\s:：]*([\d\.]+)[\s]*坪/u', $desc . ' ' . $html, $am)) {
    $area = (float)$am[1];
} elseif (preg_match('/([\d\.]+)[\s]*坪/u', $desc, $am)) {
    $area = (float)$am[1];
}

// Extract address
if (preg_match('/位於[\s:：]*([台臺北新北桃竹中彰雲嘉南高屏宜花東基][市縣].*?)(?:，|。|更多|\s)/u', $desc . ' ' . $html, $locm)) {
    $address = trim($locm[1]);
} elseif (preg_match('/([台臺北新北桃竹中彰雲嘉南高屏宜花東基][市縣][^\s"\'<>]{4,25}(?:路|街|巷|段|號))/u', $desc . ' ' . $html, $locm)) {
    $address = trim($locm[1]);
}

// Extract images
$images = [];
if (preg_match('/<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']/is', $html, $ogImg)) {
    if (filter_var($ogImg[1], FILTER_VALIDATE_URL)) {
        $images[] = $ogImg[1];
    }
}
if (preg_match_all('/https?:\/\/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)/i', $html, $allImgs)) {
    foreach ($allImgs[0] as $imgUrl) {
        if (!in_array($imgUrl, $images) && 
            stripos($imgUrl, 'logo') === false && 
            stripos($imgUrl, 'icon') === false &&
            stripos($imgUrl, 'avatar') === false &&
            count($images) < 8) {
            $images[] = $imgUrl;
        }
    }
}

$safeId = $extractedId ?: substr(md5($url), 0, 8);
$unitPrice = ($area > 0 && $rent > 0) ? round($rent / $area) : 0;
$realCost = $rent > 0 ? round($rent * 1.1211) : 0;
$deposit = 0;   // 押金網頁多半寫「面議／N個月」，不推測

echo json_encode([
    'success' => true,
    'unverified' => true,   // 解析結果一律視為未核對，需人工確認
    'platform' => $detectedPlatform,
    'id' => "{$detectedPlatform}-{$safeId}",
    'rawId' => $safeId,
    'url' => $effectiveUrl ?: $url,
    'title' => $title,
    'titleJa' => $title,
    'rent' => $rent,
    'area' => $area,
    'unitPrice' => $unitPrice,
    'deposit' => $deposit,
    'freeRent' => '洽詢',
    'realCost' => $realCost,
    'address' => $address,
    'floor' => $floor,
    'lat' => null,
    'lng' => null,
    'images' => $images,
    'canRegister' => null,
    'canInvoice' => null,
    'fireSafety' => null,
    'pros' => '',
    'cons' => ''
], JSON_UNESCAPED_UNICODE);
