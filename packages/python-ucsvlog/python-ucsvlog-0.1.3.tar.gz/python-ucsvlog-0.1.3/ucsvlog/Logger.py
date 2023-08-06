#!/usr/bin/python
# coding: utf-8
import sys;
import os
import codecs
from datetime import datetime
from ucsvlog.fields import every
from random import randint


from ucsvlog.utils import unicoder, import_name


class Logger(object):
    aindex = '' # time of current branch
    aindex_stack = None # stack of all branches
    func_fields = []
    count_log_fields = 0 # 
    def __init__(self,
                 action_log, #path to log file in file system
                 level=None, # all function or levels which will be logged
                 default_level='log', #function with will be used by default. If object of CSVLogger will be called as function
                 loglev=None, #all available function or levels for logging
                 func_fields=None, # function which will be logged in every log
                 buffering=0,
                 related_folder = None,
                 splitting_blocks = False #block can be splited in couple files
                 ):
        self.splitting_blocks = splitting_blocks
        if related_folder is not None:
            related_folder = os.path.abspath(related_folder)
            if not related_folder.endswith('/'):
                related_folder += '/'

        self.related_folder = related_folder



        self.action_log_template = action_log
        self.action_log_buffering = buffering
        self.action_log_file = None
        self.action_log_fh = None
        
        if loglev is None:
            loglev =   [
                    'crt',#critical error
                    'err',#error
                    'imp',#important information
                    'inf',#information
                    'log',#base log
                    'trc',#trace some data
                    'dbg'#debug information
                    ]
        if level is None:
            level = loglev
        if isinstance(level,int):
            level = loglev[:level]



        if func_fields is None:
            func_fields =  ['stacksize','fname','filename','lineno']
        self.aindex_stack = []
        self.aindex_empty_level = None
        
        
        for logname in loglev:
            if logname in level:
                setattr(self,logname,self.lbd_tlog(logname))
                setattr(self,'a_'+logname,self.lbd_alog('a_'+logname))
                setattr(self,'c_'+logname,self.lbd_clog('c_'+logname))
            else:
                setattr(self,logname,self.lbd_empty_tlog(logname))
                setattr(self,'a_'+logname,self.lbd_empty_alog('a_'+logname))
                setattr(self,'c_'+logname,self.lbd_clog('c_'+logname))

        self.def_log_call = getattr(self,default_level)
        
        self.func_fields = self.arr_lambda_by_name(func_fields, every)

    def __call__(self,a,s=0):
        return self.def_log_call(a,s+1)

    def get_trio_log(self,logname):
        return getattr(self,logname),getattr(self,'a_'+logname),getattr(self,'c_'+logname)

    def action_log_template_params(self):
        now = datetime.now()
        return {
            'year':now.year,
            'syear':unicode(now.year)[2:],
            'month':now.month,
            'day':now.day,
            'hour':now.hour,
            '2_hour':(now.hour/2)*2,
            '3_hour':(now.hour/3)*3,
            '5_hour':(now.hour/5)*5,
            'minute':now.minute,
            '0month': '%0.2d' % now.month,
            '0day': '%0.2d' % now.day,
            '0hour': '%0.2d' % now.hour,

        }

    def init_log_fh(self):
        new_action_log_file = self.action_log_template % self.action_log_template_params()
        if new_action_log_file == self.action_log_file and self.action_log_fh:
            return
        self.action_log_file = new_action_log_file
        self.action_log_fh = codecs.open(self.action_log_file,'a','utf8',buffering=self.action_log_buffering)

    def flush(self):
        self.action_log_fh and self.action_log_fh.flush()


    def arr_lambda_by_name(self,items,mod):
        return map(lambda a:self._lambda_by_name(a, mod),items)
       
    def _lambda_by_name(self,item,mod):
        if isinstance(item, (str,unicode)):
            try:
                item.index('.')
            except ValueError:
                item = getattr(mod, item)
            else:
                item = import_name(item)
        return item

    def lbd_empty_tlog(self,k):
        return lambda a,s=0: None
        
    def lbd_empty_alog(self,k):
        return lambda a,b,s=0: self.short_empty_alog(k,a,b,s+4)
        
    def lbd_tlog(self,k):
        return lambda a,s=0: self.short_tlog(k,a,s+3)
        
    def lbd_alog(self,k):
        return lambda a,b,s=0: self.short_alog(k,a,b,s+4)
        
    def lbd_clog(self,k):
        return lambda a,b,s=0: self.short_clog(k,a,b,s+4)

    def short_tlog(self,k,a,s):
        return self.tlog([k,a],s)

    def short_empty_alog(self,k,a,b,s):
        return self.empty_alog(a,[k,a,b],s)

    def short_alog(self,k,a,b,s):
        return self.alog(a,[k,a,b],s)

    def short_clog(self,k,a,b,s):
        return self.clog(a,[k,a,b],s)

    def clear_one_ceil(self,line):
        return unicoder(line).replace('"','""')
    def clear_one_line(self,data):
        return u'"' + u',"'.join(map(self.clear_one_ceil,data))

    def writerow(self,data):
        self.action_log_fh.write(u'\n'+self.clear_one_line(data))

    def store_row(self,data):
        if self.splitting_blocks:
            self.init_log_fh()
        self.writerow(data)

    def arr_funcs(self,items,*args,**kwargs):
        ret = []
        for item in items:# self.func_fields:
            ret.append(item(*args,**kwargs))
        return ret

    def unpack_params(self,params):
        ret = []
        for item in params:
            if isinstance(item, (tuple,list)):
                ret.extend(self.unpack_params(item))
            else:
                ret.append(item)
        return ret

    def get_append_time(self):
        if not self.aindex_stack:
            return ''
        return self.aindex_stack[-1][0]
    
    def empty_alog(self,*args,**kwargs):
        self.aindex_empty_level = len(self.aindex_stack) + 1
        self.alog(*args,**kwargs)

    def alog(self,search,params,stack=1):
        if not self.splitting_blocks and not self.aindex_stack:
            #init for new blocks only for a new file
            self.init_log_fh()
        data = self.tlog(params,stack)
        self.aindex_stack.append([data[0],search])


    def clog(self,search,params,stack=1):
        remove_length = len(self.aindex_stack)
        finded = False
        for item in reversed(self.aindex_stack):
            if item[1] == search:
                finded = True
                break
            remove_length -= 1
        if finded:
            del self.aindex_stack[remove_length:]
            self.tlog(params,stack)
            self.aindex_stack.pop()
        else:
            #convert to simple log
            self.tlog([params[0].split('_')[1]] + params[1:],stack)
            
        if self.aindex_empty_level and len(self.aindex_stack) < self.aindex_empty_level:
            self.aindex_empty_level = None
        
    
    def get_record_time(self):
        return datetime.now().isoformat()

    def tlog(self,params,stack=1):
        '''
            Write a single line
        '''
        record_key = self.get_record_time()+';'+str(randint(0,100))
        if self.aindex_empty_level:
            return [record_key]
        arr_row = [record_key,self.get_append_time()] +\
                self.arr_funcs(self.func_fields,sys._getframe(stack),self) +\
                self.unpack_params(params)
        self.store_row(arr_row)
        return arr_row


class LineLogger(Logger):
    def tlog(self,params,stack=1):
        record_key = self.get_record_time()+';'+str(randint(0,100))
        arr_row = [record_key,] +\
                self.arr_funcs(self.func_fields,sys._getframe(stack),self) +\
                self.unpack_params(params)
        self.store_row(arr_row)
        return arr_row
