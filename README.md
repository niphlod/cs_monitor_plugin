ComfortScheduler Monitor
=================

Since Web2py has its own scheduler, too many peoples asked for an embedded monitoring solution.
Right now the plugin scans the scheduler's tables, and it's a first step towards a more "precise" analyzing solution.
Please try it and report back your findings.

TODO:
 - groupings can be done in python too, to avoid db pressure
 - analyze_task works scanning scheduler_run results. It should detect automatically if no runs are there and switch groupings.
 - add REST interface ?



