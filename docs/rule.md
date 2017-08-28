# Rule（规则开发规范）

## 一、Flow（规则编写流程）
1. 开发规则文件`CVI-XXXNNN.xml`
2. 开发漏洞代码`tests/vulnerabilities/v.language`
3. 测试规则扫描`./cobra.py -t tests/vulnerabilities/`

## 二、Rule Template（规则模板）
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

## 三、规则文件命名规范
`rules/CVI-100001.xml`
- 统一存放在`rules`目录
- 大写字母CVI（Cobra Vulnerability ID）开头，横杠（-）分割
- 六位数字组成，前三位为Label ID，后三位为自增ID
- 结尾以小写.xml结束

## 四、规则编写规范

|字段（英文）|字段（中文）|是否必填|类型|描述|例子|
|---|---|---|---|---|---|
|`name`|规则名称|是|`string`|描述规则名称|`<name value="Logger敏感信息" />`|
|`language`|规则语言|是|`string`|设置规则针对的开发语言，参见`rules/languages.xml`|`<language value="php" />`|
|`match`|匹配规则1|是|`string`|匹配规则1|`<match mode="regex-only-match"><![CDATA[regex content]]></match>`|
|`match2`|匹配规则2|否|`string`|匹配规则2|`<match2 block="in-function-up"><![CDATA[regex content]]></match>`|
|`repair`|修复规则|否|`string`|匹配到此规则，则不算做漏洞|`<repair block=""><![CDATA[regex content]]></match>`|
|`level`|影响等级|是|`integer`|标记该规则扫到的漏洞危害等级，使用数字1-10。|`<level value="3" />`|
|`solution`|修复方案|是|`string`|该规则扫描的漏洞对应的**安全风险**和**修复方案**|`<solution>详细的安全风险和修复方案</solution>`|
|`test`|测试用例|是|`case`|该规则对应的测试用例|`<test><case assert="true"><![CDATA[测试存在漏洞的代码]]></case><case assert="false"><![CDATA[测试不存在漏洞的代码]]></case></test>`|
|`status`|是否开启|是|`boolean`|是否开启该规则的扫描，使用`on`/`off`来标记|`<status value="1" />`|
|`author`|规则作者|是|`attr`|规则作者的姓名和邮箱|`<author name="Feei" email="feei@feei.cn" />`|

## 五、`<match>`/`<match2>`/`<repair>`编写规范

#### `<match>` Mode（`<match>`的规则模式）
> 用来描述规则类型，只能用在`<match>`中。

|Mode|类型|默认模式|描述|
|---|---|---|---|
|regex-only-match|正则仅匹配|是|默认是此模式，但需要显式的写在规则文件里。以正则的方式进行匹配，匹配到内容则算作漏洞|
|regex-param-controllable|正则参数可控|否|以正则模式进行匹配，匹配出的变量可外部控制则为漏洞|
|function-param-controllable|函数参数可控|否|内容写函数名，将搜索所有该函数的调用，若参数外部可控则为漏洞。（此模式目前仅支持PHP）|
|find-extension|寻找指定后缀文件|否|找到指定后缀文件则算作漏洞|

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


## 六、Demo（例子）
> 把常见漏洞划分为四大类

#### 1. 单一匹配: 仅匹配单次
**例子：错误的配置(使用了ECB模式)**
```java
Cipher c = Cipher.getInstance("AES/ECB/NoPadding");
```

**Solution(规则写法)**

可以通过配置一条match规则，规则mode设置为`regex`(仅匹配，通过正则模式匹配，匹配到则算作漏洞)，即可扫描这类问题。
```xml
<match mode="regex-only-match"><![CDATA[Cipher....Instance\s?\(\s?\".*ECB]]></match>
```
#### 2. 多次匹配：需要进行多次匹配
**例子：不安全的随机数（首先需要匹配到生成了随机数`new Random`，然后要确保随机数是系统的随机数而非自定义函数）**
```java
import util.random;
Random r = new Random();
```
**Solution(规则写法)**

先配置一条`match`规则来匹配`new Random`，再配置一条`match`来匹配`import util.random`。
```xml
<match mode="regex-only-match"><![CDATA[new Random\s*\(|Random\.next]]></match>
<match2 block="in-file-up"><![CDATA[java|scala)\.util\.Random]]></match2>
```

#### 3. 参数可控：只要判定参数是用户可控的则算作漏洞
**例子：反射型XSS（直接输出入参）**
```php
$content = $_GET['content'];
print("Text: " + $content);
```

**Solution(规则写法)**

```xml
<match mode="function-param-controllable"><![CDATA[print]]></match>
```

### 4. 依赖安全：当依赖了某个不安全版本的三方组件


## 七、Labels（标签）

| ID | Label | Description(EN) | Description(CN) |
|---|---|---|---|
| 110 | MS | Misconfiguration | 错误的配置 |
| 120 | SSRF | Server-Side Forge | 服务端伪造 |
| 130 | HCP | Hard-coded Password | 硬编码密码 |
| 140 | XSS | Cross-Site Script | 跨站脚本 |
| 150 | CSRF | Cross-Site Request Forge | 跨站请求伪造 |
| 160 | SQLI | SQL Injection | SQL注入 |
| 170 | LFI/RFI | Local/ Remote File inclusion | 文件包含漏洞 |
| 180 | CI | Code Injection  | 代码注入 |
| 181 | CI | Command Injection | 命令注入 |
| 190 | IE | Information Exposure  | 信息泄露 |
| 200 | PPG | Predictable Pseudorandom Generator | 可预测的伪随机数生成器 |
| 210 | UR | Unvalidated Redirect | 未经验证的任意链接跳转 |
| 220 | HRS | HTTP Response Splitting | HTTP响应拆分 |
| 230 | SF | Session Fixation | SESSION固定 |
| 240 | XpathI | Xpath Injection | Xpath注入 |
| 250 | LDAP | LDAP Injection | LDAP注入 |
| 260 | Unserialize | unserialize | 反序列化漏洞 |
| 270 | XXEI| XML External Entity Injection | XML实体注入 |
| 280 | DF |  Deprecated Function  | 废弃的函数 |
| 290 | LB | Logic Bug  | 逻辑错误 |
| 320 | VO | Variables Override | 变量覆盖漏洞 |
| 330 | Encryption | 不安全的加密 |
| 350 | WF | Weak Function | 不安全的函数 |
| 970 | AV | Android Vulnerabilities | Android漏洞 |
| 980 | IV | iOS Vulnerabilities | iOS漏洞 |
| 999 | IC | Insecure Components| 引用了存在漏洞的三方组件(Maven/Pods/PIP/NPM) |

## 八、Level（危害等级）

| 等级 | 分值 | 描述 |
|---|---|---|
| 严重 | 9-10 | 1.可获取服务器权限; 2.严重信息泄露; |
| 高危 | 6-8 | 1.敏感信息泄露; 2.越权; 3.任意文件读取; 4.SQL注入; 5.git/svn泄露; 6.SSRF;|
| 中危 | 3-5 | 1.XSS; 2.URL跳转; 3.CRLF; 4.LFI;|
| 低危 | 1-2 | 1.CSRF; 2.JSONP劫持; 3.异常堆栈信息; 3.PHPINFO; 4.路径泄露; 5.硬编码密码; 6.硬编码内网IP域名; 7.不安全的加密方法; 8.不安全的随机数; 9.日志敏感记录;|