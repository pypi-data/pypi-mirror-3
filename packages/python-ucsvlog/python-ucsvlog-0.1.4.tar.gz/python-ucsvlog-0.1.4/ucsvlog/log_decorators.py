import functools
from ucsvlog.fields import call

def a_log_call(glog,logsearch='CALL',logname='log',open_func=None,close_func=None,except_func=None):
    #default values

    if close_func is None:
        close_func = []
    close_func = glog.arr_lambda_by_name(close_func, call)

    if except_func is None:
        except_func = []
    except_func = glog.arr_lambda_by_name(except_func, call)

    if open_func is None:
        open_func = ['full_name','args','kwargs']
    open_func = glog.arr_lambda_by_name(open_func, call)


    log_func, a_log_func, c_log_func = glog.get_trio_log(logname) 
    def render(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            a_log_func(logsearch,glog.arr_funcs(open_func,func,args,kwargs))
            try:
                ret = func(*args,**kwargs)
            except Exception,e:
                c_log_func(logsearch,glog.arr_funcs(except_func,func,args,kwargs,e))
                raise
            else:
                c_log_func(logsearch,glog.arr_funcs(close_func,func,args,kwargs,ret))
                return ret
        return wrapper
    return render



