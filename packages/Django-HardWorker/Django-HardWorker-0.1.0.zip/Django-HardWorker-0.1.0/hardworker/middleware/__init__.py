from django.contrib import messages
from hardworker.models import HardJob


class HardJobMiddleware(object):
    """

    """

    def process_request(self, request):
        """

        """
        if request.user.is_authenticated():
            jobs = [j for j in HardJob.objects.filter(owner = request.user, owner_notified = False) if j.finished]
            if jobs:
                finished_jobs = len(jobs)
                if finished_jobs == 1:
                    messages.info(request, "A job is done! (%s/%s)" % (jobs[0].app, jobs[0].worker))
                else:
                    messages.info(request, "%s jobs are done!" % finished_jobs)
                HardJob.objects.filter(id__in = [j.id for j in jobs]).update(owner_notified = True)