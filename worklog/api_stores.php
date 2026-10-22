<?php
// 公開唯讀：只輸出店面資料（白名單欄位）。不含動態、議題、留言、存證等其他資料。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$file = __DIR__ . '/grounds_data.json';
$data = file_exists($file) ? json_decode(preg_replace('/^\xEF\xBB\xBF/', '', file_get_contents($file)), true) : null;
$keys = ['id','title','titleJa','address','lat','lng','rent','area','deposit','freeRent','realCost','pros','prosJa','cons','consJa','images','status','statusLabel','canRegister','canInvoice','url'];
$out = [];
if (is_array($data) && isset($data['stores']) && is_array($data['stores'])) {
    foreach ($data['stores'] as $s) {
        $row = [];
        foreach ($keys as $k) { if (isset($s[$k])) $row[$k] = $s[$k]; }
        // 只允許 http(s) 或站內檔名的圖片／連結，避免夾帶其他內容
        if (isset($row['url']) && !preg_match('#^(https?://|[\w.-]+\.(jpe?g|png|webp)$)#i', $row['url'])) unset($row['url']);
        if (isset($row['images']) && is_array($row['images'])) {
            $row['images'] = array_values(array_filter($row['images'], function ($u) { return is_string($u) && preg_match('#^(https?://|data:image/|[\w./-]+\.(jpe?g|png|webp)$)#i', $u); }));
        }
        $out[] = $row;
    }
}
echo json_encode(['stores' => $out], JSON_UNESCAPED_UNICODE);
