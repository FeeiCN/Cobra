## Download source code
```
git clone https://github.com/wufeifei/cobra.git
cd cobra/
```

## Install system dependencies
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

# Cloc
npm install -g cloc                    # https://www.npmjs.com/package/cloc
sudo apt-get install cloc              # Debian, Ubuntu
sudo yum install cloc                  # Red Hat, Fedora
sudo pacman -S cloc                    # Arch
sudo pkg install cloc                  # FreeBSD
sudo port install cloc                 # Mac OS X with MacPorts
```

## extra install on macOS
```
# grep(gnu)
brew install homebrew/dupes/grep

# find(gnu)
brew install findutils
```

## Install Python dependencies
```
# on Cobra root
[sudo] pip install -r requirements.txt
```

## [Cobra configuration](http://cobra-docs.readthedocs.io/en/latest/configuration/)
```
cp config.example config
vim config
```

## Initialization database structure and base data
```
python cobra.py install
```

## Start Cobra
```
python cobra.py start
```

## Log
```bash
tail -f logs/cobra.log
```

## FAQ
- [http://cobra-docs.readthedocs.io/en/latest/FAQ/](http://cobra-docs.readthedocs.io/en/latest/FAQ/)
