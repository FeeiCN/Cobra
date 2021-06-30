# 目录结构（Tree）
```bash
.
├── CONTRIBUTING.md（贡献文档）
├── LICENSE（开源协议）
├── README.md（介绍页）
├── cobra（主程序目录）
│   ├── __init__.py
│   ├── __version__.py
│   ├── api.py
│   ├── cast.py
│   ├── cli.py
│   ├── config.py
│   ├── const.py
│   ├── cve_parse.py
│   ├── dependencies.py
│   ├── detection.py
│   ├── engine.py
│   ├── exceptions.py
│   ├── export.py
│   ├── git_projects.py
│   ├── log.py
│   ├── parser.py
│   ├── pickup.py
│   ├── push_to_api.py
│   ├── result.py
│   ├── rule.py
│   ├── scheduler
│   │   ├── __init__.py
│   │   ├── report.js
│   │   ├── report.py
│   │   └── scan.py
│   ├── send_mail.py
│   ├── templates
│   │   ├── asset（前台展示所需要的静态文件）
│   │   │   ├── codemirror
│   │   │   ├── css
│   │   │   ├── fonts
│   │   │   ├── ico
│   │   │   ├── icon
│   │   │   ├── img
│   │   │   └── js
│   │   └── *.html
│   ├── templite.py
│   └── utils.py
├── cobra.py（Cobra入口调用）
├── config（Cobra主配置文件）
├── config.template（Cobra主配置文件模板）
├── docs
│   ├── _config.yml（GitHub Pages配置）
│   └── *.md （相关文档）
├── logs（日志目录）
├── requirements.txt (Cobra包依赖)
├── rules（规则相关）
│   ├── CVI-110001.xml （漏洞扫描规则定义）
│   ├── frameworks.xml （框架识别的特征定义）
│   ├── languages.xml （开发语言及文件类型与后缀定义）
│   └── vulnerabilities.xml （漏洞类型及Label定义）
└── tests（测试相关）
    ├── __init__.py
    ├── ast （AST测试）
    ├── examples （测试用例所依赖的）
    ├── test_*.py （测试用例）
    └── vulnerabilities （各类测试的漏洞代码）
```

---
下一章：[单元测试](http://cobra.feei.cn/test)
