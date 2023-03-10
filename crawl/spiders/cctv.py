# -*- coding:utf-8 -*-
# CCTV官方
import requests, re, datetime,json,os
from utils.general import headers
from bs4 import BeautifulSoup as bs

def get_epgs_cctv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y%m%d')
    url = 'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=set'%(channel_id,need_date)
    try:
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'utf-8'
        programs = json.loads(re.search('set\((.*)\)', res.text).group(1))
        prog_lists = programs['data'][channel_id]['list']
        for prog_list in prog_lists:  #
            title = prog_list['title'] #节目名称
            starttime = datetime.datetime.fromtimestamp(prog_list['startTime']) #开始时间
            endtime=datetime.datetime.fromtimestamp(prog_list['endTime']) #结束时间
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   'program_date': dt,
                   }
            epgs.append(epg)
        epglen = len(epgs)
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

def get_channels_cctv():
    channels = []
    host = 'https://tv.cctv.com'
    url = '%s/epg/index.shtml' % host
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('div.channel_con > div > ul > li')
    need_date = datetime.datetime.now().strftime('%Y%m%d')
    for li in lis:
        id = li.select('img')[0].attrs['title'].strip()
        logo = 'http://' + li.select('img')[0].attrs['src'].strip()
        url_info = 'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=set' % (id, need_date)
        res = requests.get(url_info,headers = headers,timeout = 5)
        res.encoding = 'utf-8'
        research = re.search('"channelName":"(.+?)".+?"lvUrl":"(.+?)"',res.text)
        name = research.group(1)
        url = research.group(2)
        channel = {
            'name': name,
            'id': [id],
            'url': url,
            'source': 'cctv',
            'logo': logo,
            'desc': '',
            'sort':'央视',
        }
        channels.append(channel)
    return channels
