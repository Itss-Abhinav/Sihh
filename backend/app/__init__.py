import sys
import types

# Synthetic module aliasing so both 'backend.app' and 'app' work seamlessly
if 'backend' not in sys.modules:
    try:
        import backend
    except ImportError:
        _b = types.ModuleType('backend')
        sys.modules['backend'] = _b
        _b.app = sys.modules[__name__]
        sys.modules['backend.app'] = sys.modules[__name__]
