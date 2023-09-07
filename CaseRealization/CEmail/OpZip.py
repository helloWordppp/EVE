# !/usr/bin/env
# -*- coding=utf-8 -*-
'''
Created on 2015年5月27日

@author: zm
'''
from __future__ import unicode_literals
import logging
import zipfile,os
class OpZip(object):
    '''
    class doc   
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.log=logging.getLogger()
        
    def CreateZip(self,obj_path):
        #obj_path：需要zip的路径
        filelist=[]
        if os.path.isfile(obj_path):
            filelist.append(obj_path)
        else:    
            if os.path.exists(obj_path):
                for root, _, files in os.walk(obj_path):
                    for name in files:
                        filelist.append(os.path.join(root,name))
            else:
                return False
            filename=os.path.basename(obj_path)
            filename=obj_path+"\\"+filename+".zip"
        
        filename=obj_path+".zip"
        if os.path.exists(filename):
            os.remove(filename)
        zf=zipfile.ZipFile(filename,"w",zipfile.zlib.DEFLATED)
        if filename in filelist:
            filelist.remove(filename)
        for tar in filelist:
            arcname=tar[len(obj_path)+1:]
            zf.write(tar,arcname)            
        zf.close()
        return filename
    
    def ExtratZip(self,zipname): 
        zippath=os.path.dirname(zipname)
        zf=zipfile.ZipFile(zipname,"r",zipfile.zlib.DEFLATED)
        for fielitem in zf.namelist():
            fielitem=os.path.join(zippath,fielitem)
            self.extract(zf,fielitem)
              
    def extract(self, zf, fielitem):   
        
        if not fielitem.endswith('\\'):    
            path_dir= os.path.dirname(fielitem)  
            filename=os.path.basename(fielitem)
            if not os.path.exists(path_dir):   
                os.makedirs(path_dir)
            file(fielitem, 'wb').write(zf.read(filename))
if __name__=="__main__":
    myzip=OpZip()
    myzip.ExtratZip(r'c:\test.zip')