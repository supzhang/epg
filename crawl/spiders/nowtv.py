#-*- coding:utf-8 -*-
import requests,re,datetime,json,os
from utils.general import headers
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://nowtv.now.com/epg/',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'application/json, text/javascript, */*',
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Proxy-Connection': 'keep-alive',
}

def get_epgs_nowtv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'http://nowtv.now.com/gw-epg/epg/zh_tw/%s/prf0/resp-genre/ch_%s.json' % (dt.strftime("%Y%m%d"),channel_id[:3]) #d=0表示当天，至少能获取最近七天数据
    try:
        res = requests.get(url, headers=headers,timeout = 8)
        res.encoding = 'utf-8'
        j = res.json()
        chs = j['data']['chProgram'] #很多频道的这一天的节目表
        for ch in chs:
            if "ids" == ch or ch != channel_id[4:]: #一个记录，记录显示的所有ID；只有ID和需要获取的ID相同才处理。
                continue
            nowtvid = '%s-%s'%(channel_id[:3],ch.strip()) #拼出nowtv的id
            for channelepg in chs[ch]:
                starttime = datetime.datetime.fromtimestamp(channelepg['start'] / 1000)
                endtime = datetime.datetime.fromtimestamp(channelepg['end'] / 1000)
                title = channelepg['name']
                desc = channelepg['synopsis']

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
        msg = 'spider-%s- %s' % (spidername,e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban':0,
    }
    return ret
# 获取所有最新频道列表
def get_channels_nowtv():
    url = 'http://nowtv.now.com/gw-epg/epg/channelMapping.zh-TW.js'
    res = requests.get(url,headers = headers,timeout=10)
    res.encoding = 'utf-8'
    reinfo = re.search('.+?var ChannelMapping=(.*)var GenreToChanne',res.text,re.DOTALL)
    cs = reinfo.group(1)[:-2]
    cs = json.loads(cs)
    channels = []
    for c in cs:
        if 'name' not in cs[c]:
            continue
        id1 = cs[c]['genreKeys'][0]
        id2 = c
        channel_id = '%s-%s'%(id1,id2)
        print(cs[c])
        name = cs[c]['name']
        channel = {
            'name': name,
            'id': [channel_id],
            'url': url,
            'source': 'nowtv',
            'logo': '',
            'desc': '',
            'sort':'海外',
        }
        channels.append(channel)
    return channels