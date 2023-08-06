import mozlog

logger = mozlog.getLogger("TEST")
logget.setLevel(mozlog.DEBUG)
logger.info('foo')
logger.testPass('bar')
