# coding: utf8
from datetime import timedelta as timed
import datetime
from gluon.storage import Storage
from gluon import current
from gluon.serializers import json as dumps
from plugin_cs_monitor.admin_scheduler_helpers import nice_worker_status, graph_colors_task_status, nice_task_status, mybootstrap, requeue_task

response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/jquery.jqplot.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/jquery.jqplot.min.css'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.barRenderer.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.pieRenderer.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.dateAxisRenderer.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.pointLabels.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.cursor.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.enhancedLegendRenderer.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.highlighter.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.canvasTextRenderer.min.js'))
response.files.append(URL('static', 'plugin_cs_monitor/js/jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js'))

##Configure start
sc_cache = cache.ram
##Configure end

s = current._scheduler
dbs = s.db
st = dbs.scheduler_task
sw = dbs.scheduler_worker
sr = dbs.scheduler_run

response.meta.author = 'Niphlod <niphlod@gmail.com>'
response.title = 'ComfortScheduler Monitor'
response.subtitle = '0.0.1'
response.static_version = '0.0.1'

try:
    response.menu.append(
        ('Comfy Scheduler Monitor', False, URL('plugin_cs_monitor', 'index'), []),
    )
except:
    pass

@auth.requires_login()
def index():

    return dict()

@auth.requires_signature()
def workers():
    now = s.utc_time and request.utcnow or request.now
    limit = now - timed(seconds=s.heartbeat * 3 * 10)
    w = dbs(sw.id > 0).select(orderby=~sw.id)
    for row in w:
        if row.last_heartbeat < limit:
            row.status_ = nice_worker_status('Probably Dead')
        else:
            row.status_ = nice_worker_status(row.status)

    BASEURL = URL("plugin_cs_monitor", "wactions", user_signature=True)

    return dict(w=w, BASEURL=BASEURL, limit=limit)


@auth.requires_signature()
def wactions():
    default = URL('workers', user_signature=True)
    if not request.vars.action or request.vars.action == 'none':
        session.flash = "No action selected"
        redirect(default)
    if not request.vars.w_records:
        session.flash = "No worker selected"
        redirect(default)
    if isinstance(request.vars.w_records, str):
        r = [request.vars.w_records]
    else:
        r = request.vars.w_records
    rtn = dbs(sw.id.belongs(r)).validate_and_update(status=request.vars.action)
    if rtn.errors:
        session.flash = "Not a valid action"
    elif rtn.updated:
        session.flash = "%s workers updated correctly" % rtn.updated
        redirect(default)

@auth.requires_signature()
def tactions():
    default = request.vars.current_page or URL('task_group', user_signature=True)
    action = request.vars.action
    if not action or action == 'none':
        session.flash = "No action selected"
        redirect(default)
    if not request.vars.t_records:
        session.flash = "No tasks selected"
        redirect(default)
    if isinstance(request.vars.t_records, str):
        t = [request.vars.t_records]
    else:
        t = request.vars.t_records
    if action == 'disable':
        rtn = dbs(st.id.belongs(t)).update(enabled=False)
        if rtn:
            session.flash = "%s tasks disabled correctly" % rtn
        else:
            session.flash = "No tasks disabled"
        redirect(default)
    elif action == 'enable':
        rtn = dbs(st.id.belongs(t)).update(enabled=True)
        if rtn:
            session.flash = "%s tasks enabled correctly" % rtn
        else:
            session.flash = "No tasks enabled"
        redirect(default)
    elif action == 'delete':
        rtn = dbs(st.id.belongs(t)).delete()
        if rtn:
            session.flash = "%s tasks deleted" % rtn
        else:
            session.flash = "No tasks deleted"
        redirect(default)
    elif action == 'clone':
        requeued = []
        tasks = dbs(st.id.belongs(t)).select()
        for row in tasks:
            res = requeue_task(st, row)
            if res:
                requeued.append(requeued)
        if requeued:
            session.flash = "%s tasks successfully requeued" % (len(requeued))
        else:
            session.flash = "Cloning failed"

    redirect(default)


@auth.requires_signature()
def tasks():

    c = cache_tasks_counts(st)

    return dict(c=c)

@auth.requires_signature()
def task_group():
    c = cache_tasks_counts(st)
    group_name, status = request.args(0), request.args(1)
    if not group_name:
        return ''
    paginate = 10
    try:
        page = int(request.vars.page or 1)-1
    except ValueError:
        page = 0
    limitby = (paginate*page,paginate*(page+1))
    q = (st.group_name == group_name)
    if status:
        q = q & (st.status == status)
        if group_name in c and status in c[group_name]:
            total = c[group_name][status]['count']
        else:
            total = 0
    else:
        if group_name in c:
            total = sum([a['count'] for a in c[group_name].values()])
        else:
            total = 0
    qfilter = request.vars.qfilter
    if qfilter:
        parts = []
        fields = [st.task_name, st.group_name, st.function_name, st.uuid, st.args, st.vars, st.assigned_worker_name]
        for a in fields:
            parts.append(a.contains(qfilter))
            qf = reduce(lambda a, b: a | b, parts)
        q = q & qf
    tasks = dbs(q).select(limitby=limitby, orderby=st.next_run_time)
    for row in tasks:
        row.status_ = nice_task_status(row.status)

    BASEURL = URL("plugin_cs_monitor", "tactions", user_signature=True)
    return dict(tasks=tasks, paginate=paginate, total=total, page=page, BASEURL=BASEURL)

def cache_tasks_counts(t):
    c = t.id.count()
    res = dbs(t.id > 0).select(c, t.group_name, t.status, groupby=t.group_name|t.status)
    rtn = Storage()
    for row in res:
        k = row.scheduler_task.group_name
        s = row.scheduler_task.status
        if k in rtn:
            rtn[k][s] = { 'count' : row[c], 'pretty' : nice_task_status(s)}
        else:
            rtn[k] = {s : { 'count' : row[c], 'pretty' : nice_task_status(s)}}
    return rtn

@auth.requires_signature()
def task_details():
    id = request.args(0)
    task = dbs(st.id == id).select().first()
    if not task:
        return ''
    task.status_ = nice_task_status(task.status)
    return dict(task=task, st=st)

@auth.requires_signature()
def run_details():
    task_id = request.args(0)
    if not task_id:
        return ''
    paginate = 10
    try:
        page = int(request.vars.page or 1)-1
    except ValueError:
        page = 0
    limitby = (paginate*page,paginate*(page+1))
    total = dbs(sr.task_id == task_id).count()
    q = sr.task_id == task_id
    qfilter = request.vars.qfilter
    if qfilter:
        parts = []
        fields = [sr.status, sr.run_result, sr.run_output, sr.traceback, sr.worker_name]
        for a in fields:
            parts.append(a.contains(qfilter))
            qf = reduce(lambda a, b: a | b, parts)
        q = q & qf
    runs = dbs(q).select(orderby=~sr.stop_time|~sr.id, limitby=limitby)
    for row in runs:
        row.status_ = nice_task_status(row.status)
    return dict(runs=runs, paginate=paginate, total=total, page=page)

@auth.requires_signature()
def run_traceback():
    run_id = request.args(0)
    if not run_id:
        return ''
    rtn = dbs(sr.id == run_id).select(sr.traceback).first()
    if not rtn:
        return ''
    return CODE(rtn.traceback)

@auth.requires_signature()
def edit_task():
    task_id = request.args(0)
    if not task_id:
        return ''
    task = dbs(st.id == task_id).select().first()
    if not task:
        return ''
    if request.args(1) == 'delete':
        task.delete_record()
        session.flash = 'Task deleted correctly'
        redirect(URL('index'))
    elif request.args(1) == 'clone':
        result = requeue_task(st, task)
        if result:
            session.flash = 'Task requeued correctly'
            redirect(URL('task_details', args=result, user_signature=True))
        else:
            session.flash = 'Task clone failed'
            redirect(URL('edit_task', args=task_id, user_signature=True))
    elif request.args(1) == 'new':
        st.function_name.default = task.function_name
        st.task_name.default = task.task_name
        st.group_name.default = task.group_name
        task = None
    form = SQLFORM(st, task, formstyle=mybootstrap)
    if form.process().accepted:
        response.flash = 'Updated correctly'
    elif form.errors:
        response.flash = 'Errors detected'
    return dict(form=form, task=task)

def gb_duration(q):
    #byduration
    count_ = sr.id.count()
    status_ = sr.status
    duration_g = sr.stop_time.epoch() - sr.start_time.epoch()

    gb_duration_rows = dbs(q).select(count_, status_, duration_g, groupby=status_|duration_g, orderby=status_|duration_g)

    #convert to duration series
    gb_duration_series = {}
    for row in gb_duration_rows:
        status = row.scheduler_run.status
        duration = row[duration_g]
        howmany = row[count_]
        if status not in gb_duration_series:
            gb_duration_series[status] = {duration : howmany}
        else:
            if duration not in gb_duration_series[status]:
                gb_duration_series[status][duration] = howmany

    jgb_duration_series = []
    for k,v in gb_duration_series.items():
        jgb_duration_series.append(
                {'label': k, 'data' : [[kk,vv] for kk,vv in v.items()], 'color' : graph_colors_task_status(k)}
            )

    return gb_duration_rows, jgb_duration_series

def gb_status(q):
    #bystatus
    count_ = sr.id.count()
    status_ = sr.status
    gb_status_rows = dbs(q).select(count_, status_, groupby=status_, orderby=status_)
    gb_status_series = {}
    for row in gb_status_rows:
        status = row.scheduler_run.status
        howmany = row[count_]
        gb_status_series[status] = howmany

    jgb_status_series = []
    for k,v in gb_status_series.items():
        jgb_status_series.append(
            {'label' : k, 'color' : graph_colors_task_status(k), 'data' : (k,v)}
        )

    return gb_status_rows, jgb_status_series

def bydate(q):
    #by period
    count_ = sr.id.count()
    status_ = sr.status
    d = sr.start_time.year()|sr.start_time.month()|sr.start_time.day()
    gb_when_rows = dbs(q).select(count_, status_, sr.start_time.year(), sr.start_time.month(), sr.start_time.day(), groupby=status_|d, orderby=status_|d)

    gb_when_series = {}
    for row in gb_when_rows:
        status = row.scheduler_run.status
        howmany = row[count_]
        refdate = row[sr.start_time.year()], row[sr.start_time.month()], row[sr.start_time.day()]
        refdate = datetime.date(*refdate).strftime('%Y-%m-%d')
        if status not in gb_when_series:
            gb_when_series[status] = {refdate : howmany}
        else:
            gb_when_series[status][refdate] = howmany

    jgb_when_series = []
    for k, v in gb_when_series.items():
        jgb_when_series.append(
            {'label': k, 'data' : [[kk,vv] for kk,vv in v.items()], 'color' : graph_colors_task_status(k)}
        )

    return gb_when_rows, jgb_when_series

def byday(q, day):
    #by period
    count_ = sr.id.count()
    status_ = sr.status
    d = sr.start_time.hour()|sr.start_time.minutes()
    gb_whend_rows = dbs(q).select(count_, status_, sr.start_time.hour(), sr.start_time.minutes(), groupby=status_|d, orderby=status_|d)

    gb_whend_series = {}
    for row in gb_whend_rows:
        status = row.scheduler_run.status
        howmany = row[count_]
        refdate = day.year, day.month, day.day, row[sr.start_time.hour()], row[sr.start_time.minutes()], 0
        refdate = datetime.datetime(*refdate).strftime('%Y-%m-%d %H:%M')
        if status not in gb_whend_series:
            gb_whend_series[status] = {refdate : howmany}
        else:
            gb_whend_series[status][refdate] = howmany

    jgb_whend_series = []
    for k, v in gb_whend_series.items():
        jgb_whend_series.append(
            {'label': k, 'data' : [[kk,vv] for kk,vv in v.items()], 'color' : graph_colors_task_status(k)}
        )

    return gb_whend_rows, jgb_whend_series


@auth.requires_signature()
def analyze_task():
    task_id = request.args(0)
    if not task_id:
        return ''
    task = dbs(st.id == task_id).select().first()

    if not task:
        return ''

    q = sr.task_id == task_id
    first_run = dbs(q).select(sr.start_time, orderby=sr.start_time, limitby=(0,1)).first()

    last_run = dbs(q).select(sr.start_time, orderby=~sr.start_time, limitby=(0,1)).first()

    if len(request.args) >= 2:
        if request.args(1) == 'byfunction':
            q = sr.task_id.belongs(dbs(st.function_name == task.function_name)._select(st.id))
        elif request.args(1) == 'bytaskname':
            q = sr.task_id.belongs(dbs(st.task_name == task.task_name)._select(st.id))
        elif request.args(1) == 'this':
            q = sr.task_id == task_id
    if len(request.args) == 4 and request.args(2) == 'byday':
            daysback = int(request.args(3))
            now = s.utc_time and request.utcnow or request.now
            day = now.date() - timed(days=daysback)
            q = q & ((sr.start_time >= day) & (sr.start_time < day + timed(days=1)))

    gb_duration_rows, jgb_duration_series = gb_duration(q)
    jgb_duration_series = dumps(jgb_duration_series)

    gb_status_rows, jgb_status_series = gb_status(q)
    jgb_status_series = dumps(jgb_status_series)

    gb_when_rows, jgb_when_series = bydate(q)
    jgb_when_series = dumps(jgb_when_series)


    if len(request.args) == 4 and request.args(2) == 'byday':
        gb_whend_rows, jgb_whend_series = byday(q, day)
        jgb_whend_series = dumps(jgb_whend_series)
    else:
        jgb_whend_series = dumps([[]])
    return locals()
