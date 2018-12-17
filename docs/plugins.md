# Plugin
## 作用
通过编写插件中的verify方法，增加Cobra的可拓展性，可以通过插件动态的增删检测代码到Cobra的检测中，用于应对代码结构复杂的情况，实现高度的可定制化的检测方式，针对检测项目编写对应的插件进行多个风险点的判断，增加整个检测的准确率。

## Plugin Template（插件模板）
```python
class CobraScan(object):
    def __init__(self):
        # 漏洞信息
        self.id = 140007  # 插件编号（参考规则编号命名规范）
        self.name = "直接输出入参可能导致XSS"  # 插件名称
        self.language = "JAVA"  # 插件语言
        self.author = "BlBana"  # 插件作者
        self.email = "blbana@qq.com"  # 作者邮箱
        self.level = 4  # 影响等级
        self.solution = '''
            ## 安全风险
            直接输出入参会导致XSS

            ## 修复方案
            
        '''  # 修复方案

        # status
        self.status = True  # 是否开启

        # 漏洞规则
        self.match_mode = "plugins-ast"  # 插件匹配模式
        self.match = "setAttribute|getWriter|write|append"  # 正则匹配规则
        self.match_block = "in-function-down"  # 代码块位置
        self.java_rule = ['setAttribute:javax.servlet.http.HttpServletRequest',
                          'getWriter:javax.servlet.http.HttpServletResponse',
                          'write:javax.servlet.http.HttpServletResponse',
                          'append:javax.servlet.http.HttpServletResponse']  # AST规则

    def verify(self):
        """
        插件脚本代码
        :return:
        """
        status = False
        result = {
            'status': status,  # verify验证是否成功
            'msg': 'test'
        }
        return result
```

### 插件字段规范
|字段（英文）|字段（中文）|是否必填|类型|描述|例子|
|---|---|---|---|---|---|
|`id`|插件编号|是|`string`|描述插件编号|`self.id = 140007`|
|`name`|插件名称|是|`string`|描述插件名称|`self.name = "直接输出入参可能导致XSS"`|
|`language`|插件语言|是|`string`|设置插件针对的开发语言，参见`languages`|`self.language = "JAVA"`|
|`author`|插件作者|是|`string`|规则作者的姓名|`self.author = "BlBana"`|
|`email`|插件作者邮箱|是|`string`|规则作者的邮箱|`self.email = "blbana@qq.com"`|
|`level`|影响等级|是|`integer`|标记该规则扫到的漏洞危害等级，使用数字1-10。|`self.level = 4`|
|`solution`|修复方案|是|`string`|该规则扫描的漏洞对应的**安全风险**和**修复方案**|`<solution>详细的安全风险和修复方案</solution>`|
|`status`|是否开启|是|`boolean`|是否开启该规则的扫描，使用`True`/`False`来标记|`self.status = True`|
|`match_mode`|匹配模式|是|`string`|选择插件的匹配模式，`plugins-ast`或`plugins`|`self.match_mode = "plugins-ast"`|
|`match`|匹配规则|是|`string`|匹配规则|`setAttribute|getWriter|write|append`或`正则匹配`|
|`match_block`|匹配规则|否|`string`|匹配规则|`self.match_block = "in-function-down"`|
|`java_rule`|AST规则|否|`list`|AST匹配所需规则|`['setAttribute:javax.servlet.http.HttpServletRequest'`|

### 匹配模式
#### plugins-ast模式
**进入条件**
`self.match_mode = plugins-ast`且`self.java_rule`不为空

> `self.java_rule`需要跟`self.match`中的规则一一对应，`self.match`用`|`分割敏感函数名，在`self.java_rule`中`[敏感函数名1:敏感函数所在模块名1, 敏感函数名2:敏感函数所在模块名2]`，以列表的形式存放敏感函数名以及对应的模块名

**检测方式**
1. 根据`self.match`进行第一次正则匹配；
2. 进入插件检测流程，使用`verify`方法对代码进行漏洞确认，当返回值`status`为`False`时，漏洞不存在；当返回值`status`为`True`时，进入流程3；
3. 进入AST分析模式，根据`self.match`和`self.java_rule`，进入到AST模块进行分析检测

#### plugins模式
**进入条件**
`self.match_mode = plugins`且`self.java_rule`为空时

> `self.match`可以按需求写正则表达式

**检测方式**
1. 根据`self.match`进行第一次正则匹配；
2. 进入插件检测流程，使用`verify`方法对代码进行漏洞确认，当返回值`status`为`False`时，漏洞不存在；当返回值`status`为`True`时，漏洞存在，返回结果；

## 插件编写规范
### CAST模块使用
> 相对第一次正则匹配的位置，提取行上，行内，行下等代码块，使用特定的正则对代码块进行多特征匹配，提高检测的准确率

#### 基础配置
- 引入CAST模块：`from cobra.cast import CAST`
- 配置代码块信息：`self.match_block = "in-function-down"`

#### 核心配置(verify方法内)
- 实例化CAST类：`cast = CAST(info.rule_match, info.target_directory, info.file_path, info.line_number, info.code_content)`
- 调用match方法：`is_match, data = cast.match(match, info.match_block)`

> 1. `match`变量为自定义的正则表达式，用于检测代码块中的特征
> 2. `info.match_block`为`self.match_block`位置信息

- 整理返回结果：`result = {'status': is_match, 'msg': ''}`

#### 代码块编写规范
|区块|描述|
|---|---|
| in-current-line | 由第一条规则触发的所在行 |
| in-function | 由第一条规则触发的函数体内 |
| in-function-up | 由第一条规则触发的所在行之上，所在函数体之内 |
| in-function-down | 由第一条规则触发的所在行之下，所在函数体之内 |
| in-file | 由第一条规则触发的文件内 |
| in-file-up | 由第一条规则触发的所在行之上，所在文件之内 |
| in-file-down | 由第一条规则触发的所在行之下，所在文件之内 |


### 自定义插件模块
> 根据检测需要编写`verify`方法，对项目进行检测，最后整理返回结果

```python
result = {
    'status': is_match,
    'msg': ''
}
```

## 插件编写示例
### 示例漏洞代码
```java
package Java;

import java.net.URL;
import javax.servlet.HttpServletRequest;


public class Demo {
        private static Image loadImage(String url) {
                Image image= null;
                try {
                    url = request.getParameter('url');
                    a = new URL(url);
                    image = new ImageIcon(a).getImage();
                } catch (MalformedURLException e) {
                    logger.error(e.getMessage(),e);
                }
                return image;
            }
}
```
> 代码从外部引用URL且未过滤，示例化URL类a后，直接用于了图片的请求，可能引起SSRF漏洞

**漏洞特征**
1. 使用了URL类
2. 使用了ImageIcon类，并调用了getImage方法

### 示例插件代码
```python
from cobra.cast import CAST


class CobraScan(object):
    def __init__(self):
        # 漏洞信息
        self.id = 210003
        self.language = "JAVA"
        self.author = "BlBana"
        self.email = "blbana@qq.com"
        self.name = "SSRF"
        self.level = 4
        self.solution = '''
            
        '''

        # status
        self.status = True

        # 漏洞规则
        self.match_mode = "plugins-ast"
        self.match = "URL"
        self.match_block = "in-function-down"
        self.java_rule = ['URL:java.net.URL']

    def verify(self, info):
        """

        :info: 原始漏洞信息
        :return:
        """
        status = False
        match = 'new ImageIcon\(.+\)\.getImage'
        cast = CAST(info.rule_match, info.target_directory, info.file_path, info.line_number, info.code_content)
        is_match, data = cast.match(match, info.match_block)
        result = {
            'status': is_match,  # verify验证是否成功
            'msg': 'test'
        }
        return result

```

**检测流程**
1. cast.match方法结合自定义的正则表达式，定位了第一个漏洞特征：`new ImageIcon(a).getImage()`
2. `status`状态被置位`True`
3. 主流程进入AST模块进行分析，判断`URL`参数是否外部可控
4. 漏洞确认

下一章：[规则模板](http://cobra.feei.cn/rule_template)