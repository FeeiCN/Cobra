# Rule Template（规则模板）
```xml
<?xml version="1.0" encoding="UTF-8"?>

<cobra document="https://github.com/wufeifei/cobra">
    <name value="硬编码Token/Key"/>
    <language value="*"/>
    <match><![CDATA[(?![\d]{32})(?![a-fA-F]{32})([a-f\d]{32}|[A-F\d]{32})]]></match>
    <level value="2"/>
    <test>
        <case assert="true" remark="sha1"><![CDATA["41a6bc4d9a033e1627f448f0b9593f9316d071c1"]]></case>
        <case assert="true" remark="md5 lower"><![CDATA["d042343e49e40f16cb61bd203b0ce756"]]></case>
        <case assert="true" remark="md5 upper"><![CDATA[C787AFE9D9E86A6A6C78ACE99CA778EE]]></case>
        <case assert="false"><![CDATA[please like and subscribe to my]]></case>
        <case assert="false"><![CDATA[A32efC32c79823a2123AA8cbDDd3231c]]></case>
        <case assert="false"><![CDATA[ffffffffffffffffffffffffffffffff]]></case>
        <case assert="false"><![CDATA[01110101001110011101011010101001]]></case>
        <case assert="false"><![CDATA[00000000000000000000000000000000]]></case>
    </test>
    <solution>
        ## 安全风险
        硬编码密码

        ## 修复方案
        将密码抽出统一放在配置文件中，配置文件不放在git中
    </solution>
    <status value="on"/>
    <author name="Feei" email="feei@feei.cn"/>
</cobra>
```


## 规则字段规范

|字段（英文）|字段（中文）|是否必填|类型|描述|例子|
|---|---|---|---|---|---|
|`name`|规则名称|是|`string`|描述规则名称|`<name value="Logger敏感信息" />`|
|`language`|规则语言|是|`string`|设置规则针对的开发语言，参见`languages`|`<language value="php" />`|
|`match`|匹配规则1|是|`string`|匹配规则1|`<match mode="regex-only-match"><![CDATA[regex content]]></match>`|
|`match2`|匹配规则2|否|`string`|匹配规则2|`<match2 block="in-function-up"><![CDATA[regex content]]></match>`|
|`repair`|修复规则|否|`string`|匹配到此规则，则不算做漏洞|`<repair block=""><![CDATA[regex content]]></match>`|
|`level`|影响等级|是|`integer`|标记该规则扫到的漏洞危害等级，使用数字1-10。|`<level value="3" />`|
|`solution`|修复方案|是|`string`|该规则扫描的漏洞对应的**安全风险**和**修复方案**|`<solution>详细的安全风险和修复方案</solution>`|
|`test`|测试用例|是|`case`|该规则对应的测试用例|`<test><case assert="true"><![CDATA[测试存在漏洞的代码]]></case><case assert="false"><![CDATA[测试不存在漏洞的代码]]></case></test>`|
|`status`|是否开启|是|`boolean`|是否开启该规则的扫描，使用`on`/`off`来标记|`<status value="1" />`|
|`author`|规则作者|是|`attr`|规则作者的姓名和邮箱|`<author name="Feei" email="feei@feei.cn" />`|

## 核心字段`<match>`/`<match2>`/`<repair>`编写规范

#### `<match>` Mode（`<match>`的规则模式）
> 用来描述规则类型，只能用在`<match>`中。

|Mode|类型|默认模式|支持语言|描述|
|---|---|---|---|---|
|regex-only-match|正则仅匹配|是|*|默认是此模式，但需要显式的写在规则文件里。以正则的方式进行匹配，匹配到内容则算作漏洞|
|regex-param-controllable|正则参数可控|否|PHP/Java|以正则模式进行匹配，匹配出的变量可外部控制则为漏洞|
|function-param-controllable|函数参数可控|否|PHP|内容写函数名，将搜索所有该函数的调用，若参数外部可控则为漏洞。|
|find-extension|寻找指定后缀文件|否|*|找到指定后缀文件则算作漏洞|

#### `<match2>`/`<repair>` Block（`<match2>`/`<repair>`的匹配区块）
> 用来描述需要匹配的代码区块位置，只能用在`<match2>`或`<repair>`中。

|区块|描述|
|---|---|
| in-current-line | 由第一条规则触发的所在行 |
| in-function | 由第一条规则触发的函数体内 |
| in-function-up | 由第一条规则触发的所在行之上，所在函数体之内 |
| in-function-down | 由第一条规则触发的所在行之下，所在函数体之内 |
| in-file | 由第一条规则触发的文件内 |
| in-file-up | 由第一条规则触发的所在行之上，所在文件之内 |
| in-file-down | 由第一条规则触发的所在行之下，所在文件之内 |

---
下一章：[规则样例](https://wufeifei.github.io/cobra/rule_demo)