import sys
def unicoder(line):
    try:
        try:
            return unicode(line)
        except UnicodeDecodeError:
            return str(line).decode('utf-8')
    except Exception,e:
        return u'*** EXCEPTION ***'+str(e)

def import_name(line):
    line = line.split('.')
    mname = '.'.join(line[:-1])
    if mname in sys.modules:
        mname = sys.modules[mname]
    else:
        __import__(mname)
        mname = sys.modules[mname]
    return getattr(mname,line[-1])