ComfortScheduler Monitor
=================

Since Web2py had its own scheduler, too many peoples asked for an embedded monitoring solution.
ComfortScheduler it's just my way of defining it. 
It bakes a lot of features and relies on a RDBMS, which most of web apps have anyway in their stack.   
Right now the plugin scans the scheduler's tables, and it's a first step towards a more "precise" analyzing solution.
Please try it and report back your findings.

INSTRUCTIONS:
 - download it and merge with your app's code
 - change in controllers/plugin_cs_monitor.py the lines
    ```python
    sc_cache = cache.ram
    st = db.scheduler_task
    sw = db.scheduler_worker
    sr = db.scheduler_run
    s = scheduler
    ```

    to match those elements in your codebase (maybe you're running a scheduler in a separate db2, and you named it "myscheduler"), so the code should be
    ```python
    sc_cache = cache.ram
    st = db2.scheduler_task
    sw = db2.scheduler_worker
    sr = db2.scheduler_run
    s = myscheduler
    ```


TODO:
- [ ] Groupings can be done in python too, to avoid db pressure
- [ ] analyze_task works scanning scheduler_run results. It should detect automatically if no runs are there and switch groupings.
- [ ] add REST interface ?



