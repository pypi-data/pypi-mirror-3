import zope.app.wsgi


try:
    import psyco
    psyco.profile()
except:
    pass


def application_factory(global_conf):
    zope_conf = global_conf['zope_conf']
    app = zope.app.wsgi.getWSGIApplication(zope_conf)

    def wrapper(environ, start_response):
        vhost = ''
        vhost_skin = environ.get('HTTP_X_VHM_SKIN')
        if vhost_skin and \
           (not environ.get('CONTENT_TYPE', '').startswith('application/json')) and \
           (not environ.get('PATH_INFO', '').startswith('/++skin++')):
            vhost = '/++skin++' + vhost_skin
        vhost_root = environ.get('HTTP_X_VHM_ROOT', '')
        if vhost_root and (vhost_root != '/'):
            vhost += '%s/++vh++%s:%s:%s/++' % (vhost_root,
                                               environ.get('wsgi.url_scheme', 'http'),
                                               environ.get('SERVER_NAME', ''),
                                               environ.get('SERVER_PORT', '80'))
        environ['PATH_INFO'] = vhost + environ['PATH_INFO']
        return app(environ, start_response)

    return wrapper
