# -*- coding:utf-8 -*-
import datetime
import os
import re
from pathlib import Path

from django.conf import settings

from .zhtools.langconv import *

add_info_desc = ''  # 在节目表的标题里面添加信息
add_info_title = ''  # 在节目表的描述里面添加信息
##存储数据的根目录
BASE_DIR = Path(__file__).resolve().parent.parent
root_dir = os.path.join(BASE_DIR, 'download')
crawl_info = {
    'max_crawl_days': settings.MAX_CRAWL_DAYS,  # 需要采集几天节目  1为当天，2为今明两天 如果频道为多天一次获取，则不受此限制
    'gen_xml_days': settings.GEN_XML_DAYS,  # 需要生成节目表的天数 1当天 2明天  不能大于need_days,否则出错
    'del_days': settings.DEL_DAYS,  # 删除多少天之前的节目
    'recrawl_days': settings.RECRAWL_DAYS,  # 需要重新采集几天的节目，1为只重新采集当天节目
    'retry_crawl_times': settings.RETRY_CRAWL_TIMES,  # 如果采集出错，重试次数 1为不重试，2为重试一次 3....重试两次
    'change_source': settings.CHANGE_SOURCE,  # 如果获取失败是否换源
}
dirs = {
    'share': "%s" % root_dir,
    'testm3u_dir': '%s/test.m3u' % root_dir  # 生成用于测试的m3u的目录
}
# 川流TV来源，需要的节目表
chuanliu_Authorization = settings.CHUANLIU_TV_AUTH
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/99.0.4844.82 Safari/537.36'
}

# 生成数据时(不)生成此类别信息
in_exclude_channel = {
    'html': ['香港', '海外', '澳门', '台湾'],  ##生成html时不生成此类别信息
    'xml': [],  ##生成xml的文件名，分类名
    'include_html': [],  ##生成数据时，不会分类阻止也会提供频道信息  单频道
    'include_xml': [],  ##生成数据时，不会分类阻止也会提供频道信息   单频道
}
xmlinfo = {
    'all': {
        'basename': 'e.xml',
        'sortname': 'all'
    },
    'yangwei': {
        'basename': 'cc.xml',
        'sortname': ['央视', '卫视']
    },
    'difang': {
        'basename': 'difang.xml',
        'sortname': ['数字付费', '辽宁', '山东', '湖北', '四川']
    },
    'oversea': {
        'basename': 'gat.xml',
        'sortname': ['香港', '台湾', '海外']
    },
}


# 繁体转简体
def cht_to_chs(line):
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line


# 将多个频道ID解析为单个ID 解析为 {'tvmao':'cctv1','cctv':'cctv1'....}
def channel_ids_to_dict(channel_id):
    channel_list = {}
    rs = re.findall(r'<(\w+):(.+?)>', channel_id)
    for r in rs:
        c = {r[0]: r[1]}
        channel_list.update(c)
    return channel_list


def argvs_get(argv):
    """
    # 命令行运行时可使用的参数
    recrawl(重新获取)
    channel(单独获取某一频道节目单）
    dt(单独某频道时，获取日期）
    save_to_db单独获取时，是否需要存至数据库
    -r 重新获取  -n 获取某一单一频道信息 -d 某一频道的日期 -s 是否保存(如果只写-s为保存数据)
    """

    recrawl = 0
    cname = 0  # 单独获取的某一频道名
    dt = 0
    save_to_db = 1
    if '-r' in argv:
        recrawl = 1
    if '-n' in argv and len(argv) >= argv.index('-n') + 2 and '-' not in argv[argv.index('-n') + 1]:
        cname = argv[argv.index('-n') + 1]
    if '-d' in argv and len(argv) >= argv.index('-d') + 2 and '-' not in argv[argv.index('-d') + 1]:
        dt = argv[argv.index('-d') + 1]
        dt = datetime.datetime.strptime(dt, '%Y%m%d').date()
    else:
        dt = datetime.datetime.now().date()
    if '-s' in argv and len(argv) >= argv.index('-s') + 2 and '-' not in argv[argv.index('-s') + 1]:
        save_to_db = int(argv[argv.index('-s') + 1])
    if '-n' in argv and '-s' not in argv:
        save_to_db = 0

    return recrawl, cname, dt, save_to_db


def add_arguments(parser):
    parser.add_argument('--log', '-l', action='store_true', help='统计日志（未实现）')
    parser.add_argument('--channel', '-c', action='store_true', help='获取各来源的频道列表')
    parser.add_argument('--recrawl', '-r', action='store_true', help='重新获取')
    parser.add_argument('--name', '-n', help='获取某单一频道信息')
    parser.add_argument('--date', '-d', help='某一频道的日期')
    parser.add_argument('--save', '-s', action='store_true', help='是否保存，指定频道时不加此参数也默认保存')


def get_argument_values(args):
    recrawl = 1 if args['recrawl'] else 0
    cname = args['name']
    if args['date']:
        dt = datetime.datetime.strptime(args['date'], '%Y%m%d').date()
    else:
        dt = datetime.datetime.now().date()
    save_to_db = 1 if args['save'] or cname else 0

    return recrawl, cname, dt, save_to_db


def noepgjson(name, id, need_date):
    title = '精彩节目-暂未提供节目预告信息'
    epgjsons = []
    for x in range(24):
        start = datetime.datetime.combine(need_date, datetime.time(x, 0, 0)).strftime('%H:%M')
        end = datetime.datetime.combine(need_date, datetime.time(x, 59, 59)).strftime('%H:%M')
        epgjsons.append({
            'starttime': start,
            'endtime': end,
            'title': '%s%s' % (title, add_info_title),
            'descr': add_info_desc,
        })
    return epgjsons


def noepg(name, id, need_date):
    hours_epg = []
    tz = ' +0800'
    for x in range(24):
        start = datetime.datetime.combine(need_date, datetime.time(x, 0, 0))
        end = datetime.datetime.combine(need_date, datetime.time(x, 59, 59))
        starttime_str = start.strftime('%Y%m%d%H%M%M') + tz
        endtime_str = end.strftime('%Y%m%d%H%M%M') + tz
        hour_epg = '''<programme start="%s" stop="%s" channel="9999"><title lang="zh">精彩节目-暂未提供节目预告信息</title><desc lang="zh"></desc></programme>''' % (
        starttime_str, endtime_str)
        hours_epg.append(hour_epg)
    xmlepg = ''.join(hours_epg)
    return xmlepg
