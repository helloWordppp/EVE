# !/usr/bin/env
# -*- coding=utf-8 -*-

'''
Created on 2016年11月29日

@author: pc
'''
from __future__ import unicode_literals

def FuncPrint(func):
    def dectory(*args, **kwargs):
        str_args, str_kwargs = "", ""
        for arg in args[1:]:
            str_args += unicode(arg) + ","
        for kwarg in kwargs:
            str_kwargs += unicode(kwarg) + ":" + unicode(kwargs[kwarg]) + ","
        print func.__doc__
        print "Begin [{0}] function, args:{1} and kwargs:{2}".format(func.__name__, str_args, str_kwargs)
        ret = func(*args, **kwargs)
        print "End ", func.__name__
        return ret
    return dectory