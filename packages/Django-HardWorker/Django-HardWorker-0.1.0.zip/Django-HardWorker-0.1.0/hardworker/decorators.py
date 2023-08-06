

def worker(desc = '', needs_params = False, recurring_timedelta = None):
    """"

    """
    def decorated_worker(worker_func):
        worker_func.is_hardworker = True
        worker_func.needs_params = needs_params
        worker_func.description = desc
        worker_func.recurring_timedelta = recurring_timedelta

        if worker_func.__doc__:
            worker_func.description += worker_func.__doc__

        return worker_func
    return decorated_worker
