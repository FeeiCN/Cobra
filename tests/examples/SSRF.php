<?php
/**
 * Request service(Base cURL)
 *
 * @author Feei <feei@feei.cn>
 * @link   http://blog.feei.cn/ssrf
 */
function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}

$url = $_GET['url'];
curl($url);