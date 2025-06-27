from antivirus_kali.utils import helpers, logger

def test_helpers_module():
    assert hasattr(helpers, '__file__') or hasattr(helpers, '__doc__')

def test_logger_module():
    assert hasattr(logger, '__file__') or hasattr(logger, '__doc__')
