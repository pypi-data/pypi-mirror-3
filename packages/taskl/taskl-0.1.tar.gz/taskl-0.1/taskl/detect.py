import requests
from api.redmine import Redmine

REDMINE = 'Powered by <a href="http://www.redmine.org/">Redmine</a>'

def detect_api(url):
    resp = requests.get(url, verify=False)

    if REDMINE in resp.content:
        return 'redmine'

def api(impl, **kw):
    if impl == 'redmine':
        return Redmine(**kw)
    assert False, 'oops wtf is %s' % api
