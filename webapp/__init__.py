from __future__ import absolute_import, division, print_function, unicode_literals

import site

from .conf import rel
site.addpackage(rel(), "apps.pth", known_paths=set())
