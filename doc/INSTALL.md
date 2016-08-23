#### Install System Dependents
```
# Python
[sudo] yum install Python-devel

# MySQL
[sudo] yum install MySQL-python
[sudo] yum install mysql-devel

# PIP
[sudo] yum install epel-release
[sudo] yum install python-pip

# gcc-c++
[sudo] yum install gcc-c++
```

#### On Mac OS X

On latest homebrew ggrep is moved to homebrew/dupes tap.

```
# grep
brew install homebrew/dupes/grep

# find
brew install findutils
```

#### Install Python Dependents
```
cd /path/to/cobra
[sudo] pip install -r requirements.txt
```

#### Config Cobra
```
cp config.example config
vim config
```

#### Start Cobra
```
python cobra.py start
```
