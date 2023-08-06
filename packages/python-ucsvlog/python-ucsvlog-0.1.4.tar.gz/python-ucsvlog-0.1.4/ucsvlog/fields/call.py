import json
from ucsvlog.utils import unicoder

def full_name(func,fargs,fkwargs,*args,**kwargs):
    return '%s.%s'%(func.__module__,func.__name__)

def func_name(func,fargs,fkwargs,*args,**kwargs):
    return  func.__name__


def args(func,fargs,fkwargs,*args,**kwargs):
    return json.dumps(map(unicoder,fargs))


def kwargs(func,fargs,fkwargs,*args,**kwargs):
    if not fkwargs:
        return '{}'
    ret = ''
    for (fk,fv) in fkwargs.items():
        ret += '\n"'+fk+'":'+json.dumps(unicoder(fv))+','

    return '{'+ret[:-1]+'\n}'



