"""
Tinman Test Application

"""
__author__ = 'Gavin M. Roy'
__email__ = 'gmr@myyearbook.com'
__since__ = '2011-06-06'

import logging
import tinman
from tornado import web

CONFIG = {'Application': {'debug': True,
                          'xsrf_cookies': False},
         'HTTPServer': {'no_keep_alive': False,
                        'ports': [8000],
                        'xheaders': False},
         'Logging': {'filename': 'log.txt',
                     'format': "%(module)-12s# %(lineno)-5d %(levelname) -10s\
%(asctime)s  %(message)s",
                     'level': logging.DEBUG},
         'Routes': [("/", "tinman.test.DefaultHandler")]}


class DefaultHandler(web.RequestHandler):

    def get(self):

        # Send a JSON string for our test
        self.write({"message": "Hello World",
                    "request": {"method": self.request.method,
                                "protocol": self.request.protocol,
                                "path": self.request.path,
                                "query": self.request.query,
                                "remote_ip": self.request.remote_ip,
                                "version": self.request.version},
                    "tinman": {"version":  tinman.__version__}})
