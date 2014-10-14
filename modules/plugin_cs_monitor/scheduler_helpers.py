# -*- coding: utf-8 -*-

import time
import datetime


def requeue_task(st, orig_task, clone=True):
    FCOPY = ['task_name', 'group_name', 'function_name',
             'args', 'vars', 'enabled', 'start_time',
             'stop_time', 'repeats', 'retry_failed',
             'period', 'timeout', 'sync_output',
             'application_name']

    # accomodate for prevent_drift ("backward compatibility")
    if 'prevent_drift' in st.fields:
        FCOPY.append('prevent_drift')

    new_task = {}
    # https://github.com/niphlod/cs_monitor_plugin/issues/9
    # if a task is STOPPED, we need to "reset" stop_time and enabled
    if orig_task.status == 'STOPPED':
        FCOPY.remove('stop_time')
        FCOPY.remove('enabled')

    for f in FCOPY:
        new_task[f] = orig_task[f]
    orig_uuid = orig_task.uuid
    if clone:
        orig_uuid = orig_uuid[:orig_uuid.rfind(':req_at:')]
        new_task['uuid'] = '%s:req_at:%s' % (orig_uuid, int(time.mktime(datetime.datetime.utcnow().timetuple())))
        rtn = st.validate_and_insert(**new_task)
        if not rtn.errors:
            return rtn.id
        else:
            return None
    else:
        new_task['status'] = 'QUEUED'
        rtn = st.validate_and_update(st.uuid == orig_uuid, **new_task)
        if not rtn.errors:
            return orig_task.id
        else:
            return None
