import sys
import os
from scrapy.cmdline import execute
sys.path.append('E:/Python-workspace/spider/SpiderCilent/BaseSpider')
from BaseSpider.settings import http

spider_id = int(sys.argv[1])

spider_model = http.request(r'spider_model_query', {'spider_id': spider_id}).json()['spider']
model_name = spider_model['model_name']
base_key = spider_model['base_key']

# os.chdir('../runspider')
# testcmd = 'python test.py {id} {base_key}'
# testcmd = testcmd.format(id=spider_id, base_key=base_key)
# os.system(testcmd)

os.chdir('../spiders')
range_start_time = sys.argv[2]
range_end_time = sys.argv[3]
mode = sys.argv[4]
spidercmd = "scrapy crawl AnnouncementSpider -a spider_id=" + str(spider_id) +" -arange_start_time=" + range_start_time +\
            " -a range_end_time=" + range_end_time + " -a mode=" + mode

execute(spidercmd.split())
