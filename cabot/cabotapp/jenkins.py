from django.conf import settings
from django.utils import timezone

from datetime import datetime
from celery.utils.log import get_task_logger
import requests


logger = get_task_logger(__name__)

if settings.JENKINS_USER:
    auth = (settings.JENKINS_USER, settings.JENKINS_PASS)
else:
    auth = None


def get_job_status(jobname):
    ret = {
        'active': True,
        'succeeded': False,
        'blocked_build_time': None,
        'status_code': 200
    }
    endpoint = settings.JENKINS_API + 'job/%s/api/json' % jobname

    resp = requests.get(endpoint, auth=auth, verify=True)
    resp.raise_for_status()
    status = resp.json()
    ret['status_code'] = resp.status_code
    ret['job_number'] = status['lastBuild'].get('number', None)
    if status['color'].startswith('blue'):
        ret['active'] = True
        ret['succeeded'] = True
    elif status['color'] == 'disabled':
        ret['active'] = False
        ret['succeeded'] = False
    if status['queueItem'] and status['queueItem']['blocked']:
        time_blocked_since = datetime.utcfromtimestamp(
            float(status['queueItem']['inQueueSince']) / 1000).replace(tzinfo=timezone.utc)
        ret['blocked_build_time'] = (timezone.now() - time_blocked_since).total_seconds()
    return ret
