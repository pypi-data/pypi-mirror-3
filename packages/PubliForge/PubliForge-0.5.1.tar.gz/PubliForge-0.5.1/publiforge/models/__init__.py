# $Id: __init__.py 0f769dc832a4 2012/01/16 18:23:12 patrick $
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
VALUE_LEN = 128
ALL_LANG_LIST = ('en', 'fr', 'es')


# =============================================================================
def close_dbsession(request):
    """Call back function to close database session.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    """
    # pylint: disable = I0011, W0613
    DBSession.close()
