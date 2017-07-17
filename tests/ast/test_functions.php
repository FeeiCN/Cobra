<?php
# 字符串,不可控
function request1(){
    curl_setopt($curl, CURLOPT_URL, "http://blog.feei.cn/ssrf");
}

# 常量,不可控
function request2(){
    const URL = 'http://blog.feei.cn/ssrf';
    curl_setopt($curl, CURLOPT_URL, URL);
}

# 变量,不可控
function request3(){
    $url = 'http://blog.feei.cn/ssrf';
    curl_setopt($curl, CURLOPT_URL, $url);
}

# 外部取参,可控,未修复
function request4(){
    $url = $_GET['url'];
    curl_setopt($curl, CURLOPT_URL, $url);
}

# 外部取参,可控,已修复
function request5(){
    $url = $_POST['url'];
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_PROTOCOLS, CURLOPT_HTTP);
}