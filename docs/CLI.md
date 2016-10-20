```
$ python cobra.py --help
usage: cobra.py [-?] {shell,scan,db,runserver,start,statistic} ...

positional arguments:
  {shell,scan,db,runserver,start,statistic}
    shell               Runs a Python shell inside Flask application context.
    db                  Perform database migrations
    runserver           Runs the Flask development server i.e. app.run()
    start               启动Cobra
    install             初始化Cobra数据库接口和初始数据
    statistic           统计Cobra代码行数

optional arguments:
  -?, --help            show this help message and exit
```