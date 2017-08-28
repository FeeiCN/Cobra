<?php
$username = $_POST['username'];
$password = $_POST['password'];
$callback = $_POST['callback'];

# CVI-130005
$target = "10.11.2.220";

$cmd = $_REQUEST['a'];

echo($callback . ";");

extract($cmd);

# CVI-180001
@array_map("ass\x65rt",(array)@$cmd);

# CVI-181001
$cmd = $_GET['cmd'];

if (!empty($cmd)){
    eval($cmd);
    system('ls' + $cmd);
}

# CVI-230001
if (isset($_GET['sid'])) {
    setcookie("PHPSESSID", $param);
}

# CVI-190003
phpinfo();

# CVI-110001
if(!empty($url))
{
    mkdir('log/'.date("Y"),0777);
}

# CVI-120001
function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}

$url = $_GET['url'];
if (!empty($url)){
    curl($param);
}

# CVI-120002
$url = $_GET['url'];

if (!empty($url)){
    $content = file_get_contents($url);
}

# CVI-120003
$url = $_GET["url"];
if (!empty($url)){
    echo get_headers($url,1);
}

# CVI-140004
echo "Hello " . $param;

# CVI-160002
$query  = "SELECT id, name, inserted, size FROM products WHERE size = '$size' ORDER BY $order LIMIT $limit, $offset;";
mysql_query($query);


# CVI-170002
if(!empty($cmd)){
    require_once($cmd);
}

highlight_file($cmd);

# CVI-200002
$unique = uniqid();

# CVI-130002
$appKey = "C787AFE9D9E86A6A6C78ACE99CA778EE";

# CVI-130001
$password = "cobra123456!@#";

# CVI-210001
$url = $_GET["url"];
if (!empty($url)) {
    header("Location: ".$url);
}

# CVI-260001
$test = $_POST['test'];
$test_uns = unserialize($test);

# CVI-270001
$xml = $_POST['xml'];
$data = simplexml_load_string($xml);

# CVI-320001
parse_str($_SERVER['QUERY_STRING']);

# CVI-320002
$a = '0';

if($a==1){
    echo "true!";
}else{
    echo "false!";
}

# CVI-350001
$file = $_POST["file_name"];
if (!empty($file)){
    unlink($file);
}

