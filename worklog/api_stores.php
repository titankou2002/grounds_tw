<?php
// 公開唯讀：只輸出店面資料（白名單欄位）。不含動態、議題、留言、存證等其他資料。
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$file = __DIR__ . '/grounds_data.json';
require_once __DIR__ . '/lib_images.php';
require_once __DIR__ . '/lib_overrides.php';
$data = wl_migrate_grounds_file($file);
wl_migrate_overrides_file();
$keys = ['id','title','titleJa','address','lat','lng','rent','area','deposit','freeRent','pros','prosJa','cons','consJa','images','status','statusLabel','canRegister','canInvoice','url','unverified','depositText','floor','coverImg'];
$fixFile = __DIR__ . '/store_fixes.json';
$fixes = file_exists($fixFile) ? (json_decode(file_get_contents($fixFile), true) ?: []) : [];
$ov = wl_ov_load();
$out = [];
if (is_array($data) && isset($data['stores']) && is_array($data['stores'])) {
    foreach ($data['stores'] as $s) {
        // 店面資料修正檔：版本較新的欄位覆蓋舊值（null = 刪除該欄位）
        if (isset($s['id'], $fixes[$s['id']]) && (int)($s['fixV'] ?? 0) < (int)($fixes[$s['id']]['fixV'] ?? 0)) {
            foreach ($fixes[$s['id']] as $fk => $fv) { if ($fv === null) unset($s[$fk]); else $s[$fk] = $fv; }
            $s['unverified'] = !empty($fixes[$s['id']]['unverified']);
        }
        $s = wl_ov_apply($s, $ov);   // MAP 頁線上修改永遠最後套用
        $row = [];
        foreach ($keys as $k) { if (isset($s[$k])) $row[$k] = $s[$k]; }
        // 只允許 http(s) 或站內圖檔。data: 一律不輸出（讀檔時已盡量轉成 uploads/）。
        if (isset($row['url']) && !(wl_public_http_url($row['url']) || wl_public_image_ref($row['url']))) unset($row['url']);
        if (isset($row['coverImg']) && !wl_public_image_ref($row['coverImg'])) unset($row['coverImg']);
        if (isset($row['images']) && is_array($row['images'])) {
            $row['images'] = array_values(array_filter($row['images'], 'wl_public_image_ref'));
        }
        $out[] = $row;
    }
}
echo json_encode(['stores' => $out], JSON_UNESCAPED_UNICODE);
