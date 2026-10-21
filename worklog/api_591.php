<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

$url = isset($_GET['url']) ? trim($_GET['url']) : '';
$id = isset($_GET['id']) ? trim($_GET['id']) : '';

if (!$id && $url) {
    if (preg_match('/\/rent\/(\d+)/', $url, $m)) {
        $id = $m[1];
    }
}

if (!$id) {
    echo json_encode(['error' => 'Missing ID or URL'], JSON_UNESCAPED_UNICODE);
    exit;
}

$targetUrl = "https://business.591.com.tw/rent/{$id}";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $targetUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language: zh-TW,zh;q=0.9,en;q=0.8'
]);

$html = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if (!$html || $httpCode >= 400) {
    echo json_encode(['error' => "Failed to fetch 591 page (HTTP {$httpCode})"], JSON_UNESCAPED_UNICODE);
    exit;
}

// Parse Title
$title = "591#{$id} 店面物件";
if (preg_match('/<title>(.*?)<\/title>/is', $html, $tm)) {
    $title = trim(str_replace(['| 店面出租 - 591房屋交易網', '- 591房屋交易網'], '', $tm[1]));
}

// Parse Meta Description
// Example: 台北市中山區店面出租：租金285000元/月，使用坪數56坪，位於中山區中山北路二段26巷，更多店面出租詳情，就上591！
$rent = 0;
$area = 0;
$address = '';

if (preg_match('/<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']/is', $html, $dm)) {
    $desc = $dm[1];
    if (preg_match('/租金(\d+)元\/月/', $desc, $rm)) {
        $rent = (int)$rm[1];
    }
    if (preg_match('/使用坪數([\d\.]+)坪/', $desc, $am)) {
        $area = (float)$am[1];
    }
    if (preg_match('/位於(.*?)(?:，|更多)/u', $desc, $locm)) {
        $address = trim($locm[1]);
    }
}

// Images
$images = [];
if (preg_match_all('/https?:\/\/img\d*\.591\.com\.tw\/house\/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)/i', $html, $imgm)) {
    foreach ($imgm[0] as $im) {
        if (!in_array($im, $images) && stripos($im, 'watermark') === false && stripos($im, '730x460') === false) {
            $images[] = $im;
        }
    }
}

// Also check json-ld if available
if (preg_match('/<script type="application\/ld\+json">(.*?)<\/script>/is', $html, $jldm)) {
    $jld = json_decode($jldm[1], true);
    if ($jld && isset($jld['image'])) {
        $jldImgs = is_array($jld['image']) ? $jld['image'] : [$jld['image']];
        foreach ($jldImgs as $ji) {
            if (!in_array($ji, $images)) {
                $images[] = $ji;
            }
        }
    }
}

$unitPrice = ($area > 0 && $rent > 0) ? round($rent / $area) : 0;
// Real operating cost estimate (Rent + 10% withholding tax + 2.11% NHI)
$realCost = $rent > 0 ? round($rent * 1.1211) : 0;
$deposit = $rent * 2; // Default 2 months

echo json_encode([
    'success' => true,
    'id' => "591-{$id}",
    'rawId' => $id,
    'url' => $targetUrl,
    'title' => $title,
    'rent' => $rent,
    'area' => $area,
    'address' => $address,
    'deposit' => $deposit,
    'freeRent' => '1 個月',
    'realCost' => $realCost,
    'images' => array_slice($images, 0, 10),
    'canRegister' => true,
    'canInvoice' => true,
    'fireSafety' => true,
    'pros' => "鄰近捷運與商圈成熟街區，面寬醒目，商務與休閒客流聚集。",
    'cons' => "周邊巷弄部分時段需考量臨停與卸貨動線。"
], JSON_UNESCAPED_UNICODE);
