import sys
import ConfigParser
import os.path

from Globals import package_home
# Maybe we are in a subpackage , no need for grok utils
try: from collective.z3cform.grok.app_config import GLOBALS
except:pass

UNTESTED_WARNING = """\n
*****************************   WARNING   ************************************
*
* you are testing with FAILS_ON_UNTESTED_ELEMENT setted to False
*
* The only exception to do this is : cath all untested element on one shot !
*
******************************************************************************

"""

cfg_name = "testing.cfg"
# grok context
if 'GLOBALS' in globals():
    DEFAULT_CONFIG_FILE = os.path.join(package_home(GLOBALS), 'tests/', cfg_name)

    def getTestingOptionsFromIni(cfg=DEFAULT_CONFIG_FILE):
        """Get options for testing.

        >>> options = getTestingOptionsFromIni()
        >>> options
        {'TEST_VERBOSE_MODE': True, 'FAILS_ON_UNTESTED_ELEMENT': True}

        """
        Config = ConfigParser.ConfigParser()
        Config.read(cfg)

        return {'FAILS_ON_UNTESTED_ELEMENT':
            Config.getboolean("testing-options", "FAILS_ON_UNTESTED_ELEMENT"),
            'TEST_VERBOSE_MODE':
            Config.getboolean("testing-options", "TEST_VERBOSE_MODE")
            }
    try:
        _options = options = getTestingOptionsFromIni()
        FAILS_ON_UNTESTED_ELEMENT = _options['FAILS_ON_UNTESTED_ELEMENT']  
    except:pass

# if you have plone.reload out there add an helper to use in doctests while programming
# just use preload(module) in pdb :)
# it would be neccessary for you to precise each module to reload, this method is also not recursive.
# eg: (pdb) from foo import bar;preload(bar)
try:
    def preload(modules_or_module, excludelist=None):
        modules = modules_or_module
        if not (isinstance(modules_or_module, list)
                or isinstance(modules_or_module, tuple)):
            modules = [modules_or_module]
        if not excludelist:
            excludelist = []
        import sys
        if not modules:
            modules = sys.modules
        from plone.reload.xreload import Reloader
        print modules
        for module in modules:
            if not module in excludelist:
                try:
                    Reloader(module).reload()
                except Exception, e:
                    pass

except:
    pass


def get_interfaces(o):
    return [o for o in o.__provides__.interfaces()]
try:from zope.interface import implementedBy, providedBy
except:pass

# used on testing
# copied from ZopeLite Class from zope.testingZope.TestCase
# but we can't import it
# if we do we polluate our os.environment and ZopeTestcase usecase detction
def _print(msg):
    '''Writes 'msg' to stderr and flushes the stream.'''
    sys.stderr.write(msg)
    sys.stderr.flush()

if __name__ == "__main__":
    import doctest
    OPTIONS = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS |\
               doctest.NORMALIZE_WHITESPACE
    doctest.testmod(verbose=True, optionflags=OPTIONS)


try:
    import zope
    from zope.traversing.adapters import DefaultTraversable
    zope.component.provideAdapter(DefaultTraversable, [None])
    class Request(zope.publisher.browser.TestRequest):
        def __setitem__(self, name, value):
            self._environ[name] = value
    # alias
    TestRequest = Request
    def make_request(url='http://nohost/@@myview',form=None, *args,  **kwargs):
        r = Request(environ = {'SERVER_URL': url, 'ACTUAL_URL': url}, form=form, *args, **kwargs)
        zope.interface.alsoProvides(r, zope.annotation.interfaces.IAttributeAnnotatable)
        return r
except Exception, e:pass


def pstriplist(s):
    print '\n'.join([a.rstrip() for a in s.split('\n') if a.strip()])










 

