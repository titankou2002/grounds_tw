<?php
// MAP 頁的線上修改（欄位、備註、補傳照片）。存在 store_overrides.json（伺服器端，不進 repo），永遠蓋在原資料上。
const WL_OV_FILE = __DIR__ . '/store_overrides.json';
require_once __DIR__ . '/lib_images.php';

function wl_ov_load() {
    $d = file_exists(WL_OV_FILE) ? json_decode((string)file_get_contents(WL_OV_FILE), true) : null;
    return is_array($d) ? $d : [];
}

function wl_ov_image_ok($u) {
    return is_string($u) && $u !== '' && (wl_public_image_ref($u) || wl_public_http_url($u));
}

function wl_ov_apply(array $s, array $ov) {
    $o = $ov[$s['id'] ?? ''] ?? null;
    if (!$o) return $s;
    foreach (($o['fields'] ?? []) as $k => $v) { if ($v === null) unset($s[$k]); else $s[$k] = $v; }
    if (!empty($o['fields'])) $s['unverified'] = false;
    // imgOrder 是編輯後的完整順序（含新上傳、刪除、排序）。沒有它才沿用舊的增刪清單。
    if (array_key_exists('imgOrder', $o) && is_array($o['imgOrder'])) {
        $imgs = array();
        foreach ($o['imgOrder'] as $u) {
            if (!wl_ov_image_ok($u) || in_array($u, $imgs, true)) continue;
            $imgs[] = $u;
        }
        $s['images'] = $imgs;
    } else {
        $imgs = array_values(array_diff($s['images'] ?? [], $o['imgDel'] ?? []));
        foreach (($o['imgAdd'] ?? []) as $u) { if (!in_array($u, $imgs, true)) $imgs[] = $u; }
        if ($imgs || isset($s['images']) || !empty($o['imgAdd'])) $s['images'] = $imgs;
    }
    if (!empty($o['notes'])) $s['notes'] = $o['notes'];
    if (!empty($o['ts'])) $s['editedAt'] = max((int)($s['editedAt'] ?? 0), (int)$o['ts']);
    return $s;
}
