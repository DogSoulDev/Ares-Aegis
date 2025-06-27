from antivirus_kali.utils import logger

def test_logger_importable():
    assert hasattr(logger, '__file__') or hasattr(logger, '__doc__')
