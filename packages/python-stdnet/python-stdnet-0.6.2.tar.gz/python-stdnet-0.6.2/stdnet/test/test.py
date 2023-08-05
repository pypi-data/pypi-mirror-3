import os
import sys
import unittest
import logging
from inspect import isclass

from stdnet import orm
from stdnet.utils import to_string


TextTestRunner = unittest.TextTestRunner
TestSuite = unittest.TestSuite

LOGGING_MAP = {1: logging.CRITICAL,
               2: logging.INFO,
               3: logging.DEBUG}


class Silence(logging.Handler):
    def emit(self, record):
        pass


def setup_logging(verbosity):
    logger = logging.getLogger()
    level = LOGGING_MAP.get(verbosity,None)
    if level is None:
        logger.addHandler(Silence())
    else:
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(level)


class TestCase(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        self.orm = orm
        super(TestCase,self).__init__(*args, **kwargs)
        
    def register(self):
        pass
    
    def unregister(self):
        pass
    
    def __call__(self, result=None):
        """Wrapper around default __call__ method
to perform cleanup, registration and unregistration.
        """
        self.register()
        orm.clearall()
        super(TestCase, self).__call__(result)
        self.unregister()
        orm.clearall()
        
    def cleankeys(self, meta):
        tmp = meta.basekey('tmp')
        keys = []
        for key in meta.cursor.keys():
            if not key.startswith(tmp):
                keys.append(key)
        return keys
        

class TestModelBase(TestCase):
    model = None
    
    def register(self):
        self.orm.register(self.model)
        self.meta = self.model._meta
    
    def unregister(self):
        self.orm.unregister(self.model)
        
        
class TestMultiFieldMixin(object):
    '''Test class which add a couple of tests for multi fields. You need to implement the
    get_object_and_field and adddata methods'''
    
    def get_object_and_field(self):
        raise NotImplementedError
    
    def adddata(self, obj):
        raise NotImplementedError
    
    def testMultiFieldId(self):
        '''Here we check for multifield specific stuff like the instance
related keys (keys which are related to the instance rather than the model).'''
        # get instance and field, the field has no data here
        obj, field = self.get_object_and_field()
        # get the object id
        id = to_string(obj.id)
        # get the field database key
        field_key = to_string(field.id)
        self.assertTrue(id in field_key)
        keys = obj.instance_keys()
        # field id should be in instance keys
        self.assertTrue(field.id in keys)
        lkeys = list(obj._meta.cursor.keys())
        # the field has no data, so there is no key in the database
        self.assertFalse(field.id in lkeys)
        #
        # Lets add data
        self.adddata(obj)
        # The field id should be in the server keys
        lkeys = obj._meta.cursor.keys()
        self.assertTrue(field.id in lkeys)
        obj.delete()
        lkeys = list(obj._meta.cursor.keys())
        self.assertFalse(field.id in lkeys)
        

class TestLoader(unittest.TestLoader):
    '''A modified loader class which load test cases form
an interable over modules'''
    testClass = unittest.TestCase
    suiteClass = TestSuite
    
    def loadTestsFromModules(self, modules, itags = None):
        """Return a suite of all tests cases contained in the given module"""
        itags = itags or []
        tests = []
        self.all_tags = all_tags = set()
        self.all_itags = all_itags = set()
        for module,tag in modules:
            all_tags.add(tag)
            for name in dir(module):
                obj = getattr(module, name)
                if (isclass(obj) and issubclass(obj, self.testClass)):
                    tag = getattr(obj,'tag',None)
                    if tag:
                        all_itags.add(tag)
                        if not tag in itags:
                            continue
                    tests.append(self.loadTestsFromTestCase(obj))
        return self.suiteClass(tests)
        

class TestSuiteRunner(object):
    Loader = TestLoader
    
    def __init__(self, verbosity = 1, itags = None):
        self.verbosity = verbosity
        self.itags = itags
        
    def setup_test_environment(self):
        pass
    
    def teardown_test_environment(self):
        pass
    
    def run_tests(self, modules):
        self.setup_test_environment()
        suite = self.build_suite(modules)
        self.run_suite(suite)
    
    def close_tests(self, result):
        self.teardown_test_environment()
        return self.suite_result(suite, result)
    
    def build_suite(self, modules):
        loader = self.Loader()
        return loader.loadTestsFromModules(modules, itags = self.itags)
        
    def run_suite(self, suite):
        return TextTestRunner(verbosity = self.verbosity).run(suite)
    
    def suite_result(self, suite, result, **kwargs):
        return len(result.failures) + len(result.errors) 