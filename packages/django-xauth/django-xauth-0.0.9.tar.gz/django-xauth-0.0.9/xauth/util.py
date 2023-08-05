from urlparse import urljoin

from django.conf import settings

def absolute_url(url):
    "Convert url into absolute (which contains hostname)"

    return urljoin('http://%s' % settings.XAUTH_HOSTNAME, url)


def import_path(path):
    """
    Import the object using given path.

        print import_path('foo.bar.baz')

    equals to:

        import foo.bar
        print bar.baz
    """
    modpath, cls = path.rsplit('.', 1)
    mod = __import__(modpath, globals(), locals(), ['xxx'])
    return getattr(mod, cls)


def get_redirect_url(request, default_url):
    "Extract saved redirect url or use default."

    return request.session.get('xauth_redirect_url') or default_url
