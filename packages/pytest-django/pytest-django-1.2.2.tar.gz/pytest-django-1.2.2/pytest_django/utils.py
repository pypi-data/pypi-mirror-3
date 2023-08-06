from django.db import connections
from django.core.management import call_command

from django.test import TransactionTestCase, TestCase

try:
    from django.test import SimpleTestCase as DjangoBaseTestCase
    DjangoBaseTestCase  # Avoid pyflakes warning about redefinition of import
except ImportError:
    DjangoBaseTestCase = TestCase


def is_django_unittest(item):
    """
    Returns True if the item is a Django test case, otherwise False.
    """

    return hasattr(item.obj, 'im_class') and issubclass(item.obj.im_class, DjangoBaseTestCase)


def get_django_unittest(item):
    """
    Returns a Django unittest instance that can have _pre_setup() or
    _post_teardown() invoked to setup/teardown the database before a test run.
    """
    if 'transaction_test_case' in item.keywords:
        cls = TransactionTestCase
    elif item.config.option.no_db:
        cls = TestCase
        cls._fixture_setup = lambda self: None
    else:
        cls = TestCase

    return cls(methodName='__init__')


def django_setup_item(item):
    if 'transaction_test_case' in item.keywords:
        # Nothing needs to be done
        pass
    else:
        # Use the standard TestCase teardown
        get_django_unittest(item)._pre_setup()


def django_teardown_item(item):

    if 'transaction_test_case' in item.keywords:
        # Flush the database and close database connections
        # Django does this by default *before* each test instead of after
        for db in connections:
            call_command('flush', verbosity=0, interactive=False, database=db)

        for conn in connections.all():
            conn.close()
    else:
        # Use the standard TestCase teardown
        get_django_unittest(item)._post_teardown()
