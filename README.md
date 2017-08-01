# Cobra
[![Cobra Release](https://img.shields.io/github/release/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/releases)
[![Coverage](https://img.shields.io/coveralls/wufeifei/cobra.svg)](https://coveralls.io/github/wufeifei/cobra)
[![Cobra Open Issue](https://img.shields.io/github/issues-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues)
[![Cobra Close Issue](https://img.shields.io/github/issues-closed-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues?q=is%3Aissue+is%3Aclosed)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/wufeifei/cobra/blob/master/LICENSE)

## Introduction（介绍）
Cobra是一款**源代码安全审计**工具，支持检测多种开发语言源代码中的数百种漏洞和风险点。

## Features（特点）
- Multi-language support（支持多种开发语言）
    - PHP
    - Java
    - Objective-C
- Supported Multi-Vulnerabilities（支持多种漏洞）
    - 数千条依赖规则
    - 数十条代码规则
- API（提供API接口，方便和其它系统对接扩展）

## Installation（安装）
```bash
pip install https://github.com/wufeifei/cobra.git
cobra --help
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