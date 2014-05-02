# -*- coding: utf-8 -*-
from gluon.html import SPAN, FIELDSET, DIV, INPUT, CAT, SELECT, TEXTAREA, LABEL, SCRIPT
import time
import datetime

TASK_STATUS = {
        'QUEUED' : ('#3A87AD', SPAN('QUEUED', _class="label label-info")),
        'RUNNING' : ('#F89406', SPAN('RUNNING', _class="label label-warning")),
        'COMPLETED': ('#468847', SPAN('COMPLETED', _class="label label-success")),
        'FAILED' : ('#B94A48', SPAN('FAILED', _class="label label-important")),
        'STOPPED' : ('#B94A48', SPAN('STOPPED', _class="label label-important")),
        'EXPIRED' : ('#F89406', SPAN('EXPIRED', _class="label label-warning")),
        'ASSIGNED' : ('#FAA732', SPAN('ASSIGNED', _class="label label-warning")),
        }

WORKER_STATUS = {
        'ACTIVE': SPAN("ACTIVE", _class="label label-success"),
        'PICK': SPAN("PICK", _class="label label-info"),
        'DISABLED': SPAN("DISABLED", _class="label label-warning"),
        'TERMINATE': SPAN("TERMINATE", _class="label label-important"),
        'KILL': SPAN("KILL", _class="label label-important")
    }

def nice_worker_status(status):
    if status in WORKER_STATUS:
        return WORKER_STATUS[status]
    else:
        return SPAN(status, _class="label")

def graph_colors_task_status(status):
    if status in TASK_STATUS:
        return TASK_STATUS[status][0]
    else:
        return '#999999'

def nice_task_status(status):

    if status in TASK_STATUS:
        return TASK_STATUS[status][1]
    else:
        return SPAN(status, _class="label")

def mybootstrap(form, fields):
    ''' bootstrap format form layout '''
    form.add_class('form-horizontal')
    parent = FIELDSET()
    for id, label, controls, help in fields:
        # wrappers
        _help = SPAN(help, _class='help-inline')

        if isinstance(controls, (str, int, SPAN)):
            controls = SPAN(controls, _class="input-xlarge uneditable-input")

        # embed _help into _controls
        _controls = DIV(controls, _help, _class='controls')
        # submit unflag by default
        _submit = False



        if isinstance(controls, INPUT):
            controls.add_class('input-xlarge')
            if controls['_type'] == 'submit':
                # flag submit button
                _submit = True
                controls['_class'] = 'btn btn-primary'
            if controls['_type'] == 'file':
                controls['_class'] = 'input-file'

        # For password fields, which are wrapped in a CAT object.
        if isinstance(controls, CAT) and isinstance(controls[0], INPUT):
            controls[0].add_class('input-xlarge')

        if isinstance(controls, SELECT):
            controls.add_class('input-xlarge')

        if isinstance(controls, TEXTAREA):
            controls['_rows'] = 1
            controls.add_class('input-xlarge')

        if isinstance(label, LABEL):
            label['_class'] = 'control-label'

        if _submit:
            # submit button has unwrapped label and controls, different class
            parent.append(DIV(label, controls, _class='form-actions', _id=id))
            # unflag submit (possible side effect)
            _submit = False
        else:
            # unwrapped label
            parent.append(DIV(label, _controls, _class='control-group', _id=id))
    script = SCRIPT("""
    $(function() {
        $('<span class="help-block">' + $('.error_wrapper .error').text() + '</span>').
        appendTo($('.error_wrapper').closest('.controls'));
        $('.error_wrapper').hide().closest('.control-group').addClass('error');
    })""")
    parent.append(script)
    return parent

def requeue_task(st, orig_task):
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
    orig_uuid = orig_uuid[:orig_uuid.rfind(':req_at:')]
    new_task['uuid'] = '%s:req_at:%s' % (orig_uuid, int(time.mktime(datetime.datetime.utcnow().timetuple())))
    rtn = st.validate_and_insert(**new_task)
    if not rtn.errors:
        return rtn.id
    else:
        return None
