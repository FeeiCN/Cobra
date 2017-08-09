# CLI模式

## Examples（使用例子）
```bash
# 扫描一个文件夹的代码
$ ./cobra.py -t tests/vulnerabilities

# 扫描一个Git项目代码
$ ./cobra.py -t https://github.com/wufeifei/grw.git

# 扫描一个文件夹，并将扫描结果导出为JSON文件
$ ./cobra.py -t tests/vulnerabilities -f json -o /tmp/report.json

# 扫描一个Git项目，并将扫描结果JSON文件推送到API上
$ ./cobra.py -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git

# 扫描一个Git项目，并将扫描结果JSON文件发送到邮箱中
$ ./cobra.py -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git

# 扫描一个文件夹代码的某两种漏洞
$ ./cobra.py -t tests/vulnerabilities -r cvi-190001,cvi-190002

# 开启一个Cobra HTTP Server，然后可以使用API接口来添加扫描任务
$ ./cobra.py -H 127.0.0.1 -P 80

# 查看版本
$ ./cobra.py --version

# 查看帮助
$ ./cobra.py --help
```