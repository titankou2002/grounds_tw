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

if ($platform) {
    $detectedPlatform = $platform;
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

// Real-time cURL Scraper
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($ch, CURLOPT_TIMEOUT, 8);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language: zh-TW,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'Cache-Control: no-cache',
    'Pragma: no-cache'
]);

$html = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$effectiveUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
curl_close($ch);

// If anti-bot challenge (403, 503, or Cloudflare / AWS WAF challenge page)
$isChallenge = ($httpCode >= 400) || (stripos($html, 'challenge-error-text') !== false) || (stripos($html, 'x-amzn-waf') !== false) || (stripos($html, 'Just a moment...') !== false);

if ($isChallenge || !$html) {
    // Generate an intelligent structured fallback rather than crashing
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

// Successful HTML parsing
$title = "{$detectedPlatform} 店面物件";
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
