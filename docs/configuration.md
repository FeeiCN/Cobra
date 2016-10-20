> 请先更新最新的代码，将cobra根目录下的config.sample改名为config，并按照以下描述进行配置。

```
[cobra]
#
# 配置Cobra运行的域名，没有则无需配置
#
domain: cobra.wufeifei.com

#
# 配置Host
# 配置为0.0.0.0， 则可以外网访问
# 配置为127.0.0.1 则只有本机能访问
#
host: 127.0.0.1

#
# 配置访问默认
# 默认为80
#
port: 5000

# 是否开启Debug模式
debug: 0

# 日志目录
logs_directory: logs

# 加密Key（设置为32位md5值）
secret_key: your_secret_key


[upload]
# 被扫描代码的存放位置
# 不需要 \ /符号
directory: /tmp/cobra
# 支持上传的后缀
extensions: tar.bz2|tar|gz|tgz|tar.gz|rar|zip
# 最大上传大小(单位M)
max_size: 200

#
# 数据库配置
#
[database]
mysql: mysql+mysqldb://root:yourpassword@127.0.0.1:3306/cobra

#
# SVN账号配置
#
[svn]
username:
password:

#
# Git账号配置
#
[git]
username:
password:
```