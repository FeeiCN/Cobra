# Introduction（介绍）

## 什么是"源代码安全审计（白盒扫描）"？
> 由于每位开发人员的技术水平和安全意识各不相同，就导致可能写出一些存在安全漏洞的代码。
> 而攻击者可以通过渗透测试来找到这些漏洞，从而导致应用被攻击、服务器被入侵、数据被下载、业务受到影响等等问题。
> "源代码安全审计"是指通过审计发现源代码中的安全问题，而Cobra可将这个流程自动化。

## Cobra为什么能从源代码中扫描到漏洞？
> 对于一些特征较为明显的可以使用正则规则来直接进行匹配出，比如硬编码密码、错误的配置等。
> 对于一些需要判断参数是否可控的，Cobra通过预先梳理能造成危害的函数，并定位代码中所有出现该危害函数的地方，继而基于Lex(Lexical Analyzer Generator, 词法分析生成器)和Yacc(Yet Another Compiler-Compiler, 编译器代码生成器)将对应源代码解析为AST(Abstract Syntax Tree, 抽象语法树)，分析危害函数的入参是否可控来判断是否存在漏洞。

## Cobra和其它源代码审计系统有什么区别或优势？
> Cobra目标是自动化发现源代码中大部分显著的安全问题，对于一些隐藏较深或企业特有的问题建议手工审计。

- 开源免费（基于开放的MIT License）
- 支持开发语言多（支持十多种开发语言和文件类型）
- 支持漏洞类型多（支持数十种漏洞类型）
- 支持各种场景集成（提供API也可以命令行使用）
- 持续维护更新（多家企业共同维护）

## Cobra支持哪些开发语言？
> 目前Cobra主要支持PHP、Java等主要开发语言及其它数十种文件类型，并持续更新规则和引擎以支持更多开发语言，具体见`languages`。

## Cobra能发现哪些漏洞？
> 覆盖所有常见漏洞，具体见规则编写中的`labels`。

## Cobra能应用在哪些场景？
1. 【漏洞出现前】通过内置的扫描规则对公司项目进行日常扫描，并推进解决。
2. 【漏洞出现后】当出现一种新漏洞，可以立刻编写一条Cobra扫描规则对公司全部项目进行扫描来判断受影响的项目。

## Cobra是什么类型应用？
> Cobra提供Web服务的同时也提供了命令行服务。

1. 部署成Web服务，提供自助扫描服务和API服务。
2. 使用CLI模式，在命令行中进行扫描。

# Cobra文档
- 安装
    - [Cobra安装](https://wufeifei.github.io/cobra/installation)
- 使用方法
    - [CLI模式使用方法](https://wufeifei.github.io/cobra/cli)
    - [API模式使用方法](https://wufeifei.github.io/cobra/api)
- 进阶
    - [高级功能配置](https://wufeifei.github.io/cobra/config)
    - [升级框架和规则源](https://wufeifei.github.io/cobra/upgrade)
- 规则编写
    - [扫描规则开发规范](https://wufeifei.github.io/cobra/rule)
- 框架
    - [开发语言和文件类型定义](https://wufeifei.github.io/cobra/languages)
    - [漏洞类型定义](https://wufeifei.github.io/cobra/labels)
    - [危害等级定义](https://wufeifei.github.io/cobra/level)
    - [程序目录结构](https://wufeifei.github.io/cobra/tree)
- 贡献代码
    - [单元测试](https://wufeifei.github.io/cobra/test)