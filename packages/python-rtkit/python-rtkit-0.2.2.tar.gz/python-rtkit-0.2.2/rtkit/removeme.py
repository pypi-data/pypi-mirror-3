from rtkit.resource import RTResource
from rtkit.authenticators import BasicAuthenticator
from rtkit.errors import RTResourceError

from rtkit import set_logging
import logging
set_logging('debug')
logger = logging.getLogger('rtkit')

resource = RTResource('https://support.dada.net/REST/1.0/', 'ademarco', '!', BasicAuthenticator)

try:
    response = resource.get(path="search/ticket?orderby=%2Bid&query=(Status+%3D+'open'+OR+Status+%3D+'new'+OR+Status+%3D+'stalled')+AND+(Queue+%3D+'qaupdate')&format=s")
    for r in response.parsed:
        for t in r:
            logger.info(t)
except RTResourceError as e:
    logger.error(e.response.status_int)
    logger.error(e.response.status)
    logger.error(e.response.parsed)