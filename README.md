# Cobra(眼镜蛇) - 代码安全扫描系统

### 扫描方式
从业务场景出发，代码扫描方式分两种。一种为版本控制系统（GIT/SVN）提交的对比扫描，一种为项目全量扫描。

#### 1. 对比扫描
描述：通过与线上代码或上次提交进行对比，找出本次改动代码，然后仅对本次改动代码进行扫描。
优缺点：扫描速度快，能立刻知道扫描结果。但扫描范围小。
场景：对于日常发布，我们需要快速知道本次提交是否存在风险代码，采用对比扫描将能第一时间知道结果。

#### 2. 全量扫描
描述：通过打成压缩包或者传送Git/SVN地址，解压缩、下载后会对项目所有代码进行全量扫描。
优缺点：扫描速度慢，但扫描全面。
场景：对于历史不经常发布的项目，可以采用全量扫描。

### 支持的开发语言与框架
鉴于我们目前线上项目主要为PHP和JAVA，所以我们一期将支持这两种语言。
并做好我们目前使用的框架兼容性，确保我们线上大部分业务都能覆盖到。

Developer Language|Framework
--- | ---
PHP|	Kohana、Laravel
JAVA|	Spring、Struts

### 支持的漏洞类型
一期主要扫一些比较常见而又难以杜绝的漏洞，后续陆续支持一些动态扫描。

Item | Remark
--- | ---
XSS	|跨站脚本
CSRF|	跨站请求伪造
SQL Injection|	SQL注入
Sensitive Data Exposure|敏感信息泄露、备份文件泄露、代码文件泄露、服务器信息泄露、SVN/GIT信息泄露...
WebShell	|WebShell
Backdoor | 
torjor|	小马、大马
URL Redirector Abuse	|URL重定向
Misconfiguration|错误配置
LFI/RFI|	本地文件包含、远程文件包含
Command Execution|命令执行
Code Execution|代码执行
Header Injection|头注入

##### 待支持的漏洞类型（后续计划逐步接入）
Item|Remark
--- | ---
Variable Coverage	|变量覆盖
CRLF Injection CRLF|注入
Unauthorized Access|	越权访问
Weak Password	|弱口令
XML Injection	|XML实体注入
Brute Force	|暴力破解

### 整体架构