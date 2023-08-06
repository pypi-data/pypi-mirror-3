from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from hardworker import get_available_workers
from models import HardJob


def get_status(request):
    """

    """
    jobs = list(HardJob.queue())
    current_job = None
    current_progress = 0
    if jobs and jobs[0].owner == request.user:
        current_job = '%s/%s' % (jobs[0].app, jobs[0].worker)

    return  {
        'your_jobs_in_queue': len([job for job in jobs if job.owner == request.user]),
        'current_progress': current_progress,
        'current_job': current_job,
        'total_jobs_in_queue': len(jobs)
    }


@login_required
def status_view(request):
    """

    """
    return HttpResponse(simplejson.dumps(get_status(request)), mimetype="application/json")


@login_required
def register_view(request, app, worker):
    """

    """
    HardJob.register_job(request.user, app, worker)
    return HttpResponseRedirect(reverse('list-view', args = []))


@login_required
def ajax_register_view(request, app, worker):
    """

    """
    HardJob.register_job(request.user, app, worker)
    return status_view(request)


@login_required
def list_view(request):
    """

    """
    workers = []
    queue = HardJob.queue()
    filtered_queue = [job for job in queue if job.owner == request.user]
    for worker in get_available_workers():
        if worker.get('worker').needs_params:
            continue

        found = False
        for job in filtered_queue:
            found = job.app == worker.get('app') and job.worker == worker.get('name')
            if found:
                break

        if not found:
            workers.append(worker)

    current_job = len(queue) and queue[0] or None

    return render_to_response(
        'hardworker/list_workers.html',
        dict(queue = queue, workers = workers, current_job = current_job),
        context_instance = RequestContext(request))