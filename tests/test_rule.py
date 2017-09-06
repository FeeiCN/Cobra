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
    assert '110' in vulnerabilities
    assert 'MC' in vulnerabilities['110']


def test_rules():
    rules = Rule().rules
    assert isinstance(rules, object)
