# Introduction

## Rule Template（规则模板）
规则命名规范：
`CVI-100001.xml`
- 大写字母CVI（Cobra Vulnerability ID）开头，横杠（-）分割
- 六位数字组成，前三位为Label ID，后三位为自增ID
- 结尾以小写.xml结束
```xml
<?xml version="1.0" encoding="UTF-8"?>

<cobra document="https://github.com/wufeifei/cobra">
    <name value="必填，股则名称"/>
    <language value="必填，小写字符串，规则针对的语言，参见rules/languages.xml"/>
    <match><![CDATA[必填，一次匹配规则：规则使用正则编写，若为匹配到就算作漏洞的话在规则前后加上括号即可。]]></match>
    <match2 block="block表示修复规则匹配的区块位置，具体参见Block"><![CDATA[可选，二次匹配规则：当完成一次匹配规则后，若需要再次匹配可再次填写。block表示二次规则匹配的区块位置，具体参见rules/README.md]]></match2>
    <repair block="block表示修复规则匹配的区块位置，具体参见Block"><![CDATA[可选，修复规则：若匹配到此规则则不算做漏洞。]]></repair>
    <level value="必填，漏洞危害等级，使用数字1-9来表示"/>
    <solution>
        必填，安全风险和修复方案
        ## 安全风险

        ## 修复方案
    </solution>
    <test>
        <case assert="必填，是否为漏洞，使用true和false来表示"><![CDATA[必填，规则测试代码，可以多行。]]></case>
    </test>
    <status value="必填，规则状态，用on和off来表示开启和关闭"/>
    <author name="必填，规则作者姓名" email="必填，规则作者邮箱"/>
</cobra>
```

## Labels（标签）
| ID | Label | Description(EN) | Description(CN) |  |
| --- | --- | --- | --- | ---|
| 110 | MS | Misconfiguration | 错误的配置 |
| 120 | SSRF | Server-Side Forge | 服务端伪造 |
| 130 | HCP | Hard-coded Password | 硬编码密码 |
| 140 | XSS | Cross-Site Script | 跨站脚本 |
| 150 | CSRF | Cross-Site Request Forge | 跨站请求伪造 |
| 160 | SQLI | SQL Injection | SQL注入 |
| 170 | RFI | Remote File inclusion | 远程文件引用 |
| 180 | RCE | Remote Code Execution | 远程代码执行 |
| 190 | SIL | Sensitive Information Leak | 敏感信息泄露 |
| 200 | PPG | Predictable Pseudorandom Generator | 可预测的伪随机数生成器 |
| 210 | UR | Unvalidated Redirect | 未经验证的任意链接跳转 |
| 220 | HRS | HTTP Response Splitting | HTTP响应拆分 |
| 230 | SF | Session Fixation | SESSION固定 |

## Level(危害等级)

| 等级 | 分值 | 描述 |
|---|---|---|
| 严重 | 9-10 | 1.可获取服务器权限; 2.严重信息泄露; |
| 高危 | 6-8 | 1.敏感信息泄露; 2.越权; 3.任意文件读取; 4.SQL注入; 5.git/svn泄露; 6.SSRF;|
| 中危 | 3-5 | 1.XSS; 2.URL跳转; 3.CRLF; 4.LFI;|
| 低危 | 1-2 | 1.CSRF; 2.JSONP劫持; 3.异常堆栈信息; 3.PHPINFO; 4.路径泄露; 5.硬编码密码; 6.硬编码内网IP域名; 7.不安全的加密方法; 8.不安全的随机数; 9.日志敏感记录;|

## Block(匹配区块)

|区块|描述|
|---|---|
| in-current-line | 由第一条规则触发的所在行 |
| in-function | 由第一条规则触发的函数体内 |
| in-function-up | 由第一条规则触发的所在行之上，所在函数体之内 |
| in-function-down | 由第一条规则触发的所在行之下，所在函数体之内 |
| in-file | 由第一条规则触发的文件内 |
| in-file-up | 由第一条规则触发的所在行之上，所在文件之内 |
| in-file-down | 由第一条规则触发的所在行之下，所在文件之内 |