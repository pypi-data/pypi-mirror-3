import os
from tsunami.route import Router

from . import uimodules, uimethods


route = Router(os.path.join(os.path.dirname(__file__),'templates'), uimodules, uimethods)


route.static('/static/', os.path.join(os.path.dirname(__file__),'static'))
route.static('/upload/', 'upload')


from .views import *

