import urlparse
import bucho


default_message = """\
bucho provide below urls:
 * /show
 * /latest_status
 * /all_status
 * /torumemo
"""

def application(environ, start_response):
    split_result = urlparse.urlsplit(environ['PATH_INFO'])
    paths = filter(None, split_result[2].split('/'))
    headers = [('Content-Type', 'text/plain')]
    status = '200 OK'
    result = ''

    if not paths:
        result = default_message
    else:
        method = getattr(bucho, paths[0], None)
        if method is None:
            status = '404 Not Found'
            result = status
        else:
            result = method()

    start_response(status, headers)
    return [result.encode('utf-8')]


def wsgi_app(environ, start_response):
    # BBB (backword compatibility for bucho-0.0.5
    import warnings
    warnings.warn(
            "The bucho.wsgi.wsgi_app function will be removed in bucho-0.2.0. "
            "Use bucho.wsgi.application instead.", DeprecationWarning)
    return application(environ, start_response)


def app_factory(global_config, **local_conf):
    """ wsgi app factory for Paste """
    return application

