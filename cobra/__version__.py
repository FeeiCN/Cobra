__title__ = 'cobra'
__description__ = 'Code Security Audit'
__url__ = 'https://github.com/wufeifei/cobra'
__version__ = '1.2.3'
__build__ = 0x021801
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
  cobra -t {td}
  cobra -t {td} -r cvi-190001,cvi-190002
  cobra -f json -o /tmp/report.json -t {td}
  cobra -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git
  cobra -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git
  cobra -H 127.0.0.1 -P 80
""".format(td='tests/examples')
