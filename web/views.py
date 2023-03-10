from django.shortcuts import render
from django.http import HttpResponse,FileResponse
from web.models import Channel,Epg
from utils.general import noepgjson,crawl_info,root_dir
from utils.aboutdb import get_html_info
import datetime,re,json,os
from dateutil import tz
tz_sh = tz.gettz('Asia/Shanghai')
def d(request):
    return render(request,'a.html')
def index(request):
    crawl_days = crawl_info['gen_xml_days']
    start_date = datetime.datetime.now().strftime(u'%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
    start_date_no = datetime.datetime.now().strftime(u'%Y%m%d')
    end_date_date = datetime.datetime.now() + datetime.timedelta(days=crawl_days - 1)
    end_date = (end_date_date).strftime(u'%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
    info = get_html_info(end_date_date.date())
    channel_no = info['channels'].count()
    epg_no = info['epg_no']

    ret = {'channel_no':channel_no,
           'crawl_day':crawl_days,
           'epg_no':epg_no,
           'start_date':start_date,
           'start_date_no':start_date_no,
           'end_date':end_date,
           'channels':info['channels'],
           'root_dir':root_dir,
           'n':0,}
    return render(request,"index.html",context = ret)
def download(requests,title):
    file = open(os.path.join(root_dir,title),'rb')
    response = FileResponse(file)
    response['Content-Type']='application/octet-stream'
    return response
def diyp(request):
    ret = single_channel_epg(request)
    ret_epgs = ret['epgs']
    datas = []
    if len(ret['epgs']) == 0:
        ret_epgs = noepgjson('name', 'id', datetime.datetime.now().date())

    for epg in ret_epgs:
        epg1 = {
            'start':epg['starttime'],
            'end':epg['endtime'],
            'title':epg['title'],
            'desc':epg['descr'],
        }
        datas.append(epg1)

    ret1 = {
        "channel_name": ret['channel'],
        "date": ret['epg_date'].strftime('%Y-%m-%d'),
        "epg_data":datas,
    }
    try:
        j = json.dumps(ret1,ensure_ascii=False)
    except Exception as e:
        print(e,datas)
        j = 'abc'
    return HttpResponse(j,content_type='application/json') #
#WEB查询某频道信息接口
def web_single_channel_epg(request):
    ret = single_channel_epg(request)
    ret_epgs = ret['epgs']
    if len(ret_epgs) == 0:
        epg = {
            'start': '',
            'end': '',
            'title': '没有此日期节目信息--%s'%ret['msg'],
            'desc': '',
        }
        ret_epgs = [epg]
    title = '%s -- %s'%(ret['channel'],ret['epg_date'].strftime('%Y-%m-%d'))

    tomorrow_date = (ret['epg_date'] + datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
    tomorrow_url = '?ch=%s&date=%s'%(ret['tvg_name'],tomorrow_date)
    yesterday_date = (ret['epg_date'] - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
    yesterday_url = '?ch=%s&date=%s'%(ret['tvg_name'],yesterday_date)
    source = ret['source']
    ret = {
        'title':title,
        'tomorrow_url':tomorrow_url,
        'yesterday_url':yesterday_url,
        'epgs':ret_epgs,
        'source':source,
    }
    return render(request,'single_channel_epgs.html',context=ret)
#请求某个频道数据的通用接口
def single_channel_epg(request):
    tvg_name = ''
    success = 0
    epgs = []
    need_date = datetime.datetime.now().date() #没有提供时间，则使用当天
    msg = ''
    if request.method == "GET" and 'ch' in request.GET and 'date' in request.GET:
        tvg_name = request.GET['ch']
        if tvg_name in ["CCTV5 ","IPTV5 ","IPTV6 ","IPTV3 "]:
            tvg_name = tvg_name.strip() + '+'
        date_re = re.search('(\d{4})\D(\d+)+\D(\d+)', request.GET['date'])
        if date_re:
            need_date = datetime.date(int(date_re.group(1)), int(date_re.group(2)), int(date_re.group(3)))
        channels = Channel.get_spec_channel_strict(Channel,tvg_name)
        if channels.count() == 0:
            msg = '没有此频道'
            channel_name = tvg_name
            source = ''
        else:
            channel = channels.first()
            channel_name = channel.name
            epgs = Epg.get_single_epg(Epg,channel,need_date)
            source = channel.source


            if len(epgs) > 0:
                success = 1
    else:
        msg = '参数错误'
        channel_name = '未提供'
    ret = {
        'success':success,
        'msg':msg,
        'epgs':epgs,
        'channel':channel_name,
        'tvg_name':tvg_name,
        'epg_date':need_date,
        'source':source,
    }
    return ret

