# THIS MUST BE COPIED EXACTLY TO ANY streamcorpus/__init__.py
# See long comment at top of package_globals.py for why.
import os
if os.path.exists(os.path.join(os.path.dirname(__file__), 'package_globals.py')):
    __import__('pkg_resources').declare_namespace(__name__)
    from streamcorpus.package_globals import *
else:
    __import__('pkg_resources').declare_namespace(__name__)

# cleanup namespace, except that it might have already been done
if 'os' in locals().keys():
    del os
