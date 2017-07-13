class VulnerabilityResult:
    def __init__(self):
        self.vid = 0
        self.vulnerability = ''
        self.rule_name = ''
        self.file_path = None
        self.line_number = None
        self.code_content = None
        self.match_result = None
        self.discover_time = None
        self.commit_time = None
        self.commit_author = 'Unknown'
