class VulnerabilityResult:
    def __init__(self):
        self.file_path = None
        self.line_number = None
        self.code_content = None
        self.match_result = None
        self.author = None
        self.timestamp = None

    def convert_to_dict(self):
        _dict = {}
        _dict.update(self.__dict__)
        return _dict
