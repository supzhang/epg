#package spider
#__init__.py

from crawl.spiders.cctv import get_epgs_cctv,get_channels_cctv
from crawl.spiders.tbc import get_epgs_tbc,get_channels_tbc
from crawl.spiders.tvmao import get_epgs_tvmao2,get_channels_tvmao
from crawl.spiders.zhongshu import get_epgs_zhongshu,get_channels_zhongshu
from crawl.spiders.cabletv import get_epgs_cabletv,get_channels_cabletv
from crawl.spiders.g4tv import get_epgs_4gtv,get_channels_4gtv
from crawl.spiders.mod import get_epgs_mod,get_channels_mod
from crawl.spiders.tvb import get_epgs_tvb,get_channels_tvb
from crawl.spiders.nowtv import get_epgs_nowtv,get_channels_nowtv
from crawl.spiders.gdtv import get_epgs_gdtv,get_channels_gdtv
from crawl.spiders.icable import get_epgs_icable,get_channels_icable
from crawl.spiders.btv import get_epgs_btv,get_channels_btv
from crawl.spiders.tvsou import get_epgs_tvsou,get_channels_tvsou
from crawl.spiders.hks import get_epgs_hks,get_channels_hks
from crawl.spiders.viu import get_epgs_viu,get_channels_viu
from crawl.spiders.chuanliu import get_channels_chuanliu,get_epgs_chuanliu
from crawl.spiders.mytvsuper import get_epgs_mytvsuper,get_channels_mytvsuper
from crawl.spiders.gxntv import get_epgs_gxntv,get_channels_gxntv
from utils.general import chuanliu_Authorization
epg_funcs = {
                'tvmao':get_epgs_tvmao2,
                'tbc':get_epgs_tbc,
                'cctv':get_epgs_cctv,
                'zhongshu':get_epgs_zhongshu,
                'cabletv':get_epgs_cabletv,
                'tvsou':get_epgs_tvsou,
                '4gtv':get_epgs_4gtv,
                'mod':get_epgs_mod,
                'tvb':get_epgs_tvb,
                'nowtv':get_epgs_nowtv,
                'icable':get_epgs_icable,
                'gdtv':get_epgs_gdtv,
                'btv':get_epgs_btv,
                'hks':get_epgs_hks,
                'viu':get_epgs_viu,
                'chuanliu':get_epgs_chuanliu,
                'mytvsuper':get_epgs_mytvsuper,
                'gxntv':get_epgs_gxntv,
            }  #所有EPG的接口
epg_source = {
                'tvmao':get_channels_tvmao,
                'tbc':get_channels_tbc,
                'cctv':get_channels_cctv,
                'zhongshu':get_channels_zhongshu,
                'cabletv':get_channels_cabletv,
                'tvsou':get_channels_tvsou,
                '4gtv':get_channels_4gtv,
                'mod':get_channels_mod,
                'tvb':get_channels_tvb,
                'nowtv':get_channels_nowtv,
                'icable':get_channels_icable,
                'gdtv':get_channels_gdtv,
                'btv':get_channels_btv,
                'hks':get_channels_hks,
                'viu':get_channels_viu,
                'chuanliu':get_channels_chuanliu,
                'mytvsuper':get_channels_mytvsuper,
                'gxntv':get_channels_gxntv,
        }
func_args = {
                'tvmao':0,
                'tbc':0,
                'cctv':0,
                'zhongshu':0,
                'cabletv':0,
                'tvsou':0,
                '4gtv':0,
                'mod':0,
                'tvb':0,
                'nowtv':0,
                'icable':0,
                'gdtv':0,
                'btv':0,
                'hks':0,
                'viu':0,
                'chuanliu':chuanliu_Authorization,
                'mytvsuper':0,
                'gxntv':0,
            }
def epg_func(channel,id,dt,func_arg=0,source = 0):
    if source:
        source1 = source
    else:
        source1 = channel.source
    func_arg = func_args[source1] #if func_arg else func_arg
    return epg_funcs[source1](channel,id,dt,func_arg)

__all__ = ['get_epgs_4gtv',
           'get_epgs_btv',
           'get_epgs_cabletv',
           'get_epgs_cctv',
           'get_epgs_gdtv',
           'get_epgs_icable',
           'get_epgs_mod',
           'get_epgs_nowtv',
           'get_epgs_tbc',
           'get_epgs_tvb',
           'get_epgs_tvmao2',
           'get_epgs_zhongshu',
           'get_epgs_tvsou',
           'get_epgs_hks',
           'get_epgs_viu',
           'get_epgs_chuanliu',
           'get_epgs_mytvsuper',
           'get_epgs_gxntv',
            'epg_funcs',
           'func_args',
           'epg_func',
           ]





