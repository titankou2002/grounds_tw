<?php
header('Content-Type: text/plain; charset=utf-8');
$out = array();
$out[] = 'php ' . PHP_VERSION . ' curl ' . (function_exists('curl_version') ? curl_version()['version'] . ' ' . curl_version()['ssl_version'] : 'none');
$out[] = 'dns A: ' . json_encode(@gethostbynamel('business.591.com.tw'));
foreach (array(array('verify on', true), array('verify off', false)) as $t) {
  foreach (array(4, 0) as $ipr) {
    $ch = curl_init('https://business.591.com.tw/rent/22231326');
    curl_setopt_array($ch, array(CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10, CURLOPT_CONNECTTIMEOUT => 5,
      CURLOPT_SSL_VERIFYPEER => $t[1], CURLOPT_SSL_VERIFYHOST => $t[1] ? 2 : 0,
      CURLOPT_IPRESOLVE => $ipr ? CURL_IPRESOLVE_V4 : CURL_IPRESOLVE_WHATEVER,
      CURLOPT_HTTPHEADER => array('User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')));
    $b = curl_exec($ch);
    $out[] = $t[0] . ' ipv' . ($ipr ?: 'any') . ': errno=' . curl_errno($ch) . ' ' . curl_error($ch) . ' code=' . curl_getinfo($ch, CURLINFO_HTTP_CODE) . ' len=' . strlen((string)$b);
  }
}
echo implode("\n", $out), "\n";
