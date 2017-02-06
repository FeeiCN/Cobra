
# config
```
{url} = http://cobra.feei.cn/api/
{key} = *************************
```

# add
> create Cobra scan job

** URI **
```
{url}/add
```

** Params **

Name | Method | Optional | Type | Comment
---|---|---|---|---
key | POST | False | 'string' | Key
target | POST | False | 'string' | Git/SVN URL
branch | POST | False | 'string' | Code Branch
old_version | POST | False | 'string' | Old Branch Version(online version)
new_version | POST | True | 'string' | New Branch Version(current version)

** Response ** (JSON)
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

** Manual test **
```
curl -H "Content-Type: application/json" -X POST -d '{"key":"you key", "target":"https://github.com/wufeifei/grw.git","branch":"master"}' http://cobra.feei.cn/api/add

{
    code: 1001,
    result: {
        scan_id: '34b9a295d037d47eec3952e9dcdb6b2b'
    }
}
```

---

# status
get scan job status

** URI **
```
{url}/status
```

** Params **

Name | Method | Optional | Type | Comment
---|---|---|---|---
key | POST | False | 'string' | Key
scan_id | POST | False | 'string' | Scan ID

** Response **(JSON)
```
{
    status: 1001,
    result: {
        status: 'info', // Status
        text: '通过(部分存在风险，建议优化!)', // Description
        report: 'http://cobra.feei.cn/report/123', // Report URL
        allow_deploy: true // Allow deploy this code
    }
}
```

Status|Description
---|---
success|Success(未发现任何风险)
info|Risk (存在风险，建议优化，但可以发布！)
critical|Possible Vulnerabilities （可能造成漏洞，并禁止发布！）
vul|Vulnerabilities（确认是漏洞，自动通知安全团队，并禁止发布！）

** Errors and Exceptions **

Code | Mean
---|---
1001| Success
4444|unknown error

** Manual Test **
```
curl -H "Content-Type: application/json" -X POST -d '{"key":"your key", "scan_id":"24"}' http://cobra.feei.cn/api/status

{
    status: 1001,
    result: {
        status: 'info', // Status
        text: '通过(部分存在风险，建议优化!)', // Description
        report: 'http://cobra.feei.cn/report/123', // Report URL
        allow_deploy: true // Allow deploy this code
    }
}
```