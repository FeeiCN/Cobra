# Introduction

## CVI（Cobra Vulnerability ID）
> CVI由六位数字组成，前三位为漏洞标签ID（Label ID），后三位为递增ID。

```
CVI-XXXNNN
XXX: Label ID
NNN：Increase ID
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

## Level(危害等级)

| 等级 | 分值 | 描述 |
|---|---|---|
| 严重 | 9-10 | 1.可获取服务器权限; 2.严重信息泄露; |
| 高危 | 6-8 | 1.敏感信息泄露; 2.越权; 3.任意文件读取; 4.SQL注入; 5.git/svn泄露; 6.SSRF;|
| 中危 | 3-5 | 1.XSS; 2.URL跳转; 3.CRLF; 4.LFI;|
| 低危 | 1-2 | 1.CSRF; 2.JSONP劫持; 3.异常堆栈信息; 3.PHPINFO; 4.路径泄露; 5.硬编码密码; 6.硬编码内网IP域名; 7.不安全的加密方法; 8.不安全的随机数; 9.日志敏感记录;|