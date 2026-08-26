# Generated Phase 3 workflow reference

## Important status

The corrected, working workflow is currently on the user's Windows machine. This generated
reference predates a manual repair made in UiPath Studio and should not be treated as the latest
working copy unless that corrected Windows project has been copied back here.

In the original generated `Main.xaml`, UiPath displayed an unrendered `ErrorActivity` directly
below **Record Request Start**. The working Windows copy was repaired by deleting that placeholder
and adding a proper **Try Catch**:

- The Try sequence performs the HTTP request, records response time and status, deserializes JSON,
  and classifies Healthy or Degraded.
- The Catch is `System.Exception`, uses the variable `exception`, and classifies the service as
  Down while recording the exception type and message.
- The Finally section may remain empty.

Do not overwrite the working Windows project with this directory without first backing it up.

## Import procedure

1. Close UiPath Studio or close the `ServerMonitor` project.
2. Back up the current Windows project folder.
3. Copy `Main.xaml`, `project.json`, and `entry-points.json` from this folder into the Windows project folder.
4. Reopen `project.json` in UiPath Studio and allow dependencies to restore.
5. Confirm `UiPath.WebAPI.Activities 2.5.2` and `UiPath.System.Activities 26.6.3` are resolved.
6. Open `Main.xaml`, check for the ErrorActivity described above, and repair it if necessary.
7. Select **Analyze File**, then run it with all demo services healthy.

The workflow defaults to 18 cycles at a 10-second interval. Change the `Set Maximum Cycles` and `Set Poll Interval Seconds` Assign activities near the top if needed.

The CSV log is created in the Windows project execution directory with a unique name such as `monitoring-log-<runId>.csv`.

Phase 4 has not started. Do not add Gmail credentials directly to any generated file.
