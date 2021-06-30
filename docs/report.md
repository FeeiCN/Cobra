# Report模块使用
> Report模块主要用来指定时间段的漏洞统计，分为CLI模式和Web两种模式 

### CLI模式
> CLI模式在执行命令，自动使用*phantomjs*请求Report模块的Web页面，统计一周内的漏洞分布情况，并截图发送至指定邮箱

#### 配置内容
配置config文件:
1. host：SMTP服务器地址
2. port：SMTP服务器端口
3. username：SMTP服务器登陆用户
4. password：SMTP服务器登陆密码
5. sender：发送人邮箱
6. to：收件人邮箱
7. cobra_ip：Cobra服务器地址

#### 使用方法
> 与Crontab定时任务使用，完成自动发送周报功能

`python cobra.py -rp`执行命令，完成报告截图和发送邮件操作

### Web模式

#### URL
http://127.0.0.1:8080/report进入Cobra Report页面，选择start 和 end时间查看指定时间段的扫描报告

#### 报告内容
1. 各等级漏洞数量
2. Top 10漏洞饼图展示
3. 扫描文件总数
4. 扫描项目总数
5. 扫描漏洞总数
6. start时间，end时间
7. 每日漏洞数量折线图展示

下一章：[规则模板](http://cobra.feei.cn/rule_template)
