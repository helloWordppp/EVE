# -*- coding:utf-8 -*-
from __future__ import unicode_literals

"""
@author:Pengbo
@file:read_ini.py
@className:
@time:2018/9/20 17:16
@function:

"""


import os
import codecs
import re
import chardet

try:
    from collections import OrderedDict as _default_dict
except:
    _default_dict = dict


class ConfigRead(object):
    '''
    class doc
    '''
    def __init__(self, dict_type=_default_dict):
        '''
        Constructor
        '''
        super(ConfigRead, self).__init__()
        #self.log = logging.getLogger()
        self._dict = dict_type
        self._section = self._dict()
        self._section_re = r'\[(.+)\]\Z'

    def GetData(self, filepath):
        if not os.path.isfile(filepath):
            print("file not exist", filepath)
        else:
            detect_dict = chardet.detect(open(filepath, 'rb').read(4096))
            _, encodings = detect_dict['confidence'], detect_dict['encoding']
            with codecs.open(filepath, encoding=encodings) as readfile:
                contentlist = readfile.readlines()
                #print dir(readfile)
                for index,content in enumerate(contentlist):
                    if index == 0 and encodings in ('UTF-16LE', 'UTF-16BE'):
                        content = content[1:]
                    content = content.strip()
                    zhushistr = '#'
                    optstr = '='
                    if content.startswith(zhushistr):
                        continue
                    if re.match(self._section_re,content):
                        self._section[content[1:-1]] = {}
                    elif optstr in content:
                        if self._section:
                            icount = 1
                            opdict = {}
                            option = content.split(optstr)[0].strip()
                            value = ''
                            for index in range(1, len(content.split(optstr))):
                                value += content.split(optstr)[index].strip() + '='
                            value = value.strip('=')
                            while index+icount < len(contentlist)-1:
                                nextvalue = contentlist[index+icount].strip()
                                if optstr not in nextvalue and not re.match(self._section_re,nextvalue):
                                    value += nextvalue
                                    icount += 1
                                else:
                                    break
                            opdict[option] = value
                            sec_key = list(self._section.keys())[len(self._section)-1]
                            self._section[sec_key].update(opdict)
                        else:
                            raise Exception('have no section to use!')
            return encodings

    def sections(self):
        return self._section.keys()

    def options(self, section):
        if not section in self.sections():
            print('section not exist')
        else:
            opt = self._section[section].copy()
        return opt.keys()

    def get(self, section, option):
        try:
            if not section in self.sections():
                if option not in self.options(section):
                    print('option not exist')
                    return None
                print('section not exist')
                return None
            elif option not in self.options(section):
                print('option not exist')
                return None
            else:
                return self._section[section][option]
        except:
            return None

    def set(self, section, option, value):
        if not section in self.sections():
            if option not in self.options(section):
                raise Exception('option not exist')
            raise Exception('section not exist')
        elif option not in self.options(section):
            raise Exception('option not exist')
        else:
            self._section[section][option] = value

    def add_opt(self, section, option):
        if not section in self.sections():
            if option not in self.options(section):
                raise Exception('option not exist')
            raise Exception('section not exist')
        elif option in self.options(section):
            raise Exception('option is exist')
        else:
            self._section[section].update({option: ""})


