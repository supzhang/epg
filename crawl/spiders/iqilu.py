#-*- coding:utf-8 -*-
import json
import requests,datetime,os
from utils.general import headers
headers_iqilu = {
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding' : 'gzip, deflate',
    'Connection' : 'keep-alive',
}
#http://module.iqilu.com/media/apis/main/getprograms?channelID=31&date=2023-07-21
def get_epgs_iqilu(channel, channel_id, dt, func_arg):#channel_id,dt ，每次获取当天开始共7天数据
    epgs = []
    msg = ''
    success = 1
    start_date_str = dt.strftime('%Y-%m-%d')
    url = 'http://module.iqilu.com/media/apis/main/getprograms?channelID=%s&date=%s'%(channel_id.split('-')[0],start_date_str)
    try:
        res = requests.get(url,timeout = 8,headers = headers_iqilu)
        res.encoding = 'utf-8'
        text = res.text
        res = text.strip('(').strip(')')
        res_j = json.loads(res)
        epg_list = res_j['value']['list']
        for channelepg in epg_list:
            starttime = datetime.datetime.fromtimestamp(channelepg['begintime'])
            endtime = datetime.datetime.fromtimestamp(channelepg['endtime'])
            title = channelepg['name']
            desc = ""

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
        'last_program_date': dt,
        'ban': 0,
    }
    return ret
def get_channels_iqilu():
    #http://v.iqilu.com/live/sdtv/index.html通过F12 看script变量整理来的
    res = '[{"id":24,"live":"sdtv","m3u8":"98/4","catname":"山东卫视"},{"id":25,"live":"qlpd","m3u8":"98/5","catname":"齐鲁频道"},{"id":31,"live":"ggpd","m3u8":"98/6","catname":"山东公共频道"},{"id":26,"live":"typd","m3u8":"98/7","catname":"山东体育频道"},{"id":29,"live":"shpd","m3u8":"99/6","catname":"山东生活频道"},{"id":28,"live":"zypd","m3u8":"100/4","catname":"山东综艺频道"},{"id":30,"live":"nkpd","m3u8":"99/4","catname":"山东农科频道"},{"id":27,"live":"yspd","m3u8":"99/7","catname":"山东影视频道"},{"id":32,"live":"sepd","m3u8":"99/5","catname":"山东少儿频道"},{"id":33,"live":"gjpd","m3u8":"100/5","catname":"山东国际频道"}]'
    res_channels = json.loads(res)
    channels = []
    for li in res_channels:
        name = li['catname']
        name_en = ""
        href = 'http://v.iqilu.com/live/%s/index.html'%(li['live'])
        logo = ''
        id = '%s-%s'%(li['id'],li['live'])
        desc = '爱齐鲁资源采集最多只能获取今明两天'
        channel = {
            'name': name,
            'name_en':name_en,
            'id': [id],
            'url': href,
            'source': 'iqilu',
            'logo': logo,
            'desc': desc,
            'sort':'山东',
        }
        channels.append(channel)
    return channels
