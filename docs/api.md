# API接口

## 启动HTTP服务
```bash
sudo ./cobra.py -H 127.0.0.1 -P 80
```

## 添加扫描任务
```bash
# 添加一条任务
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key", "target":"https://github.com/wufeifei/grw.git:master"}' http://127.0.0.1/api/add

# 添加多条任务
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key", "target":["https://github.com/wufeifei/cobra.git:master", "https://github.com/wufeifei/grw.git:master"]}' http://127.0.0.1/api/add
```

## 查询任务状态
```bash
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key","sid": "e3ea91nd1f4"}' http://127.0.0.1/api/status
```

## 查询扫描报告
```bash
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key","task_id": "your_task_id"}' http://127.0.0.1/api/report
```

# Web 报告页

## 任务汇总报告
```
http://127.0.0.1/?sid=afbe69p7dxva
```

## 扫描详情报告
```
http://127.0.0.1/report/afbe69p7dxva/sfbe69plo5qs
```