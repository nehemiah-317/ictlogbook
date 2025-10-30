import os
import sys

# Ensure repo root (where manage.py lives) is on sys.path so top-level apps are importable
def _ensure_repo_root_on_path():
    # Start from this file's directory and walk up until we find manage.py
    here = os.path.abspath(os.path.dirname(__file__))
    path = here
    while True:
        if os.path.exists(os.path.join(path, 'manage.py')):
            if path not in sys.path:
                sys.path.insert(0, path)
            return
        parent = os.path.dirname(path)
        if parent == path:
            # reached filesystem root, fallback to one level above this package
            fallback = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if fallback not in sys.path:
                sys.path.insert(0, fallback)
            return
        path = parent


_ensure_repo_root_on_path()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thirdyear.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
