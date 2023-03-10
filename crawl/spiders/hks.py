# -*- coding:utf-8 -*-
# 香港卫视官方来源 1 个频道
from bs4 import BeautifulSoup as bs
import requests, datetime,os
from utils.general import headers
def get_epgs_hks(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    url = 'http://www.hkstv.tv/index/live.html'

    try:
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        lis = soup.select('div.living-list ul > li')
        for li in lis:
            title = [text for text in li.a.stripped_strings][1]
            starttime = datetime.datetime.fromtimestamp(int(li.a.attrs['id']))
            if starttime.date() < dt:
                continue
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': '',
                   'program_date': starttime.date() if starttime in locals() else dt,

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
        'last_program_date': starttime.date(),
        'ban':0,
    }
    return ret


def get_channels_hks():
    channels = []

    channel = {
        'name': '香港卫视',
        'id': ['hks'],
        'url': 'http://www.hkstv.tv/index/live.html',#url,
        'source': 'hks',
        'logo': 'http://www.hkstv.tv/templates/site_shared/assets/img/blogo.png',
        'desc': '香港衛視國際傳媒集團有限公司是一家集衛星電視、網路電視、影視投資、文化產業等為一體的國際傳媒集團。'
                '香港衛視集團於2008年在香港成立，擁有6個衛星頻道和1個網絡電視臺。香港衛視於2010年10月正式開播以來，'
                '以24小時開路不加密的方式，通過亞太5號、亞太6號、亞太7號三顆衛星雙波段播出，已經覆蓋亞太、北美、歐洲、中東、非洲等150多個國家和地區。'
                '香港衛視堅持“立足香港、延伸兩岸、融入世界”的戰略發展定位，堅持“中國元素，國際表達”、“傳播中華文化，傾聽世界聲音”和“溫暖、善意、積極”的傳播理念，堅持把 “講好中國故事、'
                '傳播好中國聲音、傳遞中國正能量”作為立台之本，大力推動“中國文化”、“中國變化”、“中國形象”走出去，著力建設有影響力的對外宣傳平臺，打造中西優秀文化融合傳播的窗口，'
                '媒體傳播力和品牌影響力不斷提升，在服務特區政府、助力改善香港政治輿論環境，宣傳中國、傳播好中國聲音等方面，發揮了積極、獨特的作用。',
        'sort': '香港',
    }
    channels.append(channel)
    return channels


'''


'''
