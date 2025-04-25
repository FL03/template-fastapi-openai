__name__ = "bftp"
__package__ = "bftp"
__version__ = "0.1.0"

__import__("bftp.api", globals(), locals())
__import__("bftp.core", globals(), locals())
__import__("bftp.data", globals(), locals())

__import__("bftp.agents", globals(), locals())
__import__("bftp.pipes", globals(), locals())

from bftp.app import app
