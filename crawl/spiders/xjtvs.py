# -*- coding:utf-8 -*-
import json
import requests, datetime, os
from bs4 import BeautifulSoup as bs
from utils.general import headers


# http://www.xjtvs.com.cn/bvradio_app/service/LIVE?functionName=getCurrentChannel&channelId=128&curdate=2023-07-21&_=1689845256318
def get_epgs_xjtvs(channel, channel_id, dt, func_arg):  # channel_id,dt
    epgs = []
    msg = ''
    success = 1
    start_date_str = dt.strftime('%Y-%m-%d')
    url = 'http://www.xjtvs.com.cn/bvradio_app/service/LIVE?functionName=getCurrentChannel&channelId=%s&curdate=%s' % (
        channel_id, start_date_str)
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.encoding = 'utf-8'
        res_j = json.loads(res.text)
        epg_list = res_j['channel']['programes']
        for channelepg in epg_list:
            starttime = datetime.datetime.strptime(start_date_str + ' ' + channelepg['startTime'] + ":00", "%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(start_date_str + ' ' + channelepg['endTime'] + ":00", "%Y-%m-%d %H:%M:%S")
            title = channelepg['name'].strip('网络不播出').strip('无网络版权')
            desc = ""

            epg = {
                'channel_id': channel.id,
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
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


def get_channels_xjtvs():
    #
    url = 'http://www.xjtvs.com.cn/bvradio_app/service/cms?functionName=getChannel&stationID=100'
    res = requests.get(url, headers=headers)
    res_channels = res.json()
    channels = []
    for li in res_channels:
        name = li['shortName']
        href = li['shareURL']
        logo = ''
        id = li['channelID']
        desc = li['shortName']
        #名字前面加上区别。不然后期分辨不出。
        if not name.startswith("新疆"):
            name = "新疆" + name

        channel = {
            'name': name,
            'id': [id],
            'url': href,
            'source': 'xjtvs',
            'logo': logo,
            'desc': desc,
            'sort': '新疆',
        }
        channels.append(channel)
    return channels
