#-*- coding:utf-8 -*-
#广西网络广播电视台-官网来源,2023-06-05添加到数据库，广西卫视及地方6个频道

#POST请求数据
# channelName: 广西卫视
# dateStr: 2023-06-05
# programName:
# deptId: 0a509685ba1a11e884e55cf3fc49331c
# platformId: bd7d620a502d43c09b35469b3cd8c211
#deptid及PLATFORMID为固定值，来源  https://www.gxtv.cn/static/httpRequestOfParams.js  webDeptId = "0a509685ba1a11e884e55cf3fc49331c"  webType = "bd7d620a502d43c09b35469b3cd8c211";

import requests,datetime,os
from bs4 import BeautifulSoup as bs
from utils.general import headers
def get_epgs_gxntv(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    dt_str = dt.strftime('%Y-%m-%d')
    data = {
            'channelName':channel_id ,
            'dateStr': dt_str,
            'programName': '',
            'deptId': '0a509685ba1a11e884e55cf3fc49331c',
            'platformId': 'bd7d620a502d43c09b35469b3cd8c211'
            }
    try:
        url = 'https://api2019.gxtv.cn/memberApi/programList/selectListByChannelId'
        res = requests.post(url,headers = headers,timeout=8,data= data)
        res.encoding = 'utf-8'
        res_json = res.json()
        epgs_contents = res_json['data']
        epgs = []
        for epga in epgs_contents:
            starttime_str = epga['programTime']
            time_delay = epga['programmeLength']
            starttime = datetime.datetime.strptime(starttime_str,'%Y-%m-%d %H:%M:%S')
            endtime = starttime+datetime.timedelta(seconds = time_delay)
            title = epga['programName'].strip()
            epg = {'channel_id': '',#channel.id,
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

def get_channels_gxntv():
    url = 'https://program.gxtv.cn/'
    res = requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    soup = bs(res.text,'html.parser')
    contents = soup.select('#TV_tab > ul > li')
    channels = []
    for content in contents:
        id = content.attrs['id']
        name = content.text
        channel = {
            'name': name,
            'id': [id],
            'url': 'https://program.gxtv.cn/',
            'source': 'gxntv',
            'logo': '',
            'desc': '',
            'sort':'广西',

        }
        channels.append(channel)
    return channels
