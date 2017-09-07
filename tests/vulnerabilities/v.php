<?php
$username = $_POST['username'];
$password = $_POST['password'];
$callback = $_POST['callback'];

$target = "10.11.2.220";

$cmd = $_REQUEST['a'];

echo($callback . ";");

extract($cmd);

@array_map("ass\x65rt",(array)@$cmd);

$cmd = $_GET['cmd'];

if (!empty($cmd)){
    eval($cmd);
    system('ls' + $cmd);
}

if (isset($_GET['sid'])) {
    setcookie("PHPSESSID", $cmd);
}

phpinfo();

if(!empty($url))
{
    mkdir('log/'.date("Y"),0777);
}

function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}

$url = $_GET['url'];
if (!empty($url)){
    curl($cmd);
}

$url = $_GET['url'];

if (!empty($url)){
    $content = file_get_contents($url);
}

$url = $_GET["url"];
if (!empty($url)){
    echo get_headers($url,1);
}

print("Hello " . $cmd);

$query  = "SELECT id, name, inserted, size FROM products WHERE size = '$size' ORDER BY $order LIMIT $limit, $offset;";
mysql_query($query);
mysqli_query($query);


if(!empty($cmd)){
    require_once($cmd);
}

highlight_file($cmd);

$unique = uniqid();

$appKey = "C787AFE9D9E86A6A6C78ACE99CA778EE";

$password = "cobra123456!@#";

$url = $_GET["url"];
if (!empty($url)) {
    header("Location: ".$url);
}

$test = $_POST['test'];
$test_uns = unserialize($test);

$xml = $_POST['xml'];
$data = simplexml_load_string($xml);

parse_str($_SERVER['QUERY_STRING']);

$a = '0';

if($a==1){
    echo "true!";
}else{
    echo "false!";
}

$file = $_POST["file_name"];
if (!empty($file)){
    unlink($file);
}
