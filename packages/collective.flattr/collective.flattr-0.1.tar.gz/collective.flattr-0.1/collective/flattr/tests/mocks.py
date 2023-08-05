import logging
import urllib2
from StringIO import StringIO


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class MockOpener(object):

    def __init__(self, msg, error=False, verify_data=lambda x: x.get_data() is None):
        self.msg = msg
        self.error = error
        self.verify_data = verify_data

    def open(self, req):
        if not isinstance(req, urllib2.Request):
            raise TypeError
        if not self.verify_data(req):
            raise ValueError
        if self.error:
            raise urllib2.HTTPError('http://example.com', 404,
                'nothing to see', {}, StringIO(self.msg))

        return StringIO(self.msg)
