
# Rely on our friends from numpy on the nose tests utils
from numpy.testing import Tester
from safe.version import version as __version__
from safe.version import git_revision as __git_revision__

class SafeTester(Tester):
    def _show_system_info(self):
        print "safe version %s" % __version__
        super(SafeTester, self)._show_system_info()

test = SafeTester().test


