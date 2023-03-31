# -*- coding:utf-8 -*-
"""
获取所有来源的，频道列表（ID，频道名...),存入专门的列表库方便后面处理。
"""

from crawl.spiders import epg_source
from utils.aboutdb import log
from utils.general import cht_to_chs
from web.models import ChannelList


def crawl():
    for source in epg_source:
        if True:
            channels = []
            # if source in ['zhongshu']:
            n = 0
            try:
                channels = epg_source[source]()
                for channel in channels:  # 转简体
                    channel['name'] = cht_to_chs(channel['name'])
                save_ret = ChannelList.save_to_db(ChannelList, channels)
                msg = '频道整理--来源:%s,频道数量:%s,%s' % (source, len(channels), save_ret['msg'])
            except Exception as e:
                msg = '频道整理--来源:%s,获取错误:%s' % (source, e)
            log(msg)
            for r in channels:
                n += 1
                print(n, r['name'], ','.join(r['id']), r['sort'], r['source'], r['url'], r['logo'], r['desc'])
