#-*- coding:utf-8 -*-
import requests,datetime,os
from utils.general import headers
def get_epgs_mytvsuper(channel, channel_id, dt, func_arg):#channel_id,dt ，每次获取当天开始共7天数据
    epgs = []
    msg = ''
    success = 1
    start_date_str = dt.strftime('%Y%m%d')
    end_date = dt + datetime.timedelta(days=6)
    end_date_str = end_date.strftime('%Y%m%d')
    url = 'https://content-api.mytvsuper.com/v1/epg?network_code=%s&from=%s&to=%s&platform=web '%(channel_id,start_date_str,end_date_str)
    try:
        res = requests.get(url,timeout = 8,headers = headers)
        res.encoding = 'utf-8'
        res_j = res.json()
        items = res_j[0]['item']
        for item in items:
            epg_list = item['epg']
            firtst_line_date = 1
            for li in epg_list:
                starttime = datetime.datetime.strptime(li['start_datetime'],'%Y-%m-%d %H:%M:%S')
                title = li['programme_title_tc']
                title_en = li['programme_title_en']
                desc=li['episode_synopsis_tc']
                desc_en = li['episode_synopsis_en']
                url = 'https://www.mytvsuper.com/tc/programme/%s'%li['programme_path']
                program_date = starttime.date() if 'starttime' in locals() else dt
                if firtst_line_date:
                    last_program_date = starttime
                    first_line_date = 0
                #print(title,starttime,title_en)
                epg = {'channel_id': channel.id,
                       'starttime': starttime,
                       'endtime': None,
                       'title': '%s-%s'%(title,title_en),
                       'title_en':title_en,
                       'desc': desc,
                       'desc_en':desc_en,
                       'program_date': program_date,
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
        'last_program_date': last_program_date if 'last_program_date' in locals() else dt,
        'ban': 0,
    }
    return ret
def get_channels_mytvsuper():
    url = 'https://content-api.mytvsuper.com/v1/channel/list?platform=web'
    res = requests.get(url,headers = headers)
    res_channels = res.json()['channels']
    channels = []
    for li in res_channels:
        name = li['name_tc']
        name_en = li['name_en']
        cn = li['channel_no']
        href = 'https://www.mytvsuper.com/tc/epg/%s/'%cn
        logo = li['path'] if 'path' in li else ''
        id = li['network_code']
        desc = ''
        channel = {
            'name': name,
            'name_en':name_en,
            'id': [id],
            'url': href,
            'source': 'mytvsuper',
            'logo': logo,
            'desc': desc,
            'sort':'香港',
        }
        channels.append(channel)
    return channels