from datetime import datetime
#from django.db.models import Q
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import simplejson
from hardworker import get_worker
from django.utils.timezone import now, get_default_timezone, make_aware


class HardJob(models.Model):
    """

    """
    owner = models.ForeignKey(User)
    app = models.CharField(max_length = 100)
    worker = models.CharField(max_length = 100)
    params = models.TextField(null = True, blank = True)
    registration_date = models.DateTimeField(auto_now = True)
    started =  models.DateTimeField(null = True, blank = True)
    finished = models.DateTimeField(null = True, blank = True)
    log = models.TextField(null = True, blank = True)
    successful = models.NullBooleanField(null = True, blank = True)
    progress = models.PositiveIntegerField(null = True, blank = True, default = 0)
    owner_notified = models.BooleanField(default = False)
    due_date = models.DateTimeField(null = True, blank = True)

    def __unicode__(self):
        return "%s registered %s.%s at %s. Status: %s." % (self.owner.username, self.app, self.worker, self.registration_date, self.successful)

    @classmethod
    def queue(cls):
        """

        """
        return cls.objects.select_related().filter(finished = None).order_by('-registration_date')

    @classmethod
    def register_job(cls, owner, app, worker, params = None, due_date = None):
        """

        """
        return HardJob.objects.create(owner = owner, app = app, worker = worker, params = simplejson.dumps(params), due_date = due_date)

    @classmethod
    def look_for_jobs(cls):
        """

        """
        jobs = list(HardJob.queue())
        if jobs:
            current_job = jobs[0]
            worker = get_worker(current_job.app, current_job.worker)
            if worker:
                HardJob.do_work(current_job, worker)

    @classmethod
    def set_progress(cls, job_id, progress):
        """

        """
        if progress < 0 or progress > 100:
            raise Exception("Invalid value for progress. Must be between 0 and 100. Was %s." % progress)
        HardJob.objects.filter(id = job_id).update(progress = progress)

    @classmethod
    def do_work(cls, job, worker):
        """

        """
        try:
            if settings.DEBUG:
                print "Found work! %s %s %s ..." % (job.owner, job.app, job.worker),
            job.started = now()
            params = {}
            if worker.needs_params:
                if not job.params or job.params == u'null':
                    raise Exception("Worker called without required parameters.")

                params.update(simplejson.loads(job.params))

            params['job_id'] = job.id
            worker(**params)
            job.successful = True
            job.progress = 100
            if settings.DEBUG:
                print "done."

        except Exception, e:
            if settings.DEBUG:
                print "failed with exception: %s!" % e
            job.successful = False
            job.log = "Job failed with exception: %s" % e
        job.finished = now()
        job.save()

        if worker.recurring_timedelta:
            print "recurring", worker.recurring_timedelta
            due_date = datetime.today() + worker.recurring_timedelta
            HardJob.register_job(job.owner, job.app, job.worker, due_date = make_aware(due_date, get_default_timezone()))

