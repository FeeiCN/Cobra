import sys
import platform

__title__ = 'cobra'
__description__ = 'Code Security Audit'
__url__ = 'https://github.com/WhaleShark-Team/cobra'
__issue_page__ = 'https://github.com/WhaleShark-Team/cobra/issues/new'
__python_version__ = sys.version.split()[0]
__platform__ = platform.platform()
__version__ = '2.0.0-alpha.5'
__author__ = 'Feei'
__author_email__ = 'feei@feei.cn'
__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2018 Feei. All rights reserved'
__introduction__ = """
    ,---.     |
    |    ,---.|---.,---.,---.
    |    |   ||   ||    ,---|
    `---``---``---``    `---^ v{version}

GitHub: https://github.com/WhaleShark-Team/cobra

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.""".format(version=__version__)
__epilog__ = """Usage:
  python {m} -t {td}
  python {m} -t {td} -r cvi-190001,cvi-190002
  python {m} -t {td} -f json -o /tmp/report.json 
  python {m} -t {tg} -f json -o feei@feei.cn 
  python {m} -t {tg} -f json -o http://push.to.com/api 
  python {m} -H 127.0.0.1 -P 8888
""".format(m='cobra.py', td='tests/vulnerabilities', tg='https://github.com/ethicalhack3r/DVWA')

__introduction_git__ = """
This script can push your target to the api
Please write cobra_ip, secret_key in config when you want to scan the specified git address
Please write gitlab_url, private_token, cobra_ip, secret_key when you want to scan all gitlab's projects
"""

__epilog_git__ = """Usage:
  python {m} -a
  python {m} -a -r cvi-190001,cvi-190002
  python {m} -a -f json -o /tmp/report.json 

  python {m} -t {td}
  python {m} -t {td},{td1}
  python {m} -t {td},{td1} -d
  python {m} -t {td} -r cvi-190001,cvi-190002
  python {m} -t {td} -f json -o /tmp/report.json 
  python {m} -t {tg} -f json -o feei@feei.cn 
  python {m} -t {tg} -f json -o http://push.to.com/api 
""".format(m='git_projcets.py', td='tests/vulnerabilities', td1='tests/dvwa',
           tg='https://github.com/ethicalhack3r/DVWA')
