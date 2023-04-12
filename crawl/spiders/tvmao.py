# -*- coding:utf-8 -*-
import requests, time, datetime,re
from utils.general import headers
from bs4 import BeautifulSoup as bs
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
}

# 先直接请求获取上半天节目http://m.tvmao.com/program/NANFANG-NANFANG2-w2.html，然后再获取加密相关信息，再生成下半天地址https://m.tvmao.com/api/pg?p=......获取下半天节目
#####非当天时，先使用 “｜＋q"运算得到后半部分，再使用 ”id + | + a"使用此函数运行得到前半部分
def get_desc(url_part):  # 获取节目介绍,总是出问题，暂不使用
    return ''
    try:
        url = 'https://m.tvmao.com' + url_part
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        if soup.select('div.section'):
            desc = soup.select('div.section')[0].text
        else:
            desc = soup.select('div.d_s_info')[0].text + soup.select('div.desc_col')[0].text
    except Exception as e:
        desc = ''
    return desc.replace('\r', '\n').replace('\n\n', '\n').replace('\n\n', '\n')
def get_morning_lis(url, today):  # 获取当天上午的lis，如果不是当天，另外处理,today参数为是否当天
    res = requests.get(url, headers=headers,timeout=5)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('ul#pgrow > li')
    return lis

def get_token():
    url = 'https://www.tvmao.com/servlet/accessToken?p=channelEpg'
    res = requests.get(url,headers = headers,timeout = 5)
    res.encoding = 'utf-8'
    res_json = res.json()
    if res_json[0]:
        success = 1
    else:
        success = 0
    token = res_json[1]
    ret = {
        'success':success,
        'token':token,
    }
    return ret

def get_epgs_tvmao(channel, channel_id, dt, func_arg):
    afternoon_url = 'https://www.tvmao.com/servlet/channelEpg'
    time.sleep(4)  # 防止 被BAN
    sleep_time = 10 #出错时等待时间
    epgs = []
    msg = ''
    success = 1
    ban = 0 #标识是否被BAN掉了
    today_dt = datetime.datetime.now()
    need_weekday = dt.weekday() + 1  # 需要获取周几的节目可以获取下周数据 w8 下周一 w9下周二
    epg_url_part = 'http://m.tvmao.com/program/'
    url = '%s%s-w%s.html' % (epg_url_part, channel_id, need_weekday)
    try:
        nn,lis = 0,[]
        while len(lis) == 0:  # 如果没有返回上午节目重新抓取上午节目，防止tvmao不稳定
            today = 1 if today_dt.date() == dt else 0
            lis = get_morning_lis(url, today)
            time.sleep(0.7)
            nn += 1
            if nn > 3:
                break
        time.sleep(0.5)
    except Exception as e:
        msg = 'spider-tvmao-get_morning_lis获取上午数据失败！%s' % (e)
        success = 0
        ret = {
            'success': success,
            'epgs': epgs,
            'msg': msg,
            'last_program_date': dt,
        }
        return ret
    for li in lis:
        if "id" in li.attrs:
            continue
        title = li.select('span.p_show')[0].text
        # starttime = li.select('span.epg-row-time')[0].text if len(li.select('span.epg-row-time')) else li.select('span.epg-row-playing')[0].text
        starttime_str = li.select('span.am')[0].text.strip()
        if starttime_str == '直播中' or '正在播出' in starttime_str.strip():
            starttime = today_dt
        else:
            starttime = datetime.datetime.combine(dt,datetime.time(int(starttime_str[:2]),int(starttime_str[-2:])))
        href = li.a['href'] if 'href' in str(li.a) else ''
        desc = get_desc(href)
        url = 'https://www.tvmao.com' + href.replace('tvcolumn', 'drama')
        epg = {'channel_id': channel.id,
               'starttime': starttime,
               'endtime': None,
               'title': title,
               'desc': desc,
               'program_date': dt,
               }
        epgs.append(epg)
    try:
        tccc = channel_id.split('-')
        if len(tccc) == 2:
            tc,cc = tccc
        else:
            tc = 'digital'
            cc = '-'.join(tccc[1:])
        data = {
            'tc':tc,
            'cc':cc,
            'w':need_weekday,
            'token':get_token()['token'],
        }
        res = requests.post(afternoon_url, headers=headers,data=data, timeout=30)
        lss = res.json()[1]
        if res.json()[0] == -2:
            msg = '^v^========被电视猫BAN掉了，等待 %s 秒！' % sleep_time
            #print(msg)
            time.sleep(sleep_time)
            success = 0
            ban = 1
            ret = {
                'success': success,
                'epgs': epgs,
                'msg': msg,
                'last_program_date': dt,
                'ban':ban,
            }
            return ret
        # 因返回时，有时是列表，有时为一段完整的HMTL，分开处理
        if isinstance(lss,str):
            soup = bs(lss, 'html.parser')  # 20201109以前为一段html,现在改为列表，然后再HTML
            lis1 = soup.select('li')
            for tr in lis1:
                if not tr.find('div'): #<li id="night">晚间节目</li> 里面有这种的跳过
                    continue
                spans = tr.select('span')
                if len(spans) > 1:
                    if '正在播出' in spans[0].text:
                        title = spans[1].text
                    else:
                        title = spans[1].text
                starttime_str = spans[0].text.replace('正在播出','').strip()
                starttime = datetime.datetime.combine(dt,
                                                      datetime.time(int(starttime_str[:2]), int(starttime_str[-2:])))
                epg = {'channel_id': channel.id,
                       'starttime': starttime,
                       'endtime': None,
                       'title': title,
                       'desc': '',
                       'program_date': dt,
                       'super_id': channel.super_id,
                       }
                epgs.append(epg)
        else:
            for tr in lss:  # 列表形式的结果
                tr1 = bs(tr['program'], 'html.parser')
                title = tr1.text
                # starttime = datetime.datetime.strptime(tr1.a['res'][:16],'%Y-%m-%d %H:%M')#部分结果没有 res，所有不能直接使用
                starttime_str = tr['time']
                starttime = datetime.datetime.combine(dt,
                                                      datetime.time(int(starttime_str[:2]), int(starttime_str[-2:])))
                href = tr1.a['href'] if 'href' in str(tr1.a) else ''
                program_url = 'https://www.tvmao.com' + href.replace('tvcolumn', 'drama')
                desc = get_desc(href)
                epg = {'channel_id': channel.id,
                       'starttime': starttime,
                       'endtime': None,
                       'title': title,
                       'desc': desc,
                       'program_date': dt,
                       }
                epgs.append(epg)
    except Exception as e:
        success = 0
        msg = 'spider-tvmao-%s'%e
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
        'source':'tvmao'
    }
    return ret
#使用另外的接口直接获取全天数据，不需要token等
def get_epgs_tvmao2(channel,channel_id,dt,func_arg):
    epgs = []
    desc = ''
    msg = ''
    success = 1
    ban = 0 #标识是否被BAN掉了,此接口不确定是否有反爬机制
    now_date = datetime.datetime.now().date()
    need_date = dt
    delta = need_date - now_date
    now_weekday = now_date.weekday()
    need_weekday = now_weekday + delta.days + 1
    id_split = channel_id.split('-')
    if len(id_split) == 2:
        id = id_split[1]
    elif len(id_split) ==3:
        id = '-'.join(id_split[1:3])
    else:
        id = channel_id
    url = "https://lighttv.tvmao.com/qa/qachannelschedule?epgCode=%s&op=getProgramByChnid&epgName=&isNew=on&day=%s"%(id,need_weekday)
    try:
        res = requests.get(url,headers = headers)
        res_j = res.json()
        datas = res_j[2]['pro']
        for data in datas:
            title = data['name']
            starttime_str = data['time']
            starttime = datetime.datetime.combine(dt,
                                                  datetime.time(int(starttime_str[:2]), int(starttime_str[-2:])))
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': desc,
                   'program_date': dt,
                   }
            epgs.append(epg)
    except Exception as e:
        success = 0
        msg = 'spider-tvmao-%s'%e
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
        'source':'tvmao'
    }
    return ret

def get_channels_tvmao():
    url_sort = 'https://www.tvmao.com/program/playing/'
    res = requests.get(url_sort,headers = headers,timeout = 5)
    res.encoding = 'utf-8'
    soup = bs(res.text,'html.parser')
    provinces = {}
    big_sorts = {}
    channels = []
    provinces_more = soup.select('div.province > ul.province-list > li')
    big_sorts_more = soup.select('dl.chntypetab > dd')
    for province_more in provinces_more:
        province = province_more.text.strip().replace('黑龙','黑龙江')
        province_id = province_more.a['href'].replace('/program/playing/','').replace('/','')
        province = {
            province:province_id,
        }
        provinces.update(province)
    for big_sort_more in big_sorts_more:
        sort_name = big_sort_more.text.strip()
        url = big_sort_more.a['href']
        sort_id = url.replace('/program/playing/','').replace('/','')
        if sort_name in provinces or sort_name == '收藏':
            continue
        big_sorts.update({sort_name:sort_id})
    provinces.update(big_sorts)
    sorts = provinces
    n = 0
    for sort_name in sorts:
        url = 'https://www.tvmao.com/program/playing/%s'%sorts[sort_name]
        time.sleep(0.5)
        res = requests.get(url,headers = headers,timeout = 5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        channel_trs = soup.select('table.timetable > tr')
        n += 1
        for tr in channel_trs:
            tr1 = tr.td.a
            name = tr1['title']
            href = tr1['href']
            id = href.replace('/program/','').replace('/','-').replace('.html','').replace('-program_','')
            id = re.sub('-w\d$','',id)
            res1 = tr1['res']
            channel = {
                'name': name,
                'id': [id],
                'url': 'https://m.tvmao.com/program/%s.html' % id,
                'source': 'tvmao',
                'logo': '',
                'desc': '',
                'sort': sort_name,
                'res': res1,
            }
            channels.append(channel)
        print('%s,%s,id:%s,共有频道：%s'%(n,sort_name,sorts[sort_name],len(channel_trs)))

    return channels
