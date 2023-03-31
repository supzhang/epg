# -*- coding:utf-8 -*-
# 广东广播电视台-官网来源,2021-12-16添加到数据库，只有广东地区频道共10多个
import datetime
import os
import requests
from bs4 import BeautifulSoup as bs

from utils.general import headers


def get_epgs_gdtv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    try:
        url = 'http://epg.gdtv.cn/f/%s/%s.xml' % (channel_id, dt.strftime('%Y-%m-%d'))
        res = requests.get(url, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        epgs_contents = soup.select('content')
        epgs = []
        for epga in epgs_contents:
            starttime = datetime.datetime.fromtimestamp(int(epga.attrs['time1']))
            endtime = datetime.datetime.fromtimestamp(int(epga.attrs['time2']))
            title = epga.get_text().strip()
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   'program_date': dt,
                   }
            epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s- %s' % (spidername, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


def get_channels_gdtv():
    url = 'http://epg.gdtv.cn/f/1.xml'
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    contents = soup.select('channel')
    channels = []
    for content in contents:
        id = content.attrs['id']
        name = content.ctitle.text
        cdate = content.cdate.text
        channel = {
            'name': name,
            'id': [id],
            'url': 'http://epg.gdtv.cn/',
            'source': 'gdtv',
            'logo': '',
            'desc': '',
            'sort': '广东',
            'newestdate': cdate
        }
        channels.append(channel)
    return channels
