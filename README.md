# Cobra
[![Cobra Release](https://img.shields.io/github/release/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/releases)
[![Coverage](https://img.shields.io/coveralls/wufeifei/cobra.svg)](https://coveralls.io/github/wufeifei/cobra)
[![Cobra Open Issue](https://img.shields.io/github/issues-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues)
[![Cobra Close Issue](https://img.shields.io/github/issues-closed-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues?q=is%3Aissue+is%3Aclosed)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/wufeifei/cobra/blob/master/LICENSE)

## Introduction（介绍）
Cobra是一款**源代码安全审计**工具，支持检测多种开发语言源代码中的数十种漏洞和风险点。

## Features（特点）
#### Multi-language support（支持多种开发语言）
> 支持PHP、Java、Objective-C等开发语言，并支持数十种文件格式。

#### Supported Multi-Vulnerabilities（支持多种漏洞）
> 首批开放数万条不安全的依赖检查规则和数十条代码安全扫描规则，后续将持续开放更多扫描规则。

#### CLI、API（命令行模式和API模式）
> 提供本地Server服务，可支持本地API接口，方便和其它系统（发布系统、CI等）对接扩展

## Installation（安装）
```bash
git clone https://github.com/wufeifei/cobra.git && cd cobra
pip install -r requirements.txt
./cobra.py --help
```

## Config（配置）
> 若用到以下功能，则需要配置config文件，否则无需变动。

```bash
cp config.template config
```

- 将扫描结果发送到指定邮箱
- 扫描私有GIT项目
- 变更API Server端口域名

## Upgrade（升级框架和规则）
> 规则文件夹(Rules)也在开源代码中，所以只需要更新代码即可。

```bash
git pull origin master
```

## Usage（使用）
```bash
# 扫描一个文件夹的代码
$ ./cobra.py -t tests/vulnerabilities

# 扫描一个Git项目代码
$ ./cobra.py -t https://github.com/wufeifei/grw.git

# 扫描一个文件夹，并将扫描结果导出为JSON文件
$ ./cobra.py -t tests/vulnerabilities -f json -o /tmp/report.json

# 扫描一个Git项目，并将扫描结果JSON文件推送到API上
$ ./cobra.py -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git

# 扫描一个Git项目，并将扫描结果JSON文件发送到邮箱中
$ ./cobra.py -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git

# 扫描一个文件夹代码的某两种漏洞
$ ./cobra.py -t tests/vulnerabilities -r cvi-190001,cvi-190002

# 开启一个Cobra HTTP Server，然后可以使用API接口来添加扫描任务
$ ./cobra.py -H 127.0.0.1 -P 80

# 查看版本
$ ./cobra.py --version

# 查看帮助
$ ./cobra.py --help
```

## Reference（引用）
- [规则开发规范](https://github.com/wufeifei/cobra/blob/beta/rules/README.md)