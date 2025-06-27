from antivirus_kali.utilidades import logger

def test_logger_importable():
    assert hasattr(logger, '__file__') or hasattr(logger, '__doc__')
