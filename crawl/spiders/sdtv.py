# -*- coding:utf-8 -*-
# 齐鲁网-官网来源,2023-08-07添加到数据库，只有山东地区12个频道
import requests, datetime, os, re, time, json
from utils.general import headers


def get_epgs_sdtv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    t = time.time()
    try:
        url = 'http://module.iqilu.com/media/apis/main/getprograms?jsonpcallback=jQuery37004547755401387288_%s&channelID=%s&date=%s&_=%s' % (
            t, channel_id, dt, t)
        res = requests.get(url, timeout=8)
        res.encoding = 'utf-8'
        re_j = re.search('.+?\((.+?)\)', res.text, re.DOTALL).group(1)
        re_json = json.loads(re_j)
        contents = re_json['value']['list']
        for content in contents:
            starttime = datetime.datetime.fromtimestamp(int(content['begintime']))
            endtime = datetime.datetime.fromtimestamp(int(content['endtime']))
            title = content['name']
            epg = {'channel_id': channel_id,
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


def get_channels_sdtv():
    url = 'http://v.iqilu.com/live/qlpd/'
    res = requests.get(url)
    res.encoding = 'utf-8'
    re_l = re.search('var channels = (.+?);', res.text, re.DOTALL).group(1)
    contents = re.findall(
        '\"\w+\"\:{.+?\"id\"\:(\d+)\,\"live\"\:\"(\w+)\"\,\"m3u8\"\:\"(.+?)\"\,\"catname\"\:\"(\w+)\".+?}', re_l,
        re.DOTALL)
    channels = []
    for content in contents:
        id = content[0]
        name = content[3]
        curl = 'http://v.iqilu.com/live/%s/' % content[1]
        channel = {
            'name': name,
            'id': [id],
            'url': curl,
            'source': 'sdtv',
            'logo': '',
            'desc': '',
            'sort': '山东' if name != '山东卫视' else '卫视'

        }
        channels.append(channel)
    return channels
