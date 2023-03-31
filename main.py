# -*- coding:utf-8 -*-
import argparse
import os

import django

from crawl.crawl import main as start_crawl
from utils.crawl_channel_lists import crawl
from utils.general import add_arguments, get_argument_values

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epg.settings')
    django.setup()

    parser = argparse.ArgumentParser(
        prog='EpgCrawler',
        description='EPG 抓取',
        epilog='')
    add_arguments(parser)

    args = parser.parse_args()

    if args.log:
        '''
        统计日志
        '''
        pass
    elif args.channel:
        '''
        获取各来源的频道列表
        '''
        crawl()
    else:
        '''
        启动抓取程序
        '''
        recrawl, cname, dt, save_to_db = get_argument_values(vars(args))

        start_crawl(recrawl, cname, dt, save_to_db)
