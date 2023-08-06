import os
import json
from utils.property import cached_property
from utils.exception import Error
from ..account import Account

TEST_ACCOUNTS_FILENAME = 'test_accounts.json'
COMMON_DISCLAIMER = """
Unittests rely on the existence of the file: '%s', and on it having valid credentials at least for the 'default' key.  See %s.example for what this file should look like.  
Unittests are designed to be non-destructive to current data on the account.  
Of course a bug could break that design, but precluding that, you should be able to run these unittests on your webex account without it affecting the current state of things.
""" % ([TEST_ACCOUNTS_FILENAME]*2)

class TestError(Error): pass

class AccountMenu(object):

    def __getitem__(self, key):
        try:
            return Account(**self._accounts_dict[key])
        except KeyError as err:
            msg = "%s doesn't appear to have a 'default' key.  Unittest rely on the creds specified under that key.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()

    @cached_property
    def account(self):
        return self.__getitem__('default')

    @cached_property
    def _accounts_dict(self):
        try:
            raw_text = open(os.path.join(os.path.dirname(__file__), TEST_ACCOUNTS_FILENAME)).read()
        except IOError as err:
            msg = "Unable to open '%s' for integration tests.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()
        try:
            d = json.loads(raw_text)
        except ValueError:
            msg = "'%s' doesn't appear to be valid json!\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()
        return d


