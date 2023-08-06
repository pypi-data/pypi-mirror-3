#!/usr/bin/python
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------
# Name:        pyramid_perfstat/perf_serializer.py
# Purpose:     
#
# Author:      sbard
#
# Created:      01/02/2012
# Copyright:   --
# Licence:     BSD License
# New field:   ----------
#-----------------------------------------------------------------------------

import logging
import datetime

from zope.interface import Interface

from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IView

import sqlite3

from pyramid.events import NewRequest
from pyramid_perfstat.utils import ROUTE_PREFIX

def new_perfstat_request_subscriber(event):
    request = event.request
    request._PerfDbManager__perfstat_db = sqlite3.connect('perf_app.db')
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    request._PerfDbManager__perfstat_db.close()

class PerfDbManager(object):
    """
    sqlite hand serializer
    """
    # unique id identifier each time pyramid web app
    # reload
    
    id_session = None

    def __init__(self, request):
        """
        connect to db ...
        """
        # init behavior ?
        if request is None :
            self.conn = sqlite3.connect('perf_app.db')
        else :
            self.conn = request.__perfstat_db
        
        if request is not None :
            self.matched_url = request.path_url
            self.route = request.matched_route
            self.matched_route = self.route.name
            
            self.mapper = request.registry.queryUtility(IRoutesMapper)
    
            registry = request.registry
    
            request_iface = registry.queryUtility(IRouteRequest,
                                                  name=self.route.name)
            self.matched_route_name = self.route.name

            view_callable = '<unknown>'
            if (request_iface is None) or (self.route.factory is not
                                           None):
                view_callable = '<unknown>'
            else:
                view_callable = registry.adapters.lookup(
                    (IViewClassifier, request_iface, Interface),
                    IView, name='', default=None)
                view_callable = ".".join((view_callable.__module__,view_callable.__name__))

            self.view_name = view_callable

    def init_db(self, from_scratch=False):
        """
        create table and usefull stuff ...
        in the db ...
        """
        
        c = self.conn.cursor()
        
        if from_scratch :
            c.execute("""drop table if exists pyramid_measure""")

        c.execute("""create table if not exists pyramid_measure (id integer PRIMARY KEY,
                                                                 date_measure datetime)""")

        PerfDbManager.session_perf_id = c.execute("""insert into pyramid_measure values (null, ?)""",
                                                  (datetime.datetime.now(),))
        PerfDbManager.session_perf_id = c.lastrowid

        if from_scratch :
            c.execute("""drop table if exists pyramid_perf""")
            
        c.execute("""create table if not exists pyramid_perf ( id integer PRIMARY KEY,
                                                               id_measure integer,
                                                               url text,
                                                               route_name text,
                                                               view_name text,
                                                               measure real,
                                                               date_measure datetime )""")
        if from_scratch :
            c.execute("""drop table if exists pyramid_agg_route_perf""")
            
        c.execute("""create table if not exists pyramid_agg_route_perf ( id integer PRIMARY KEY,
                                                               id_measure integer,
                                                               url text,
                                                               route_name text,
                                                               view_name text,
                                                               measure real,
                                                               fetch_count integer )""")

        if from_scratch :
            c.execute("""drop table if exists pyramid_agg_view_perf""")
            
        c.execute("""create table if not exists pyramid_agg_view_perf ( id integer PRIMARY KEY,
                                                               id_measure integer,
                                                               view_name text,
                                                               measure real,
                                                               fetch_count integer )""")
        
        self.conn.commit()
        self.end_connection()

    def get_session_liste(self):
        """
        return sessions liste
        """
        c = self.conn.cursor()
        c.execute("""select m.id, m.date_measure, count(p.id) 
                    from pyramid_measure m
                        left join pyramid_agg_view_perf p on p.id_measure=m.id
                group BY m.id order by m.id asc""")
        rows = c.fetchall()
        c.close()
        return rows

    def get_urls_measure_liste(self, id_measure, id_route):
        """
        return resume measure liste
        """
        c = self.conn.cursor()
        c.execute("""select pr.id, pr.measure, pr.url from pyramid_perf pr
                     join pyramid_agg_route_perf rp on rp.id=%d and pr.route_name=rp.route_name
                     where rp.id_measure=%d and pr.id_measure=%d"""%(id_route, id_measure, id_measure))
        rows = c.fetchall()
        c.close()
        return rows 

    def get_route_measure_summary_liste(self, id_measure, id_view):
        """
        return measure liste
        :param id_measure: the session id
        :param id_view: an view recorded id
        """
        c = self.conn.cursor()
        c.execute("""select pr.id, pv.id, pr.measure, pr.url, pr.route_name, pr.view_name, pr.fetch_count
                     from pyramid_agg_route_perf pr
                     join pyramid_agg_view_perf pv on pv.id=%d and pr.view_name=pv.view_name
                     where pr.id_measure=%d order by pr.measure desc, pr.fetch_count desc, pr.url desc"""%(id_view,id_measure))
        rows = c.fetchall()
        c.close()
        return rows 

    def get_view_measure_summary_liste(self, id_measure):
        """
        return measure liste
        :param id_measure: the session id
        """
        c = self.conn.cursor()
        c.execute("""select id, measure, view_name, fetch_count from pyramid_agg_view_perf 
                     where id_measure=%d order by measure desc, fetch_count desc, view_name desc"""%id_measure)
        rows = c.fetchall()
        c.close()
        return rows 

    def end_connection(self):
        """
        close the connection
        """
        self.conn.close()

    def get_last_route_mean_perf(self):
        """
          return last value inserted in pyramid_agg_route_perf
        """
        c = self.conn.cursor()
        c.execute("""select measure, fetch_count from pyramid_agg_route_perf 
                    where id_measure=%d and url='%s'"""%(self.session_perf_id, self.matched_url))
        rows = c.fetchall()
        measure, fetch_count = None, None
        if rows :
           measure, fetch_count = rows[0]
        c.close()
        return measure, fetch_count


    def get_last_view_mean_perf(self):
        """
          return last value inserted in pyramid_agg_route_perf
        """
        c = self.conn.cursor()
        c.execute("""select measure, fetch_count from pyramid_agg_view_perf 
                    where id_measure=%d and view_name='%s'"""%(self.session_perf_id, self.view_name))
        rows = c.fetchall()
        measure, fetch_count = None, None
        if rows :
           measure, fetch_count = rows[0]
        c.close()
        return measure, fetch_count

    def update_mean_route_perf_value(self, resume_perf, insert=False):
        """
            return last value inserted in pyramid_agg_route_perf
        """
        c = self.conn.cursor()
        if insert :
            c.execute("""insert into pyramid_agg_route_perf values 
                     (null, ?, ?, ?, ?, ?, 1)""", (self.session_perf_id,
                                                  self.matched_url,
                                                  self.matched_route_name,
                                                  self.view_name,
                                                  resume_perf,))
        else :
            c.execute("""update pyramid_agg_route_perf
             set measure=%f, fetch_count=fetch_count+1 
                     where id_measure=%d and url='%s'"""%(resume_perf,
                                                   self.session_perf_id,
                                                   self.matched_url))
        c.close()

    def update_mean_view_perf_value(self, resume_perf, insert=False):
        """
        """
        c = self.conn.cursor()
        if insert :
            c.execute("""insert into pyramid_agg_view_perf values 
                     (null, ?, ?, ?, 1)""", (self.session_perf_id,
                                            self.view_name,
                                            resume_perf,))
        else :
            c.execute("""update pyramid_agg_view_perf
             set measure=%f, fetch_count=fetch_count+1 
                     where id_measure=%d and view_name='%s'"""%(resume_perf,
                                                   self.session_perf_id,
                                                   self.view_name))         
        c.close()
        
    def insert_data(self, perf):
        """
        insert the perf data in db
        :param matched_url: the application pyramid url
        :param matched_route_name: the application pyramid matched route name
               if url dispatched si used and request.matched_route is fill
        :param pef: the time measure (should be ms)
        """
        # we forget pyramid_perfstat self routes
        if self.matched_route_name is not None and self.matched_url.count(ROUTE_PREFIX) == 0 :
             c = self.conn.cursor()
             c.execute("""insert into pyramid_perf values 
                          (null, ?, ?, ?, ?, ?, ?)""", (self.session_perf_id,
                                                        self.matched_url,
                                                        self.matched_route_name,
                                                        self.view_name,
                                                        perf,
                                                        datetime.datetime.now(),))
     
             last_record_resume, last_cpt = self.get_last_route_mean_perf()
     
             if last_record_resume is None :
                last_record_resume = perf
                self.update_mean_route_perf_value(last_record_resume, insert=True)
             else :
                last_record_resume = (last_record_resume+(perf/float(last_cpt)))*(float(last_cpt)/float(last_cpt+1))
                self.update_mean_route_perf_value(last_record_resume)
     
             last_record_resume, last_cpt = self.get_last_view_mean_perf()
             if last_record_resume is None :
                last_record_resume = perf
                self.update_mean_view_perf_value(last_record_resume, insert=True)
             else :
                last_record_resume = (last_record_resume+(perf/float(last_cpt)))*(float(last_cpt)/float(last_cpt+1))
                self.update_mean_view_perf_value(last_record_resume)
     
     
             self.conn.commit()
             c.close()

        self.end_connection()
