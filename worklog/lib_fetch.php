<?php
// 只抓房仲網站。每個網址（含轉址的每一跳）都要：
// 主機在允許清單、解析出的 IP 不是內網／本機／metadata，而且 curl 鎖在剛才查到的 IP 上。

function wl_listing_bases() {
    return array('591.com.tw', 'rakuya.com.tw', 'yungching.com.tw', 'sinyi.com.tw', 'hbhousing.com.tw', 'cthouse.com.tw', 'twhg.com.tw');
}

function wl_host_allowed($host) {
    $host = strtolower(rtrim((string)$host, '.'));
    if ($host === '' || !preg_match('/^[a-z0-9.-]+$/', $host)) return false;
    if (strpos($host, '..') !== false) return false;
    if ($host[0] === '.' || substr($host, -1) === '.' || $host[0] === '-') return false;
    if (filter_var($host, FILTER_VALIDATE_IP)) return false;
    foreach (wl_listing_bases() as $base) {
        if ($host === $base || substr($host, -strlen($base) - 1) === '.' . $base) return true;
    }
    return false;
}

function wl_ipv4_blocked($ip) {
    $long = ip2long($ip);
    if ($long === false) return true;
    $cidrs = array(
        array('0.0.0.0', 8),
        array('10.0.0.0', 8),
        array('100.64.0.0', 10),
        array('127.0.0.0', 8),
        array('169.254.0.0', 16),
        array('172.16.0.0', 12),
        array('192.0.0.0', 24),
        array('192.0.2.0', 24),
        array('192.168.0.0', 16),
        array('198.18.0.0', 15),
        array('198.51.100.0', 24),
        array('203.0.113.0', 24),
        array('224.0.0.0', 4),
        array('240.0.0.0', 4),
    );
    foreach ($cidrs as $c) {
        $mask = ($c[1] === 0) ? 0 : (-1 << (32 - $c[1]));
        $net = ip2long($c[0]);
        if (($long & $mask) === ($net & $mask)) return true;
    }
    return false;
}

function wl_ip_blocked($ip) {
    $ip = trim((string)$ip);
    if ($ip === '') return true;
    if (stripos($ip, '::ffff:') === 0) {
        $v4 = substr($ip, 7);
        if (filter_var($v4, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) return wl_ip_blocked($v4);
    }
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) return wl_ipv4_blocked($ip);
    if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) return true;
    $bin = @inet_pton($ip);
    if ($bin === false || strlen($bin) !== 16) return true;
    if ($bin === inet_pton('::') || $bin === inet_pton('::1')) return true;
    $b0 = ord($bin[0]);
    $b1 = ord($bin[1]);
    if (($b0 & 0xFE) === 0xFC) return true;                 // fc00::/7 唯一本機
    if ($b0 === 0xFE && ($b1 & 0xC0) === 0x80) return true; // fe80::/10 鏈路本機
    if ($b0 === 0xFF) return true;                          // 多播
    // IPv4-mapped
    if (substr($bin, 0, 12) === "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff") {
        $v4 = inet_ntop(substr($bin, 12, 4));
        if ($v4 !== false && wl_ip_blocked($v4)) return true;
    }
    // 6to4 2002::/16 把 IPv4 嵌在裡面
    if ($b0 === 0x20 && $b1 === 0x02) {
        $v4 = inet_ntop(substr($bin, 2, 4));
        if ($v4 !== false && wl_ip_blocked($v4)) return true;
    }
    // NAT64 64:ff9b::/96（前 12 bytes 是前綴，後 4 bytes 是 IPv4）
    $nat = @inet_pton('64:ff9b::');
    if ($nat !== false && substr($bin, 0, 12) === substr($nat, 0, 12)) {
        $v4 = inet_ntop(substr($bin, 12, 4));
        if ($v4 !== false && wl_ip_blocked($v4)) return true;
    }
    return false;
}

function wl_resolve_host_ips($host) {
    $ips = array();
    if (function_exists('dns_get_record')) {
        $a = @dns_get_record($host, DNS_A);
        $aaaa = @dns_get_record($host, DNS_AAAA);
        foreach (array_merge(is_array($a) ? $a : array(), is_array($aaaa) ? $aaaa : array()) as $row) {
            if (!empty($row['ip'])) $ips[] = $row['ip'];
            if (!empty($row['ipv6'])) $ips[] = $row['ipv6'];
        }
    }
    if (!$ips) {
        $v4 = @gethostbynamel($host);
        if (is_array($v4)) $ips = array_merge($ips, $v4);
    }
    $out = array();
    foreach ($ips as $ip) {
        if (is_string($ip) && $ip !== '' && !in_array($ip, $out, true)) $out[] = $ip;
    }
    return $out;
}

function wl_resolve_location($base, $loc) {
    $loc = trim((string)$loc);
    if ($loc === '') return '';
    if (preg_match('#^https?://#i', $loc)) return $loc;
    $p = parse_url($base);
    if (!$p || empty($p['host']) || empty($p['scheme'])) return '';
    $origin = $p['scheme'] . '://' . $p['host'] . (isset($p['port']) ? ':' . $p['port'] : '');
    if (strpos($loc, '//') === 0) return $p['scheme'] . ':' . $loc;
    if (isset($loc[0]) && $loc[0] === '/') return $origin . $loc;
    $path = isset($p['path']) ? $p['path'] : '/';
    $dir = preg_replace('#/[^/]*$#', '/', $path);
    return $origin . $dir . $loc;
}

// 回傳 array(ok, url, resolve, error)。ok 時 resolve 是 curl CURLOPT_RESOLVE 用的清單。
function wl_validate_fetch_target($url) {
    $fail = function ($why) { return array('ok' => false, 'url' => '', 'resolve' => array(), 'error' => $why); };
    $url = trim((string)$url);
    if ($url === '' || strlen($url) > 2000) return $fail('url');
    if (!preg_match('#^https?://#i', $url)) return $fail('scheme');
    $p = parse_url($url);
    if (!$p || empty($p['scheme']) || empty($p['host'])) return $fail('url');
    if (!empty($p['user']) || !empty($p['pass'])) return $fail('userinfo');
    $scheme = strtolower($p['scheme']);
    if ($scheme !== 'http' && $scheme !== 'https') return $fail('scheme');
    $port = isset($p['port']) ? (int)$p['port'] : ($scheme === 'https' ? 443 : 80);
    if ($scheme === 'https' && $port !== 443) return $fail('port');
    if ($scheme === 'http' && $port !== 80) return $fail('port');
    $host = $p['host'];
    if (!wl_host_allowed($host)) return $fail('host');
    $ips = wl_resolve_host_ips($host);
    if (!$ips) return $fail('dns');
    $resolve = array();
    foreach ($ips as $ip) {
        if (wl_ip_blocked($ip)) return $fail('ip');
        if (strpos($ip, ':') !== false) $resolve[] = $host . ':' . $port . ':[' . $ip . ']';
        else $resolve[] = $host . ':' . $port . ':' . $ip;
    }
    return array('ok' => true, 'url' => $url, 'resolve' => $resolve, 'error' => '', 'host' => $host, 'port' => $port);
}

function wl_curl_once($target, $timeoutSec) {
    $body = '';
    $location = '';
    $limit = 2 * 1024 * 1024;
    $ch = curl_init();
    $opts = array(
        CURLOPT_URL => $target['url'],
        CURLOPT_RETURNTRANSFER => false,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_CONNECTTIMEOUT => min(5, $timeoutSec),
        CURLOPT_TIMEOUT => $timeoutSec,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        CURLOPT_RESOLVE => $target['resolve'],
        CURLOPT_HTTPHEADER => array(
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language: zh-TW,zh;q=0.9,ja;q=0.8,en;q=0.7',
            'Cache-Control: no-cache',
            'Pragma: no-cache',
        ),
    );
    if (empty($target['has_v6'])) $opts[CURLOPT_IPRESOLVE] = CURL_IPRESOLVE_V4;
    curl_setopt_array($ch, $opts);
    curl_setopt($ch, CURLOPT_HEADERFUNCTION, function ($ch, $header) use (&$location) {
        if (preg_match('/^Location:\s*(\S+)/i', $header, $m)) $location = trim($m[1]);
        return strlen($header);
    });
    curl_setopt($ch, CURLOPT_WRITEFUNCTION, function ($ch, $chunk) use (&$body, $limit) {
        $body .= $chunk;
        if (strlen($body) > $limit) return 0;
        return strlen($chunk);
    });
    curl_exec($ch);
    $errno = curl_errno($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $tooBig = ($errno === CURLE_WRITE_ERROR && strlen($body) > $limit);
    if ($tooBig) return array('ok' => false, 'redirect' => '', 'body' => '', 'code' => 0);
    if ($code >= 300 && $code < 400 && $location !== '') {
        return array('ok' => false, 'redirect' => $location, 'body' => '', 'code' => $code);
    }
    if ($errno !== 0 || $code < 200 || $code >= 300) {
        return array('ok' => false, 'redirect' => '', 'body' => '', 'code' => $code);
    }
    return array('ok' => true, 'redirect' => '', 'body' => $body, 'code' => $code);
}

function wl_http_get($startUrl) {
    $deadline = microtime(true) + 8.0;
    $current = $startUrl;
    $seen = array();
    for ($hop = 0; $hop < 4; $hop++) {
        if (isset($seen[$current])) return array('ok' => false, 'body' => '', 'code' => 0, 'url' => '', 'error' => 'loop');
        $seen[$current] = true;
        $target = wl_validate_fetch_target($current);
        if (!$target['ok']) return array('ok' => false, 'body' => '', 'code' => 0, 'url' => '', 'error' => $target['error']);
        $hasV6 = false;
        foreach ($target['resolve'] as $row) {
            if (strpos($row, '[') !== false) $hasV6 = true;
        }
        $target['has_v6'] = $hasV6;
        $left = (int)ceil($deadline - microtime(true));
        if ($left < 1) return array('ok' => false, 'body' => '', 'code' => 0, 'url' => '', 'error' => 'timeout');
        $res = wl_curl_once($target, $left);
        if (!empty($res['redirect'])) {
            $next = wl_resolve_location($target['url'], $res['redirect']);
            if ($next === '') return array('ok' => false, 'body' => '', 'code' => 0, 'url' => '', 'error' => 'redirect');
            $current = $next;
            continue;
        }
        if (empty($res['ok'])) return array('ok' => false, 'body' => '', 'code' => (int)$res['code'], 'url' => $target['url'], 'error' => 'fetch');
        return array('ok' => true, 'body' => $res['body'], 'code' => (int)$res['code'], 'url' => $target['url'], 'error' => '');
    }
    return array('ok' => false, 'body' => '', 'code' => 0, 'url' => '', 'error' => 'redirects');
}
