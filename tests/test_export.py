from cobra import export
from cobra.result import VulnerabilityResult
import random
from cobra.send_mail import send_mail
from cobra.push_to_api import PushToHades


def test_export():
    find_vul = []
    for i in range(4):
        srv = []
        for j in range(3):
            mr = VulnerabilityResult()
            mr.file_path = "/etc/passwd"
            mr.line_number = 182
            mr.author = "author"
            mr.code_content = "<script>alert(document.cookie)</script>"
            mr.match_result = "pregex"
            mr.timestamp = "2017-04-04"
            mr.mode = "javascript"
            mr.id = random.randint(10000, 99999)
            mr.type = "xss"
            srv.append(mr)
        find_vul.append(srv)
    export.write_to_file(find_vul, 'html', 'examples/test.html')
    send_mail(filename="examples/test.html")
    pusher = PushToHades()
    pusher.add_data(find_vul=find_vul)
    pusher.push()
