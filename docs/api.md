# API接口

## 1. 添加扫描任务

#### 请求接口
接口：`/api/add`
方法：`POST`
类型：`JSON`

#### 请求参数

|参数|类型|必填|描述|例子|
|---|---|---|---|---|
|key|string|是|`config`文件中配置的`secret_key`|`{"key":"your_secret_key"}`|
|target|string或list|是|需要扫描的git地址，默认为master分支，如需指定分支或tag可在git地址末尾加上`:master`|单个项目扫描：`{"target": "https://github.com/FeeiCN/dict.git:master"}`；<br>多个项目扫描：`{"target": ["https://github.com/FeeiCN/dict.git:master", "https://github.com/FeeiCN/autossh.git:master"]}`|
|rule|string|否|仅扫描指定规则，以,分隔|`{"rule": "cvi-130003,cvi-130004"}`|

#### 响应例子
```json
{
    "code": 1001, # 状态码为1001则表示逻辑处理正常
    "result": {
        "msg": "Add scan job successfully.", # 消息
        "sid": "a938e2y2vnkf", # 扫描的任务ID（调用任务状态查询时需要用到）
        "total_target_num": 1 # 扫描任务的项目总数
    }
}
```

## 2. 查询扫描任务状态

#### 请求接口
接口：`/api/status`
方法：`POST`
类型：`JSON`

#### 请求参数

|参数|类型|必填|描述|例子|
|---|---|---|---|---|
|key|string|是|`config`文件中配置的`secret_key`|`{"key":"your_secret_key"}`|
|sid|string|是|扫描的任务ID|

#### 响应例子
```json
{
    "code": 1001, # 状态码为1001则表示逻辑处理正常
    "result": {
        "msg": "success", # 消息
        "not_finished": 0, # 未完成的项目数
        "report": "http://127.0.0.1/?sid=ae3ea90pkoo5", # 扫描报告页
        "sid": "ae3ea90pkoo5", # 扫描的任务ID
        "allow_deploy": true, # 是否允许发布上线
        "statistic": { # 高中低危漏洞数量
            "high": 5,
            "medium": 18,
            "critical": 0,
            "low": 28
        },
        "status": "done", # 扫描状态
        "still_running": {}, # 正在扫描的项目
        "total_target_num": 1, # 扫描任务的项目总数
    }
}
```

# 完整的例子
## 启动HTTP服务
```bash
python cobra.py -H 127.0.0.1 -P 8888
```

## 添加扫描任务
```bash
# 添加一条任务
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key", "target":"https://github.com/FeeiCN/grw.git:master", "rule": "cvi-130003,cvi-130004"}' http://127.0.0.1:8888/api/add

# 添加多条任务
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key", "target":["https://github.com/WhaleShark-Team/cobra.git:master", "https://github.com/FeeiCN/grw.git:master"]}' http://127.0.0.1:8888/api/add
```

## 查询任务状态
```bash
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key","sid": "a938e29vdse8"}' http://127.0.0.1:8888/api/status
```

# Web 报告页

```
http://127.0.0.1:8888/?sid=afbe69p7dxva
```

# Web 指定时间段漏洞统计
```
http://127.0.0.1:8888/report
```

---
下一章：[高级功能配置](http://cobra.feei.cn/config)
