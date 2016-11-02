Rename Cobra root's ** config.sample ** to ** config **.

```
[Cobra]
#
# Configure Cobra to run the domain name, but do not need to configure it
#
Domain: cobra.wufeifei.com

#
# Configure the host
# Configure 0.0.0.0 to allow external network access
# Only 127.0.0.1 can be configured
#
Host: 127.0.0.1

#
# Configure the access default
# The default is 80
#
Port: 5000

# Enable Debug mode
Debug: 0

# The log directory
Logs_directory: logs

# Encryption Key (set to 32-bit md5 value)
# Secret_key used to encrypt session and cookie, you can set any random number. For example `os.urandom(32)` or `hashlib.sha1('your_password').hexdigest()`
Secret_key: your_secret_key


[Upload]
# The location where the scanned code is stored
# The \ / symbol is not required
Directory: / tmp / cobra
# Support upload suffix
Extensions: tar.bz2 | tar | gz | tgz | tar.gz | rar | zip
# Maximum upload size (in M)
Max_size: 200

#
# Database account
#
[Database]
Mysql: mysql + mysqldb: // root: yourpassword@127.0.0.1: 3306 / cobra

#
# SVN account
#
[Svn]
Username:
Password:

#
# Inner git (gitlab or deploy git server) account
#
[Git]
Username:
Password:
```