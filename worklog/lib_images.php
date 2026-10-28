<?php
// 店面照片、以及動態內文裡的 data:image/...;base64，
// 會在讀寫時轉成 uploads/ 檔（同一張圖永遠同一個檔名，可重跑）。
// 轉檔失敗（磁碟寫不入）就保留原本字串，不把照片弄丟。
// 不是圖片的 data: 店面欄位會丟掉；貼在內文裡、轉不了的則原樣留著。

function wl_atomic_write($path, $contents) {
    $tmp = $path . '.tmp.' . bin2hex(random_bytes(4));
    if (file_put_contents($tmp, $contents) === false) {
        @unlink($tmp);
        return false;
    }
    if (!@rename($tmp, $path)) {
        @unlink($tmp);
        return false;
    }
    return true;
}

// 回傳相對路徑字串＝已存檔；null＝不是可用的圖片（可丟）；false＝是圖片但寫不進去（要留著）
function wl_data_image_to_file($dataUrl) {
    if (!is_string($dataUrl)) return null;
    if (!preg_match('#^data:image/(jpeg|jpg|png|gif|webp)\b#i', $dataUrl)) return null;
    $comma = strpos($dataUrl, ',');
    if ($comma === false) return null;
    $b64 = preg_replace('/\s+/', '', substr($dataUrl, $comma + 1));
    if (!is_string($b64) || $b64 === '' || !preg_match('#^[A-Za-z0-9+/=]+$#', $b64)) return null;
    $raw = base64_decode($b64, true);
    if ($raw === false || strlen($raw) < 16) return null;
    if (strlen($raw) > 15 * 1024 * 1024) return false;
    if (stripos($raw, '<?php') !== false || strpos($raw, '<?=') !== false) return null;
    $info = @getimagesizefromstring($raw);
    $exts = array(IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_GIF => 'gif', IMAGETYPE_WEBP => 'webp');
    if (!$info || !isset($exts[$info[2]])) return null;
    $name = 'uploads/' . hash('sha256', $raw) . '.' . $exts[$info[2]];
    $dir = __DIR__ . '/uploads';
    if (!is_dir($dir) && !@mkdir($dir, 0755, true)) return false;
    $dest = __DIR__ . '/' . $name;
    if (is_file($dest) && filesize($dest) === strlen($raw)) return $name;
    $tmp = $dest . '.tmp.' . bin2hex(random_bytes(4));
    if (file_put_contents($tmp, $raw) === false) {
        @unlink($tmp);
        return false;
    }
    if (!@rename($tmp, $dest)) {
        @unlink($tmp);
        return false;
    }
    return $name;
}

function wl_replace_data_image(&$value) {
    if (!is_string($value) || stripos($value, 'data:') !== 0) return false;
    $saved = wl_data_image_to_file($value);
    if ($saved === false) return false;
    if (is_string($saved) && $saved !== '') {
        $value = $saved;
        return true;
    }
    $value = null;
    return true;
}

function wl_scrub_store_images(&$store) {
    if (!is_array($store)) return false;
    $changed = false;
    if (isset($store['images']) && is_array($store['images'])) {
        $out = array();
        foreach ($store['images'] as $img) {
            if (!is_string($img)) continue;
            if (stripos($img, 'data:') === 0) {
                $saved = wl_data_image_to_file($img);
                if ($saved === false) {
                    $out[] = $img;
                } elseif (is_string($saved) && $saved !== '') {
                    $out[] = $saved;
                    $changed = true;
                } else {
                    $changed = true;
                }
            } else {
                $out[] = $img;
            }
        }
        if ($changed) $store['images'] = array_values(array_unique($out));
    }
    foreach (array('coverImg', 'url') as $k) {
        if (!isset($store[$k]) || !is_string($store[$k]) || stripos($store[$k], 'data:') !== 0) continue;
        $saved = wl_data_image_to_file($store[$k]);
        if ($saved === false) continue;
        $changed = true;
        if (is_string($saved) && $saved !== '') $store[$k] = $saved;
        else unset($store[$k]);
    }
    return $changed;
}

// 內文、回覆、附件網址裡的 data:image 換成 uploads/ 路徑。
// 寫不進去就留著原本的字，下次再試。不是圖片的 data: 不刪，避免把人打的字弄掉。
function wl_replace_embedded_data_images(&$text) {
    if (!is_string($text) || stripos($text, 'data:image/') === false) return false;
    $changed = false;
    $out = '';
    $i = 0;
    $len = strlen($text);
    while (($p = stripos($text, 'data:image/', $i)) !== false) {
        $out .= substr($text, $i, $p - $i);
        $end = $p;
        while ($end < $len) {
            $c = $text[$end];
            if ($c === '"' || $c === "'" || $c === '<' || $c === '>' || $c === ' ' || $c === "\n" || $c === "\r" || $c === "\t" || $c === ')') break;
            $end++;
        }
        if ($end <= $p) $end = min($len, $p + 11);
        $url = substr($text, $p, $end - $p);
        $saved = wl_data_image_to_file($url);
        if (is_string($saved) && $saved !== '') {
            $out .= $saved;
            $changed = true;
        } elseif ($saved === null && strlen($url) > 500) {
            // 很長、又不是真的圖片：拿掉，避免每次讀檔都再解一次。短的內文不動。
            $changed = true;
        } else {
            $out .= $url;
        }
        $i = $end;
    }
    if (!$changed) return false;
    $out .= substr($text, $i);
    $text = $out;
    return true;
}

function wl_scrub_embedded_images(&$node) {
    if (is_string($node)) return wl_replace_embedded_data_images($node);
    if (!is_array($node)) return false;
    $changed = false;
    foreach ($node as &$child) {
        if (wl_scrub_embedded_images($child)) $changed = true;
    }
    unset($child);
    return $changed;
}

function wl_scrub_data_array(&$data) {
    if (!is_array($data)) return false;
    $changed = false;
    if (isset($data['stores']) && is_array($data['stores'])) {
        foreach ($data['stores'] as $i => $s) {
            if (is_array($s) && wl_scrub_store_images($data['stores'][$i])) $changed = true;
        }
    }
    // 動態與審議裡的 data: 照片（比較表內文、舊附件）同一把流程處理
    foreach (array('posts', 'boardTopics') as $key) {
        if (isset($data[$key]) && is_array($data[$key]) && wl_scrub_embedded_images($data[$key])) $changed = true;
    }
    return $changed;
}

function wl_scrub_override_record(&$o) {
    if (!is_array($o)) return false;
    $changed = false;
    if (isset($o['fields']) && is_array($o['fields'])) {
        foreach (array('coverImg', 'url') as $k) {
            if (!isset($o['fields'][$k]) || !is_string($o['fields'][$k]) || stripos($o['fields'][$k], 'data:') !== 0) continue;
            $saved = wl_data_image_to_file($o['fields'][$k]);
            if ($saved === false) continue;
            $changed = true;
            if (is_string($saved) && $saved !== '') $o['fields'][$k] = $saved;
            else unset($o['fields'][$k]);
        }
    }
    if (isset($o['imgOrder']) && is_array($o['imgOrder'])) {
        $ord = array();
        $ordChanged = false;
        foreach ($o['imgOrder'] as $u) {
            if (!is_string($u)) continue;
            if (stripos($u, 'data:') === 0) {
                $saved = wl_data_image_to_file($u);
                $ordChanged = true;
                if (is_string($saved) && $saved !== '') $ord[] = $saved;
            } else $ord[] = $u;
        }
        if ($ordChanged) {
            $o['imgOrder'] = array_values(array_unique($ord));
            $changed = true;
        }
    }
    if (isset($o['imgAdd']) && is_array($o['imgAdd'])) {
        $add = array();
        $imgChanged = false;
        foreach ($o['imgAdd'] as $u) {
            if (!is_string($u)) continue;
            if (stripos($u, 'data:') === 0) {
                $saved = wl_data_image_to_file($u);
                if ($saved === false) $add[] = $u;
                elseif (is_string($saved) && $saved !== '') { $add[] = $saved; $imgChanged = true; }
                else $imgChanged = true;
            } else $add[] = $u;
        }
        if ($imgChanged) {
            $o['imgAdd'] = array_values(array_unique($add));
            $changed = true;
        }
    }
    return $changed;
}

// 呼叫端如果已經握住 grounds_data.lock，不要再呼叫會上同一把鎖的函式（會自己等自己）。
function wl_migrate_grounds_file($path) {
    $lock = fopen(__DIR__ . '/grounds_data.lock', 'c');
    if ($lock) flock($lock, LOCK_EX);
    $data = null;
    $raw = '';
    if (is_file($path)) {
        $raw = preg_replace('/^\xEF\xBB\xBF/', '', (string)file_get_contents($path));
        $decoded = json_decode($raw, true);
        if (is_array($decoded)) $data = $decoded;
    }
    if (is_array($data) && strpos($raw, 'data:') !== false && wl_scrub_data_array($data)) {
        $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        if ($json !== false) wl_atomic_write($path, $json);
    }
    if ($lock) { flock($lock, LOCK_UN); fclose($lock); }
    return $data;
}

function wl_migrate_overrides_file() {
    if (!defined('WL_OV_FILE')) return;
    if (!is_file(WL_OV_FILE)) return;
    $fp = fopen(WL_OV_FILE, 'c+');
    if (!$fp) return;
    flock($fp, LOCK_EX);
    $raw = stream_get_contents($fp);
    $ov = $raw ? json_decode($raw, true) : array();
    if (!is_array($ov)) $ov = array();
    $changed = false;
    if (strpos((string)$raw, 'data:') !== false) {
        foreach ($ov as $id => $rec) {
            if (is_array($rec) && wl_scrub_override_record($ov[$id])) $changed = true;
        }
    }
    if ($changed) {
        $json = json_encode($ov, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        if ($json !== false) {
            ftruncate($fp, 0);
            rewind($fp);
            fwrite($fp, $json);
            fflush($fp);
        }
    }
    flock($fp, LOCK_UN);
    fclose($fp);
}

function wl_public_http_url($u) {
    if (!is_string($u) || $u === '' || stripos($u, 'data:') === 0) return false;
    if (!preg_match('#^https?://#i', $u)) return false;
    $p = parse_url($u);
    if (!$p || empty($p['host'])) return false;
    $scheme = strtolower($p['scheme']);
    if ($scheme !== 'http' && $scheme !== 'https') return false;
    if (!empty($p['user']) || !empty($p['pass'])) return false;
    return true;
}

function wl_public_image_ref($u) {
    if (!is_string($u) || $u === '' || strpos($u, '..') !== false || strpos($u, '\\') !== false) return false;
    if (stripos($u, 'data:') === 0 || preg_match('#^\s*javascript:#i', $u)) return false;
    if (wl_public_http_url($u)) return true;
    return (bool)preg_match('#^(?:uploads/|files/)?[\w./-]+\.(?:jpe?g|png|gif|webp)$#i', $u);
}
