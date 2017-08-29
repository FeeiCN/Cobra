# Demo（例子）
> 把常见漏洞划分为四大类

## 1. 单一匹配: 仅匹配单次
**例子：错误的配置(使用了ECB模式)**
```java
Cipher c = Cipher.getInstance("AES/ECB/NoPadding");
```

**Solution(规则写法)**

可以通过配置一条match规则，规则mode设置为`regex`(仅匹配，通过正则模式匹配，匹配到则算作漏洞)，即可扫描这类问题。
```xml
<match mode="regex-only-match"><![CDATA[Cipher....Instance\s?\(\s?\".*ECB]]></match>
```
## 2. 多次匹配：需要进行多次匹配
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

## 3. 参数可控：只要判定参数是用户可控的则算作漏洞
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
> 依赖安全的规则固定配置在`CVI-999999.xml`中。

**例子：FastJSON v1.2.24版本存在RCE漏洞**

**Solution(规则写法)**

```xml
<cve id="FastJSON RCE" level="HIGH">
    <product>fastjson:1.2.24</product>
</cve>
```

---
下一章：[规则文件命名规范](https://wufeifei.github.io/cobra/rule_name)