> API接口是供第三方系统调用，比如代码发布系统。

```
{url} = http://cobra.wufeifei.com/api/
{key} = *************************
```

## add接口
创建Cobra扫描任务

#### 接口描述
```
{url}/add
```

#### 参数
Name | Method | Optional | Type | Comment
---|---|---|---|---
key | POST | False | 'string' | Key
target | POST | False | 'string' | Git/SVN URL
branch | POST | False | 'string' | Code Branch
old_version | POST | False | 'string' | Old Branch Version(online version)
new_version | POST | True | 'string' | New Branch Version(current version)

#### 返回值
JSON
```
{
    code: 1001,
    result: {
        msg: 'success',
        scan_id: '34b9a295d037d47eec3952e9dcdb6b2b',
        project_id: 1
    }
}
```

#### 手动测试例子
使用Curl测试
```
curl -H "Content-Type: application/json" -X POST -d '{"key":"you key", "target":"https://github.com/wufeifei/grw.git","branch":"master"}' http://cobra.wufeifei.com/api/add
```
Response
```
{
    code: 1001,
    result: {
        scan_id: '34b9a295d037d47eec3952e9dcdb6b2b'
    }
}
```

## status接口
查询创建的任务扫描状态

#### 接口地址
```
{url}/status
```

#### 参数
Name | Method | Optional | Type | Comment
---|---|---|---|---
key | POST | False | 'string' | Key
scan_id | POST | False | 'string' | Scan ID

#### 返回值
JSON
```
{
    status: 1001,
    result: {
        status: 'info', // 状态
        text: '通过(部分存在风险，建议优化!)', // 描述
        report: 'http://cobra.wufeifei.com/report/123', // 报告地址
        allow_deploy: true // 是否允许发布
    }
}
```

Status|Description
---|---
success|Success(未发现任何风险)
info|Risk (存在风险，建议优化，但可以发布！)
critical|Possible Vulnerabilities （可能造成漏洞，并禁止发布！）
vul|Vulnerabilities（确认是漏洞，自动通知安全团队，并禁止发布！）

#### 错误和异常代码
Code | Mean
---|---
1001| Success
4444|unknown error

#### 手动测试例子
使用Curl测试
```
curl -H "Content-Type: application/json" -X POST -d '{"key":"your key", "scan_id":"24"}' http://cobra.wufeifei.com/api/status
```
Response
```
{
    status: 1001,
    result: {
        status: 'info', // 状态
        text: '通过(部分存在风险，建议优化!)', // 描述
        report: 'http://cobra.wufeifei.com/report/123', // 报告地址
        allow_deploy: true // 是否允许发布
    }
}
```