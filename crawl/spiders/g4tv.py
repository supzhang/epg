# -*- coding:utf-8 -*-
import datetime
import os
import requests

from utils.general import headers, cht_to_chs


def get_epgs_4gtv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'https://www.4gtv.tv/ProgList/%s.txt' % (channel_id)
    try:
        res = requests.get(url, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        res_json = res.json()
        for j in res_json:
            title = j['title']
            start_date = j['sdate']
            start_time = j['stime']
            end_date = j['edate']
            end_time = j['etime']
            starttime = datetime.datetime.strptime('%s%s' % (start_date, start_time), '%Y-%m-%d%H:%M:%S')
            endtime = datetime.datetime.strptime('%s%s' % (end_date, end_time), '%Y-%m-%d%H:%M:%S')
            if starttime.date() < dt:  # 对于已经采集过的日期，跳过
                continue
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   'program_date': starttime.date(),
                   }
            epgs.append(epg)
        epglen = len(epgs)
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


def get_channels_4gtv():
    url = 'http://api2.4gtv.tv/Channel/GetAllChannel/pc/L'
    headers.update({
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CA;q=0.8,en;q=0.7,zh-TW;q=0.6',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    })
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    js = res.json()['Data']
    channels = []
    for j in js:
        id = str(j['fnID'])
        type = j['fsTYPE']
        name = cht_to_chs(j['fsNAME'])
        gtvid = j['fs4GTV_ID']
        logo = j['fsLOGO_MOBILE']
        desc = j['fsDESCRIPTION'] if 'fsDESCRIPTION' in j else ''
        all = [name, gtvid, logo]

        channel = {
            'name': name,
            'id': [gtvid],
            'url': 'https://www.4gtv.tv/channel',
            'source': '4gtv',
            'logo': logo,
            'desc': desc,
            'sort': '台湾',
        }
        channels.append(channel)
    return channels
