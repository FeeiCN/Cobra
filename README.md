# Cobra
[![Build Status](https://travis-ci.org/wufeifei/cobra.svg?branch=master)](https://travis-ci.org/wufeifei/cobra)
[![Coverage Status](https://coveralls.io/repos/github/wufeifei/cobra/badge.svg?branch=master)](https://coveralls.io/github/wufeifei/cobra?branch=master)
[![GitHub (pre-)release](https://img.shields.io/github/release/wufeifei/cobra/all.svg)](https://github.com/wufeifei/cobra/releases)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/wufeifei/cobra/blob/master/LICENSE)

当前版本非正式版本，正式版本正在做最后的内测中，建议等正式版本出来后再使用，敬请期待！
[![asciicast](https://asciinema.org/a/132572.png)](https://asciinema.org/a/132572)
[![report01](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/report_01.jpg)](https://wufeifei.github.io/cobra/api)
[![report02](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/report_02.jpg)](https://wufeifei.github.io/cobra/api)

## Introduction（介绍）
Cobra是一款**源代码安全审计**工具，支持检测多种开发语言源代码中的大部分显著的安全问题和漏洞。

## Features（特点）
#### Multi-language support（支持多种开发语言）
> 支持PHP、Java等开发语言，并支持数十种类型文件。

#### Supported Multi-Vulnerabilities（支持多种漏洞类型）
> 首批开放数万条不安全的依赖检查规则和数十条代码安全扫描规则，后续将持续开放更多扫描规则。

#### CLI、API（命令行模式和API模式）
> 提供本地Server服务，可支持本地API接口，方便和其它系统（发布系统、CI等）对接扩展

## Documents（文档）
- 安装
    - [Cobra安装](https://wufeifei.github.io/cobra/installation)
- 基础使用
    - [CLI模式使用方法](https://wufeifei.github.io/cobra/cli)
    - [API模式使用方法](https://wufeifei.github.io/cobra/api)
- 进阶使用
    - [高级功能配置](https://wufeifei.github.io/cobra/config)
    - [升级框架和规则源](https://wufeifei.github.io/cobra/upgrade)
- 规则开发规范
    - [规则模板](https://wufeifei.github.io/cobra/rule_template)
    - [规则样例](https://wufeifei.github.io/cobra/rule_demo)
    - [规则开发流程](https://wufeifei.github.io/cobra/rule_flow)
- 框架引擎
    - [开发语言和文件类型定义](https://wufeifei.github.io/cobra/languages)
    - [漏洞类型定义](https://wufeifei.github.io/cobra/labels)
    - [危害等级定义](https://wufeifei.github.io/cobra/level)
    - [程序目录结构](https://wufeifei.github.io/cobra/tree)
- 贡献代码
    - [单元测试](https://wufeifei.github.io/cobra/test)
    - [贡献者](https://wufeifei.github.io/cobra/contributors)