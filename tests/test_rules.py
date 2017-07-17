from cobra.rule import Rule


def test_languages():
    languages = Rule().languages
    assert isinstance(languages, dict)
    assert 'php' in languages
    assert 'chiefly' in languages['php']
    assert 'extensions' in languages['php']
    assert 'True' in languages['php']['chiefly']
    assert '.php' in languages['php']['extensions']


def test_frameworks():
    frameworks = Rule().frameworks
    assert isinstance(frameworks, dict)
    assert 'python' in frameworks
    assert 'flask' in frameworks['python']
    assert 'rules' in frameworks['python']['flask']
    assert 'dependency' in frameworks['python']['flask']['rules'][0]
    assert 'code' in frameworks['python']['flask']


def test_vulnerabilities():
    vulnerabilities = Rule().vulnerabilities
    assert isinstance(vulnerabilities, dict)
    assert '10010' in vulnerabilities
    assert 'name' in vulnerabilities['10010']
    assert 'description' in vulnerabilities['10010']
    assert 'level' in vulnerabilities['10010']
    assert 'repair' in vulnerabilities['10010']


def test_rules():
    rules = Rule().rules
    assert isinstance(rules, list)
    assert len(rules) > 1
    assert 'name' in rules[0]
    assert 'status' in rules[0]
    assert 'vulnerability' in rules[0]
    assert 'author' in rules[0]
    assert 'file' in rules[0]
    assert 'test' in rules[0]
    assert 'true' in rules[0]['test']
    assert 'false' in rules[0]['test']
    assert 'match' in rules[0]
    assert 'match2' in rules[0]
    assert 'match2-block' in rules[0]
    assert 'repair' in rules[0]
    assert 'repair-block' in rules[0]
    assert 'language' in rules[0]
