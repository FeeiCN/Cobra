import sys
import platform

__title__ = 'cobra'
__description__ = 'Code Security Audit'
__url__ = 'https://github.com/wufeifei/cobra'
__issue_page__ = 'https://github.com/wufeifei/cobra/issues/new'
__python_version__ = sys.version.split()[0]
__platform__ = platform.platform()
__version__ = '2.0.0-alpha.3'
__author__ = 'Feei'
__author_email__ = 'feei@feei.cn'
__license__ = 'MIT License'
__copyright__ = 'Copyright (C) 2017 Feei. All Rights Reserved'
__introduction__ = """
    ,---.     |
    |    ,---.|---.,---.,---.
    |    |   ||   ||    ,---|
    `---``---``---``    `---^ v{version}

GitHub: https://github.com/wufeifei/cobra

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.""".format(version=__version__)
__epilog__ = """Usage:
  python {m} -t {td}
  python {m} -t {td} -r cvi-190001,cvi-190002
  python {m} -t {td} -f json -o /tmp/report.json 
  python {m} -t {tg} -f json -o feei@feei.cn 
  python {m} -t {tg} -f json -o http://push.to.com/api 
  sudo python {m} -H 127.0.0.1 -P 80
""".format(m='cobra.py', td='tests/vulnerabilities', tg='https://github.com/ethicalhack3r/DVWA')
