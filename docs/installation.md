<<<<<<< HEAD
# Installation
```
git clone https://github.com/wufeifei/cobra.git
git checkout -b beta
cd cobra
python setup.py install
```

# Usage
```
# Scan Directory
python cobra.py -t tests/examples/

# Scan Git
python cobra.py -t https://github.com/wufeifei/cobra.git
=======
# Installation（安装）

## Python版本
Cobra可运行在以下Python版本
  - 2.6
  - 2.7
  - 3.3
  - 3.4
  - 3.5
  - 3.6

## macOS系统依赖
```
brew install grep findutils
```

## 安装Cobra
```bash
git clone https://github.com/wufeifei/cobra.git && cd cobra
pip install -r requirements.txt
./cobra.py --help
>>>>>>> upstream/master
```