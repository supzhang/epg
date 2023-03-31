# -*- coding:utf-8 -*-
import datetime
import json
import os
import re
import requests
from bs4 import BeautifulSoup as bs

from utils.general import headers

'''
TVB来源
2023-2-15更新为新的接口，旧html接口失效，更改获取频道ID方式
'''


def get_epgs_tvb(channel, channel_id, dt, func_arg):  # channel_id,dt
    epgs = []
    msg = ''
    success = 1
    dt_str = dt.strftime('%Y%m%d')
    url = 'https://programme.tvb.com/api/schedule?input_date=%s&network_code=%s' % (dt_str, channel_id)
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.encoding = 'utf-8'
        res_j = res.json()
        epg_list = res_j['data']['list'][0]['schedules']
        for li in epg_list:
            starttime = datetime.datetime.fromtimestamp(int(li['event_time']))
            title = li['programme_title']
            title_en = li['en_programme_title']
            desc = li['synopsis']
            desc_en = li['en_synopsis']
            url = li['mytv_super_url']
            # print(title,starttime,title_en)
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': '%s-%s' % (title, title_en),
                   'title_en': title_en,
                   'desc': desc,
                   'desc_en': desc_en,
                   'program_date': starttime.date() if 'starttime' in locals() else dt,
                   }

            epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s- %s' % (spidername, e)
        # print(li)

    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


def get_epgs_tvb_old(channel, channel_id, dt, func_arg):  # 只需要channel_id即可 ,同时获取15天，包含前面时间的节目
    epgs = []
    msg = ''
    success = 1
    url = 'http://programme.tvb.com/%s/week/' % channel_id
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.encoding = 'utf-8'
        soup = bs(res.text.replace('/>', '>'), 'html.parser')
        lis = soup.select('div.channel > ul > li')
        for li in lis:
            if 'time' not in li.attrs:
                continue
            starttime = datetime.datetime.fromtimestamp(int(li.attrs['time']))
            em_time = li.select('em')[0].text
            title = li.text.strip().replace(em_time, '')
            if starttime.date() < dt:  # 已经采集过的数据忽略
                continue
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': '',
                   'program_date': starttime.date() if 'starttime' in locals() else dt,
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
        'last_program_date': starttime.date() if 'starttime' in locals() else dt,
        'ban': 0,
    }
    return ret


def get_channels_tvb():
    url = 'https://programme.tvb.com/assets/index.85ba94a8.js'
    res = requests.get(url)
    res_re = re.search('const e\=(.+?),n\=', res.text)
    channels_str = res_re.group(1)
    channels_str = channels_str.encode('raw_unicode_escape').decode('unicode_escape').strip().replace('null', '0')
    channels_str = re.sub('([{,])(?!")(\w+)(\:)', lambda m: m.group(1) + '"' + m.group(2) + '"' + m.group(3),
                          channels_str)
    channels_j = json.loads(channels_str)
    channels = []
    for li in channels_j:
        name = li['name']
        name_en = li['nameEn']
        href = li['liveUrl'] if 'liveUrl' in li else ''
        id = li['code']
        desc = li['description']
        channel = {
            'name': name,
            'name_en': name_en,
            'id': [id],
            'url': href,
            'source': 'tvb',
            'logo': '',
            'desc': desc,
            'sort': '香港',
        }
        channels.append(channel)
    return channels
