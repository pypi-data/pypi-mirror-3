import unittest, doctest
import sw.grokcore.jsonp

from grokcore.json.ftests.test_functional import checker, http_call

from pkg_resources import resource_listdir
from zope.app.wsgi.testlayer import BrowserLayer, http

FunctionalLayer = BrowserLayer(sw.grokcore.jsonp)

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'sw.grokcore.jsonp.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            checker=checker,
            extraglobs=dict(http_call=http_call,
                            http=http,
                            getRootFolder=FunctionalLayer.getRootFolder),
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF))
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in ['jsonp']:
        suite.addTest(suiteFromPackage(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

