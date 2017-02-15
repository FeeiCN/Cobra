Copy **config.example** to *config* in the Cobra root directory.
```bash
cp config.example config 
```

```
[cobra]
#
# Configure Cobra to run the domain name, but do not need to configure it
#
domain: cobra.feei.cn

#
# Configure the host
# Configure 0.0.0.0 to allow external network access
# Only 127.0.0.1 can be configured
#
host: 127.0.0.1

#
# Configure the access default
# The default is 80
#
port: 5000

# Enable Debug mode
debug: 0

# The log directory
logs_directory: logs

# Encryption Key (set to 32-bit md5 value)
# Secret_key used to encrypt session and cookie, you can set any random number. For example `os.urandom(32)` or `hashlib.sha1('your_password').hexdigest()`
secret_key: your_secret_key


[upload]
# The location where the scanned code is stored
# The \ / symbol is not required
directory: /tmp/cobra

# Support upload suffix
extensions: tar.bz2|tar|gz|tgz|tar.gz|rar|zip

# Maximum upload size (in M)
max_size: 200

[third_party_vulnerabilities]
# Push vulnerabilities to third vulnerabilities
status: 0

# Third vulnerabilities api url
api:

# Key
key:

#
# If need push mail/vulnerability
#
[queue]
broker:redis://:password@127.0.0.1:7890/4
backend:redis://:password@127.0.0.1:7890/4

#
# Database account
#
[database]
mysql: mysql+mysqldb://root:yourpassword@127.0.0.1:3306/cobra

[email]
host:
port:
user:
password:

[report]
to:

#
# SVN account
#
[svn]
username:
password:

#
# Inner git account
#
[git]
username:
password:
```