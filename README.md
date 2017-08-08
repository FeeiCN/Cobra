# Cobra
[![Build Status](https://travis-ci.org/wufeifei/cobra.svg?branch=master)](https://travis-ci.org/wufeifei/cobra)
[![Coverage](https://img.shields.io/coveralls/wufeifei/cobra.svg)](https://coveralls.io/github/wufeifei/cobra)
[![Cobra Release](https://img.shields.io/github/release/wufeifei/cobra.svg)](https://github.com/wufeifei/cobra/releases)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/wufeifei/cobra/blob/master/LICENSE)

当前版本非正式版本，正式版本正在做最后的内测中，建议等正式版本出来后再使用，敬请期待！
[![asciicast](https://asciinema.org/a/132572.png)](https://asciinema.org/a/132572)

## Introduction（介绍）
Cobra是一款**源代码安全审计**工具，支持检测多种开发语言源代码中的数十种漏洞和风险点。

## Features（特点）
#### [Multi-language support（支持多种开发语言）](https://github.com/wufeifei/cobra/blob/master/rules/languages.xml)
> 支持PHP、Java等开发语言，并支持数十种类型文件。

#### [Supported Multi-Vulnerabilities（支持多种漏洞）](https://github.com/wufeifei/cobra/blob/master/rules/vulnerabilities.xml)
> 首批开放数万条不安全的依赖检查规则和数十条代码安全扫描规则，后续将持续开放更多扫描规则。

#### CLI、API（命令行模式和API模式）
> 提供本地Server服务，可支持本地API接口，方便和其它系统（发布系统、CI等）对接扩展

## Documents（文档）
- [Cobra安装](https://github.com/wufeifei/cobra/blob/master/docs/installation.md)
- [CLI模式使用方法](https://github.com/wufeifei/cobra/blob/master/docs/cli.md)
- [API模式使用方法](https://github.com/wufeifei/cobra/blob/master/docs/api.md)
- [高级功能配置](https://github.com/wufeifei/cobra/blob/master/docs/config.md)
- [升级框架和规则源](https://github.com/wufeifei/cobra/blob/master/docs/upgrade.md)
- [扫描规则开发规范](https://github.com/wufeifei/cobra/blob/master/rules/README.md)