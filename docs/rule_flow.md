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
