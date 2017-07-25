# Introduction

## CVI（Cobra Vulnerability ID）
> CVI由六位数字组成，前三位为漏洞标签ID（Label ID），后三位为递增ID。

```
CVI-XXXNNN
XXX: Label ID
NNN：Increase ID
```

## Labels（标签）
| CVI ID | Label | Description(EN) | Description(CN) |  |
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
| 210 | UD | Untrusted Data | 不受信任的数据 |