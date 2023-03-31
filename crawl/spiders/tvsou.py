# -*- coding:utf-8 -*-
import datetime
import requests
from bs4 import BeautifulSoup as bs

from utils.general import headers


def get_desc_tvsou(url):
    return ''
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        s = soup.select('div.prog_content_txt')[0].text
        desc = s.replace('\n', '').replace(' ', '').replace('\t', '').replace('剧情简介：', '').replace('　', '')
    except Exception as e:
        desc = ''
    return desc


def get_epgs_tvsou(channel, channel_id_, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    desc = ''
    need_weekday = dt.weekday() + 1  # 需要获取周几的节目可以获取下周数据 .下周节目,另一个周一即为w1 ,需要再次确认
    if "#" in channel_id_:
        channel_id, sort_class = channel_id_.split('#')
        url = 'https://www.tvsou.com/epg/%s/w%s' % (channel_id, need_weekday)
    else:
        url = 'https://www.tvsou.com/epg/%s/w%s' % (channel_id_, need_weekday)

    # url = 'https://www.tvsou.com/epg/%s_w%s' % (channel_id_, need_weekday)
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        rows = soup.select('table.layui-table')[0].select('tr')
    except Exception as e:
        msg = 'spider-tvsou-连接失败，%s' % e
        success = 0
        ret = {
            'success': success,
            'epgs': epgs,
            'msg': msg,
            'last_program_date': dt,
            'ban': 0,
        }
        return ret
    program_urls = {}
    for row in rows:
        try:
            if row.select('td > a'):
                starttime_str = row.select('td > a')[0].text
                title = row.select('td > a')[1].text
            else:
                starttime_str = row.select('td')[0].text
                title = row.select('td')[1].text
            starttime = datetime.datetime.combine(dt, datetime.time(int(starttime_str[:2]), int(starttime_str[-2:])))
            program_url = None
            if row.select('td > a') and 'href' in row.select('td > a')[0].attrs:
                program_url = 'https:' + row.select('td > a')[0].attrs['href']
                program_url = program_url.replace(' ', '')
                if program_url in program_urls:  # 同一频道，同一天的节目同一个描述只抓取一次
                    desc = program_urls[program_url]
                else:
                    if len(program_url) > 17:
                        desc = get_desc_tvsou(program_url)
                        program_urls.update({program_url: desc})
                    else:
                        program_url, desc = '', ''
            else:
                program_url, desc = '', ''
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': desc,
                   'program_date': dt,
                   'super_id': channel.super_id,
                   }
            epgs.append(epg)
        except Exception as e:
            msg = 'spider-tvsou-FOR:%s' % e
            continue

    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


def get_channels_tvsou():
    channels = []
    sorts = []
    host = 'https://www.tvsou.com'
    url = '%s/%s' % (host, 'epg/difang/')
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    div_sorts = soup.select('div.pd_list > div.pd_tit')
    div_channels = soup.select('div.pd_list > div.pd_con > ul')
    n = 0
    # print(div_sorts)
    for div_channel in div_channels:
        sort_name = div_sorts[n].text.strip()
        lis = div_channel.select('li')
        n += 1
        for li in lis:
            name = li.a.text.strip()
            url = host + li.a['href']
            id = li.a['href'].replace('epg', '').replace('/', '')
            if len(id) < 5:
                continue
            channel = {
                'name': name,
                'id': [id],
                'url': url,
                'source': 'tvsou',
                'logo': '',
                'desc': '',
                'sort': sort_name,
            }
            channels.append(channel)
    print('共有：%s 个分类，%s 个频道' % (n, len(channels)))
    return channels
