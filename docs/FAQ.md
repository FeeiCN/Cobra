## python cobra.py start

* 提示: Digest::MD5 not installed; will skip file uniqueness checks.
* 解决:
```
perl -MCPAN -e "shell"
> install Digest::MD5
```

## MySQL

|Code|Reason|
|---|---|
|1146|数据表不存在，请走完[安装流程](https://github.com/wufeifei/cobra/wiki/Installation)|
|1048|字段不能为NULL|
|1045|账号密码错误|
|1044|账号密码正确，但没有权限访问该DB|
|1129|该IP请求连接过多，使用```mysqladmin flush-hosts -p```刷新|

## 扫描
* 问题：输入SVN地址无法扫描
* 原因：目前SVN Checkout还存在问题，请手动SVN Checkout到本地，然后使用绝对路径扫描。

* 问题：提示扫描完成，但是没有扫到任何漏洞
* 原因：Cobra是一套扫描框架，你需要在后台为各种漏洞增加扫描规则。
