PYRAMID_PERFSTAT
================

pyramid_perstat application depends on **pyramid** (a light webframework)
see : http://www.pylonsproject.org/ for more information

In fact this application is a pyramid tween
( look at http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/whatsnew-1.2.html?highlight=tween
for more information). It surrounds your webapp in order to measure performance over time.

Pyramid_debugtoolbar is a very good tween to analyze the code and measure the performance of a view. It's very accurate and
it adds a very unique exposure of youre code. Pyramid perfstat try to record each request and its execution time and some other stuff
(average queries count per request etc ...). Thus it can display averages by view or route. This gives you an overview of your
application in order to quickly determine its points of improvement.

For the moment it's only tested with pyramid route dispatch scaffold.

Please feel free to 

             - test it
             - use it
             - enjoy it
             - improve it :)

it's published under BSD licence.

Note :
======

     if you use a previous version of pyramid_perfstat please
     remove perf_app.db before updating pyramid_perfstat.
     0.2 version is incompatible with the structure of the previous base.

     Look at changes for more information.

Requirement :
=============


     - pyramid 1.2>

Usage :
=======

it's have been tested with pythons dependencies of pyramid.

change your development.ini to add this line

development.ini ::

       pyramid.includes = pyramid_perfstat
                          pyramid_tm

instead of usual .ini file

development.ini ::

       pyramid.includes = pyramid_debugtoolbar
                          pyramid_tm

And that's all.  After a few uses of your favorite application,
thank you go to the following URL to see some statistics :

pyramid_perfstat doesn't filter url so feel free to use localhost
or whatever ip:port you're using :

http://localhost:6543/__perfstat/stat

