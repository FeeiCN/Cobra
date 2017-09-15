# CLI模式

## Examples（使用例子）
```bash
# 扫描一个文件夹的代码
$ python cobra.py -t tests/vulnerabilities

# 扫描一个Git项目代码
$ python cobra.py -t https://github.com/wufeifei/grw.git

# 扫描一个文件夹，并将扫描结果导出为JSON文件
$ python cobra.py -t tests/vulnerabilities -f json -o /tmp/report.json

# 扫描一个Git项目，并将扫描结果JSON文件推送到API上
$ python cobra.py -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git

# 扫描一个Git项目，并将扫描结果JSON文件发送到邮箱中
$ python cobra.py -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git

# 扫描一个文件夹代码的某两种漏洞
$ python cobra.py -t tests/vulnerabilities -r cvi-190001,cvi-190002

# 开启一个Cobra HTTP Server，然后可以使用API接口来添加扫描任务
$ python cobra.py -H 127.0.0.1 -P 80

# 查看版本
$ python cobra.py --version

# 查看帮助
$ python cobra.py --help
```

## Help（帮助）
```bash
➜  cobra git:(master) ✗ python cobra.py --help
usage: cobra [-h] [-t <target>] [-f <format>] [-o <output>] [-r <rule_id>]
             [-d] [-sid SID] [-H <host>] [-P <port>]

    ,---.     |
    |    ,---.|---.,---.,---.
    |    |   ||   ||    ,---|
    `---``---``---``    `---^ v2.0.0

GitHub: https://github.com/wufeifei/cobra

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.

optional arguments:
  -h, --help            show this help message and exit

Scan:
  -t <target>, --target <target>
                        file, folder, compress, or repository address
  -f <format>, --format <format>
                        vulnerability output format (formats: html, json, csv,
                        xml)
  -o <output>, --output <output>
                        vulnerability output STREAM, FILE, HTTP API URL, MAIL
  -r <rule_id>, --rule <rule_id>
                        specifies rules e.g: CVI-100001,cvi-190001
  -d, --debug           open debug mode
  -sid SID, --sid SID   scan id(API)

RESTful:
  -H <host>, --host <host>
                        REST-JSON API Service Host
  -P <port>, --port <port>
                        REST-JSON API Service Port

Usage:
  python cobra.py -t tests/vulnerabilities
  python cobra.py -t tests/vulnerabilities -r cvi-190001,cvi-190002
  python cobra.py -t tests/vulnerabilities -f json -o /tmp/report.json
  python cobra.py -t https://github.com/ethicalhack3r/DVWA -f json -o feei@feei.cn
  python cobra.py -t https://github.com/ethicalhack3r/DVWA -f json -o http://push.to.com/api
  python cobra.py -H 127.0.0.1 -P 8888
```
---
下一章：[API模式使用方法](https://wufeifei.github.io/cobra/api)