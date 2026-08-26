# Importing the generated Phase 3 workflow

1. Close UiPath Studio or close the `ServerMonitor` project.
2. Back up the current Windows project folder.
3. Copy `Main.xaml`, `project.json`, and `entry-points.json` from this folder into the Windows project folder.
4. Reopen `project.json` in UiPath Studio and allow dependencies to restore.
5. Open `Main.xaml` and select **Analyze File**, then run it with all demo services healthy.

The workflow defaults to 18 cycles at a 10-second interval. Change the `Set Maximum Cycles` and `Set Poll Interval Seconds` Assign activities near the top if needed.

The CSV log is created in the Windows project execution directory with a unique name such as `monitoring-log-<runId>.csv`.

