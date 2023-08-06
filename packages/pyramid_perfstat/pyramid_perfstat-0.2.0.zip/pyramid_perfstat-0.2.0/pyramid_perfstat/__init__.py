#!/usr/bin/python
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------
# Name:       __init__.py
# Purpose:     
#
# Author:      Stéphane Bard
#
# Created:      31/01/2012
# Copyright:   -
# Licence:     BSD License
# New field:   ----------
#-----------------------------------------------------------------------------


import logging
import sys
from pprint import pformat
from textwrap import dedent

from pyramid.tweens import EXCVIEW
from pyramid.events import NewRequest
from pyramid.settings import aslist
from pyramid.settings import asbool
from pyramid.util import DottedNameResolver
from pyramid.httpexceptions import WSGIHTTPException

import time
import datetime

from pyramid_perfstat.utils import STATIC_PATH, ROUTE_PREFIX
from pyramid_perfstat.perf_serializer import PerfDbManager

def to_int(*segment_names):
    def predicate(info, request):
        match = info['match']
        for segment_name in segment_names:
            try:
                match[segment_name] = int(match[segment_name])
            except (TypeError, ValueError):
                pass
        return True
    return predicate


def perf_tween_factory(handler, registry):
    """
    """
    PerfDbManager(None).init_db()
    
    def perf_tween(request, getLogger=logging.getLogger):
        """
        """
        t0=time.time()
        result = handler(request)

        perf_manager = PerfDbManager(request)
        perf_manager.insert_data(time.time()-t0)
        return result
    
    return perf_tween

def include_perf_routes(config):
    """
    add some routes
    """
    config.add_route('pyramid_perfstat.reporting', '/stat')
    config.add_route('pyramid_perfstat.reset','/reset')

    config.add_route('pyramid_perfstat.reporting.session_detail', '/stat/{id_session}',
                     custom_predicates=(to_int('id_session'),))
    
    config.add_route('pyramid_perfstat.reporting.view_detail', '/stat/{id_session}/{id_view}',
                     custom_predicates=(to_int('id_session', 'id_view'),))

    config.add_route('pyramid_perfstat.reporting.url_detail', '/stat/{id_session}/{id_view}/{id_route}',
                     custom_predicates=(to_int('id_session', 'id_view', 'id_route'),))
    
    
def includeme(config):
    """
    Set up am implicit :term:`tween` to log performance information of each
    Pyramid url application. 

    This tween configured to be placed 'top' view tween.  It
    will log all excution time and log it in sqlite db. It should
    provite a url to allow log performance display.
    such as mean time, number of request urls etc ...
    """
    config.add_static_view(ROUTE_PREFIX+'/static', STATIC_PATH)
    
    config.add_tween('pyramid_perfstat.perf_tween_factory', under=EXCVIEW)
    config.include(include_perf_routes, route_prefix=ROUTE_PREFIX)

    # scan views
    config.scan('pyramid_perfstat.views')
    config.scan('pyramid_perfstat.perf_serializer')

