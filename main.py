#-*- coding:utf-8 -*-
import sys
from crawl.crawl import main as start_crawl
from utils.crawl_channel_lists import crawl
if '-log' in sys.argv:
    '''
    统计日志
    '''
    pass
if '-channel' in sys.argv:
    '''
    获取各来源的频道列表
    '''
    crawl()
else:
    '''
    启动抓取程序
    '''
    start_crawl()
