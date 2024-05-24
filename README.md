# 下载依赖
```shell
pip install -r requirements.txt
```
# 部署前配置
将以下代码替换 scrapyd第三方库文件里的webservice.py文件中的DaemonStatus类
```python

import psutil

class DaemonStatus(WsResource):
    def render_GET(self, txrequest):
        pending = sum(q.count() for q in self.root.poller.queues.values())
        running = len(self.root.launcher.processes)
        finished = len(self.root.launcher.finished)

        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_total_mb = memory.total / 1024 / 1024
        memory_used_mb = memory.used / 1024 / 1024
        disk = psutil.disk_usage('/')
        disk_total_mb = disk.total / 1024 / 1024
        disk_used_mb = disk.used / 1024 / 1024

        return {
            "node_name": self.root.nodename,
            "status": "ok",
            "pending": pending,
            "running": running,
            "finished": finished,
            "cpu_count": cpu_count,
            "cpu_percent": cpu_percent,
            "memory_total_mb": memory_total_mb,
            "memory_used_mb": memory_used_mb,
            "disk_total_mb": disk_total_mb,
            "disk_used_mb": disk_used_mb,
        }
```

# 打包
```shell
cd scrapyd

scrapyd

scrapyd-deploy -F egg=output.egg  
```
将打包后的egg文件通过web部署到scrapyd服务