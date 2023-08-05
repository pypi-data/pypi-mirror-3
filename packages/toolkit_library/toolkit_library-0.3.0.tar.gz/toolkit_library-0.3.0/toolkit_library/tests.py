# coding=utf-8
"""
    toolkit_library.tests
    ~~~~~~~~~~~~~~~~~~~~~
    Unit tests for code quality.
"""
import unittest


from mail_server import MailServer
class MailServerTestCase(unittest.TestCase):
    """Test mail_server.py"""

    def setUp(self):
        """Initiate the smtp mail server"""
        self.server = MailServer(host = 'smtp.gmail.com', port = 587, tls = True, account = 'wendaren.service@gmail.com', password = 'wendaren123')

    def test_send_mail(self):
        """send an email"""
        with self.server:
            self.server.send_mail('tyler4long@gmail.com', 'unittest of python', 'greetings from unittest of python')


from encryption import Encryption
class EncryptionTestCase(unittest.TestCase):
    """Test encryption.py"""

    def setUp(self):
        self.password = '123456'

    def test_generate_password(self):
        """Ensure generated salt and password could authenticate the original password"""
        hashcode, salt = Encryption.generate_hashcode_and_salt(self.password)
        assert Encryption.check_password(self.password, hashcode, salt)

    def test_different_hashcode(self):
        """Ensure everytime a different hashcode is generated. This is for preventing Rainbow-tables cracking"""
        hashcode1 = Encryption.generate_hashcode_and_salt(self.password)[0]
        hashcode2 = Encryption.generate_hashcode_and_salt(self.password)[0]
        assert hashcode1 != hashcode2


from database import Database
from sqlalchemy import Column, Integer, String
class Test:
    """This is an user defined model"""
    __metaclass__ = Database.DefaultMeta
    email = Column(String(70))
class DatabaseTestCase(unittest.TestCase):
    """Test database.py"""
    def setUp(self):
        self.database = Database('mysql://root:wendaren123@localhost/tl_test?charset=utf8')

    def test_basic_query(self):
        """Make sure that the database is available"""
        assert self.database.engine.execute('select 1+1').scalar() == 2

    def test_init_db(self):
        """After initiation of database, there should be one table called 'test'"""
        self.database.create_tables()
        assert self.database.engine.execute('show tables').scalar() == 'test'

    def test_clear_db(self):
        """After clearing the database, there should be no table left"""
        self.database.create_tables()
        self.database.drop_tables()
        assert not self.database.engine.execute('show tables').first()

    def tearDown(self):
        self.database.session.remove()
        self.database.drop_tables()


def greetings(a, b = 'default b'):
    print 'hello', a
    print 'hello', b
import sys
from inspector import ModuleInspector
class InspectorTestCase(unittest.TestCase):
    """Test inspector.py"""
    def test_invoke(self):
        inspector = ModuleInspector(sys.modules[__name__])
        inspector.invoke()
        inspector.invoke('greetings')
        inspector.invoke('greetings', 'aaa')
        inspector.invoke('greetings', 'aaa', 'bbb')
        inspector.invoke(None, 'aaa')
        inspector.invoke(None, 'aaa', 'bbb')
        inspector.invoke(None, 'aaa', 'bbb', 'ccc')


def suite():
    """Which test cases to test"""
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(MailServerTestCase))
    suite.addTest(unittest.makeSuite(EncryptionTestCase))
    suite.addTest(unittest.makeSuite(DatabaseTestCase))
    #suite.addTest(unittest.makeSuite(InspectorTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
