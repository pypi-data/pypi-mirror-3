import sys
from django.conf import settings


def get_available_workers():
    """

    """
    result = []
    for app in [app for app in settings.INSTALLED_APPS if not 'django' in app]:
        try:
            for worker in get_workers(app):
                result.append({
                    'app': app,
                    'name': worker.__name__,
                    'worker': worker,
                    'description': worker.description,
                })
        except ImportError:
            pass

    return result


def get_worker_module(app):
    """

    """
    return sys.modules.has_key("%s.workers" % app)\
             and sys.modules["%s.workers" % app] or __import__("%s.workers" % app)


def filter_workers(module, worker = None):
    """

    """
    for item in dir(module):
        f = getattr(module, item)
        if hasattr(f, 'is_hardworker') and (worker == item or worker == None):
            yield f


def get_worker(app, worker = None):
    """

    """
    workers = list(filter_workers(get_worker_module(app), worker))
    return workers and workers[0] or None


def get_workers(app):
    """

    """
    module = get_worker_module(app)
    return filter_workers(module)
