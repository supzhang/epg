#-*- coding:utf-8 -*-
import requests,re,datetime,os
from utils.general import headers
from bs4 import BeautifulSoup as bs
def get_epgs_cabletv(channel, channel_id, dt, func_arg):
    url = 'http://www.cabletv.com.hk/ct/_cabletv_list_common.php?%s&date=%s' % (channel_id,dt.strftime('%Y%m%d'))
    msg = ''  # 临时MSG，记录出错信息
    success = 0  # 设置采集成功为否
    epgs = []
    try:
        res = requests.get(url, headers=headers,timeout=5)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        trs = soup.select('div#LiScrollContent > table > tr')
        old_dt = datetime.datetime(1999, 12, 31, 12, 12)
        for tr in trs:  #<tr><td width="50" valign="top" align="center"><div>05:30 </div></td><td width="15" valign="top"><div>&nbsp;</div></td><td valign="top"><div>有線新聞</div></td>  <td width="30"valign="top"><div>&nbsp;</div></td>              </tr>
            divs = tr.select('div')
            starttime_str = divs[0].text.replace('\n', '').replace(' ', '')  # 提取时间,5:55
            title = divs[2].text.replace('\n','').strip()
            starttime = datetime.datetime(year = dt.year,month = dt.month,day = dt.day,hour = int(starttime_str[:2]),minute=int(starttime_str[-2:]))
            if starttime < old_dt:
                starttime = starttime + datetime.timedelta(hours=12)
                if starttime < old_dt:
                    starttime = starttime + datetime.timedelta(hours = 12)
            epg = {'channel_id': channel.id,
                   'starttime': starttime,
                   'endtime': None,
                   'title': title,
                   'desc': '',
                   'program_date': dt,
                   }
            epgs.append(epg)
            old_dt = starttime
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


######################爬取cabletv上的频道名单##########################
def get_channels_cabletv():  #使用原来代码，只更改输出
    dds = []
    lis = []
    ds = [] #最终的频道名称列表
    dsinfo= {} #最终频道信息列表,{频道名:[频道ID，频道IMG]}
    ls = {}  #ID与名称对应的列表
    nx = 0 #记录获取到的非重复频道数量
    headers1 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CA;q=0.8,en;q=0.7,zh-TW;q=0.6'
    }
    for x in range(10):
        url =  'http://www.cabletv.com.hk/ct/cabletv.php?id=%s'%(x+1)
        res = requests.get(url,headers = headers1)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        dds1 = soup.select('div.channel > dl.list > dd')
        dds += dds1
    us = ['id=11&cid=187','id=5&cid=85','id=1&cid=267','id=2&cid=188','id=3&cid=73','id=6&cid=234','id=7&cid=139','id=8&cid=109','id=9&cid=21']
    for u in us:  #获取不同类别的频道的，频道名称
        url = 'http://www.cabletv.com.hk/ct/_cabletv_list_common.php?%s'%u
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        lis1 = soup.select('ul.selector_list > li')
        lis += lis1
    for li in lis:  #获取频道名称与ID对应的列表
        try:
            id1 = re.search('(id=\d+&cid=\d+)',li['onclick'])
            id = id1.group(1)
        except Exception as e:
            print(e)
            continue
        name = li.text.replace('\n','').replace(' ','').replace("(高清)",'')
        ls.update({id:name})
    for dd in dds:
        title = re.sub('\s', '', dd.text.replace(' ','').replace('\n',''))
        id = dd.attrs['onclick'].replace("href('?",'').replace('&amp;','&').replace("')",'')
        img = 'http://www.cabletv.com.hk' + dd.select('img')[0].attrs['src']
        if id in ls: #将CHxxx    换成频道名称
            title = ls[id]
        else:
            print('========未匹配到频道的名称======:%s'%dd)
        if title in ds:#检测是否有重复的频道，有重复的频道ID叠加
            idold = dsinfo[title][0]
            id = '%s\t%s'%(idold,id)
            dsinfo.update({title:[id,img]})
        else:
            nx += 1
            dsinfo.update({title:[id,img]})
            ds.append(title)
    channels = []
    for x in dsinfo:
        channel = {
            'name': x,
            'id': dsinfo[x][0].split('\t'),
            'url': '',
            'source': 'cabletv',
            'logo': dsinfo[x][1],
            'desc': '',
            'sort':'海外'
        }
        channels.append(channel)
    print('页面上显示的包含重复的频道有:%s\n节目表中的频道有（可能有重复):%s\n最终非重复的频道有:%s'%(len(dds),len(lis),nx))
    return channels