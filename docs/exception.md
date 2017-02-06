# Special circumstances

__(The following actions will cause Cobra to skip the security scan of the corresponding project or file. Use caution!!!)__

### 1. TestCase file

> Must fixed if the test case password is a common password at work.
>
> If it is not a common password, modify it in the following way，[Cobra](https://github.com/wufeifei/cobra) will skip。

```
- /test/
- /tests/
- /unitTests/
```

##### - Java TestCase

The file path contains test / tests / unitTests，[Cobra](https://github.com/wufeifei/cobra) will skip。



##### - PHP TestCase

```php
/**
 * The first case: a single function for the test function
 * @test // When you add this line to a function comment, Cobra skips all the security checks for that function.
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
 * The second case: the entire file or class for the test function
 * @test // When you add this line in the comment at the top of the file, Cobra skips all the security checks for that file.
 */
class test{
  function test_1(){}
  function test_2(){}
  function test_n(){}
}
```

### 2. Project offline (not deployed, not on-line, not used)

Add a file to the project root directory and make sure that the file is not available through the online Web directory.

Filename: cobra

File content:

```javascript
#
# This file is the Cobra security scan configuration file, please contact @Security before making changes!
#
# @author   Feei <feei#feei.cn>
# @link     https://github.com/wufeifei/cobra
# @document http://cobra-docs.readthedocs.io/
scan:false
```

### 3. Third-party Open Source code

Open source projects in the sweep to the general problem, is no need to modify.

You can skip the scan of the file by adding `@cobra third-party` in the header comment on the corresponding trigger file.

```php
/**
 * Something else
 *
 * @author Feei<wufeifei#wufeifei>
 * @param something
 * @cobra third-party
 */
 something code...
```

### 4. Const in Hard-coded Password Case

When determining that the constant does not have authentication, add `@cobra const` to the file's header comment to skip the file's scan.

```php
/**
 * Something else
 *
 * @author Feei<wufeifei#wufeifei>
 * @param something
 * @cobra const
 */
 something code...
```