<?php
// MAP 頁的線上修改（欄位、備註、補傳照片）。存在 store_overrides.json（伺服器端，不進 repo），永遠蓋在原資料上。
const WL_OV_FILE = __DIR__ . '/store_overrides.json';

function wl_ov_load() {
    $d = file_exists(WL_OV_FILE) ? json_decode((string)file_get_contents(WL_OV_FILE), true) : null;
    return is_array($d) ? $d : [];
}

function wl_ov_apply(array $s, array $ov) {
    $o = $ov[$s['id'] ?? ''] ?? null;
    if (!$o) return $s;
    foreach (($o['fields'] ?? []) as $k => $v) { if ($v === null) unset($s[$k]); else $s[$k] = $v; }
    if (!empty($o['fields'])) $s['unverified'] = false;
    $imgs = array_values(array_diff($s['images'] ?? [], $o['imgDel'] ?? []));
    foreach (($o['imgAdd'] ?? []) as $u) { if (!in_array($u, $imgs, true)) $imgs[] = $u; }
    if ($imgs || isset($s['images']) || !empty($o['imgAdd'])) $s['images'] = $imgs;
    if (!empty($o['notes'])) $s['notes'] = $o['notes'];
    return $s;
}
