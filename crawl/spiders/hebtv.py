# -*- coding:utf-8 -*-
import json
import requests, datetime, os
from utils.general import headers
from bs4 import BeautifulSoup as bs

def get_epgs_hebtv(channel, channel_id, dt, func_arg):  # channel_id,dt
    epgs = []
    msg = ''
    success = 1
    today = dt.strftime('%Y-%m-%d')
    url = 'https://api.cmc.hebtv.com/appapi/api/content/get-live-info'
    data = {
        "sourceId": channel_id,
        "tenantId": "0d91d6cfb98f5b206ac1e752757fc5a9",
        "tenantid": "0d91d6cfb98f5b206ac1e752757fc5a9",
        "api_version": "3.7.0",
        "client": "android",
        "cms_app_id": "19",
        "app_id": 2,
        "app_version": "1.0.39",
        "no_cache": "yes"
    }
    headers['Referer'] = "https://www.hebtv.com/"
    try:
        res = requests.post(url, timeout=8, headers=headers, json=data)
        res.encoding = 'utf-8'
        res_j = json.loads(res.text)
        epg_list = res_j['result']['data']
        start_get = 0
        for date, item in epg_list.items():
            if date == today:
                start_get = 1

            if start_get == 1:
                #他一次性会返回很多以前的数据，只要目标日期以后的数据
                for channelepg in item:
                    starttime = datetime.datetime.strptime(channelepg['startDateTime'], "%Y-%m-%d %H:%M:%S")
                    endtime = datetime.datetime.strptime(channelepg['endDateTime'], "%Y-%m-%d %H:%M:%S")
                    title = channelepg['name']
                    desc = ""

                    epg = {
                        'channel_id': channel.id,
                        'starttime': starttime,
                        'endtime': endtime,
                        'title': title,
                        'desc': desc,
                        'program_date': date,
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
        'last_program_date': date,
        'ban': 0,
    }
    return ret


def get_channels_hebtv():
    #
    channels = []
    host = 'https://www.hebtv.com/'
    url = '%s/2/2gfwz/jmb/index.shtml' % host
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('div.program_left > ul > li')
    for li in lis:
        id = li.attrs['data-id'].strip()
        name = li.text
        if not name.startswith("河北"):
            name = "河北" + name

        channel = {
            'name': name,
            'id': [id],
            'url': "https://www.hebtv.com/19/19js/st/xdszb/index.shtml",
            'source': 'hebtv',
            'logo': "",
            'desc': '',
            'sort': '河北',
        }
        channels.append(channel)
    return channels
