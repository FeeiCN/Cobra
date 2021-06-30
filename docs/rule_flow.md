# Flow（规则编写流程）

#### 1. 编写规则文件`CVI-XXXNNN.xml`
    参考[规则命名](http://cobra.feei.cn/rule_name)建立规则文件。
    参考[规则模板](http://cobra.feei.cn/rule_template)和[规则样例](http://cobra.feei.cn/rule_demo)编写对应的规则、修复方案、测试用例等。

#### 2. 编写漏洞代码`tests/vulnerabilities/v.language`
    编写实际可能出现的业务场景代码（只需编写一处即可）。

#### 3. 测试规则扫描`python cobra.py -t tests/vulnerabilities/`
    测试扫描结果

---
下一章：[开发语言和文件类型定义](http://cobra.feei.cn/languages)
