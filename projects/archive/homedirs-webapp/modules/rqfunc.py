#!/usr/bin/env python

import os
import redis
import pickle
import subprocess

from rq.decorators import job
from rq.compat import as_text, decode_redis_hash, string_types, text_type
from rq.utils import utcparse
from rq.exceptions import UnpickleError

redis_conn = redis.Redis(db=2)


@job('filemover', connection=redis_conn, result_ttl=864000, timeout=3600)
def run_filemover_cmd(cmd):
    '''
    Run a command on the system
    Returns: stdout, stderr
    '''
    child = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return child.communicate()


@job('getsize', connection=redis_conn, result_ttl=300)
def get_size(start_path):
    '''
    Gets the size of all files within a specified directory.
    Size is returned as a number in bytes.
    '''
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_all_jobs(queue = None):
    '''
    The RQ library apparently doesn't let you pull all finished jobs, so we get
    to recreate this from scratch. Maybe we should use celery?
    This is pretty much a ripoff of what RQ does for queued jobs, recreated so
    that we can grab ALL jobs.
    '''
    def to_date(date_str):
        if date_str is None:
            return
        else:
            return utcparse(as_text(date_str))


    def unpickle(pickled_string):
        try:
            obj = pickle.loads(pickled_string)
        except Exception as e:
            raise UnpickleError('Could not unpickle.', pickled_string, e)
        return obj


    job_ids = redis_conn.keys('rq:job:*')
    jobs = {}

    for job_id in job_ids:
        obj = decode_redis_hash(redis_conn.hgetall(job_id))
        if len(obj) == 0:
            pass
        if queue is not None:
            if queue != as_text(obj.get('origin')):
                # If a specific queue was requested and this job isn't it, don't
                # process the details of this job and don't return the job.
                continue
        jobs[job_id] = {
            'job_id': job_id.replace('rq:job:', ''),
            'created_at': obj.get('created_at'),
            'origin': as_text(obj.get('origin')),
            'description': as_text(obj.get('description')),
            'enqueued_at': to_date(as_text(obj.get('enqueued_at'))),
            'ended_at': to_date(as_text(obj.get('ended_at'))),
            'result': unpickle(obj.get('result')) if obj.get('result') else None,  # noqa
            'exc_info': obj.get('exc_info'),
            'timeout': int(obj.get('timeout')) if obj.get('timeout') else None,
            'result_ttl': int(obj.get('result_ttl')) if obj.get('result_ttl') else None,  # noqa
            'status': as_text(obj.get('status') if obj.get('status') else None),
            'dependency_id': as_text(obj.get('dependency_id', None)),
            'meta': unpickle(obj.get('meta')) if obj.get('meta') else {}}
        if jobs[job_id]['status'] == 'finished':
            jobs[job_id]['color'] = '#008000'
        elif jobs[job_id]['status'] == 'started':
            jobs[job_id]['color'] = '#A79600'
        elif jobs[job_id]['status'] == 'queued':
            jobs[job_id]['color'] = '#A79600'
        elif jobs[job_id]['status'] == 'failed':
            jobs[job_id]['color'] = '#FF0000'
        else:
            jobs[job_id]['color'] = '#000000'
        if jobs[job_id]['result']:
            if type(jobs[job_id]['result']) == tuple:
                if jobs[job_id]['result'][1] != '':
                    jobs[job_id]['color'] = '#FF0000'
                    jobs[job_id]['code'] = 'F'
                else:
                    jobs[job_id]['code'] = 'S'
        else:
            jobs[job_id]['code'] = 'P'

    return jobs
