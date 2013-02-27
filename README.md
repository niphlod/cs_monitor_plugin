ComfortScheduler Monitor
=================

Since Web2py had its own scheduler, too many peoples asked for an embedded monitoring solution.
ComfortScheduler it's just my way of defining it. 
It bakes a lot of features and relies on a RDBMS, which most of web apps have anyway in their stack.   
Right now the plugin scans the scheduler's tables, and it's a first step towards a more "precise" analyzing solution.
Please try it and report back your findings.

INSTRUCTIONS:
 - download it and merge with your app's code
 - no cache is used ATM, but I'm planning to use that to avoid db pressure. Change in controllers/plugin_cs_monitor.py the line
    ```python
    ##Configure start
    sc_cache = cache.ram
    ##Configure end
    ```

    to match you preferred cache
    ```python
    ##Configure start
    sc_cache = cache.disk
    ##Configure end
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
- [ ] Groupings can be done in python too, to avoid db pressure
- [ ] analyze_task works scanning scheduler_run results. It should detect automatically if no runs are there and switch groupings.
- [ ] add REST interface ?

