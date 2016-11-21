# 密码硬编码特殊情况下的处理方式

#### 1. 该文件为测试用例的话怎么办？

> 首先，如测试用例中的密码是工作中常用密码，必须改掉。
>
> 如果不是常用密码，则按照以下方式修改，[Cobra](https://github.com/wufeifei/cobra)将跳过检测。

##### - Java测试用例

请将上层文件夹命名为test，[Cobra](https://github.com/wufeifei/cobra)将跳过对该文件夹中所有文件的所有安全检测。



##### - PHP测试用例

```php
/**
 * 第一种情况：单函数为测试函数
 * @test // 在函数注释中增加此行，Cobra将跳过该函数的所有安全检查。
 */
function test_sendSMS()
{
	$password = "123456";
  	$response = curl(API, $password);
  	return $response;
}
```

```php
/**
 * 第二种情况：整个文件或者类都为测试函数
 * @test // 在文件顶部注释中增加此行，Cobra将跳过该文件的所有安全检查。
 */
class test{
  function test_1(){}
  function test_2(){}
  function test_n(){}
}
```

#### 2. 如果整个项目都废弃了（未部署、未上线、未使用）

在项目根目录增加一个文件，并确保该文件无法通过线上Web目录获取到。

文件名：cobra

文件内容：

```javascript
#
# 本文件为Cobra安全扫描配置文件，如不清楚使用方法请联系@止介，请勿擅自修改！
#
# @author   Feei <wufeifei#wufeifei.com>
# @link     https://github.com/wufeifei/cobra
# @document http://cobra-docs.readthedocs.io/
scan:false
```