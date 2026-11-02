<?php
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/worklog/lib_fetch.php';
$h='business.591.com.tw';
echo "ips: ", json_encode(wl_resolve_host_ips($h)), "\n";
$t = wl_validate_fetch_target('https://business.591.com.tw/rent/22231326');
echo "target: ", json_encode($t), "\n";
$r = wl_http_get('https://business.591.com.tw/rent/22231326');
echo "get: ok=", var_export($r['ok'],true), " code=", $r['code'], " err=", $r['error'], " len=", strlen($r['body']), "\n";
