#
# Copyright John Reid 2009, 2010, 2011
#

"""
Code to choose whether to import debug or release build of stempy module.
"""

import sys, logging

logger = logging.getLogger(__name__)

#
# decide whether to import debug or release stempy C++ extension
#
_python_debug_build = hasattr(sys, "gettotalrefcount") # only available in python debug build
if _python_debug_build:

    logger.info('Loading debug build of STEME C++-python interface')
    from ._debug_build import *
    from ._debug_build import _dummy_fn, _debug, _using_old_bg_model
    from . import _debug_build as S

else:
    
    logger.info('Loading release build of STEME C++-python interface')
    from ._release_build import *
    from ._release_build import _dummy_fn, _debug, _using_old_bg_model, _has_google_profiler
    from . import _release_build as S
    
    if _has_google_profiler:
        from _release_build import __google_profiler_start, __google_profiler_stop
        
logger.info('Loaded STEME C++-python interface from %s', S.__name__)

