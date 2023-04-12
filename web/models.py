# -*- coding:utf-8 -*-
from django.db import models, transaction
from django.db.models import Q
from dateutil import tz
from utils.general import cht_to_chs, add_info_desc, add_info_title
import datetime
from django.utils import timezone
tz_sh = tz.gettz('Asia/Shanghai')
class Channel(models.Model):
    source_choices = [
        ('tvmao','电视猫'),
        ('tvsou','搜视'),
        ('cctv','央视'),
        ('zhongshu', '中数'),
        ('tbc','台湾宽频tbc'),
        ('mod','中华电信MOD'),
        ('cabletv','香港有线宽频caletv'),
        ('g4tv','台湾四季电视'),
        ('icable','香港有线宽频i-cable'),
        ('nowtv','香港NOWTV'),
        ('tvb','香港无线电视TVB'),
        ('smg','上海广播电视'),
        ('btv', '北京卫视'),
        ('gdtv', '广东卫视'),
        ('hks','香港卫视'),
        ('viu','viutv'),
        ('chuanliu','川流TV'),
        ('mytvsuper','myTVSUPER')

    ]
    need_get = [
        (1,'是'),
        (0,'否')
    ]
    channel_id = models.CharField('频道来源网站ID', max_length=300)
    tvg_name = models.CharField('匹配用的tvg-name', null=False, max_length=100, db_index=True)
    name = models.CharField('频道显示名称', null=False, max_length=100, db_index=True)
    sort = models.CharField('频道分类', null=False, max_length=50, db_index=True)  # 1，2，3，4，5
    logo = models.CharField('台标地址', max_length=400, null=True)
    last_program_date = models.DateField('最新节目日期', db_index=True, null=True)
    last_crawl_dt = models.DateTimeField('最近的采集日期', auto_now=True, null=True)
    create_dt = models.DateTimeField('创建日期', auto_now_add=True, null=True)
    descr = models.CharField('频道描述', max_length=500, null=True,blank=True)
    has_epg = models.IntegerField('是否有节目表',choices=need_get, default=0, db_index=True)
    ineed = models.IntegerField('是否需获取', choices=need_get,default=0, db_index=True)
    source = models.CharField('节目来源', choices = source_choices,max_length=50, db_index=True, null=True)
    recrawl = models.IntegerField('需重新获取当天数据', choices = need_get,db_index=True, default=0)
    patten = models.CharField('本频道正则', max_length=100, null=True,blank = True)
    remark = models.CharField('备注', max_length=500, null=True ,blank = True)

    def __str__(self):
        return '-'.join([str(self.id),self.name,self.tvg_name,self.source if self.source else ''])

    class Meta:
        verbose_name = '频道列表'
        verbose_name_plural = '频道列表'
    # 获取需要抓取的频道，如果需要重新抓取，则使用，recrawl = 1
    def get_crawl_channels(self, need_date, recrawl=0):
        if recrawl == 1:
            return self.objects.filter(ineed=1, has_epg=1).filter(Q(recrawl=1) | Q(last_program_date__lt=need_date))
        else:
            return self.objects.filter(has_epg=1, ineed=1, last_program_date__lt=need_date)
        # 获取指定名称的频道，用于测试,只返回获取到数据的第一个

    def get_spec_channel(self, name=0, id=0):
        if name:
            ret = self.objects.filter(tvg_name__icontains=name)[:1]
            if ret.count() == 0:
                ret = self.objects.filter(name__icontains=name)[:1]
        elif id:
            ret = self.objects.filter(id=id)
        else:
            ret = self.objects.filter(tvg_name='CCTV1')
        return ret

    # 获取某一频道的信息（严格匹配）
    def get_spec_channel_strict(self, name=0, id=0):
        if name:
            ret = self.objects.filter(tvg_name=name)
        else:
            ret = self.objects.filter(id=id)
        return ret

    def get_need_channels(self, sorts):
        if sorts == 'all':
            channels = self.objects.filter(ineed=1, has_epg=1)
        else:
            channels = self.objects.filter(sort__in=sorts, ineed=1, has_epg=1)
        return [channels, channels.values_list('id')]
    def get_match_channels(self):
        channels = self.objects.filter(ineed = 1,has_epg=1)
        return channels
    def save(self, *args, **kwargs):
        if self.source in self.channel_id:
            super().save(*args, **kwargs)
        else:
            pass


class Epg(models.Model):
    channel_id = models.CharField('频道ID', db_index=True, max_length=50)
    starttime = models.DateTimeField('开始时间', db_index=True)
    endtime = models.DateTimeField('结束时间', null=True)
    title = models.CharField('节目名称', max_length=200)
    descr = models.TextField('节目描述', null=True)
    program_date = models.DateField('节目所属于日期', db_index=True)
    crawl_dt = models.DateTimeField('采集时间', auto_now_add=True, null=True)
    source = models.CharField('节目来源', max_length=20, null=True)
    def __str__(self):
        return '%s %s %s' % (self.channel_id, self.starttime.astimezone(tz=tz_sh), self.title)

    def to_dict(self):
        ret = {
            'channel_id': self.channel_id,
            'starttime': self.starttime,
            'endtime': self.endtime,
            'title': self.title,
            'descr': self.descr,
            'program_date': self.program_date,
            'source': self.source,
        }
        return ret

    class Meta:
        verbose_name = '节目表'
        verbose_name_plural = '节目表'

    def save(self, *args, **kwargs):
        self.crawl_dt = timezone.now()
        super().save(*args, **kwargs)

    # 获取指定天数的EPG
    def get_epgs(self, channel_ids, need_program_date):
        if need_program_date > datetime.datetime.now().date():
            epgs = self.objects.filter(
                channel_id__in=channel_ids,program_date__gte=datetime.datetime.now(),program_date__lte=need_program_date)  # ,program_date__lte=program_date,program_date__gte=datetime.datetime.now().date())
            if epgs.count() == 0:  # 没有数据则获取当天数据
                epgs = self.objects.filter(channel_id__in=channel_ids, program_date=datetime.datetime.now().date())
        else:
            epgs = self.objects.filter(channel_id__in=channel_ids, program_date=need_program_date)
        for epg in epgs:
            if epg.endtime is None:
                epg.endtime = datetime.datetime.combine(epg.starttime.date(),
                                                        datetime.time(hour=23, minute=59, second=59))
        return epgs

    def test(self):
        return self.objects.filter(source='smg')

    def get_single_epg(self, channel, need_date):
        epgs_list = []
        no_endtime_endtime = datetime.datetime.combine(need_date,
                                                       datetime.time(hour=12, minute=59, second=59)).astimezone(
            tz=tz_sh)
        epgs = self.objects.filter(channel_id=channel.id, program_date=need_date)

        for epg in epgs:  # 将结束时间为空白的字段，加上当天最晚一秒.直接在此处处理时区问题，后面获取后不再处理
            if epg.endtime is None:
                epg.endtime = no_endtime_endtime
            epg.starttime = epg.starttime.astimezone(tz=tz_sh).strftime('%H:%M')
            epg.endtime = epg.endtime.astimezone(tz=tz_sh).strftime('%H:%M')
            epg.descr = '%s%s' % (epg.descr, add_info_desc)
            epg.title = '%s%s' % (epg.title, add_info_title)
            epg1 = epg.to_dict()
            epgs_list.append(epg1)
        return epgs_list

    def save_to_dbs(self, ret):
        success = 1
        msg = ''
        querylist = []
        n = 0
        # 对只有开始日期，没有终止日期的来源，增加上一个的终止日期（不同来源处理不同方式）,全部不在各自方法中更改
        if ret['source'] in ['tvmao', 'tvsou', 'smg', 'cabletv', 'icable', 'mod', 'tvb', 'zhongshu','hks','mytvsuper']:
            epglen = len(ret['epgs'])
            for x in range(epglen):
                if x < epglen - 1:
                    ret['epgs'][x]['endtime'] = ret['epgs'][x + 1]['starttime']
            cs = self.objects.filter(channel_id=ret['epgs'][0]['channel_id'],
                                     starttime__lt=ret['epgs'][0]['starttime'].astimezone(tz=tz_sh))
            if cs:
                cs = cs.latest('starttime')
                if (ret['epgs'][0]['starttime'].astimezone(tz=tz_sh) - cs.starttime.astimezone(
                        tz=tz_sh)).seconds < 19000:  # 只有库里最新的记录，离当前第一条记录小于2.5小时才会填充前一条记录。
                    cs.endtime = ret['epgs'][0]['starttime'].astimezone(tz=tz_sh)
                    cs.save()
        n = 0
        for epg in ret['epgs']:
            try:
                n+=1
                if ret['source'] in ['mod', 'cabletv', 'tbc', 'g4tv', 'icable', 'nowtv', 'tvb','viu','mytvsuper']:  # 对繁体的转简体中文
                    epg['title'] = cht_to_chs(epg['title'])
                    descr = cht_to_chs(epg['desc']) if 'desc' in epg else ''
                else:
                    descr = epg['desc'] if 'desc' in epg else ''
                querye = Epg(channel_id=epg['channel_id'], starttime=epg['starttime'].astimezone(tz=tz_sh),
                             endtime=epg['endtime'].astimezone(tz=tz_sh) if epg['endtime'] else None,
                             title=epg['title'], descr=descr,
                             program_date=epg['program_date'], source=ret['source'])
                querylist.append(querye)
            except Exception as e:
                success = 0
                msg = 'web-models-Epg-save_to_dbs %s' % (e)
                continue
        try:
            ret = self.objects.bulk_create(querylist)
        except Exception as e:
            success = 0
            msg = 'web-models-Epg-save_to_dbs bulk_create2： %s' % (e)
        return {
            'success': success,
            'data': ret,
            'msg': msg
        }

    # 删除某一频道的某一时间段的节目表_
    def del_channel_epgs(self, channel_id, program_date, last_program_date):
        if program_date == last_program_date:
            ret = self.objects.filter(channel_id=channel_id, program_date=program_date).delete()
        else:
            ret = self.objects.filter(channel_id=channel_id, program_date__gte=program_date,
                                      program_date_lte=last_program_date).delete()
        return ret


class Crawl_log(models.Model):
    LOG_LEVELS = (
        (1, '信息'),
        (2, '错误警告')
    )
    dt = models.DateTimeField('日志时间', auto_now_add=True, db_index=True)
    msg = models.TextField('内容', max_length=1000)
    level = models.IntegerField('日志级别', choices=LOG_LEVELS, default=1)  # 1 正常信息 2 错误

    def __str__(self):
        return '%s-%s-%s' % (self.dt.strftime('%Y-%m-%d %H:%M'), self.msg, '警告' if self.level == 2 else '信息')

    def save(self, *args, **kwargs):
        self.msg = self.msg[:900] + '...'
        super().save(self, *args, **kwargs)

    class Meta:
        verbose_name = '抓取日志'
        verbose_name_plural = '抓取日志'

class Channel_list(models.Model):
    is_alive_choice = (
        (0, '否'),
        (1, '是')
    )
    inner_channel_id = models.IntegerField('内部id',default=99999,db_index = True)
    out_channel_id = models.CharField('来源网站上的id',max_length=100)
    inner_name = models.CharField('内部tvg-name',max_length=20)
    out_name = models.CharField('来源网站上的名称',max_length=20)
    source = models.CharField('来源网站',max_length=20)
    is_alive = models.IntegerField('来源网站上是否仍然存在',choices = is_alive_choice,default = 1)
    create_date = models.DateField('加入日期',auto_now_add = True)
    update_date = models.DateField('更新日期',auto_now_add=True)
    #del_date = models.DateField('来源网站取消日期',auto_now_add=True)
    def __str__(self):
        return '%s-%s-%s' % (self.inner_channel_id,self.inner_name,self.out_name)
    class Meta:
        verbose_name = "频道来源整理表"
        verbose_name_plural = "频道来源整理表"
    def save_to_db(self,channels):
        msg = 'Channel_list save success!'
        success = 1
        old_channels_same_source = self.objects.filter(source = channels[0]['source'])
        querylist = []
        new_no = 0  #新增加
        update_no = 0 #更新的
        not_alive_no = 0 #已经失效的
        dt_now = datetime.datetime.now().date()
        is_alive_list = []
        for channel in channels:
            try:
                for channel_old in old_channels_same_source:
                    #原来已经保存过
                    if channel_old.out_name == channel['name']:
                        channel_old.out_channel_id = ','.join(channel['id'])
                        channel_old.update_date = dt_now
                        channel_old.save()
                        is_alive_list.append(channel_old)
                        update_no += 1
                        break
                else:#新数据
                    querye = Channel_list(inner_channel_id=0,
                                          out_channel_id=','.join(channel['id']),
                                          inner_name='',
                                          out_name=channel['name'],
                                          source=channel['source'],
                                          is_alive=True,
                                          create_date=dt_now,
                                          update_date=dt_now)
                    new_no += 1
                    querylist.append(querye)
            except Exception as e:
                success = 0
                msg = 'web-models-channel_list-save1 %s' % (e)
                continue
        #已经从官网剔除的标记IS_ALIVE false
        for old_channel in old_channels_same_source:
            if old_channel not in is_alive_list:
                old_channel.is_alive = False
                old_channel.save()
                not_alive_no += 1
        try:
            ret = self.objects.bulk_create(querylist)
        except Exception as e:
            success = 0
            msg = 'web-models-channel_list-save_to_dbs bulk_create2： %s' % (e)
        msg = '新增:%s,更新:%s,失效:%s,%s'%(new_no,update_no,not_alive_no,msg)
        ret = {
            'success':success,
            'msg':msg
        }
        return ret
