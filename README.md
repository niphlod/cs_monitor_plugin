ComfortScheduler Monitor
=================

Since Web2py had its own scheduler, too many peoples asked for an embedded monitoring solution.
ComfortScheduler it's just my way of defining it. 
It bakes a lot of features and relies on a RDBMS, which most of web apps have anyway in their stack.   
Right now the plugin scans the scheduler's tables, and it's a first step towards a more "precise" analyzing solution.
Please try it and report back your findings.

INSTRUCTIONS:
 - download it and merge with your app's code
 - no cache is used ATM, but I'm planning to use that to avoid db pressure. Change in controllers/plugin_cs_monitor.py the lines
    ```python
    sc_cache = cache.ram
    GROUPING_MODE = 'database' # or 'python'
    ANALYZE_CACHE_TIME = 60
    TASKS_SUMMARY_CACHE_TIME = 10
    ```

    to match your preferences
    
    ```python
    sc_cache = cache.ram #your cache backend
    GROUPING_MODE = 'database' # or 'python', to save the db from some heavy queries
    ANALYZE_CACHE_TIME = 60 #how many seconds cache the queries done to analyze the task
    TASKS_SUMMARY_CACHE_TIME = 10 #how many seconds cache the queries for the task summary on the index page
    ```
 
 - the index() function is just a placeholder, every URL is generated with user_signature, so change the permission according to your requirements only in the index() function. 

    ```python
    @auth.requires_login()
    def index():
        return dict()
    ```
    e.g to
    
    ```python
    @auth.requires_membership('superadministrators')
    def index():
        return dict()
    ```
        

TODO:
- [x] Groupings can be done in python too, to avoid db pressure
- [x] analyze_task works scanning scheduler_run results. It should detect automatically if no runs are there and switch groupings.
- [ ] add REST interface ?

