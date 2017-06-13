from cobra.engine.rules import Rules


def test_languages():
    languages = Rules().languages
    assert isinstance(languages, dict)
    assert 'php' in languages
    assert '.php' in languages['php']


def test_frameworks():
    frameworks = Rules().frameworks
    assert isinstance(frameworks, dict)
    assert 'python' in frameworks
    assert 'flask' in frameworks['python']
    assert 'rules' in frameworks['python']['flask']
    assert 'dependency' in frameworks['python']['flask']['rules'][0]
    assert 'code' in frameworks['python']['flask']


def test_vulnerabilities():
    vulnerabilities = Rules().vulnerabilities
    assert isinstance(vulnerabilities, dict)
    assert '10010' in vulnerabilities
    assert 'name' in vulnerabilities['10010']
    assert 'description' in vulnerabilities['10010']
    assert 'level' in vulnerabilities['10010']
    assert 'repair' in vulnerabilities['10010']


def test_rules():
    rules = Rules().rules
    assert isinstance(rules, dict)
    rule_name = 'Hardcoded-Password'
    assert rule_name in rules
    assert 'status' in rules[rule_name][0]
    assert 'name' in rules[rule_name][0]
    assert 'vid' in rules[rule_name][0]
    assert 'author' in rules[rule_name][0]
    assert 'test' in rules[rule_name][0]
    assert 'match' in rules[rule_name][0]
