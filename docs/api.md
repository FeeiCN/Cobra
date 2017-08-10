# API接口

## 启动HTTP服务
```bash
sudo ./cobra.py -H 127.0.0.1 -P 80
```

## 添加扫描任务
```bash
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key", "target":"https://github.com/wufeifei/grw.git","branch":"master"}' http://127.0.0.1/api/add
```

## 查询任务状态
```bash
curl -H "Content-Type: application/json" -X POST -d '{"key":"your_secret_key","sid": "e3ea91nd1f4"}' http://127.0.0.1/api/status
```