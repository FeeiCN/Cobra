## 下载代码
```
git clone https://github.com/wufeifei/cobra.git
cd cobra/
```

## 安装系统依赖
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

# Cloc (任选其一)
npm install -g cloc                    # https://www.npmjs.com/package/cloc
sudo apt-get install cloc              # Debian, Ubuntu
sudo yum install cloc                  # Red Hat, Fedora
sudo pacman -S cloc                    # Arch
sudo pkg install cloc                  # FreeBSD
sudo port install cloc                 # Mac OS X with MacPorts
```

## 额外安装（如果在Mac OS X下）
```
# grep(gnu)
brew install homebrew/dupes/grep

# find(gnu)
brew install findutils
```

## 安装Python依赖
```
# Python目录下
[sudo] pip install -r requirements.txt
```

## 配置Cobra（[Cobra配置方法](https://github.com/wufeifei/cobra/wiki/Config)）
```
cp config.example config
vim config
```

## 初始化数据库表结构和数据
```
python cobra.py install
```

## 启动Cobra
```
python cobra.py start
```

## 常见安全问题
- https://github.com/wufeifei/cobra/wiki/Error

## 下一步
- [使用Cobra](https://github.com/wufeifei/cobra/wiki/Usage)