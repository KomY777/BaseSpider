import sys
from scrapy.cmdline import execute

spider_id = int(sys.argv[1])
range_start_time = sys.argv[2].replace('_', ' ')
range_end_time = sys.argv[3].replace('_', ' ')
mode = sys.argv[4]
tolerance = sys.argv[5]
spidercmd = "scrapy crawl AnnouncementSpider -a spider_id=" + str(spider_id) +" -arange_start_time=" + range_start_time +\
            " -a range_end_time=" + range_end_time + " -a mode=" + mode + " -a tolerance=" + tolerance

execute(['scrapy', 'crawl', 'AnnouncementSpider', '-a', 'spider_id=' + str(spider_id), '-a', 'range_start_time=' + range_start_time, '-a', 'range_end_time=' + range_end_time, '-a', 'mode=' + mode, '-a', 'tolerance=' + tolerance])
