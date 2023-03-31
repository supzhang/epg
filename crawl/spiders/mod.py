# -*- coding:utf-8 -*-
import datetime
import os
import re
import requests
from bs4 import BeautifulSoup as bs

from utils.general import headers


def get_epgs_mod(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    days = (dt - datetime.datetime.now().date()).days
    url = 'http://mod.cht.com.tw/tv/channel.php?id=%s&d=%s' % (
        channel_id, days)  # d=0表示当天，至少能获取最近七天数据  http://mod.cht.com.tw/tv/channel.php?id=6&d=2
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        old_dt = datetime.datetime(1999, 12, 31, 12, 12)
        lis = soup.select('ul.striped-time-table > li')
        for li in lis[1:]:
            title = li.select('h4')[0].text.replace('\t', '').replace('\r', '').replace('\n', '').strip()
            timestr = li.select('time.time')[0].text.strip()
            starttime = datetime.datetime(dt.year, dt.month, dt.day, int(timestr[:2]), int(timestr[-2:]))
            if starttime < old_dt:  # 第一条记录可能为上一天的，剔除。
                epgs.pop(0)
                old_dt = datetime.datetime(2999, 12, 31, 12, 12)
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
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


def get_channels_mod():
    # http://mod.cht.com.tw/tv/channel.php?id=006   采集节目表地址
    url = 'http://mod.cht.com.tw/bepg2/'
    res = requests.get(url, timeout=10)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    divs = soup.select('div.rowat')
    divs2 = soup.select('div.rowat_gray')
    divs += divs2
    channels = []
    for div in divs:
        try:
            urlid = div.select('div > a')[0].attrs['href']
            name = div.select('div.channel_info')[0].text
            id = name[:3].strip()
            img = 'http://mod.cht.com.tw' + re.sub('\?rand=\d*', '', div.select('img')[0].attrs['src']).strip()
            channel = {
                'name': name,
                'id': [id],
                'url': '%s%s' % ('http://mod.cht.com.tw/', urlid),
                'source': 'mod',
                'logo': img,
                'desc': '',
                'sort': '海外',
            }
            channels.append(channel)
        except Exception as e:
            print(div)
    return channels
