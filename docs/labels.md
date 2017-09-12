# Labels（标签）
> 标签用来标记扫描规则所属的漏洞类型。

| ID | Label | Description(EN) | Description(CN) |
|---|---|---|---|
| 110 | MS | Misconfiguration | 错误的配置 |
| 120 | SSRF | Server-Side Forge | 服务端伪造 |
| 130 | HCP | Hard-coded Password | 硬编码密码 |
| 140 | XSS | Cross-Site Script | 跨站脚本 |
| 150 | CSRF | Cross-Site Request Forge | 跨站请求伪造 |
| 160 | SQLI | SQL Injection | SQL注入 |
| 163 | XI | Xpath Injection | Xpath注入 |
| 165 | LI | LDAP Injection | LDAP注入 |
| 167 | XEI| XML External Entity Injection | XML实体注入 |
| 170 | FI | Local/Remote File Inclusion | 文件包含漏洞 |
| 180 | CI | Code Injection  | 代码注入 |
| 181 | CI | Command Injection | 命令注入 |
| 190 | IE | Information Exposure  | 信息泄露 |
| 200 | PPG | Predictable Pseudorandom Generator | 可预测的伪随机数生成器 |
| 210 | UR | Unvalidated Redirect | 未经验证的任意链接跳转 |
| 220 | HRS | HTTP Response Splitting | HTTP响应拆分 |
| 230 | SF | Session Fixation | SESSION固定 |
| 260 | US | unSerialize | 反序列化漏洞 |
| 280 | DF |  Deprecated Function  | 废弃的函数 |
| 290 | LB | Logic Bug  | 逻辑错误 |
| 320 | VO | Variables Override | 变量覆盖漏洞 |
| 350 | WF | Weak Function | 不安全的函数 |
| 355 | WE |Weak Encryption | 不安全的加密 |
| 360 | WS | WebShell | WebShell |
| 970 | AV | Android Vulnerabilities | Android漏洞 |
| 980 | IV | iOS Vulnerabilities | iOS漏洞 |
| 999 | IC | Insecure Components| 引用了存在漏洞的三方组件(Maven/Pods/PIP/NPM) |

## Label制定规范
- 大类别以10为基数叠加ID的第一位和第二位，小类别以2为基数叠加ID第三位。
- Label缩写默认使用描述的首字母缩写，最长四位字符。
- 编辑后请修改对应的`rules/vulnerabilities.xml`

---
下一章：[危害等级定义](https://wufeifei.github.io/cobra/level)