<?php
echo ($_GET['test']);


function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}

$url = $_GET['url'];
curl($url);


$appKey = "C787AFE9D9E86A6A6C78ACE99CA778EE";
$password = "34b9a295d037d47eec3952e9dcdb6b2b";