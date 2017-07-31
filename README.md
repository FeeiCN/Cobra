# Cobra
 [![Cobra Release](https://img.shields.io/github/release/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/releases)
 [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/wufeifei/cobra/blob/master/LICENSE)
 [![Cobra Open Issue](https://img.shields.io/github/issues-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues)
 [![Cobra Close Issue](https://img.shields.io/github/issues-closed-raw/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/issues?q=is%3Aissue+is%3Aclosed)

## Introduction（介绍）
Cobra是一款**源码审计工具**，支持检测源代码中的数十种漏洞和风险点。

## Features（特点）
- Multi-language support（支持多种开发语言）
    - PHP
    - Java
    - Objective-C
- Supported Multi-Vulnerabilities（支持多种漏洞）
    - 依赖
- API（提供API接口，方便和其它系统对接扩展）

## Installation（安装）
```bash
pip install https://github.com/wufeifei/cobra.git
cobra --help
```

## Usage（使用）
```bash
➜  cobra git:(master) ✗ python cobra.py --help
usage: cobra [-h] [-v] [-t <target>] [-f <format>] [-o <output>]
             [-r <rule_id>] [-d] [-sid SID] [-H <host>] [-P <port>]

    ,---.     |
    |    ,---.|---.,---.,---.
    |    |   ||   ||    ,---|
    `---``---``---``    `---^ v1.2.3

GitHub: https://github.com/wufeifei/cobra

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Scan:
  -t <target>, --target <target>
                        file, folder, compress, or repository address
  -f <format>, --format <format>
                        vulnerability output format (formats: html, json, csv,
                        xml)
  -o <output>, --output <output>
                        vulnerability output STREAM, FILE, HTTP API URL, MAIL
  -r <rule_id>, --rule <rule_id>
                        specifies rule id e.g: CVI-100001
  -d, --debug           open debug mode
  -sid SID, --sid SID   scan id(API)

RESTful:
  -H <host>, --host <host>
                        REST-JSON API Service Host
  -P <port>, --port <port>
                        REST-JSON API Service Port

Usage:
  cobra -t /tmp/your_project_path
  cobra -r /tmp/rule.fei -t /tmp/your_project_path
  cobra -f json -o /tmp/report.json -t /tmp/project_path
  cobra -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git
  cobra -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git
  cobra -H 127.0.0.1 -P 80
```