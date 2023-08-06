from virtstrap import plugins
from virtstrap.log import logger

@plugins.create('install', ['after'])
def sample_after_install(event, options, project=None, **kwargs):
    logger.info('This message should appear after everything has installed!')
