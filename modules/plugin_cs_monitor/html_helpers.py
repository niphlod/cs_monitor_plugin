# -*- coding: utf-8 -*-

from gluon.html import SPAN, FIELDSET, DIV, INPUT, TEXTAREA, LABEL, P
from gluon.sqlhtml import FormWidget

TASK_STATUS = {
        'QUEUED' : ('#3A87AD', SPAN('QUEUED', _class="label label-info")),
        'RUNNING' : ('#F89406', SPAN('RUNNING', _class="label label-warning")),
        'COMPLETED': ('#468847', SPAN('COMPLETED', _class="label label-success")),
        'FAILED' : ('#B94A48', SPAN('FAILED', _class="label label-danger")),
        'STOPPED' : ('#B94A48', SPAN('STOPPED', _class="label label-danger")),
        'EXPIRED' : ('#F89406', SPAN('EXPIRED', _class="label label-warning")),
        'ASSIGNED' : ('#FAA732', SPAN('ASSIGNED', _class="label label-warning")),
        'TIMEOUT' : ('#B94A48', SPAN('TIMEOUT', _class="label label-warning")),
        }

WORKER_STATUS = {
        'ACTIVE': SPAN("ACTIVE", _class="label label-success"),
        'PICK': SPAN("PICK", _class="label label-info"),
        'DISABLED': SPAN("DISABLED", _class="label label-warning"),
        'TERMINATE': SPAN("TERMINATE", _class="label label-danger"),
        'KILL': SPAN("KILL", _class="label label-danger")
    }


def nice_worker_status(status):
    if status in WORKER_STATUS:
        return WORKER_STATUS[status]
    else:
        return SPAN(status, _class="label label-default")


def nice_worker_stats(stats):
    collect = []
    if 'errors' in stats:
        collect.append(SPAN("Errors", SPAN(stats['errors'], _class="badge"), _class="list-group-item"))
    if 'total' in stats:
        collect.append(SPAN("Total", SPAN(stats['total'], _class="badge"), _class="list-group-item"))
    if 'sleep' in stats:
        collect.append(SPAN("Sleep", SPAN(stats['sleep'], _class="badge"), _class="list-group-item"))
    if 'empty_runs' in stats:
        collect.append(SPAN("Empty loops", SPAN(stats['empty_runs'], _class="badge"), _class="list-group-item"))
    return DIV(collect, _class="list-group")


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
        _help = None
        if help:
            _help = SPAN(help, _class='help-block')

        if isinstance(controls, (str, int, SPAN)):
            controls = P(controls, _class="form-control-static")

        # submit unflag by default
        _submit = False

        if isinstance(controls, INPUT):
            if controls['_type'] == 'submit':
                # flag submit button
                _submit = True
                controls['_class'] = 'btn btn-primary'
            if controls['_type'] == 'file':
                controls['_class'] = 'input-file'

        if isinstance(label, LABEL):
            label['_class'] = 'col-sm-2 control-label'

        if _submit:
            # submit button has unwrapped label and controls, different class
            parent.append(DIV(DIV(controls,_class="col-sm-offset-2 col-sm-10"),
                _class='form-group form-group-sm', _id=id))
            # unflag submit (possible side effect)
            _submit = False
        else:
            # unwrapped label
            if _help:
                parent.append(DIV(label, DIV(controls, _help, _class="col-sm-10"),
                    _class='form-group form-group-sm', _id=id))
            else:
                parent.append(DIV(label, DIV(controls, _class="col-sm-10"),
                    _class='form-group form-group-sm', _id=id))
    return parent


class BS3StringWidget(FormWidget):
    _class = 'string form-control'

    @classmethod
    def widget(cls, field, value, **attributes):

        default = dict(
            _type='text',
            value=(not value is None and str(value)) or '',
        )
        attr = cls._attributes(field, default, **attributes)

        return INPUT(**attr)


class BS3TextWidget(FormWidget):
    _class = 'text form-control'

    @classmethod
    def widget(cls, field, value, **attributes):

        default = dict(value=value)
        attr = cls._attributes(field, default, **attributes)
        return TEXTAREA(**attr)


class BS3BooleanWidget(FormWidget):
    _class = 'boolean checkbox'

    @classmethod
    def widget(cls, field, value, **attributes):

        default = dict(_type='checkbox', value=value)
        attr = cls._attributes(field, default,
                               **attributes)
        return INPUT(**attr)


class BS3TimeWidget(BS3StringWidget):
    _class = 'time form-control'


class BS3DateWidget(BS3StringWidget):
    _class = 'date form-control'


class BS3DatetimeWidget(BS3StringWidget):
    _class = 'datetime form-control'


class BS3IntegerWidget(BS3StringWidget):
    _class = 'integer form-control'


class BS3DoubleWidget(BS3StringWidget):
    _class = 'double form-control'


class BS3DecimalWidget(BS3StringWidget):
    _class = 'decimal form-control'


def fixup_bs3_widgets(SQLFORM):
    SQLFORM.widgets.string = BS3StringWidget
    SQLFORM.widgets.text = BS3TextWidget
    SQLFORM.widgets.boolean = BS3BooleanWidget
    SQLFORM.widgets.date = BS3DateWidget
    SQLFORM.widgets.time = BS3TimeWidget
    SQLFORM.widgets.datetime = BS3DatetimeWidget
    SQLFORM.widgets.integer = BS3IntegerWidget
    SQLFORM.widgets.double = BS3DoubleWidget
    SQLFORM.widgets.decimal = BS3DecimalWidget
