# Cobra
 [![Cobra Release](https://img.shields.io/github/release/wufeifei/cobra.svg)]()
 [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://raw.githubusercontent.com/wufeifei/cobra/master/doc/COPYING)
 [![Cobra Open Issue](https://img.shields.io/github/issues-raw/wufeifei/cobra.svg)]()
 [![Cobra Close Issue](https://img.shields.io/github/issues-closed-raw/wufeifei/cobra.svg)]()
 [![GitHub stars](https://img.shields.io/github/stars/wufeifei/cobra.svg?style=social&label=Star)]()
 [![GitHub followers](https://img.shields.io/github/followers/wufeifei.svg?style=social&label=Follow&maxAge=2592000)](https://github.com/wufeifei)

Static code analysis common security issues and scan common security vulnerabilities

## 项目介绍
Cobra（眼镜蛇）是一款定位于静态代码安全漏洞分析系统。通过收集互联网常规漏洞的检测方法并输出成Cobra扫描规则，即可以自动化分析出源代码中存在的漏洞并生成完整的漏洞审计报告和详细的修复方案。

## 目标用户
**1. 互联网企业**

互联网公司可以将Cobra部署在企业内,供开发人员使用,用来扫描项目风险.
也可以集成到内部的代码发布系统,让Cobra成为发布系统中的一环,扫描开发人员提交到线上的代码的安全性,从而限制不安全的代码上线,减少线上风险.

**2. 安全公司**

安全公司为互联网公司进行安全测试时,可以通过Cobra的全局项目扫描功能对甲方的所有项目进行自动代码安全审计.

**3. 白帽**

白帽们可以通过定制私有Cobra扫描规则, 对开源项目进行代码审计,发现其中漏洞.

## 应用场景

**1.漏洞出现前（检测）**

我们将互联网上常见的漏洞梳理为Cobra的检测规则，能够在漏洞被白帽子发现前就扫描出风险点并解决，防范于未然。

例： 提前检测代码中是否存在高危文件(.tar.gz/.rar/.bak/.swp)，可以避免高危文件被下载。

**2.漏洞出现中（扫描）**

当企业收到白帽子提交的漏洞后，企业会在第一时间修复漏洞，并可以通过Cobra来添加扫描规则检测企业的所有项目是否存在类似漏洞。

例： 出现了ImageMagick漏洞后，可以通过Cobra设置扫描规则对历史所有项目进行快速扫描，几分钟内就能知道企业数十个项目中哪些有用到ImageMagick组件，哪些存在漏洞，哪些可以免疫。

**3.漏洞出现后（限制）**

当企业修复漏洞后，可以通过设置修复/验证规则来限制以后所有提交的代码都需要过修复/验证规则，否则不予上线，减少相同漏洞再次出现的可能性。

## 项目截图
##### Cobra自助扫描
![Cobra Manual Scan](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/MANUAL.png)
##### Cobra扫描报告
![Cobra Report](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/REPORT.png)
##### Cobra管理后台
![Cobra Manage](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/MANAGE.png)

## 相关链接
- Cobra文档 - https://github.com/wufeifei/cobra/wiki
- 建议意见 - https://github.com/wufeifei/cobra/issues/new
- 在线试用 - 敬请期待!

