> Cobra itself is a white box scanning framework, and other black-and-white box scanner, the number of loopholes can be swept depends on the quality and quantity of your scanning rules. The Cobra open source version currently provides only a few test scans for everyone to use. Cobra core contributors will share all private scanning rules, and Cobra Online will also open all scanning rules.


> If you have a good scan rule, please update to here after creating a [Rule Issue](https://github.com/wufeifei/cobra/issues/new).

_This chapter is perfect, please continue to pay attention!_

You can use this to learn how to write a scan rule: [Cobra scan rule writing](http://blog.feei.cn/scan-engine/)

## Open scan rule list (sorted)

|SSRF|curl|
|---|---|
|Author|Feei|
|Language| PHP|
|Regex location|`curl_setopt\s?\(.*,\s?CURLOPT_URL\s?,(.*)\)`|
|Regex repair|`curl_setopt\s?\(.*,\s?CURLOPT_PROTOCOLS\s?,(.*)\)`|
|TestCase|TODO|
|Repair|[WAVR(SSRF)](https://github.com/wufeifei/WAVR/blob/master/SSRF.md)|

|Trojan|eval|
|---|---|
|Author|Feei|
|Language| PHP|
|Regex location|`eval\(base64_decode\(\$_POST\[`|
|Regex repair|None|
|TestCase|TODO|
|Repair|TODO|

|Hard-coded Password|md5|
|---|---|
|Author|Magerx|
|Language| PHP|
|Regex location|`([\$\w\->]+\s*(?:=|=>)\s*["'][a-f0-9]{32}\s*["']\s*[;,])`|
|Regex repair|None|
|TestCase|TODO|
|Repair|[WAVR(Hard-coded Password)](https://github.com/wufeifei/WAVR/blob/master/Hard-coded_password.md)|

