from twisted.trial import unittest

import os

import mock

from darcsver import darcsvermodule

samplexml1="<changelog> <patch author='zooko@zooko.com' date='20100801031436' local_date='Sat Jul 31 21:14:36 MDT 2010' inverted='False' hash='20100801031436-92b7f-aed5e3393a2c66c394b701d2706dc966c23cba6f.gz'> <name>TAG darcsver-9.9.9</name> <comment>Ignore-this: 9fadfa5ad8e825f893d902bbe832560a</comment> </patch> <patch author='zooko@zooko.com' date='20071230025146' local_date='Sat Dec 29 19:51:46 MST 2007' inverted='False' hash='20071230025146-92b7f-383299bb445c8dcf82559d1613d0c385148fcbf4.gz'> <name>darcsver: init import of darcsver from pyutil-1.3.12-4</name> </patch> </changelog>"

samplexml2="<changelog> <patch author='zooko@zooko.com' date='20100801031436' local_date='Sat Jul 31 21:14:36 MDT 2010' inverted='False' hash='20100801031436-92b7f-aed5e3393a2c66c394b701d2706dc966c23cba6f.gz'> <name>TAG darcsver-9.9.9rc9</name> <comment>Ignore-this: 9fadfa5ad8e825f893d902bbe832560a</comment> </patch> <patch author='zooko@zooko.com' date='20071230025146' local_date='Sat Dec 29 19:51:46 MST 2007' inverted='False' hash='20071230025146-92b7f-383299bb445c8dcf82559d1613d0c385148fcbf4.gz'> <name>darcsver: init import of darcsver from pyutil-1.3.12-4</name> </patch> </changelog>"

samplexml3="<changelog> <patch author='zooko@zooko.com' date='20100801031436' local_date='Sat Jul 31 21:14:36 MDT 2010' inverted='False' hash='20100801031436-92b7f-aed5e3393a2c66c394b701d2706dc966c23cba6f.gz'> <name>TAG darcsver-9.9.9c9</name> <comment>Ignore-this: 9fadfa5ad8e825f893d902bbe832560a</comment> </patch> <patch author='zooko@zooko.com' date='20071230025146' local_date='Sat Dec 29 19:51:46 MST 2007' inverted='False' hash='20071230025146-92b7f-383299bb445c8dcf82559d1613d0c385148fcbf4.gz'> <name>darcsver: init import of darcsver from pyutil-1.3.12-4</name> </patch> </changelog>"

class T(unittest.TestCase):
    @mock.patch('subprocess.Popen')
    def _help_test(self, mockPopen, samplexml):
        mockpopobj = mock.Mock()
        def communicate():
            return (samplexml, '')
        mockpopobj.communicate = communicate
        mockpopobj.returncode = 0
        mockPopen.return_value = mockpopobj

        try:
            os.remove('tmpfilefname')
        except OSError:
            pass
        return darcsvermodule.update('darcsver', 'tmpfilefname', revision_number=True)

    def test_basic_pyutil(self):
        try:
            from pyutil import version_class
            version_class.VERSION_BASE_RE_STR
        except (ImportError, AttributeError):
            raise unittest.SkipTest('need pyutil to test this')

        res = self._help_test(samplexml=samplexml1)
        self.failUnlessEqual(res[1], '9.9.9')

    def test_rc_pyutil(self):
        try:
            from pyutil import version_class
            version_class.VERSION_BASE_RE_STR
        except (ImportError, AttributeError):
            raise unittest.SkipTest('need pyutil to test this')

        res = self._help_test(samplexml=samplexml2)
        self.failUnlessEqual(res[1], None, str(res))

    def test_c_pyutil(self):
        try:
            from pyutil import version_class
            version_class.VERSION_BASE_RE_STR
        except (ImportError, AttributeError):
            raise unittest.SkipTest('need pyutil to test this')

        res = self._help_test(samplexml=samplexml3)
        self.failUnlessEqual(res[1], '9.9.9c9', str(res))

    def test_basic_no_pyutil(self):
        origVBRS = darcsvermodule.VERSION_BASE_RE_STR
        darcsvermodule.VERSION_BASE_RE_STR=darcsvermodule.OUR_VERSION_BASE_RE_STR
        try:
            res = self._help_test(samplexml=samplexml1)
            self.failUnlessEqual(res[1], '9.9.9')
        finally:
            darcsvermodule.VERSION_BASE_RE_STR=origVBRS

    def test_rc_no_pyutil(self):
        origVBRS = darcsvermodule.VERSION_BASE_RE_STR
        darcsvermodule.VERSION_BASE_RE_STR=darcsvermodule.OUR_VERSION_BASE_RE_STR
        try:
            res = self._help_test(samplexml=samplexml2)
            self.failUnlessEqual(res[1], None, str(res))
        finally:
            darcsvermodule.VERSION_BASE_RE_STR=origVBRS

    def test_c_no_pyutil(self):
        origVBRS = darcsvermodule.VERSION_BASE_RE_STR
        darcsvermodule.VERSION_BASE_RE_STR=darcsvermodule.OUR_VERSION_BASE_RE_STR
        try:
            res = self._help_test(samplexml=samplexml3)
            self.failUnlessEqual(res[1], '9.9.9c9', str(res))
        finally:
            darcsvermodule.VERSION_BASE_RE_STR=origVBRS
