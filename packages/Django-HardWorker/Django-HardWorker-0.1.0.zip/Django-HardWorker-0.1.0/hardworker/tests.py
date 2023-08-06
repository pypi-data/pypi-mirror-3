import sys,imp
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson

from models import HardJob

settings.DEBUG = True

def importCode(code, name, add_to_sys_modules = True):
    """

    """
    module = imp.new_module(name)
    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module

    return module

dynamic_workers_for_test = """
from hardworker.decorators import worker

@worker()
def somefunc(**kwargs):
    print "Just a simple worker"

@worker(needs_params=True)
def paramfunc(**kwargs):
    print "Gosh, I need params to work!"

@worker()
def crashingfunc(**kwargs):
    raise Exception("It all went to hell.")

"""

importCode(dynamic_workers_for_test, "hardworker.workers")

class SimpleTest(TestCase):


    def setUp(self):
        self.username1 = User.objects.create_user('username1', 'fake@example.com', 'password')
        self.username2 = User.objects.create_user('username2', 'fake@example.com', 'password')


    def tearDown(self):
        HardJob.objects.all().delete()


    def test_registration_views(self):
        c1 = Client()
        c1.login(username='username1', password='password')
        c1.post(reverse('register-view', args=['hardworker', 'somefunc']), {})
        self.assertEqual(HardJob.objects.all().count(), 1)
        response = c1.post(reverse('status-view'), {})
        data = simplejson.loads(response.content)
        self.assertEqual(data.get('total_jobs_in_queue'), 1)
        HardJob.look_for_jobs()
        response = c1.post(reverse('status-view'), {})
        data = simplejson.loads(response.content)
        self.assertEqual(data.get('total_jobs_in_queue'), 0)


    def test_status_view(self):
        c1 = Client()
        c2 = Client()
        c1.login(username='username1', password='password')
        c2.login(username='username2', password='password')
        response = c1.post(reverse('ajax-register-view', args=['hardworker', 'somefunc']), {})

        self.assertEqual(simplejson.loads(response.content).get('total_jobs_in_queue'), 1)
        c2.post(reverse('ajax-register-view', args=['hardworker', 'somefunc']), {})

        response = c1.post(reverse('status-view'), {})
        self.assertEqual(simplejson.loads(response.content).get('total_jobs_in_queue'), 2)

        HardJob.look_for_jobs()
        response = c1.post(reverse('status-view'), {})
        self.assertEqual(simplejson.loads(response.content).get('total_jobs_in_queue'), 1)
        self.assertTrue(simplejson.loads(response.content).get('current_job'))

        response = c2.post(reverse('status-view'), {})
        self.assertEqual(simplejson.loads(response.content).get('total_jobs_in_queue'), 1)
        self.assertFalse(simplejson.loads(response.content).get('current_job'))


    def test_exception_logging(self):
        c1 = Client()
        c1.login(username='username1', password='password')
        c1.post(reverse('ajax-register-view', args=['hardworker', 'crashingfunc']), {})
        HardJob.look_for_jobs()
        job = HardJob.objects.all()[0]
        self.assertTrue('failed with exception' in job.log)


    def test_exception_raised_when_calling_func_needing_params(self):
        c1 = Client()
        c1.login(username='username1', password='password')
        c1.post(reverse('ajax-register-view', args=['hardworker', 'paramfunc']), {})
        HardJob.look_for_jobs()
        job = HardJob.objects.all()[0]
        self.assertTrue('failed with exception' in job.log)


    def test_set_progress(self):
        job = HardJob.register_job(self.username1, 'hardworker', 'somefunc')
        self.assertEqual(HardJob.objects.get(id = job.id).progress, 0)
        HardJob.set_progress(job.id, 10)
        self.assertEqual(HardJob.objects.get(id = job.id).progress, 10)
        HardJob.look_for_jobs()
        self.assertEqual(HardJob.objects.get(id = job.id).progress, 100)
