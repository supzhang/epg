# -*- coding:utf-8 -*-
import datetime
import os
import re
import requests
import time
from bs4 import BeautifulSoup as bs

from utils.general import headers


def get_epgs_tbc(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel_id.replace('tbc', '')
    url = 'https://www.tbc.net.tw/EPG/Channel?channelId=%s' % channel_id
    try:
        res = requests.get(url, timeout=30)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        uls = soup.select('ul.list_program2')
        for ul in uls:
            n1 = 0  # 记录当天的节目数
            lis = ul.select('li')
            for li in lis:
                title = li.p.text
                desc = li.attrs['desc']
                date_ = li.attrs['date']
                time_delay = li.attrs['time'].strip()
                time_delay_re = re.search('(\d+:\d+)~(\d+:\d+)', time_delay)
                if time_delay_re:  # 有节目信息则解析
                    start_str, end_str = time_delay_re.group(1), time_delay_re.group(2)  # 将开始与结束时间的文本分开
                    starttime = datetime.datetime.strptime(date_ + start_str, '%Y/%m/%d%H:%M')
                    endtime = datetime.datetime.strptime(date_ + end_str, '%Y/%m/%d%H:%M')
                    if starttime > endtime:
                        endtime = endtime + datetime.timedelta(days=1)
                    if starttime.date() < dt:
                        continue
                epg = {'channel_id': channel.id,
                       'starttime': starttime,
                       'endtime': endtime,
                       'title': title,
                       'desc': desc,
                       'program_date': starttime.date(),
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
        'last_program_date': starttime.date() if 'starttime' in dir() else dt,
        'ban': 0,
    }
    return ret


today_int = int(time.strftime('%Y%m%d', time.localtime()))  # 今天的日期数字  20190325  一次抓取多天数据,不能重复爬取


# 下载TBC所有频道ID及名称
def get_channels_tbc():
    channels = []
    cookies = {
        'ASP.NET_SessionId': 'v111fiox1mzc0wpc0d4iue5c'
    }
    url = 'https://www.tbc.net.tw/EPG'
    res = requests.get(url, headers=headers, cookies=cookies, timeout=6)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('ul.list_tv > li')
    for li in lis:
        name = li['title']
        id = li['id']
        img = li.select('img')[0]['src']
        url = li.a['href']
        channel = {
            'name': name,
            'id': [id],
            'url': url,
            'source': 'tbc',
            'logo': img,
            'desc': '',
            'sort': '海外',
        }
        channels.append(channel)
    return channels
