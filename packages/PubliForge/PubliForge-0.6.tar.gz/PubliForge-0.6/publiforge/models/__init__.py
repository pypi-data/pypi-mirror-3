# $Id: __init__.py 64955b6d4569 2012/05/23 20:20:45 patrick $
# pylint: disable = I0011, C0103
"""Here are defined database main objects and constants."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

ID_LEN = 32
LABEL_LEN = 64
DESCRIPTION_LEN = 255
PATH_LEN = 255
VALUE_LEN = 255
ALL_LANG_LIST = ('en', 'fr', 'es')


# =============================================================================
def close_dbsession(request):
    """Call back function to close database session.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    """
    # pylint: disable = I0011, W0613
    DBSession.close()
