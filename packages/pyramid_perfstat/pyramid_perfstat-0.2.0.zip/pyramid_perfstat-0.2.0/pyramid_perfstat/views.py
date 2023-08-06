#!/usr/bin/python
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------
# Name:       views.py
# Purpose:
#
# Author:      Stéphane Bard
#
# Created:      31/01/2012
# Copyright:   -
# Licence:     BSD License
# New field:   ----------
#-----------------------------------------------------------------------------

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_perfstat.perf_serializer import PerfDbManager
from pyramid_perfstat import utils
from pyramid.security import NO_PERMISSION_REQUIRED

@view_config(route_name='pyramid_perfstat.reporting',
             renderer='pyramid_perfstat:templates/reporting.mako',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='pyramid_perfstat.reporting.session_detail',
             renderer='pyramid_perfstat:templates/reporting.mako',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='pyramid_perfstat.reporting.view_detail',
             renderer='pyramid_perfstat:templates/reporting.mako',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='pyramid_perfstat.reporting.url_detail',
             renderer='pyramid_perfstat:templates/reporting.mako',
             permission=NO_PERMISSION_REQUIRED)
def reporting(request):
    """
    display tables with all reports ...
    """
    
    id_session = None
    if 'id_session' in request.matchdict :
       id_session = request.matchdict['id_session']    
    
    id_view = None
    if 'id_view' in request.matchdict :
       id_view = request.matchdict['id_view']

    id_route = None
    if 'id_route' in request.matchdict :
       id_route = request.matchdict['id_route']

    perf_manager = PerfDbManager(None)
    lst_ids_measures_date = perf_manager.get_session_liste()

    if id_session is None :
        id_session = lst_ids_measures_date[-1][0]

    lst_agg_routes_measures = None
    lst_urls_measures = None

    if id_view : 
         lst_agg_routes_measures = perf_manager.get_route_measure_summary_liste(id_session, id_view)

    if id_route : 
         lst_urls_measures = perf_manager.get_urls_measure_liste(id_session, id_route)

    lst_agg_views_measures = perf_manager.get_view_measure_summary_liste(id_session)
    
    # absolute is better
    static_path = request.static_url(utils.STATIC_PATH)
    
    return {
                'static_path':static_path,
                'id_session':id_session,
                'lst_ids_measures_date':lst_ids_measures_date,
                'lst_agg_routes_measures':lst_agg_routes_measures,
                'lst_agg_views_measures':lst_agg_views_measures,
                'lst_urls_measures':lst_urls_measures
            }

@view_config(route_name='pyramid_perfstat.reset',
             permission=NO_PERMISSION_REQUIRED)
def reset_db(request):
    """
    """
    perf_manager = PerfDbManager(request)
    perf_manager.init_db(from_scratch=True)
    return HTTPFound(request.route_url(route_name='pyramid_perfstat.reporting'))
