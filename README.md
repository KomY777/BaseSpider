# 下载依赖
```shell
pip install -r requirements.txt
```

# 添加爬虫
在base_component 目录下放置解析器文件，注意文件名与类名格式

web端先添加解析器，再添加爬虫

添加完后打包项目并部署


# 打包
```shell
scrapyd-deploy --build-egg=output.egg 
```
将打包后的egg文件通过web部署到scrapyd服务


# 多节点部署
1. 在目标服务器上安装python3.9，并安装scrapyd
```shell
pip install scrapyd
```

2. 进入python第三方库site-packages<br/>
使用以下代码替换 scrapyd第三方库文件里的webservice.py文件中的DaemonStatus类 
>> scrapyd没有实现获取服务器状态的接口，需要自己实现。后续可以把scrapyd的代码fork下来再封装
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

3. 将scrapyd文件夹拷贝到目标服务器,进入scrapyd文件夹，使用scrapyd.conf启动scrapyd
```shell
scrapyd
```
