"""cubicweb-narval application package

the Narval agent
"""

try:
    # development version
    import _narvalbot
except ImportError:
    pass
else:
    import sys
    sys.modules['narvalbot'] = _narvalbot
