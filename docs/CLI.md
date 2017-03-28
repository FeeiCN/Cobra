```
$ python cobra.py --help
usage: cobra.py [-?]
                {repair,shell,scan,runserver,start,install,statistic,report,pull}
                ...

Cobra v1.7 ( https://github.com/wufeifei/cobra ) is a static code analysis
system that automates the detecting vulnerabilities and security issue.

positional arguments:
  {repair,shell,scan,runserver,start,install,statistic,report,pull}
    repair              Detection of existing vulnerabilities to repair the
                        situation
    shell               Runs a Python shell inside Flask application context.
    scan                Scan vulnerabilities
    runserver           Runs the Flask development server i.e. app.run()
    start               Runs the Flask development server i.e. app.run()
    install             Initialize the table structure
    statistic           Statistics code-related information
    report              Send report
    pull                Pull project code

optional arguments:
  -?, --help            show this help message and exit
```
### Install
```
# Install
python cobra.py install
```

### Start
```
# Start
python cobra.py start
```

### Scan
```bash
# Scan all projects
python cobra.py scan --all=true

# Scan special project (Not recommended manually)
python cobra.py scan --target=project_directory --tid=task_id --pid=project_id
```

### Report
```bash
# Send weekly reports (Use the mail)
python cobra.py report --time=w

# Send monthly reports (Use the mail)
python cobra.py report --time=m

# Send February monthly reports (Use the mail)
python cobra.py report --time=m --month=2

# Send quarterly reports (Use the mail)
python cobra.py report --time=q
```

### Repair
```bash
python cobra.py repair --pid=your_project_id
```

### Statistic (Not recommended manually)
```bash
python cobra.py statistic --target=project_directory --tid=task_id
```

### Pull
```bash
# Pull special project code
python cobra.py pull --pid=project_id

# Pull all projects code
python cobra.py pull --all=true
```