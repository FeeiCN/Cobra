<?php
/**
 * Cobra Vulnerabilities Examples
 *
 * @author Feei <feei#feei.cn>
 * @link   https://github.com/wufeifei/cobra
 */
$username = $_POST['username'];
$password = $_POST['password'];
$callback = $_POST['callback'];

print($callback);

# CVI-220001
if (isset($_GET['url']) {
    header("Location: ".$_GET["url"]);
}

# CVI-230001
if (isset($_GET['sid']) {
    setcookie("PHPSESSID", $_GET["sid"]);
}

# CVI-190003
phpinfo();

# CVI-120001
function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}

$url = $_GET['url'];
curl($url);

# CVI-140003
echo ("Hello " . $_GET['name']);

# CVI-200002
$unique = uniqid();

# CVI-130002
$appKey = "C787AFE9D9E86A6A6C78ACE99CA778EE";

# CVI-130001
$password = "cobra123456!@#";