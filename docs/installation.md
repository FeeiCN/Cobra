# Installation（安装）

## 系统支持

|系统|支持情况|
|---|---|
| mac OS | 支持 |
| Linux | 支持 |
| Windows | 暂不支持 |

## Python版本
Cobra可运行在以下Python版本
  - 2.6
  - 2.7
  - 3.3
  - 3.4
  - 3.5
  - 3.6
  - 3.6+

## 特殊依赖
> 以下系统需要单独安装依赖。

#### macOS系统依赖
```
brew install grep findutils flex phantomjs
```

#### Ubuntu系统依赖
```
apt-get install flex bison phantomjs
```

#### CentOS系统依赖
```
yum install flex bison phantomjs
```

## 安装方法
```bash
git clone https://github.com/WhaleShark-Team/cobra.git && cd cobra
pip install -r requirements.txt
python cobra.py --help
```



---
下一章：[CLI模式使用方法](http://cobra.feei.cn/cli)
