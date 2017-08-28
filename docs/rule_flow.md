# Flow（规则编写流程）

1. 开发规则文件`CVI-XXXNNN.xml`
2. 开发漏洞代码`tests/vulnerabilities/v.language`
3. 测试规则扫描`./cobra.py -t tests/vulnerabilities/`

## 规则文件命名规范
`rules/CVI-100001.xml`
- 统一存放在`rules`目录
- 大写字母CVI（Cobra Vulnerability ID）开头，横杠（-）分割
- 六位数字组成，前三位为Label ID，后三位为自增ID
- 结尾以小写.xml结束

## 规则编写规范

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

## `<match>`/`<match2>`/`<repair>`编写规范

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