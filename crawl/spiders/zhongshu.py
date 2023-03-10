import requests,re,datetime
from utils.general import headers
from bs4 import BeautifulSoup as bs
#中数传媒官网抓取数据,一次抓取多天数据,但不能重复抓取
#从前一天最后一个节目，到今天最后的节目
def get_epgs_zhongshu(channel, channel_id, dt, func_arg):
    epgs = []
    msg = ''
    success = 1
    host = 'http://epg.tv.cn'
    w = 0 #本周节目
    #如果这一天不是本周节目，则获取下周的节目
    if dt.weekday() < datetime.datetime.now().weekday():
        w = 1
    url = '%s/epg/%s/live/index.php?week=%s' % (host,channel_id,w)
    try:
        res = requests.get(url, headers=headers,timeout=5)
        rs = re.findall('epgs\[\d+\]=new Array\(\"(\d+)\",\"(\d+)\",\"(\d+:\d+)\", \"(.+?)\",.+?\)',res.text) #0 月 1日 2时间 3节目
    except Exception as e:
        msg = 'spider-zhongshu-request-%s'%e
        ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban':0,
        }
        return ret
    for r in rs:
        try:
            starttime = datetime.datetime.strptime('%s%02d%02d%s' % (dt.year, int(r[0]), int(r[1]), r[2]),'%Y%m%d%H:%M')
            title = r[3]  # 节目名称
            if starttime.date() < dt:
                continue
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': '',
                   'program_date': starttime.date(),
                   }
        except Exception as e:
            msg = 'spider-zhongshu-获取具体信息出错-%s'%e
            starttime = datetime.datetime.combine(dt,datetime.time(1,0,0))
            continue
        epgs.append(epg)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': starttime.date(),
        'ban': 0,
    }
    return ret

def get_channels_zhongshu():
    channels = []
    host = 'http://epg.tv.cn/'
    res = requests.get(host, headers=headers)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    uls = soup.select('div.epgleft > ul')
    sorts = []
    spans = soup.select('div.epgleft > ul#channel > div > span')
    sort_name_change = {
        '央视高清付费频道':'央视',
        '4K超高清频道':'央视',
        '央视频道':'央视',
        '卫视频道':'卫视',
        '其他':'北京',
        '其他付费频道':'数字付费',
    }
    for span in spans:
        sort = span.text.strip()
        sorts.append(sort)
    uls = soup.select('div.epgleft > ul#channel > li > ul')
    x = 0
    for ul in uls:
        lis = ul.select('li')
        for li in lis:
            name = li.a.text.strip()
            id = li.a['href'].strip()
            url = '%s%s' % (host, id)
            channel = {
                'name': name,
                'id': [id],
                'url': url,
                'source': 'zhongshu',
                'logo': '',
                'desc': '',
                'sort':sort_name_change[sorts[x]],
            }
            channels.append(channel)
        x += 1
    return channels