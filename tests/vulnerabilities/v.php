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

# CVI-130005
$target = "10.11.2.220";

$cmd = $_REQUEST['a']

print($callback);

# CVI-210001
if (isset($_GET['url']) {
    header("Location: ".$_GET["url"]);
}

# CVI-180001
@array_map("ass\x65rt",(array)@$cmd);

$a = base64_decode($_POST['test']);
eval($a);

# CVI-181001
$cmd = $_GET['cmd'];
system('ls' + $cmd);

ssh2_exec($connection, '$_GET['pass']')

# CVI-230001
if (isset($_GET['sid']) {
    setcookie("PHPSESSID", $_GET["sid"]);
}

# CVI-190003
phpinfo();

# CVI-190008
print_r($a);

# CVI-110001
if(!file_exists('log/'.date("Y")))
{
    mkdir('log/'.date("Y"),0777);
}
chmod("move.php", 0777);

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

# CVI-120002
$url = $_GET['url'];
$content = file_get_contents($url)

# CVI-120003
$url = $_GET["url"];
echo get_headers($url,1);

# CVI-140003
print_r ("Hello " . $_GET['name']);

# CVI-140004
echo "Hello " . $_GET['name'];

# CVI-160002  CVI-160003
$query = "SELECT * FROM users WHERE user = $username AND password = $password;";
mysql_query($query);

# CVI-160002  CVI-160004
$query  = "SELECT id, name, inserted, size FROM products WHERE size = '$size' ORDER BY $order LIMIT $limit, $offset;";
$result = odbc_exec($conn, $query);

# CVI-170002
require_once($_GET['file']);

# CVI-200002
$unique = uniqid();

# CVI-130002
$appKey = "C787AFE9D9E86A6A6C78ACE99CA778EE";

# CVI-130001
$password = "cobra123456!@#";

# CVI-210001
header("Location: ".$_GET["url"]);

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
extract($_GET)；
if($a==1){
    echo "true!";
}else{
    echo "false!";
}

# CVI-350001
$file = $_POST["file_name"];
unlink($file);