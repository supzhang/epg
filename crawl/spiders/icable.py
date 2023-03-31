# -*-coding:utf-8-*-
import datetime
import os
import requests

from utils.general import cht_to_chs, headers


def get_epgs_icable(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'http://epg.i-cable.com/ci/channel/epg/%s/%s?api=api&locale=chi' % (channel_id, dt.strftime('%Y%m%d'))
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        js = res.json()
        epg_list = js['epgs']
        for g in epg_list:
            title = cht_to_chs(g['programme_name_chi'])  # 可以选择英文名
            ampm = g['session_mark']
            t = g['time']
            starttime = datetime.datetime.strptime(dt.strftime('%Y%m%d') + t, '%Y%m%d%H:%M')
            if ampm.upper() == 'PM':
                starttime = starttime + datetime.timedelta(hours=12)
            elif ampm.upper() == 'NM':
                starttime = starttime + datetime.timedelta(days=1)
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': '',
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
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


def get_channels_icable():
    url = 'http://epg.i-cable.com/ci/home/?api=api&locale=chi'
    res = requests.get(url)
    res_json = res.json()
    channels_json = res_json['channels']
    channels = []
    for c in channels_json:
        name = c['channel_name']
        id = c['channel_id']
        url = 'http://epg.i-cable.com/ci/channel/epg/%s' % c['channel_no']
        logo = 'http://epg.i-cable.com/new/images/epgMobileIcon/%s.png' % c['channel_no']
        name_eng = c['channel_name_en']
        catelog = c['cate_id']

        channel = {
            'name': name,
            'id': [id],
            'url': url,
            'source': 'icable',
            'logo': logo,
            'desc': '',
            'sort': '海外',
            'name_eng': name_eng,
            'catelog': catelog,
        }
        channels.append(channel)
    return channels
