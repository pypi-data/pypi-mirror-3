# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django import template
register = template.Library()

from asv_seo.models import *
from asv_utils.common import Str2Int
#---------------------------------------------------------------
#---------------------------------------------------------------
def GetDefaultSEO(U='/'):
    try:
        rv =  settings.DEFAULT_SEO
    except:
        rv = {}
        for i in ['keywords_ru', 'descriptions_en', 'title_en', 'descriptions_ru', 'title_ru', 'keywords_en']:
            rv[i] = ''
    return rv
#---------------------------------------------------------------
def GetRecurseSEO(ct,id):
    S = SEO.objects.filter(content_type=ct, object_id=id).values(
        'title_en','title_ru','keywords_en','keywords_ru','description_en','description_ru'
    )
    if (S.count() < 1):
        try:
            e = ct.get_object_for_this_type(id=id)
            if (e.parent):
                S = GetRecurseSEO(ct,e.parent.id)
            else:
                S = GetDefaultSEO()
        except:
            S = GetDefaultSEO()
    else:
        S = S[0]
    return S
#---------------------------------------------------------------
@register.inclusion_tag('ic_seo_headers.html', takes_context=True)
def seo_hdrs(context,*args,**kwargs):
    D = GetDefaultSEO()
    request = context.get('request',None)
    CT = context.get('CT',None)
    if (CT == False):
        S = D
    else:
        try:
            id = CT.id
            ct = ContentType.objects.get_for_model(CT)
            S = GetRecurseSEO(ct,id)
            for i in D.keys():
                ii = S.get(i,None)
                if not ii:
                    S[i] = D.get(i,'')
        except AttributeError:
            if settings.DEBUG:
                try:
                    meta = request.get('META',{})
                    http_ctype = meta.get('CONTENT_TYPE','undefined')
                except:
                    http_ctype = 'undefined'
                try:
                    uri = request.get_full_path()
                except:
                    uri = None
                print('asv_seo:: Can\'t find ID or ContentType for {} [{}::{}]'.format(CT,http_ctype,uri))
            S = D
    # retreiving SEO by requested LANG
    L = context.get('LANG', settings.DEF_LANG)
    SS = {}
    for i in ('title','keywords','description'):
        try:
            SSi = '{}_{}'.format(i,L)
            SS[i] = S.get(SSi,settings.DEFAULT_SEO.get(SSi,''))
        except:
            pass
    return {
        'SEO': SS,
    }
#---------------------------------------------------------------
#---------------------------------------------------------------
