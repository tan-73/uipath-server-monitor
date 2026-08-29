few changes I want - 
1. the interactive visualiser demo running on the server is sometimes too late to register keystrokes such as "1", or "R" or "3" and there's a lot of delay. Try fixing this issue. 
2. i feel it will be better for certain issues (such as degraded, or full down) to have popups on UiPath, instead of just writing in console output
3. create 2 more services with different levels of degradation if possible (and different HTTP codes such as 404, etc)
4. one service should be monitored, where that service has a certain web UI, and is accessible when healthy, but when degraded, shows an error page. (maybe any pre existing service such as trillium notes, or hedgedoc, etc)


later phases -
1. implement an unattended uipath robot to constantly monitor services
2. when a service goes down, uipath must attempt to restart a service (implement a clean mechanism for this)
3. if possible, connect to any service like uptime kuma for better monitoring

## SMTP implementation follow-up

- SMTP connectivity practice is complete using the UiPath Integration Service connection.
- SMTP transition alerts are implemented on the smtp-implement branch.
- Gamma hard-outage CRITICAL alert has been verified from Windows, including connection-refused
  details and Run ID.
- Run Analyze File and Windows runtime tests for warning, critical, escalation, recovery,
  duplicate suppression, and SMTP failure handling before closing Phase 4.
