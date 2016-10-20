> Cobra本身是一款白盒扫描框架，和其它黑白盒扫描器一样，能扫到多少漏洞取决于你的扫描规则的质量和数量。Cobra开源版本目前只会提供几条测试的扫描规则供大家使用，Cobra核心贡献者将可共享所有私有的扫描规则，Cobra线上版本也会开启所有扫描规则。


> 如果您有好的扫描规则，请通过创建[Rule Issue](https://github.com/wufeifei/cobra/issues/new)，我们测试审核后会更新到此处。

_本章节正在补充完善，请持续关注!_

你可以通过这篇来学习如何写一个扫描规则：[Cobra扫描规则编写](http://wufeifei.com/scan-engine/)

## 扫描规则列表 (整理中)

|支持语言|类型|规则|贡献者|准确率|规则|
|---|---|---|---|---|---|
|PHP||||||
||XSS|||||
|||Ouput|[@Feei](http://wufeifei.com)|100%|[Output Param](https://github.com/wufeifei/cobra/wiki/rule_xss_output_param)|
||SSRF||||||
|||CURL|[@Feei](http://wufeifei.com)|100%|[CURL SSRF](https://github.com/wufeifei/cobra/wiki/rule_ssrf_curl)|
||Logic Bug||||||
||Stack Trace||||||
||Deprecated Function||||||
||Information Disclosure||||||
|Java||||||
|Backup||||||
|PSD||||||
|Thumb||||||
|log||||||
