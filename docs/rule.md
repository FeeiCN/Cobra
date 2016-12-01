# Rule verify template

### Teamplate
```
Matched 1
***
Matched 2
***
Matched 3
---
Not matched 1
***
# something annotation
Not matched 2
***
Not matched 3
```
- 以 `---` 作为匹配和非匹配的分隔符,上面的每行为必须匹配的,下面的每行为不能匹配的;
- 以 `***` 作为每条记录的分隔符;
- 可以以#号写注释;

### Only location regex

##### Ex:

Location regex
```
([\$\w\->]+\s*(?:=|=>)\s*["'][a-f0-9]{32}\s*["']\s*[;,])
```

Verify
```
# 32位字符串赋值
$pwd = "1111111111111111111111111111111f";
***
# 32位数字赋值
$key   =   "11111111111111111111111111111111";
---
# 37位字符串赋值
$test = "1111111111111111111111111111111fasdf";
***
# 18位字符串赋值
$test = "11111111111111";
```

### Location regex && Repair regex
Template
```
function request($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}
***
function request() {
    $url = $_GET['url'];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}
---
# 修复语句在定位行之后
function request($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}
***
# 修复语句在定位行之前
function request() {
    $url = $_GET['url'];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
}
```