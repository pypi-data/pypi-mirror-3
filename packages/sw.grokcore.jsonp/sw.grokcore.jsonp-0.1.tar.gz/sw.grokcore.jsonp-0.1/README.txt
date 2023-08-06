=========================
JSON-P base view for Grok
=========================

This is a base view for Grok, which enables you to make JSON-P calls to your
Grok application. It works nearly the same as the `grokcore.json.JSON` view,
except the fact, that it requires the name of a JavaScript callback in the
request into which it wraps the JSON data returned by your view.

>>> import sw.grokcore.json

>>> class MyView(sw.grokcore.jsonp.JSONP):
...     ...
...     def data(self):
...         return {'foo': 1234}

>>> print http('GET /data?callback=jQuery-123 HTTP/1.1')
HTTP/1.0 200 Ok
Content-Length: 30
Content-Type: application/json
<BLANKLINE>
jQuery-123({'foo': 1234});
