
def handle(namespace, extra):
    import clutchclient
    vstr = '.'.join(map(str, clutchclient.__version__))
    print 'Clutch Client Version: %s' % (vstr,)