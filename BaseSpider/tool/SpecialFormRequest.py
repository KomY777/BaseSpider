"""
This module implements the FormRequest class which is a more convenient class
(than Request) to generate Requests based on form data.

See documentation in docs/topics/request-response.rst
"""

import six
from six.moves.urllib.parse import urljoin, urlencode
from scrapy.http.request import Request


class SpecialForm(Request):
    valid_form_methods = ['GET', 'POST']

    def __init__(self, *args, **kwargs):
        flag = False
        formdata = kwargs.pop('formdata', None)
        if kwargs.pop("special", None):
            flag = True
        if formdata and kwargs.get('method') is None:
            kwargs['method'] = 'POST'

        super(SpecialForm, self).__init__(*args, **kwargs)

        if formdata:
            items = formdata.items() if isinstance(formdata, dict) else formdata

            if flag:
                querystr = urlencode(formdata).split("special=")[1]
            if self.method == 'POST':
                self.headers.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
                self._set_body(querystr)
            else:
                self._set_url(self.url + ('&' if '?' in self.url else '?') + querystr)
