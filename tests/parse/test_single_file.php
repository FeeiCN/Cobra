<?php
# 不可控
$url = "http://blog.feei.cn/ssrf"
curl_setopt($curl, CURLOPT_URL, $url);

# 可控
$url = $_GET['url'];
curl_setopt($curl, CURLOPT_URL, $url);

# 可控,且修复
$url = $_GET['url'];
curl_setopt($curl, CURLOPT_URL, $url);
curl_setopt($curl, CURLOPT_PROTOCOLS, CURLOPT_HTTP);
