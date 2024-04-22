import sys
import os
from scrapy.cmdline import execute
sys.path.append('E:/Python-workspace/spider/SpiderCilent/BaseSpider')
from BaseSpider.settings import http

spider_id = sys.argv[1]


os.chdir('../runspider')
testcmd = 'python test.py {id} {base_key}'
os.system(testcmd)

os.chdir('../spiders')
range_start_time = sys.argv[2]
range_end_time = sys.argv[3]
mode = sys.argv[4]
spidercmd = "scrapy crawl BASE_SPIDER -a spider_id=" + spider_id +" -arange_start_time=" + range_start_time +\
            " -a range_end_time=" + range_end_time + " -a mode=" + mode

execute(spidercmd.split())
