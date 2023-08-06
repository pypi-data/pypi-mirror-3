"""
  >>> getRootFolder()['cave'] = cave = Cave()

JSON views answer a special content-type::

  >>> print http('GET /cave/show?callback=jQuery-123 HTTP/1.1')
  HTTP/1.0 200 Ok
  Content-Length: 30
  Content-Type: application/json
  <BLANKLINE>
  jQuery-123("A Cavemans cave");

"""

import grokcore.json as grok
import sw.grokcore.jsonp

class Cave(grok.Context):
    pass

class CaveJSON(sw.grokcore.jsonp.JSONP):
    def show(self):
        return 'A Cavemans cave'
