import cookielib
import urllib2
import urlparse
import logging

from lxml import html
from pyquery import PyQuery

from stanislaw.forms import FormManager

LOG = logging.getLogger("stanislaw.browser")

class Browser(object):
    def __init__(self, debug=False, opener_handlers=[]):
        self.debug = debug
        self.tree = None
        self.current_response = None
        self.current_html = None
        self._pyquery = None
        self.form_manager = FormManager(self)
        self.cookie_jar = cookielib.CookieJar()
        self.opener_handlers = opener_handlers

        if self.debug:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.WARNING)

    def _set_response(self, response):
        self.current_response = response
        self.current_html = response.read()
        self.tree = html.fromstring(self.current_html)
        self._pyquery = PyQuery(self.tree)

    def _get_opener(self):
        cookie_processor = urllib2.HTTPCookieProcessor(self.cookie_jar)
        handlers = [cookie_processor] + self.opener_handlers
        return urllib2.build_opener(*handlers)

    def _open(self, request):
        url = self.get_absolute_url(request.get_full_url())
        abs_request = urllib2.Request(url, request.data, request.headers,
                                      request.origin_req_host,
                                      request.unverifiable)
        opener = self._get_opener()
        self._maybe_log_request(request)
        response = opener.open(abs_request)
        self._set_response(response)

    def _maybe_log_request(self, request):
        if not LOG.isEnabledFor(logging.DEBUG):
            return
        message = "HTTP request: (%s) %s" % (request.get_method(),
                                             request.get_full_url())
        if request.get_method() == "POST":
            message += "\n  POSTDATA: %s" % request.get_data()
        LOG.debug(message)

    def visit(self, url):
        self._open(urllib2.Request(url))

    def fill(self, selector_value_dict):
        return self.form_manager.fill(selector_value_dict)

    def submit(self, form_selector=None):
        request = self.form_manager.get_submit_request(form_selector)
        self._open(request)

    def query(self, selector):
        return self._pyquery(selector)


    def html(self, selector=None):
        if selector is None:
            return self._pyquery.html()

    def get_absolute_url(self, relative_url):
        if self.url is None:
            # Browser not used yet
            return relative_url

        return urlparse.urljoin(self.url, relative_url)

    @property
    def url(self):
        if not self.current_response:
            return None

        return self.current_response.url
