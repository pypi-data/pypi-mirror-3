#!/usr/bin/python
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------
# Name:        pyramid_perfstat/perf_serializer.py
# Purpose:     serialize recorded data inside a db
#              for the moment only sqlite db is supported ...
#
#              this module don't use sqlalchemy or ORM to keep 
#              performance as best as possible. SqlAlchemy would
#              bring confort and will decrease performance as well...
#              pyramid_perfstat try to be as light as possible
#              
#              (even if sql is boring ...  :'( )
#
#              to reduce overhead :
#                    - no object
#                    - procedural code
#                    - simple sql query
#
#              TODO : add some configuration key to change default db
#              TODO : add interface for serialization
#              TODO : write other db target
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
import sqlite3
import time
import threading

from zope.interface import Interface

from pyramid.events import subscriber
from pyramid.events import NewRequest

from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IView

from pyramid.threadlocal import get_current_request
from pyramid_perfstat.utils import ROUTE_PREFIX
from sqlalchemy.ext.sqlsoup import SqlSoup

lock = threading.Lock()

try:
    from sqlalchemy import event
    from sqlalchemy.engine.base import Engine

    @event.listens_for(Engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, stmt, params, context, execmany):
        setattr(conn, 'pfstb_start_timer', time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
        stop_timer = time.time()
        request = get_current_request()
        duration = stop_timer - conn.pfstb_start_timer
        if request is not None:
            with lock:
                duration_queries = getattr(request, 'pfstb_duration_queries', [])
                duration_queries.append(duration)
                setattr(request, 'pfstb_duration_queries', duration_queries)
        delattr(conn, 'pfstb_start_timer')
    has_sqla = True
except ImportError:
    has_sqla = False

@subscriber(NewRequest)
def new_perfstat_request_subscriber(event):
    """
    open the connection to sqlite db
    subscribe to event NewRequest
    """
    request = event.request
    request._PerfDbManager__perfstat_db = sqlite3.connect('perf_app.db')
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    """
    close the connection to sqlite db
    """
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
        
        self.request = request

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
                                                               sql_avg_duration real,
                                                               sql_nb_queries integer,
                                                               date_measure datetime )""")

        c.execute("""create index if not exists idx_url on pyramid_perf (url)""")
        c.execute("""create index if not exists idx_route on pyramid_perf (route_name)""")
        c.execute("""create index if not exists idx_view on pyramid_perf (view_name)""")

        if from_scratch :
            c.execute("""drop table if exists pyramid_agg_route_perf""")
            
        c.execute("""create table if not exists pyramid_agg_route_perf ( id integer PRIMARY KEY,
                                                               id_measure integer,
                                                               route_name text,
                                                               view_name text,
                                                               measure real,
                                                               sql_avg_duration real,
                                                               sql_nb_queries integer,
                                                               fetch_count integer )""")

        c.execute("""create index if not exists idx_url on pyramid_agg_route_perf (url)""")
        c.execute("""create index if not exists idx_route on pyramid_agg_route_perf (route_name)""")
        c.execute("""create index if not exists idx_view on pyramid_agg_route_perf (view_name)""")

        if from_scratch :
            c.execute("""drop table if exists pyramid_agg_view_perf""")
            
        c.execute("""create table if not exists pyramid_agg_view_perf ( id integer PRIMARY KEY,
                                                               id_measure integer,
                                                               view_name text,
                                                               measure real,
                                                               sql_avg_duration real,
                                                               sql_nb_queries integer,
                                                               fetch_count integer )""")
        c.execute("""create index if not exists idx_view on pyramid_agg_view_perf (view_name)""")

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
        c.execute("""select pr.id, pr.measure, pr.sql_avg_duration, pr.sql_nb_queries, pr.url from pyramid_perf pr
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
        c.execute("""select pr.id, pv.id, pr.measure, pr.sql_avg_duration, pr.sql_nb_queries,
                            pr.route_name, pr.view_name, pr.fetch_count
                     from pyramid_agg_route_perf pr
                     join pyramid_agg_view_perf pv on pv.id=%d and pr.view_name=pv.view_name
                     where pr.id_measure=%d order by pr.measure desc, pr.fetch_count desc"""%(id_view,id_measure))
        rows = c.fetchall()
        c.close()
        return rows 

    def get_view_measure_summary_liste(self, id_measure):
        """
        return measure liste
        :param id_measure: the session id
        """
        c = self.conn.cursor()
        c.execute("""select id, measure, sql_avg_duration, sql_nb_queries, view_name, fetch_count 
                     from pyramid_agg_view_perf 
                     where id_measure=%d
                     order by measure desc, fetch_count desc, view_name desc"""%id_measure)
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
          return last values inserted in pyramid_agg_route_perf
        """
        c = self.conn.cursor()
        c.execute("""select measure, sql_avg_duration, sql_nb_queries, fetch_count from pyramid_agg_route_perf 
                    where id_measure=%d and route_name='%s'"""%(self.session_perf_id, self.matched_route_name))
        rows = c.fetchall()
        measure, sql_avg_duration, sql_nb_queries, fetch_count = None, None, None, None
        if rows :
           measure, sql_avg_duration, sql_nb_queries, fetch_count = rows[0]
        c.close()
        return measure, sql_avg_duration, sql_nb_queries, fetch_count

    def get_last_view_mean_perf(self):
        """
          return last value inserted in pyramid_agg_route_perf
        """
        c = self.conn.cursor()
        c.execute("""select measure, sql_avg_duration, sql_nb_queries, fetch_count from pyramid_agg_view_perf 
                    where id_measure=%d and view_name='%s'"""%(self.session_perf_id, self.view_name))
        rows = c.fetchall()
        measure, sql_avg_duration, sql_nb_queries, fetch_count = None, None, None, None
        if rows :
           measure, sql_avg_duration, sql_nb_queries, fetch_count = rows[0]
        c.close()
        return measure, sql_avg_duration, sql_nb_queries, fetch_count

    def update_mean_route(self, request_duration_time, sql_sigma_duration, sql_nb_queries):
        """
        """
        last_record_resume, last_sql_avg_duration, last_sql_nb_queries, last_cpt = self.get_last_route_mean_perf()
        new_record_resume = self.cumulative_upkeep(last_record_resume, last_cpt, request_duration_time)
        
        new_sql_sigma_duration = 0.0
        new_sql_nb_queries = 0
        if sql_sigma_duration is not None :
            new_sql_sigma_duration = self.cumulative_upkeep(last_sql_avg_duration, last_cpt, sql_sigma_duration)
            new_sql_nb_queries = int(round(self.cumulative_upkeep(last_sql_nb_queries, last_cpt, sql_nb_queries)))
        if last_record_resume is None :
            self.update_mean_route_perf_value(new_record_resume, new_sql_sigma_duration, new_sql_nb_queries, insert=True)
        else :
            self.update_mean_route_perf_value(new_record_resume, new_sql_sigma_duration, new_sql_nb_queries)

    def update_mean_route_perf_value(self, resume_perf, sql_resume_perf, sql_nb_queries, insert=False):
        """
        :resume_perf: the average to request time duration
        :sql_resume_perf: the average to sql time duration
        :sql_nb_queries: the number of queries occured during view call
        :key-param insert: this key-word indicate we should insert or update
        """
        c = self.conn.cursor()
        if insert :
            c.execute("""insert into pyramid_agg_route_perf values 
                     (null, ?, ?, ?, ?, ?, ?, 1)""", (self.session_perf_id,
                                                      self.matched_route_name,
                                                      self.view_name,
                                                      resume_perf,
                                                      sql_resume_perf,
                                                      sql_nb_queries))
        else :
            c.execute("""update pyramid_agg_route_perf
             set measure=%f, sql_avg_duration=%f, sql_nb_queries=%d, fetch_count=fetch_count+1 
                     where id_measure=%d and route_name='%s'"""%(resume_perf,
                                                   sql_resume_perf,
                                                   sql_nb_queries,
                                                   self.session_perf_id,
                                                   self.matched_route_name))
        c.close()

    def update_mean_view(self, request_duration_time, sql_sigma_duration, sql_nb_queries):
        """
        update the average time table for view resume
        
        :param request_duration_time: 
        :param sql_sigma_duration:
        :param sql_nb_queries:
        """
        last_record_resume, last_sql_avg_duration, last_sql_nb_queries, last_cpt = self.get_last_view_mean_perf()
        new_avg_resume = self.cumulative_upkeep(last_record_resume, last_cpt, request_duration_time)
        new_sql_sigma_duration = 0.0
        new_sql_nb_queries = 0
        
        if sql_sigma_duration is not None :
            new_sql_sigma_duration = self.cumulative_upkeep(last_sql_avg_duration, last_cpt, sql_sigma_duration)
            new_sql_nb_queries = int(round(self.cumulative_upkeep(last_sql_nb_queries, last_cpt, sql_nb_queries)))
        
        if last_record_resume is None :
            self.update_mean_view_perf_value(new_avg_resume, new_sql_sigma_duration, new_sql_nb_queries, insert=True)
        else :
            self.update_mean_view_perf_value(new_avg_resume, new_sql_sigma_duration, new_sql_nb_queries)
        

    def update_mean_view_perf_value(self, request_time_avg, sql_resume_perf, sql_nb_queries, insert=False):
        """
           update every recorded params linked to the current view
           :request_time_avg:
           :sql_resume_perf:
           :sql_nb_queries:
           :insert: boolean
        """
        c = self.conn.cursor()
        if insert :
            c.execute("""insert into pyramid_agg_view_perf values 
                     (null, ?, ?, ?, ?, ?, 1)""", (self.session_perf_id,
                                                   self.view_name,
                                                   request_time_avg,
                                                   sql_resume_perf,
                                                   sql_nb_queries))
        else :
            c.execute("""update pyramid_agg_view_perf
             set measure=%f, sql_avg_duration=%f, sql_nb_queries=%d, fetch_count=fetch_count+1 
                     where id_measure=%d and view_name='%s'"""%(request_time_avg,
                                                                sql_resume_perf,
                                                                sql_nb_queries,
                                                                self.session_perf_id,
                                                                self.view_name))
        c.close()
    
    def cumulative_upkeep(self, last_resume, last_cpt, perf):
        """
        :param last_resume: the last recorded average
        :param last_cpt: last average number of elements having served for the calculation
        :param perf: new record
        """
        result = None
        if last_resume is None :
           result = perf
        else :
           result = (last_resume+(perf/float(last_cpt)))*(float(last_cpt)/float(last_cpt+1))
        return result
    
    def get_queries_information(self):
        """
        if sql alchemy is know. we can return sql query sigma time execution
        :param return :
              sql_sigma_duration : sum duration of every sql request executed during the request
              sql_nb_queries : the number of queries executed in the request
        """
        sql_sigma_duration, sql_nb_queries = None, None
        
        if self.request is not None and has_sqla and hasattr(self.request,'pfstb_duration_queries') :
              duration_queries_liste = self.request.pfstb_duration_queries
              # sum duration of every sql request executed during the request
              sql_sigma_duration = sum(duration_queries_liste)
              # the number of queries executed in the request
              sql_nb_queries = len(duration_queries_liste)

        return sql_sigma_duration, sql_nb_queries
    
    def insert_data(self, request_duration_time):
        """
        insert all recorded data in db
        :param request_duration_time: the request time duration
        """
        
        sql_sigma_duration, sql_nb_queries = self.get_queries_information()

        # we forget pyramid_perfstat self routes
        if self.matched_route_name is not None and self.matched_url.count(ROUTE_PREFIX) == 0 :
             c = self.conn.cursor()
             c.execute("""insert into pyramid_perf values 
                          (null, ?, ?, ?, ?, ?, ?, ?, ?)""", (self.session_perf_id,
                                                             self.matched_url,
                                                             self.matched_route_name,
                                                             self.view_name,
                                                             request_duration_time,
                                                             sql_sigma_duration,
                                                             sql_nb_queries,
                                                             datetime.datetime.now(),))
     
             # update specific view table
             self.update_mean_view(request_duration_time, sql_sigma_duration, sql_nb_queries)
             
             # update specific route table 
             self.update_mean_route(request_duration_time, sql_sigma_duration, sql_nb_queries)
             
             self.conn.commit()
             c.close()

        self.end_connection()
