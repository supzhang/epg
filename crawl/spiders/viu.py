# -*- coding:utf-8 -*-
# 仅提供viu频道节目信息https://viu.tv/epg/99
# https://api.viu.tv/production/epgs/99
import datetime
import os
import requests

from utils.general import headers


def get_epgs_viu(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'https://api.viu.tv/production/epgs/99'
    try:
        res = requests.get(url, headers=headers, timeout=6)
        res.encoding = 'utf-8'
        js = res.json()['epgs']
        for j in js:
            title = j['program_title'].strip()
            desc1 = j['episode_title'] if 'episode_title' in j else ''
            desc2 = j['short_synopsis'] if 'short_synopsis' in j else ''
            desc = '--'.join([desc1, desc2]) if len(desc2) > 0 else desc1
            desc = ''
            starttime = datetime.datetime.fromtimestamp(j['start'] / 1000)
            endtime = datetime.datetime.fromtimestamp(j['end'] / 1000)
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


# 下载所有频道ID及名称
def get_channels_viu():
    channel = {
        'name': 'ViuTV',
        'id': ['viu'],
        'url': 'https://viu.tv/epg/99',
        'source': 'viu',
        'logo': 'https://viu.tv/assets/img/logo.png',
        'desc': '',
        'sort': '海外',
    }
    channels = [channel]
    return channels
