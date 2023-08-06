from builder import E, Element
from urllib2 import urlopen, Request, HTTPError


class BasicSOAP(object):
    class Fault(Exception):
        pass

    def __init__(self, url, ns):
        self.request_NS = ns
        self.endpoint_URL = url

    def _envelope(self):
        return E.soap__Envelope(
            xmlns__xsi = "http://www.w3.org/2001/XMLSchema-instance",
            xmlns__xsd = "http://www.w3.org/2001/XMLSchema",
            xmlns__soap = "http://schemas.xmlsoap.org/soap/envelope/"
        )

    def _header(self):
        return E.soap__Header()

    def _body(self, method, _wrapper='request', _wrap_attrs={}, **kwargs):
        return E.soap__Body()(
            Element(method, xmlns=self.request_NS)
            (
                *(self._body_wrapper(_wrapper, _wrap_attrs))(
                    *(Element(key)(value) for key, value
                    in sorted(kwargs.iteritems()))
                )
            )
        )

    def _body_wrapper(self, tag, attrs):
        if tag is None:
            return lambda *children: children

        return lambda *children: (Element(tag, **attrs)(*children),)

    def _request_xml(self, method, **kwargs):
        return self._envelope()(self._header(), self._body(method, **kwargs))

    def _process_response(self, data, method):
        return data

    def __getattr__(self, method):
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"%s/%s"' % (self.request_NS.rstrip('/'), method)
        }

        def request(**kwargs):
            data = '<?xml version="1.0" encoding="utf-8"?>%s' % self._request_xml(method, **kwargs)
            try:
                # normal operation
                request = Request(self.endpoint_URL, data, headers)
                return self._process_response(urlopen(request).read(), method)
            except HTTPError as e:
                # look body for Fault
                response = e.read()
                if '<soap:Fault>' in response:
                    raise self.Fault(self._process_response(response, method))
                raise
            except:
                # everything else...
                raise
        return request

    def __call__(self, method, **kwargs):
        return self.__getattr__(method)(**kwargs)


try:
    from lxml import etree

    def e2dict(e):
        """Squash everything into dict-o-dicts"""
        return e.tag.rsplit('}', 1)[-1], dict(e2dict(c) for c in e) or e.text

    def strip_ns(tag):
        """Remove Namespace from tag name"""
        return tag.rsplit('}', 1)[-1]

    class LxmlProcessor(object):
        def _result_map(self, envelope):
            """Unpack SOAP response into a sequence of items."""

            for body in envelope:
                for response in body:
                    if strip_ns(response.tag) == 'Fault':
                        for fault in body:
                            for data in fault:
                                yield strip_ns(data.tag), \
                                      data.text and data.text.strip()
                    else:
                        for result in response:
                            for data in result.getchildren() or [result]:
                                yield strip_ns(data.tag),                \
                                      data.text and data.text.strip() or \
                                      [e2dict(item) for item in data]

        def _result_reduce(self, stream):
            """Wrap items into final data"""
            reply = {}
            for tag, value in stream:
                if tag in reply:
                    if not isinstance(reply[tag], list):
                        reply[tag] = [reply[tag]]
                    reply[tag].append(self._result_reduce(value) if isinstance(value, list) else value)
                else:
                    reply[tag] = self._result_reduce(value) if isinstance(value, list) else value
            return reply

        def _process_response(self, data, method):
            """Extract result or failure from SOAP Envelope.

            Output is a dict like this:
            {
                'shallow_key': 'value',
                'deep_key': [{'deep': 'data', {'even': 'deeper'}}, ...]
            }
            """
            reply = self._result_reduce(self._result_map(etree.fromstring(data)))
            return reply.get("%sResult" % method, reply)

    class SOAP(LxmlProcessor, BasicSOAP):
        pass

except ImportError:
    pass
