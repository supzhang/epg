# -*- coding:utf-8 -*-
# 看看新闻网-官网来源,上海6个频道
import requests, datetime, os, re, time, json, hashlib
from utils.general import headers
from bs4 import BeautifulSoup as bs

def get_epgs_kankan(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    timestamp = int(time.time())
    date = dt.strftime("%Y-%m-%d")
    payload = {}
    params = {
        'Api-Version': 'v1',
        'channel_id': channel_id,
        'date': date,
        'nonce': '1',
        'platform': 'pc',
        'timestamp': timestamp,
        'version': 'v2.0.0',
    }
    s = '&'.join([f'{key}={params[key]}' for key in sorted(params.keys())])
    s = f'{s}&28c8edde3d61a0411511d3b1866f0636'
    hashed_s = hashlib.md5(s.encode()).hexdigest()
    sign = hashlib.md5(hashed_s.encode()).hexdigest()
    headers = {
        'Api-version': 'v1',
        'nonce': '1',
        'platform': 'pc',
        'version': 'v2.0.0',
        'sign': sign,
        'timestamp': str(timestamp),
    }
    try:
        url = f"https://kapi.kankanews.com/content/pc/tv/programs?channel_id={channel_id}&date={date}"
        res = requests.request("GET", url, headers=headers, data=payload, timeout=8)
        res.encoding = 'utf-8'
        re_json = json.loads(res.text)
        contents = re_json['result']['programs']
        for content in contents:
            starttime = datetime.datetime.fromtimestamp(content['start_time'])
            endtime = datetime.datetime.fromtimestamp(content['end_time'])
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
        msg = f'spider-{spidername}- {e}'
    return {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }

def get_channels_kankan():  # sourcery skip: avoid-builtin-shadow
    ids = {'东方卫视': '1',
           '新闻综合': '2',
           '第一财经': '5',
           '纪实人文': '6',
           '都市频道': '4',
           '哈哈炫动': '9'}
    channels = []
    url = 'https://live.kankanews.com/huikan/'
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = bs(res.text,'html.parser')
    div_channels = soup.select('div.channel.item.cur > li')
    for div_channel in div_channels:
        name = div_channel.p.text.strip()
        id = ids[name]
        channel = {
            'name': name,
            'id': [id],
            'url': url,
            'source': 'kankan',
            'logo': '',
            'desc': '',
            'sort': '上海',
        }
        channels.append(channel)
    print(f'共有：{len(channels)}个频道')
    return channels