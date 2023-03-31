from django.contrib import admin

from .models import Channel, Epg, CrawlLog, ChannelList

admin.site.site_header = '老张的EPG--频道配置'
admin.site.site_title = "老张的EPG"
admin.site.index_title = "后台首页"


# Register your models here.
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tvg_name', 'name', 'source', 'last_program_date', 'ineed')
    # list_per_page设置每页显示多少条记录
    list_per_page = 50
    # ordering设置默认排序字段
    ordering = ('id',)
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('tvg_name', 'name')
    # 筛选器
    list_filter = ('sort',)  # 过滤器
    search_fields = ('tvg_name', 'name', 'channel_id')  # 搜索字段


admin.site.register(Channel, ChannelAdmin)


class EpgAdmin(admin.ModelAdmin):
    list_display = ('channel_id', 'starttime', 'title', 'program_date', 'source')
    date_hierarchy = 'program_date'
    search_fields = ('channel_id',)  # 搜索字段


admin.site.register(Epg, EpgAdmin)


class Crawl_logAdmin(admin.ModelAdmin):
    list_display = ('dt', 'msg', 'level')


admin.site.register(CrawlLog, Crawl_logAdmin)


class Channel_listAdmin(admin.ModelAdmin):
    list_display = ('inner_channel_id', 'inner_name', 'out_channel_id', 'out_name', 'source')
    list_filter = ('source',)  # 过滤器
    list_display_links = ('inner_name', 'out_name')


admin.site.register(ChannelList, Channel_listAdmin)
