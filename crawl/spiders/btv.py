# -*- coding:utf-8 -*-
# 北京电视台官方来源 10 个频道
#2022-11-03官方更改接口
#https://dynamic.rbc.cn/bvradio_app/service/LIVE?functionName=getCurrentChannel&channelId=135&curdate=2022-11-01
# http://jiemudan.brtv.org.cn/index.html?channel=TvCh1602660467213184  地址
# http://www.brtv.org.cn/mobileinf/rest/cctv/videolivelist/dayWeb?json={'id':'TvCh1602660467213184','day':'2021-12-15'}  接口
from bs4 import BeautifulSoup as bs
import requests, datetime,os
from utils.general import headers


def get_epgs_btv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y-%m-%d')
    url = "https://dynamic.rbc.cn/bvradio_app/service/LIVE?functionName=getCurrentChannel&channelId=%s&curdate=%s"%(channel_id, need_date)

    try:
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'utf-8'
        res_j = res.json()['channel']['programes']
        old_dt = datetime.datetime(1999, 12, 31, 12, 12)
        n = 0 #计数 节目表的第几个节目
        max_n = len(res_j)
        for epga in res_j:
            n += 1
            starttime = epga['startTime']
            endtime = epga['endTime']
            title = epga['name']
            starttime = datetime.datetime.strptime(need_date + starttime, '%Y-%m-%d%H:%M')
            if n == max_n and endtime[:2] == '00':
                endtime = datetime.datetime.strptime(need_date + endtime, '%Y-%m-%d%H:%M')
                endtime = endtime + datetime.timedelta(days=1)
            else:
                endtime = datetime.datetime.strptime(need_date + endtime, '%Y-%m-%d%H:%M')
            epg = {'channel_id': channel.id,
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
        msg = 'spider-%s- %s' % (spidername,e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban':0,
    }
    return ret


def get_channels_btv():
    channels = []
    url= 'https://www.brtv.org.cn/gbdsb.shtml'
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('div.conWrapper > div.templateBox > ul > li')
    for li in lis:
        name = li.div.text.replace('\n','').strip()
        id = li.attrs['channelid']
        channel = {
            'name': name,
            'id': [id],
            'url': 'https://www.brtv.org.cn/gbdsb.shtml',#url,
            'source': 'btv',
            'logo': '',
            'desc': '',
            'sort': '北京',
        }
        channels.append(channel)
    infos = soup.select('div.introductionWrapper')
    n = 0
    for info in infos:
        desc = info.text.strip().replace(' ','').replace('\t','').replace('\r','').replace('\n\n','\n').replace('\n\n','\n')
        if '青年频道' in desc:
            continue
        channels[n]['desc'] = desc
        n += 1
    return channels
