## python cobra.py start

* Q: Digest::MD5 not installed; will skip file uniqueness checks.
* A:
```
perl -MCPAN -e "shell"
> install Digest::MD5
```

## MySQL

|Code|Reason|
|---|---|
|1146|数据表不存在，请走完[安装流程](http://cobra-docs.readthedocs.io/en/latest/installation/)|
|1048|字段不能为NULL|
|1045|账号密码错误|
|1044|账号密码正确，但没有权限访问该DB|
|1129|该IP请求连接过多，使用```mysqladmin flush-hosts -p```刷新|

## Scan
* Q: 输入SVN地址无法扫描
* A: 目前SVN Checkout还存在问题，请手动SVN Checkout到本地，然后使用绝对路径扫描。

---
* Q: 提示扫描完成，但是没有扫到任何漏洞
* A: Cobra是一套扫描框架，你需要在后台为各种漏洞增加扫描规则。

---
* Q: Key verify failed
* A: config文件中的secret_key未配置